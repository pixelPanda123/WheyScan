from datetime import datetime

from app.domains.listings.models import (
    Store,
    Listing,
    PriceHistory,
)

from app.domains.listings.repository import (
    StoreRepository,
    ListingRepository,
    PriceHistoryRepository,
)

from app.domains.listings.schemas import (
    StoreCreate,
    ListingCreate,
)


class StoreService:

    def __init__(self, repository: StoreRepository):
        self.repository = repository

    def create_store(self, data: StoreCreate):

        store = Store(
            name=data.name,
            base_url=data.base_url,
            active=data.active,
        )

        return self.repository.create(store)

    def list_stores(self):

        return self.repository.get_all()


class ListingService:

    def __init__(
        self,
        listing_repo: ListingRepository,
        history_repo: PriceHistoryRepository,
    ):
        self.listing_repo = listing_repo
        self.history_repo = history_repo

    def create_listing(self, data: ListingCreate):

        listing = Listing(
            product_id=data.product_id,
            store_id=data.store_id,
            url=data.url,
            current_price=data.current_price,
            availability=data.availability,
            last_scraped=datetime.utcnow(),
        )

        listing = self.listing_repo.create(listing)

        history = PriceHistory(
            listing_id=listing.id,
            price=listing.current_price,
            valid_from=datetime.utcnow(),
            valid_to=None,
        )

        self.history_repo.create(history)

        return listing

    def get_listing(self, listing_id: int):

        return self.listing_repo.get_by_id(listing_id)

    def list_listings(self):

        return self.listing_repo.get_all()

    def listing_history(self, listing_id: int):

        return self.history_repo.get_listing_history(listing_id)