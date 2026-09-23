from difflib import SequenceMatcher

from app.ingestion.matching.types import (
    MatchScore,
    ProductFingerprint,
)
from app.ingestion.matching.enums import MatchReason
from app.ingestion.normalization.protein import GENERIC_WHEY, ProteinType

# A name saying just "whey" is compatible with forms brands often leave out
# of the name (blend, concentrate), but not with isolate/hydrolysed, which
# are always advertised: "Gold Standard 100% Whey" != "... 100% Isolate".
_COMPATIBLE_FORMS = {
    frozenset({GENERIC_WHEY, ProteinType.WHEY_BLEND}),
    frozenset({GENERIC_WHEY, ProteinType.WHEY_CONCENTRATE}),
}


def forms_conflict(left: str | None, right: str | None) -> bool:
    """True when both names state a protein form and the forms differ."""

    if left is None or right is None or left == right:
        return False

    return frozenset({left, right}) not in _COMPATIBLE_FORMS

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
        # Protein form (from names)
        # ------------------------
        # Only forms stated in the product names can block a match.
        # protein_type from retailer attributes is deliberately NOT a veto:
        # retailers classify the same product differently (HealthKart calls
        # Gold Standard "Whey Blend"), which alone must not split products.
        if forms_conflict(left.name_form, right.name_form):
            return MatchScore(
                matched=False,
                score=0.0,
                reason=MatchReason.FORM_MISMATCH,
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