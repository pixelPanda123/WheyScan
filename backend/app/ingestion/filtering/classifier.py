from app.ingestion.filtering.enums import ProductKind
from app.ingestion.filtering.rules import *


class ProductClassifier:

    @classmethod
    def classify(cls, name: str) -> ProductKind:
    
        if not name: 
            return ProductKind.UNKNOWN

        text = name.lower()

        # Bundles first
        if any(word in text for word in BUNDLE_KEYWORDS):
            return ProductKind.BUNDLE

        if any(word in text for word in ACCESSORY_KEYWORDS):
            return ProductKind.ACCESSORY

        if any(word in text for word in CREATINE_KEYWORDS):
            return ProductKind.CREATINE

        if any(word in text for word in PRE_WORKOUT_KEYWORDS):
            return ProductKind.PRE_WORKOUT

        if any(word in text for word in VITAMIN_KEYWORDS):
            return ProductKind.VITAMIN

        # Before protein: gainer names usually also contain "protein"/"whey".
        if any(word in text for word in MASS_GAINER_KEYWORDS):
            return ProductKind.MASS_GAINER

        if any(word in text for word in PROTEIN_KEYWORDS):
            return ProductKind.PROTEIN

        return ProductKind.UNKNOWN