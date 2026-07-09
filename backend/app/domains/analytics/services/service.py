from decimal import Decimal

from app.domains.analytics.exceptions import AnalyticsProductNotFoundError
from app.domains.analytics.repositories import AnalyticsRepository
from app.domains.analytics.schemas import ProductAnalyticsResponse, PriceTrendPoint


class AnalyticsService:

    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository

    def get_product_analytics(self, product_id: int) -> ProductAnalyticsResponse:
        if not self.repository.product_exists(product_id):
            raise AnalyticsProductNotFoundError("Product not found.")

        stats = self.repository.get_current_price_stats(product_id)
        best_listing = self.repository.get_current_best_listing(product_id)
        trend_rows = self.repository.get_historical_trend(product_id)
        historical_trend = [
            PriceTrendPoint.model_validate(row)
            for row in trend_rows
        ]

        lowest_price = self._to_float(stats["lowest_price"])
        highest_price = self._to_float(stats["highest_price"])
        average_price = self._to_float(stats["average_price"])
        best_price = self._to_float(best_listing["current_price"]) if best_listing else None

        return ProductAnalyticsResponse(
            product_id=product_id,
            lowest_price=lowest_price,
            highest_price=highest_price,
            average_price=average_price,
            current_best_listing_id=best_listing["listing_id"] if best_listing else None,
            current_best_store_id=best_listing["store_id"] if best_listing else None,
            current_best_store_name=best_listing["store_name"] if best_listing else None,
            price_drop_percent=self._price_drop_percent(
                historical_trend,
                best_price,
            ),
            buy_wait_recommendation=self._recommendation(
                best_price,
                average_price,
            ),
            historical_trend=historical_trend,
        )

    def _price_drop_percent(
        self,
        historical_trend: list[PriceTrendPoint],
        current_price: float | None,
    ) -> float | None:
        if not historical_trend or current_price is None:
            return None

        first_price = Decimal(str(historical_trend[0].price))

        if first_price == 0:
            return None

        drop = (
            (first_price - Decimal(str(current_price)))
            / first_price
            * Decimal("100")
        )
        return round(float(drop), 2)

    def _recommendation(
        self,
        current_price: float | None,
        average_price: float | None,
    ) -> str:
        if current_price is None or average_price is None:
            return "insufficient_data"

        if Decimal(str(current_price)) <= Decimal(str(average_price)):
            return "buy"

        return "wait"

    def _to_float(self, value) -> float | None:
        if value is None:
            return None

        return float(value)
