from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domains.listings.models import Listing, PriceHistory, Store
from app.domains.products.models import Product


class AnalyticsRepository:

    def __init__(self, db: Session):
        self.db = db

    def product_exists(self, product_id: int) -> bool:
        return self.db.get(Product, product_id) is not None

    def get_current_price_stats(self, product_id: int):
        stmt = select(
            func.min(Listing.current_price).label("lowest_price"),
            func.max(Listing.current_price).label("highest_price"),
            func.avg(Listing.current_price).label("average_price"),
        ).where(
            Listing.product_id == product_id,
            Listing.availability.is_(True),
        )

        return self.db.execute(stmt).mappings().one()

    def get_current_best_listing(self, product_id: int):
        stmt = (
            select(
                Listing.id.label("listing_id"),
                Listing.store_id,
                Store.name.label("store_name"),
                Listing.current_price,
            )
            .join(Store, Store.id == Listing.store_id)
            .where(
                Listing.product_id == product_id,
                Listing.availability.is_(True),
            )
            .order_by(Listing.current_price.asc(), Listing.id.asc())
            .limit(1)
        )

        return self.db.execute(stmt).mappings().first()

    def get_historical_trend(self, product_id: int):
        stmt = (
            select(
                PriceHistory.listing_id,
                Listing.store_id,
                Store.name.label("store_name"),
                PriceHistory.price,
                PriceHistory.valid_from,
                PriceHistory.valid_to,
            )
            .join(Listing, Listing.id == PriceHistory.listing_id)
            .join(Store, Store.id == Listing.store_id)
            .where(Listing.product_id == product_id)
            .order_by(PriceHistory.valid_from.asc(), PriceHistory.id.asc())
        )

        return self.db.execute(stmt).mappings().all()
