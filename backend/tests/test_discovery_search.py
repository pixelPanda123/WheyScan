from datetime import datetime

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.domains.discovery.repositories import DiscoveryRepository
from app.domains.discovery.services import DiscoveryService
from app.domains.listings.models import Listing, Store
from app.domains.products.models import Brand, Product


@pytest.fixture
def discovery_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False)()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def add_product(discovery_db, name, slug, brand, listings):
    brand_obj = discovery_db.scalar(select(Brand).where(Brand.name == brand))
    if brand_obj is None:
        brand_obj = Brand(name=brand)
        discovery_db.add(brand_obj)
        discovery_db.flush()

    product = Product(
        brand=brand_obj,
        name=name,
        slug=slug,
        protein_type="Whey Blend",
        flavour="Chocolate",
        weight=1000,
        weight_unit="g",
        image_url=f"https://images.example/{slug}.jpg",
    )
    discovery_db.add(product)
    discovery_db.flush()

    for index, listing in enumerate(listings, start=1):
        store = discovery_db.scalar(
            select(Store).where(Store.name == listing["store"])
        )
        if store is None:
            store = Store(
                name=listing["store"],
                base_url=f"https://{listing['store'].lower().replace(' ', '')}.example",
            )
            discovery_db.add(store)
            discovery_db.flush()

        discovery_db.add(
            Listing(
                product=product,
                store=store,
                retailer_product_id=f"{slug}-{index}",
                url=f"{store.base_url}/{slug}",
                current_price=listing["price"],
                availability=listing.get("availability", True),
                last_scraped=datetime(2026, 9, 23, 10, 0, 0),
            )
        )

    discovery_db.commit()
    return product


def search(discovery_db, **kwargs):
    return DiscoveryService(DiscoveryRepository(discovery_db)).search(**kwargs)


def test_product_with_two_retailers_is_returned(discovery_db):
    product = add_product(
        discovery_db,
        "Gold Standard 100% Whey",
        "gold-standard",
        "ON",
        [
            {"store": "HealthKart", "price": 4999},
            {"store": "Optimum Nutrition", "price": 4899},
        ],
    )

    results = search(discovery_db)

    assert [result.id for result in results] == [product.id]
    assert results[0].name == "Gold Standard 100% Whey"
    assert results[0].brand == "ON"
    assert results[0].image_url == "https://images.example/gold-standard.jpg"


def test_product_with_one_retailer_is_excluded(discovery_db):
    add_product(
        discovery_db,
        "Solo Whey",
        "solo-whey",
        "Solo",
        [{"store": "HealthKart", "price": 2999}],
    )

    assert search(discovery_db) == []


def test_multiple_retailer_listings_are_grouped_under_product(discovery_db):
    add_product(
        discovery_db,
        "Biozyme Whey",
        "biozyme-whey",
        "MuscleBlaze",
        [
            {"store": "HealthKart", "price": 3999},
            {"store": "MuscleBlaze", "price": 3799},
        ],
    )

    result = search(discovery_db)[0]

    assert len(result.listings) == 2
    assert {listing.store_name for listing in result.listings} == {
        "HealthKart",
        "MuscleBlaze",
    }
    assert {listing.product_url for listing in result.listings} == {
        "https://healthkart.example/biozyme-whey",
        "https://muscleblaze.example/biozyme-whey",
    }
    assert all(listing.price_per_100g is not None for listing in result.listings)


def test_search_and_filters_still_apply_to_comparison_products(discovery_db):
    matching = add_product(
        discovery_db,
        "Gold Standard 100% Whey",
        "gold-standard",
        "ON",
        [
            {"store": "HealthKart", "price": 4999},
            {"store": "Optimum Nutrition", "price": 4899},
        ],
    )
    add_product(
        discovery_db,
        "Biozyme Whey",
        "biozyme-whey",
        "MuscleBlaze",
        [
            {"store": "HealthKart", "price": 3999},
            {"store": "MuscleBlaze", "price": 3799},
        ],
    )
    add_product(
        discovery_db,
        "Gold Single Retailer Whey",
        "gold-single",
        "ON",
        [{"store": "HealthKart", "price": 2599}],
    )

    results = search(
        discovery_db,
        query="gold",
        brand_id=matching.brand_id,
        price_min=4800,
        store_id=1,
    )

    assert [result.id for result in results] == [matching.id]
    assert len(results[0].listings) == 2


def test_pagination_applies_to_canonical_products(discovery_db):
    add_product(
        discovery_db,
        "Alpha Whey",
        "alpha-whey",
        "A Brand",
        [{"store": "A Store", "price": 1000}, {"store": "B Store", "price": 1100}],
    )
    second = add_product(
        discovery_db,
        "Beta Whey",
        "beta-whey",
        "B Brand",
        [{"store": "C Store", "price": 2000}, {"store": "D Store", "price": 2100}],
    )
    add_product(
        discovery_db,
        "Gamma Whey",
        "gamma-whey",
        "C Brand",
        [{"store": "E Store", "price": 3000}, {"store": "F Store", "price": 3100}],
    )

    results = search(discovery_db, skip=1, limit=1)

    assert [result.id for result in results] == [second.id]
    assert len(results[0].listings) == 2


def test_empty_results_behave_cleanly(discovery_db):
    add_product(
        discovery_db,
        "Biozyme Whey",
        "biozyme-whey",
        "MuscleBlaze",
        [
            {"store": "HealthKart", "price": 3999},
            {"store": "MuscleBlaze", "price": 3799},
        ],
    )

    assert search(discovery_db, query="missing product") == []
