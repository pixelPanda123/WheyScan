from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RawProduct:
    retailer: str

    retailer_product_id: Optional[str]

    name: str
    brand: str

    weight: Optional[str]
    flavour: Optional[str]
    # The retailer's *structured* protein attribute only (e.g. HealthKart's
    # "Protein Type"). Leave None rather than guessing from tags or text;
    # the normalizer falls back to the product name.
    protein_type: Optional[str]

    current_price: float
    original_price: Optional[float]
    discount: Optional[float]

    product_url: str
    image_url: Optional[str]

    availability: Optional[str]

    rating: Optional[float]
    review_count: Optional[int]

    scraped_at: datetime