from dataclasses import dataclass
from decimal import Decimal

from slugify import slugify
from sqlalchemy.orm import Session

from app.domains.listings.models import Listing, PriceHistory, Store
from app.domains.listings.repositories.repository import (
    ListingRepository,
    PriceHistoryRepository,
    StoreRepository,
)
from app.domains.products.models import Brand, Product
from app.domains.products.repositories.brand_repository import BrandRepository
from app.domains.products.repositories.product_repository import ProductRepository
from app.ingestion.filtering.catalog_filter import CatalogFilter
from app.ingestion.matching.matcher import ProductMatcher
from app.ingestion.normalization.normalizer import ProductNormalizer
from app.ingestion.normalization.types import NormalizedProduct
from app.ingestion.scraper.base.types import RawProduct


@dataclass(slots=True)
class IngestResult:
    product: Product
    listing: Listing
    created_product: bool
    created_listing: bool
    price_changed: bool
    match_score: float


class IngestionService:
    """
    Turns one scraped RawProduct into Product / Listing / PriceHistory rows.

    This service never commits. It only flushes, so the caller decides the
    transaction boundary (see app.ingestion.run, which wraps every product
    in its own savepoint). If the caller rolls back, it must call
    reset_cache() because cached catalog entries may no longer exist.
    """

    def __init__(self, db: Session):
        self.db = db

        self.brand_repo = BrandRepository(db)
        self.product_repo = ProductRepository(db)

        self.store_repo = StoreRepository(db)
        self.listing_repo = ListingRepository(db)
        self.price_history_repo = PriceHistoryRepository(db)

        self._stores: dict[str, Store] = {}

        # (db product, its normalized form); loaded once, then kept in sync
        self._catalog: list[tuple[Product, NormalizedProduct]] | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ingest(self, raw_product: RawProduct) -> IngestResult | None:

        # 1. Filter on the RAW name. The name normalizer strips words such
        #    as "whey" and "protein", so filtering after normalization would
        #    reject every protein product.
        if not CatalogFilter.accept(raw_product):
            return None

        # 2. Normalize
        normalized = ProductNormalizer.normalize(raw_product)

        # Stripping brand/"whey"/"protein" can leave nothing (e.g.
        # "Nakpro Whey Protein Concentrate"); keep the raw name instead.
        if not normalized.name and raw_product.name:
            normalized.name = raw_product.name.strip()

        # 3. Store
        store = self._get_store(normalized.retailer)

        # 4. Match against canonical catalog
        catalog = self._get_catalog()

        matched, score = ProductMatcher.match(
            normalized,
            [entry[1] for entry in catalog],
        )

        # 5. Resolve canonical Product
        if matched is not None:
            product = next(p for p, n in catalog if n is matched)
            created_product = False
        else:
            product = self._create_product(normalized)
            catalog.append((product, self._product_to_normalized(product)))
            created_product = True

        # 6. Listing
        listing, created_listing = self._upsert_listing(
            product,
            store,
            normalized,
        )

        # 7. Price history
        price_changed = self._update_price_history(listing, normalized)

        return IngestResult(
            product=product,
            listing=listing,
            created_product=created_product,
            created_listing=created_listing,
            price_changed=price_changed,
            match_score=score.score,
        )

    def reset_cache(self) -> None:
        self._stores.clear()
        self._catalog = None

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------

    def _get_store(self, name: str) -> Store:

        if name not in self._stores:
            store = self.store_repo.get_by_name(name)

            if store is None:
                raise ValueError(
                    f"Store not found: {name!r}. "
                    "Run app.ingestion.run, which seeds stores first."
                )

            self._stores[name] = store

        return self._stores[name]

    def _get_catalog(self) -> list[tuple[Product, NormalizedProduct]]:

        if self._catalog is None:
            self._catalog = [
                (product, self._product_to_normalized(product))
                for product in self.product_repo.get_all()
            ]

        return self._catalog

    def _product_to_normalized(self, product: Product) -> NormalizedProduct:

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

            scraped_at=product.created_at,
        )

    # ------------------------------------------------------------------
    # Writes (flush only, never commit)
    # ------------------------------------------------------------------

    def _get_or_create_brand(self, name: str) -> Brand:

        brand = self.brand_repo.get_by_name(name)

        if brand is None:
            brand = Brand(name=name)
            self.db.add(brand)
            self.db.flush()

        return brand

    def _create_product(self, normalized: NormalizedProduct) -> Product:

        if not normalized.brand:
            raise ValueError(
                f"Cannot create product without brand: {normalized.name!r}"
            )

        if not normalized.name:
            raise ValueError("Cannot create product with an empty name")

        brand = self._get_or_create_brand(normalized.brand)

        product = Product(
            brand_id=brand.id,
            name=normalized.name,
            slug=self._unique_slug(normalized),
            protein_type=normalized.protein_type,
            flavour=normalized.flavour,
            weight=normalized.weight_g,
            weight_unit="g" if normalized.weight_g is not None else None,
            image_url=normalized.image_url,
        )
        product.brand = brand

        self.db.add(product)
        self.db.flush()

        return product

    def _upsert_listing(
        self,
        product: Product,
        store: Store,
        normalized: NormalizedProduct,
    ) -> tuple[Listing, bool]:

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

        available = normalized.availability == "In Stock"

        if listing is not None:
            # A listing keeps the product it was first matched to. Moving it
            # could collide with the (product_id, store_id) unique constraint.
            if listing.retailer_product_id is None:
                listing.retailer_product_id = normalized.retailer_product_id

            listing.url = normalized.product_url
            listing.availability = available
            listing.last_scraped = normalized.scraped_at

            self.db.flush()
            return listing, False

        listing = Listing(
            product_id=product.id,
            store_id=store.id,
            retailer_product_id=normalized.retailer_product_id,
            url=normalized.product_url,
            current_price=normalized.current_price,
            availability=available,
            last_scraped=normalized.scraped_at,
        )

        self.db.add(listing)
        self.db.flush()

        return listing, True

    def _update_price_history(
        self,
        listing: Listing,
        normalized: NormalizedProduct,
    ) -> bool:

        price = Decimal(str(normalized.current_price))
        timestamp = normalized.scraped_at

        current = self.price_history_repo.get_current_for_listing(listing.id)

        if current is not None and Decimal(str(current.price)) == price:
            return False

        if current is not None:
            current.valid_to = timestamp

        listing.current_price = price

        self.db.add(
            PriceHistory(
                listing_id=listing.id,
                price=price,
                valid_from=timestamp,
                valid_to=None,
            )
        )
        self.db.flush()

        return True

    def _unique_slug(self, normalized: NormalizedProduct) -> str:

        base = slugify(
            " ".join(
                str(part)
                for part in (
                    normalized.brand,
                    normalized.name,
                    f"{normalized.weight_g}g" if normalized.weight_g else None,
                    normalized.flavour,
                )
                if part
            )
        )[:240]

        slug = base
        suffix = 2

        while self.product_repo.get_by_slug(slug) is not None:
            slug = f"{base}-{suffix}"
            suffix += 1

        return slug
