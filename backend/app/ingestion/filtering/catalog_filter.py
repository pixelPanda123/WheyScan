from app.ingestion.filtering.classifier import ProductClassifier
from app.ingestion.filtering.enums import ProductKind

from app.ingestion.scraper.base.types import RawProduct


class CatalogFilter:

    # Mass gainers were ingested before they got their own kind; keep them.
    ACCEPTED_KINDS = {ProductKind.PROTEIN, ProductKind.MASS_GAINER}

    @classmethod
    def accept(cls, product: RawProduct) -> bool:

        kind = ProductClassifier.classify(product.name)

        return kind in cls.ACCEPTED_KINDS
