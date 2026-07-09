from datetime import datetime
from decimal import Decimal

from app.domains.listings.exceptions import (
    ListingAlreadyExistsError,
    ListingNotFoundError,
    ListingProductNotFoundError,
    ListingStoreNotFoundError,
    StoreAlreadyExistsError,
    StoreHasListingsError,
    StoreNotFoundError,
)
from app.domains.listings.models import (
    Listing,
    PriceHistory,
    Store,
)

from app.domains.listings.repositories import (
    StoreRepository,
    ListingRepository,
    PriceHistoryRepository,
)

from app.domains.listings.schemas import (
    ListingCreate,
    ListingUpdate,
    StoreCreate,
    StoreUpdate,
)


class StoreService:

    def __init__(self, repository: StoreRepository):
        self.repository = repository

    def create_store(self, data: StoreCreate):

        if self.repository.get_by_name(data.name):
            raise StoreAlreadyExistsError("Store already exists.")

        store = Store(
            name=data.name,
            base_url=data.base_url,
            active=data.active,
        )

        return self.repository.create(store)

    def list_stores(self):

        return self.repository.get_all()

    def get_store(self, store_id: int):

        store = self.repository.get_by_id(store_id)

        if not store:
            raise StoreNotFoundError("Store not found.")

        return store

    def update_store(
        self,
        store_id: int,
        data: StoreUpdate,
    ):

        store = self.repository.get_by_id(store_id)

        if not store:
            raise StoreNotFoundError("Store not found.")

        update_data = data.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"] is not None:
            existing = self.repository.get_by_name(update_data["name"])

            if existing and existing.id != store.id:
                raise StoreAlreadyExistsError("Store already exists.")

        for key, value in update_data.items():
            setattr(store, key, value)

        return self.repository.update(store)

    def delete_store(self, store_id: int):

        store = self.repository.get_by_id(store_id)

        if not store:
            raise StoreNotFoundError("Store not found.")

        if self.repository.has_listings(store_id):
            raise StoreHasListingsError("Store has listings.")

        self.repository.delete(store)


class ListingService:

    def __init__(
        self,
        listing_repo: ListingRepository,
        history_repo: PriceHistoryRepository,
    ):
        self.listing_repo = listing_repo
        self.history_repo = history_repo

    def create_listing(self, data: ListingCreate):

        if not self.listing_repo.product_exists(data.product_id):
            raise ListingProductNotFoundError("Product not found.")

        if not self.listing_repo.store_exists(data.store_id):
            raise ListingStoreNotFoundError("Store not found.")

        if self.listing_repo.get_by_product_and_store(
            data.product_id,
            data.store_id,
        ):
            raise ListingAlreadyExistsError("Listing already exists.")

        now = datetime.utcnow()

        listing = Listing(
            product_id=data.product_id,
            store_id=data.store_id,
            url=data.url,
            current_price=data.current_price,
            availability=data.availability,
            last_scraped=now,
        )

        listing = self.listing_repo.create(listing)

        history = PriceHistory(
            listing_id=listing.id,
            price=listing.current_price,
            valid_from=now,
            valid_to=None,
        )

        self.history_repo.create(history)

        return listing

    def get_listing(self, listing_id: int):

        listing = self.listing_repo.get_by_id(listing_id)

        if not listing:
            raise ListingNotFoundError("Listing not found.")

        return listing

    def list_listings(self):

        return self.listing_repo.get_all()

    def get_product_listings(self, product_id: int):

        if not self.listing_repo.product_exists(product_id):
            raise ListingProductNotFoundError("Product not found.")

        return self.listing_repo.get_by_product(product_id)

    def update_listing(
        self,
        listing_id: int,
        data: ListingUpdate,
    ):

        listing = self.listing_repo.get_by_id(listing_id)

        if not listing:
            raise ListingNotFoundError("Listing not found.")

        update_data = data.model_dump(exclude_unset=True)

        product_id = update_data.get("product_id", listing.product_id)
        store_id = update_data.get("store_id", listing.store_id)

        if (
            "product_id" in update_data
            and not self.listing_repo.product_exists(product_id)
        ):
            raise ListingProductNotFoundError("Product not found.")

        if (
            "store_id" in update_data
            and not self.listing_repo.store_exists(store_id)
        ):
            raise ListingStoreNotFoundError("Store not found.")

        if product_id != listing.product_id or store_id != listing.store_id:
            existing = self.listing_repo.get_by_product_and_store(
                product_id,
                store_id,
            )

            if existing and existing.id != listing.id:
                raise ListingAlreadyExistsError("Listing already exists.")

        now = datetime.utcnow()
        new_price = update_data.pop("current_price", None)

        for key, value in update_data.items():
            setattr(listing, key, value)

        if (
            new_price is not None
            and Decimal(str(new_price)) != Decimal(str(listing.current_price))
        ):
            current_history = self.history_repo.get_current_for_listing(listing.id)

            if current_history:
                current_history.valid_to = now
                self.history_repo.update(current_history)

            listing.current_price = new_price
            listing.last_scraped = now

            history = PriceHistory(
                listing_id=listing.id,
                price=new_price,
                valid_from=now,
                valid_to=None,
            )
            self.history_repo.create(history)

        elif new_price is not None:
            listing.last_scraped = now

        return self.listing_repo.update(listing)

    def delete_listing(self, listing_id: int):

        listing = self.listing_repo.get_by_id(listing_id)

        if not listing:
            raise ListingNotFoundError("Listing not found.")

        self.listing_repo.delete(listing)

    def listing_history(self, listing_id: int):

        if not self.listing_repo.get_by_id(listing_id):
            raise ListingNotFoundError("Listing not found.")

        return self.history_repo.get_listing_history(listing_id)
