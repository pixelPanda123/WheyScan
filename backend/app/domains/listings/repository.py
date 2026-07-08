from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.listings.models import (
    Store,
    Listing,
    PriceHistory,
)


class StoreRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, store: Store) -> Store:
        self.db.add(store)
        self.db.commit()
        self.db.refresh(store)
        return store

    def get_all(self) -> list[Store]:
        stmt = select(Store)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, store_id: int) -> Store | None:
        return self.db.get(Store, store_id)


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

    def get_all(self) -> list[Listing]:
        stmt = select(Listing)
        return list(self.db.scalars(stmt).all())

    def get_by_product(self, product_id: int) -> list[Listing]:
        stmt = select(Listing).where(Listing.product_id == product_id)
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

    def get_listing_history(self, listing_id: int) -> list[PriceHistory]:
        stmt = (
            select(PriceHistory)
            .where(PriceHistory.listing_id == listing_id)
            .order_by(PriceHistory.valid_from.desc())
        )
        return list(self.db.scalars(stmt).all())