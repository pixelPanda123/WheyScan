from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.listings.models import (
    Listing,
    PriceHistory,
    Store,
)
from app.domains.products.models import Product


class StoreRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, store: Store) -> Store:
        self.db.add(store)
        self.db.commit()
        self.db.refresh(store)
        return store

    def get_all(self) -> list[Store]:
        stmt = select(Store).order_by(Store.id)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, store_id: int) -> Store | None:
        return self.db.get(Store, store_id)

    def get_by_name(self, name: str) -> Store | None:
        stmt = select(Store).where(Store.name == name)
        return self.db.scalar(stmt)

    def has_listings(self, store_id: int) -> bool:
        stmt = select(Listing.id).where(Listing.store_id == store_id).limit(1)
        return self.db.scalar(stmt) is not None

    def update(self, store: Store) -> Store:
        self.db.commit()
        self.db.refresh(store)
        return store

    def delete(self, store: Store) -> None:
        self.db.delete(store)
        self.db.commit()


class ListingRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, listing: Listing) -> Listing:
        self.db.add(listing)
        self.db.commit()
        self.db.refresh(listing)
        return listing

    def get_by_id(self, listing_id: int) -> Listing | None:
        return self.db.get(Listing, listing_id)

    def product_exists(self, product_id: int) -> bool:
        return self.db.get(Product, product_id) is not None

    def store_exists(self, store_id: int) -> bool:
        return self.db.get(Store, store_id) is not None

    def get_by_product_and_store(
        self,
        product_id: int,
        store_id: int,
    ) -> Listing | None:
        stmt = select(Listing).where(
            Listing.product_id == product_id,
            Listing.store_id == store_id,
        )
        return self.db.scalar(stmt)

    def get_all(self) -> list[Listing]:
        stmt = select(Listing).order_by(Listing.id)
        return list(self.db.scalars(stmt).all())

    def get_by_product(self, product_id: int) -> list[Listing]:
        stmt = (
            select(Listing)
            .where(Listing.product_id == product_id)
            .order_by(Listing.id)
        )
        return list(self.db.scalars(stmt).all())

    def update(self, listing: Listing) -> Listing:
        self.db.commit()
        self.db.refresh(listing)
        return listing

    def delete(self, listing: Listing) -> None:
        self.db.delete(listing)
        self.db.commit()


class PriceHistoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, history: PriceHistory) -> PriceHistory:
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def get_by_id(self, history_id: int) -> PriceHistory | None:
        return self.db.get(PriceHistory, history_id)

    def get_listing_history(self, listing_id: int) -> list[PriceHistory]:
        stmt = (
            select(PriceHistory)
            .where(PriceHistory.listing_id == listing_id)
            .order_by(PriceHistory.valid_from.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_current_for_listing(self, listing_id: int) -> PriceHistory | None:
        stmt = (
            select(PriceHistory)
            .where(
                PriceHistory.listing_id == listing_id,
                PriceHistory.valid_to.is_(None),
            )
            .order_by(PriceHistory.valid_from.desc())
        )
        return self.db.scalar(stmt)

    def update(self, history: PriceHistory) -> PriceHistory:
        self.db.commit()
        self.db.refresh(history)
        return history

    def delete(self, history: PriceHistory) -> None:
        self.db.delete(history)
        self.db.commit()
