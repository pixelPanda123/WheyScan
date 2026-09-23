from pydantic import BaseModel, ConfigDict


class DiscoveryListing(BaseModel):
    listing_id: int
    store_id: int
    store_name: str
    current_price: float
    price_per_100g: float | None = None
    availability: bool
    product_url: str


class DiscoveryResult(BaseModel):
    id: int
    product_id: int
    name: str
    brand: str
    brand_id: int
    brand_name: str
    slug: str
    protein_type: str | None = None
    flavour: str | None = None
    weight: float | None = None
    weight_unit: str | None = None
    image_url: str | None = None
    listings: list[DiscoveryListing]

    model_config = ConfigDict(from_attributes=True)
