from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class NormalizedProduct:
    retailer: str
    retailer_product_id: str | None

    name: str

    brand: str | None
    weight_g: int | None
    flavour: str | None
    protein_type: str | None

    current_price: float
    original_price: float | None

    product_url: str
    image_url: str | None

    availability: str | None

    rating: float | None
    review_count: int | None

    scraped_at: datetime