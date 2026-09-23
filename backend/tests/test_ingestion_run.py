from dataclasses import replace
from types import SimpleNamespace

from sqlalchemy import func, select

from app.domains.listings.models import Listing, PriceHistory, Store
from app.domains.products.models import Product
from app.ingestion import run
from app.ingestion.scraper.retailers.optimum_nutrition.extractor import (
    OptimumNutritionExtractor,
)
from app.ingestion.services.ingestion_service import IngestionService


def summary(stats):
    keys = (
        "seen", "ingested", "new_products", "matched_existing",
        "new_listings", "updated_listings", "price_changes",
    )
    return {key: stats[key] for key in keys}


# ----------------------------------------------------------------------
# Counting (no database)
# ----------------------------------------------------------------------

def result(created_product, created_listing, price_changed):
    return SimpleNamespace(
        created_product=created_product,
        created_listing=created_listing,
        price_changed=price_changed,
    )


def test_tally_counts_each_flag_independently():
    stats = run.new_stats()

    # Known product, but first time this store lists it (the ON case).
    run.tally(stats, result(False, True, True))
    # Brand-new product and listing.
    run.tally(stats, result(True, True, True))
    # Re-scrape, nothing changed.
    run.tally(stats, result(False, False, False))
    # Filtered out.
    run.tally(stats, None)

    assert stats["ingested"] == 3
    assert stats["filtered_out"] == 1
    assert stats["new_products"] == 1
    assert stats["matched_existing"] == 2
    assert stats["new_listings"] == 2
    assert stats["updated_listings"] == 1
    assert stats["price_changes"] == 2


def test_summary_always_contains_every_key():
    assert set(run.STAT_KEYS) <= set(run.new_stats())


def test_check_against_db_flags_disagreement():
    stats = run.new_stats()
    stats["new_listings"] = 0

    assert not run.check_against_db(
        "optimum_nutrition",
        stats,
        {"products": 5, "listings": 0},
        {"products": 5, "listings": 5},
    )


# ----------------------------------------------------------------------
# Full runs against Postgres
# ----------------------------------------------------------------------

def source(store_name, items):
    return run.RetailerSource(store_name, f"https://{store_name}", lambda c, s, d: iter(items))


def ingest(db, store_name, items):
    if db.scalar(select(Store).where(Store.name == store_name)) is None:
        db.add(Store(name=store_name, base_url=f"https://{store_name}", active=True))
        db.commit()

    before = run.db_counts(db, store_name)
    stats = run.ingest_retailer(
        db,
        IngestionService(db),
        source(store_name, items),
        client=None,
        limit=None,
        delay=0,
        dry_run=False,
    )
    assert run.check_against_db(store_name, stats, before, run.db_counts(db, store_name))
    return stats


def on_items(on_client, on_products):
    extractor = OptimumNutritionExtractor(on_client)
    return [extractor.extract(url) for url in on_products]


def test_healthkart_first_run_and_rerun(db, healthkart_products):
    first = ingest(db, "healthkart", healthkart_products)
    again = ingest(db, "healthkart", healthkart_products)

    assert summary(first) == {
        "seen": 5, "ingested": 5, "new_products": 5, "matched_existing": 0,
        "new_listings": 5, "updated_listings": 0, "price_changes": 5,
    }
    assert summary(again) == {
        "seen": 5, "ingested": 5, "new_products": 0, "matched_existing": 5,
        "new_listings": 0, "updated_listings": 5, "price_changes": 0,
    }


def test_optimum_nutrition_first_run_reports_new_listings(
    db, healthkart_products, on_client, on_products
):
    ingest(db, "healthkart", healthkart_products)

    stats = ingest(db, "optimum_nutrition", on_items(on_client, on_products))

    # Five listings are created for the ON store and each gets its first price.
    assert stats["new_listings"] == 5
    assert stats["price_changes"] == 5
    assert stats["new_products"] + stats["matched_existing"] == 5

    listings = db.scalars(
        select(Listing).join(Store).where(Store.name == "optimum_nutrition")
    ).all()
    assert len(listings) == 5

    for listing in listings:
        product = listing.product
        assert product.name == "Gold Standard 100%"
        assert "|" not in product.name
        assert product.flavour == "Chocolate"

    assert sorted(int(l.product.weight) for l in listings) == [152, 454, 907, 1700, 2270]


def test_optimum_nutrition_rerun_matches_its_own_listings(
    db, healthkart_products, on_client, on_products
):
    ingest(db, "healthkart", healthkart_products)
    ingest(db, "optimum_nutrition", on_items(on_client, on_products))

    again = ingest(db, "optimum_nutrition", on_items(on_client, on_products))

    # This is the output reported for the second ON run: correct, because
    # the listings were created by the first run.
    assert summary(again) == {
        "seen": 5, "ingested": 5, "new_products": 0, "matched_existing": 5,
        "new_listings": 0, "updated_listings": 5, "price_changes": 0,
    }


def test_price_change_closes_previous_history_row(db, healthkart_products):
    ingest(db, "healthkart", healthkart_products)

    cheaper = [replace(healthkart_products[0], current_price=3499.0)]
    stats = ingest(db, "healthkart", cheaper)

    assert stats["price_changes"] == 1

    listing = db.scalar(select(Listing).where(Listing.retailer_product_id == "84971"))
    history = db.scalars(
        select(PriceHistory)
        .where(PriceHistory.listing_id == listing.id)
        .order_by(PriceHistory.id)
    ).all()

    assert [float(h.price) for h in history] == [3999.0, 3499.0]
    assert history[0].valid_to is not None
    assert history[1].valid_to is None
    assert float(listing.current_price) == 3499.0


def test_known_listing_keeps_its_product_when_names_change(db, healthkart_products):
    ingest(db, "healthkart", healthkart_products)

    # Simulate a stored product name that current normalization no longer
    # produces (e.g. rows written before a normalizer fix).
    listing = db.scalar(select(Listing).where(Listing.retailer_product_id == "143771"))
    listing.product.name = "Gold Standard 100% | Double Rich | s"
    db.commit()

    stats = ingest(db, "healthkart", healthkart_products)

    assert stats["new_products"] == 0
    assert db.scalar(select(func.count(Product.id))) == 5
