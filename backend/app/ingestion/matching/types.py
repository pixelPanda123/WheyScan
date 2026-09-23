from dataclasses import dataclass

from app.ingestion.matching.enums import MatchReason


@dataclass(slots=True)
class ProductFingerprint:
    brand: str | None
    name: str
    weight_g: int | None
    flavour: str | None
    protein_type: str | None
    # Protein form stated in the product's own name (see detect_form).
    name_form: str | None = None


@dataclass(slots=True)
class MatchScore:
    matched: bool
    score: float
    reason: MatchReason