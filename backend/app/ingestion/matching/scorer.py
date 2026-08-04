from difflib import SequenceMatcher

from app.ingestion.matching.types import (
    MatchScore,
    ProductFingerprint,
)
from app.ingestion.matching.enums import MatchReason

class ProductScorer:

    WEIGHT_TOLERANCE = 30

    @classmethod
    def score(
        cls,
        left: ProductFingerprint,
        right: ProductFingerprint,
    ) -> MatchScore:

        # ------------------------
        # Brand
        # ------------------------
        if left.brand != right.brand:
            return MatchScore(
                matched=False,
                score=0.0,
                reason=MatchReason.BRAND_MISMATCH,
            )

        # ------------------------
        # Weight
        # ------------------------
        if (
            left.weight_g is not None
            and right.weight_g is not None
            and abs(left.weight_g - right.weight_g) > cls.WEIGHT_TOLERANCE
        ):
            return MatchScore(
                matched=False,
                score=0.0,
                reason=MatchReason.WEIGHT_MISMATCH,
            )

        # ------------------------
        # Protein
        # ------------------------
        if (
            left.protein_type is not None
            and right.protein_type is not None
            and left.protein_type != right.protein_type
        ):
            return MatchScore(
                matched=False,
                score=0.0,
                reason=MatchReason.PROTEIN_MISMATCH,
            )

        # ------------------------
        # Flavour
        # ------------------------
        if (
            left.flavour is not None
            and right.flavour is not None
            and left.flavour != right.flavour
        ):
            return MatchScore(
                matched=False,
                score=0.0,
                reason=MatchReason.FLAVOUR_MISMATCH,
            )

        # ------------------------
        # Name similarity
        # ------------------------
        similarity = SequenceMatcher(
            None,
            left.name.lower(),
            right.name.lower(),
        ).ratio()

        return MatchScore(
            matched=True,
            score=similarity,
            reason=MatchReason.OK,
        )