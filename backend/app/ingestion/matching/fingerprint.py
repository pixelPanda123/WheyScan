from app.ingestion.matching.types import ProductFingerprint
from app.ingestion.normalization.protein import detect_form
from app.ingestion.normalization.types import NormalizedProduct


class Fingerprinter:

    @staticmethod
    def create(product: NormalizedProduct) -> ProductFingerprint:
        return ProductFingerprint(
            brand=product.brand,
            name=product.name.lower(),
            weight_g=product.weight_g,
            flavour=product.flavour,
            protein_type=product.protein_type,
            name_form=detect_form(product.name),
        )