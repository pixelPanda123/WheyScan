from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class PriceTrendPoint(BaseModel):
    listing_id: int
    store_id: int
    store_name: str
    price: float
    valid_from: datetime
    valid_to: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductAnalyticsResponse(BaseModel):
    product_id: int
    lowest_price: float | None = None
    highest_price: float | None = None
    average_price: float | None = None
    current_best_listing_id: int | None = None
    current_best_store_id: int | None = None
    current_best_store_name: str | None = None
    price_drop_percent: float | None = None
    buy_wait_recommendation: Literal["buy", "wait", "insufficient_data"]
    historical_trend: list[PriceTrendPoint]

    model_config = ConfigDict(from_attributes=True)
