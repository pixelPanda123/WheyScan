from .brand import BrandNormalizer
from .flavour import FlavourNormalizer
from .name import NameNormalizer
from .protein import ProteinNormalizer
from .types import NormalizedProduct
from .weight import WeightNormalizer

from app.ingestion.scraper.base.types import RawProduct


class ProductNormalizer:

    @classmethod
    def normalize(cls, raw: RawProduct) -> NormalizedProduct:

        brand = BrandNormalizer.normalize(raw.brand)

        weight = WeightNormalizer.normalize(raw.weight)

        flavour = FlavourNormalizer.normalize(raw.flavour)

        protein = ProteinNormalizer.normalize(
            raw.protein_type,
            raw.name,
        )

        name = NameNormalizer.normalize(
            raw.name,
            brand,
            flavour,
            raw_flavour=raw.flavour,
        )

        return NormalizedProduct(
            retailer=raw.retailer,
            retailer_product_id=raw.retailer_product_id,

            name=name,
            brand=brand,

            weight_g=weight,
            flavour=flavour,
            protein_type=protein,

            current_price=raw.current_price,
            original_price=raw.original_price,

            product_url=raw.product_url,
            image_url=raw.image_url,

            availability=raw.availability,

            rating=raw.rating,
            review_count=raw.review_count,

            scraped_at=raw.scraped_at,
        )