"""
Canonical protein_type vocabulary and protein-form detection.

protein_type describes one thing: the protein composition of the product as
sold. None means unknown. Product categories such as mass gainers are not
protein types; see app.ingestion.filtering.enums.ProductKind.
"""

import re
from enum import Enum


class ProteinType(str, Enum):
    WHEY_CONCENTRATE = "WHEY_CONCENTRATE"
    WHEY_ISOLATE = "WHEY_ISOLATE"
    WHEY_HYDROLYSED = "WHEY_HYDROLYSED"
    WHEY_BLEND = "WHEY_BLEND"          # several whey forms, e.g. Gold Standard 100% Whey
    CASEIN = "CASEIN"
    MULTI_SOURCE = "MULTI_SOURCE"      # e.g. whey + casein
    PLANT = "PLANT"


# A name that says "whey" but no specific form ("Gold Standard 100% Whey").
# Used only as matching evidence, never stored as a protein_type.
GENERIC_WHEY = "WHEY"


_WHEY = re.compile(r"\bwhey\b|hydrowhey", re.I)
_CASEIN = re.compile(r"\bcasein\b", re.I)
_PLANT = re.compile(r"\bplant\b|\bvegan\b|\bpea protein\b", re.I)
_MULTI = re.compile(r"\bmulti[- ]?(source|protein)\b|\bmatrix\b", re.I)
_BLEND = re.compile(r"\bblend\b", re.I)
_HYDRO = re.compile(r"hydroly[sz]ed|\bhydro", re.I)
_ISOLATE = re.compile(r"\bisolate\b|\biso[\s-]?100\b", re.I)
_CONCENTRATE = re.compile(r"\bconcentrate\b", re.I)


def detect_form(text: str | None) -> ProteinType | str | None:
    """
    Protein form stated in `text` (a product name or a retailer attribute).

    Returns a ProteinType, GENERIC_WHEY when only "whey" is stated, or None
    when the text says nothing about protein form.
    """
    if not text:
        return None

    whey = bool(_WHEY.search(text))
    casein = bool(_CASEIN.search(text))
    plant = bool(_PLANT.search(text))

    if _MULTI.search(text) or (casein and whey) or (plant and (whey or casein)):
        return ProteinType.MULTI_SOURCE

    if casein:
        return ProteinType.CASEIN

    if plant:
        return ProteinType.PLANT

    # Whey forms, most specific claim first
    if _BLEND.search(text):
        return ProteinType.WHEY_BLEND

    if _HYDRO.search(text):
        return ProteinType.WHEY_HYDROLYSED

    if _ISOLATE.search(text):
        return ProteinType.WHEY_ISOLATE

    if _CONCENTRATE.search(text):
        return ProteinType.WHEY_CONCENTRATE

    if whey:
        return GENERIC_WHEY

    return None


def _specific(form: ProteinType | str | None) -> ProteinType | None:
    return form if isinstance(form, ProteinType) else None


class ProteinNormalizer:

    @classmethod
    def normalize(
        cls,
        protein_type: str | None,
        name: str,
    ) -> str | None:
        """
        protein_type is the retailer's *structured* attribute (e.g. HealthKart's
        "Protein Type": "Whey Blend"). It takes precedence; the product name is
        only used when the attribute is missing or states no specific form, so
        a word in the name can no longer override a reliable attribute.
        """
        resolved = _specific(detect_form(protein_type)) or _specific(detect_form(name))

        return resolved.value if resolved else None
