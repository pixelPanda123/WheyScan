from pydantic import BaseModel, ConfigDict


class DiscoveryResult(BaseModel):
    product_id: int
    brand_id: int
    brand_name: str
    name: str
    slug: str
    protein_type: str
    flavour: str
    weight: float
    weight_unit: str
    image_url: str | None = None
    listing_id: int | None = None
    store_id: int | None = None
    store_name: str | None = None
    current_price: float | None = None
    availability: bool | None = None

    model_config = ConfigDict(from_attributes=True)
