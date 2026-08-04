from dataclasses import dataclass

from app.ingestion.matching.enums import MatchReason


@dataclass(slots=True)
class ProductFingerprint:
    brand: str | None
    name: str
    weight_g: int | None
    flavour: str | None
    protein_type: str | None


@dataclass(slots=True)
class MatchScore:
    matched: bool
    score: float
    reason: MatchReason