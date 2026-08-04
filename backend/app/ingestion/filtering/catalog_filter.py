from app.ingestion.filtering.classifier import ProductClassifier
from app.ingestion.filtering.enums import ProductKind

from app.ingestion.scraper.base.types import RawProduct


class CatalogFilter:

    @classmethod
    def accept(cls, product: RawProduct) -> bool:

        kind = ProductClassifier.classify(product.name)

        return kind == ProductKind.PROTEIN