from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StoreCreate(BaseModel):
    name: str
    base_url: str
    active: bool = True


class StoreUpdate(BaseModel):
    name: str | None = None
    base_url: str | None = None
    active: bool | None = None


class StoreResponse(BaseModel):
    id: int
    name: str
    base_url: str
    active: bool

    model_config = ConfigDict(from_attributes=True)


class ListingCreate(BaseModel):
    product_id: int
    store_id: int
    url: str
    current_price: float
    availability: bool = True


class ListingUpdate(BaseModel):
    product_id: int | None = None
    store_id: int | None = None
    url: str | None = None
    current_price: float | None = None
    availability: bool | None = None


class ListingResponse(BaseModel):
    id: int
    product_id: int
    store_id: int
    url: str
    current_price: float
    availability: bool
    last_scraped: datetime

    model_config = ConfigDict(from_attributes=True)


class PriceHistoryResponse(BaseModel):
    id: int
    listing_id: int
    price: float
    valid_from: datetime
    valid_to: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
