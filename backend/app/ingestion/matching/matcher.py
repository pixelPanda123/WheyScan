from app.ingestion.matching.enums import MatchReason
from app.ingestion.matching.fingerprint import Fingerprinter
from app.ingestion.matching.scorer import ProductScorer
from app.ingestion.matching.types import MatchScore
from app.ingestion.normalization.types import NormalizedProduct


class ProductMatcher:

    MATCH_THRESHOLD = 0.85

    @classmethod
    def match(
        cls,
        product: NormalizedProduct,
        catalog: list[NormalizedProduct],
    ) -> tuple[NormalizedProduct | None, MatchScore]:

        if not catalog:
            return None, MatchScore(
                matched=False,
                score=0.0,
                reason=MatchReason.NO_CANDIDATES,
            )

        source = Fingerprinter.create(product)

        best_product = None
        best_score = MatchScore(
            matched=False,
            score=0.0,
            reason=MatchReason.NO_CANDIDATES,
        )

        for candidate in catalog:

            target = Fingerprinter.create(candidate)

            result = ProductScorer.score(source, target)

            if result.score > best_score.score:
                best_score = result
                best_product = candidate

        if (
            best_product is None
            or best_score.score < cls.MATCH_THRESHOLD
        ):
            return None, MatchScore(
                matched=False,
                score=best_score.score,
                reason=MatchReason.BELOW_THRESHOLD,
            )

        return best_product, best_score