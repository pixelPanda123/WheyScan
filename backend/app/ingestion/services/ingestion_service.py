from datetime import datetime

from sqlalchemy.orm import Session

from app.domains.products.models import Product
from app.domains.products.repositories.brand_repository import BrandRepository
from app.domains.products.repositories.product_repository import ProductRepository

from app.domains.listings.models import Listing, PriceHistory
from app.domains.listings.repositories.repository import (
    StoreRepository,
    ListingRepository,
    PriceHistoryRepository,
)

from app.ingestion.normalization.normalizer import ProductNormalizer
from app.ingestion.normalization.types import NormalizedProduct
from app.ingestion.filtering.catalog_filter import CatalogFilter
from app.ingestion.matching.matcher import ProductMatcher


class IngestionService:

    def __init__(self, db: Session):
        self.db = db

        self.brand_repo = BrandRepository(db)
        self.product_repo = ProductRepository(db)

        self.store_repo = StoreRepository(db)
        self.listing_repo = ListingRepository(db)
        self.price_history_repo = PriceHistoryRepository(db)

    def ingest(self, raw_product):

        # 1. Normalize
        normalized = ProductNormalizer.normalize(raw_product)

        # 2. Filter
        if not CatalogFilter.accept(normalized):
            return None

        # 3. Get retailer/store
        store = self.store_repo.get_by_name(
            normalized.retailer
        )

        if not store:
            raise ValueError(
                f"Store not found: {normalized.retailer}"
            )

        # 4. Load canonical catalog
        products = self.product_repo.get_all()

        catalog = [
            self._product_to_normalized(product)
            for product in products
        ]

        # 5. Match
        matched_product, match_score = ProductMatcher.match(
            normalized,
            catalog,
        )

        # 6. Resolve canonical Product
        if matched_product:
            product = self._find_db_product(
                matched_product,
                products,
            )
        else:
            product = self._create_product(normalized)

        # 7. Create/update listing
        listing = self._upsert_listing(
            product,
            store,
            normalized,
        )

        # 8. Update price history
        self._update_price_history(
            listing,
            normalized.current_price,
            normalized.scraped_at,
        )

        return product

    def _product_to_normalized(
        self,
        product: Product,
    ) -> NormalizedProduct:

        return NormalizedProduct(
            retailer="canonical",
            retailer_product_id=None,

            name=product.name,
            brand=product.brand.name if product.brand else None,

            weight_g=(
                int(product.weight)
                if product.weight is not None
                else None
            ),

            flavour=product.flavour,
            protein_type=product.protein_type,

            current_price=0,
            original_price=None,

            product_url="",
            image_url=product.image_url,

            availability=None,
            rating=None,
            review_count=None,

            scraped_at=datetime.utcnow(),
        )

    def _find_db_product(
        self,
        matched_product: NormalizedProduct,
        products: list[Product],
    ) -> Product:

        for product in products:

            if (
                product.name == matched_product.name
                and product.brand
                and product.brand.name == matched_product.brand
                and (
                    product.flavour == matched_product.flavour
                )
                and (
                    product.weight is None
                    or matched_product.weight_g is None
                    or int(product.weight)
                    == matched_product.weight_g
                )
            ):
                return product

        raise ValueError(
            "Matcher returned a product that could not be "
            "resolved to a database Product"
        )

    def _create_product(
        self,
        product: NormalizedProduct,
    ) -> Product:

        if not product.brand:
            raise ValueError(
                f"Cannot create product without brand: {product.name}"
            )

        brand = self.brand_repo.get_or_create(
            product.brand
        )

        db_product = Product(
            brand_id=brand.id,

            name=product.name,

            slug=self._generate_slug(product),

            protein_type=product.protein_type,

            flavour=product.flavour,

            weight=product.weight_g,
            weight_unit="g",

            image_url=product.image_url,
        )

        return self.product_repo.create(db_product)

    def _upsert_listing(
        self,
        product: Product,
        store,
        normalized: NormalizedProduct,
    ) -> Listing:

        listing = None

        if normalized.retailer_product_id:
            listing = self.listing_repo.get_by_store_and_retailer_product_id(
                store.id,
                normalized.retailer_product_id,
            )

        if listing is None:
            listing = self.listing_repo.get_by_product_and_store(
                product.id,
                store.id,
            )

        if listing:
            listing.product_id = product.id
            listing.url = normalized.product_url
            listing.current_price = normalized.current_price
            listing.availability = (
                normalized.availability == "In Stock"
            )
            listing.last_scraped = normalized.scraped_at

            return self.listing_repo.update(listing)

        listing = Listing(
            product_id=product.id,
            store_id=store.id,

            retailer_product_id=normalized.retailer_product_id,

            url=normalized.product_url,
            current_price=normalized.current_price,

            availability=(
                normalized.availability == "In Stock"
            ),

            last_scraped=normalized.scraped_at,
        )

        return self.listing_repo.create(listing)

    def _update_price_history(
        self,
        listing: Listing,
        price: float,
        timestamp: datetime,
    ):

        current = self.price_history_repo.get_current_for_listing(
            listing.id
        )

        if current and float(current.price) == price:
            return

        if current:
            current.valid_to = timestamp
            self.price_history_repo.update(current)

        history = PriceHistory(
            listing_id=listing.id,
            price=price,
            valid_from=timestamp,
            valid_to=None,
        )

        self.price_history_repo.create(history)

    def _generate_slug(
        self,
        product: NormalizedProduct,
    ) -> str:

        parts = [
            product.brand,
            product.name,
            str(product.weight_g) if product.weight_g else None,
            product.flavour,
        ]

        slug = "-".join(
            part.lower().replace(" ", "-")
            for part in parts
            if part
        )

        return slug