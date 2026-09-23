from datetime import datetime

import pytest

from app.ingestion.filtering.classifier import ProductClassifier
from app.ingestion.filtering.catalog_filter import CatalogFilter
from app.ingestion.filtering.enums import ProductKind
from app.ingestion.matching.matcher import ProductMatcher
from app.ingestion.matching.enums import MatchReason
from app.ingestion.normalization.normalizer import ProductNormalizer
from app.ingestion.normalization.protein import (
    GENERIC_WHEY,
    ProteinNormalizer,
    ProteinType,
    detect_form,
)
from app.ingestion.scraper.base.types import RawProduct


def raw(name, brand="Optimum Nutrition", weight="907 g", flavour="Double Rich Chocolate",
        protein_type=None, retailer="healthkart"):
    return RawProduct(
        retailer=retailer,
        retailer_product_id="1",
        name=name,
        brand=brand,
        weight=weight,
        flavour=flavour,
        protein_type=protein_type,
        current_price=1.0,
        original_price=None,
        discount=None,
        product_url="",
        image_url=None,
        availability="In Stock",
        rating=None,
        review_count=None,
        scraped_at=datetime(2026, 1, 1),
    )


def match(left: RawProduct, right: RawProduct):
    a = ProductNormalizer.normalize(left)
    b = ProductNormalizer.normalize(right)
    return ProductMatcher.match(a, [b])


# ----------------------------------------------------------------------
# Vocabulary
# ----------------------------------------------------------------------

def test_vocabulary_is_exactly_the_canonical_set():
    assert {t.value for t in ProteinType} == {
        "WHEY_CONCENTRATE", "WHEY_ISOLATE", "WHEY_HYDROLYSED", "WHEY_BLEND",
        "CASEIN", "MULTI_SOURCE", "PLANT",
    }


@pytest.mark.parametrize(
    "attribute, expected",
    [
        # HealthKart / MuscleBlaze structured "Protein Type" values
        ("Whey Blend", "WHEY_BLEND"),
        ("Whey Isolate", "WHEY_ISOLATE"),
        ("Whey Protein Concentrate", "WHEY_CONCENTRATE"),
        ("Hydrolysed Whey", "WHEY_HYDROLYSED"),
        ("Casein", "CASEIN"),
        ("Plant Protein", "PLANT"),
        ("Whey & Casein Blend", "MULTI_SOURCE"),
    ],
)
def test_structured_attribute_normalized_to_vocabulary(attribute, expected):
    assert ProteinNormalizer.normalize(attribute, "Some Product") == expected


def test_structured_attribute_wins_over_name():
    # Before: any "isolate" in the name overrode the retailer's attribute.
    assert ProteinNormalizer.normalize("Whey Blend", "Blend With Whey Isolate") == "WHEY_BLEND"
    assert ProteinNormalizer.normalize("Whey Blend", "Gold Standard 100% Whey Isolate Added") == "WHEY_BLEND"


def test_name_used_when_attribute_missing_or_unspecific():
    assert ProteinNormalizer.normalize(None, "Raw Whey Isolate") == "WHEY_ISOLATE"
    assert ProteinNormalizer.normalize("Whey Protein", "Raw Whey Isolate") == "WHEY_ISOLATE"


def test_plain_whey_is_unknown_not_a_type():
    assert ProteinNormalizer.normalize(None, "Gold Standard 100% Whey Protein") is None
    assert detect_form("Gold Standard 100% Whey") == GENERIC_WHEY


def test_casein_preserved_instead_of_none():
    normalized = ProductNormalizer.normalize(raw("Gold Standard 100% Casein Protein"))

    assert normalized.protein_type == "CASEIN"


# ----------------------------------------------------------------------
# Mass gainer is a ProductKind, not a protein type
# ----------------------------------------------------------------------

def test_mass_gainer_is_a_product_kind():
    assert ProductClassifier.classify("Serious Mass Weight Gainer") == ProductKind.MASS_GAINER
    assert ProductClassifier.classify("MuscleBlaze Mass Gainer XXL, 3 kg") == ProductKind.MASS_GAINER
    assert ProteinNormalizer.normalize(None, "Serious Mass Weight Gainer") is None
    assert "MASS_GAINER" not in {t.value for t in ProteinType}


def test_mass_gainers_still_ingested():
    assert CatalogFilter.accept(raw("Serious Mass Weight Gainer"))


# ----------------------------------------------------------------------
# Matching
# ----------------------------------------------------------------------

def test_healthkart_blend_matches_on_title_whey():
    hk = raw("Optimum Nutrition Gold Standard 100% Whey Protein", brand="ON",
             weight="2 lb", protein_type="Whey Blend")
    on = raw("Gold Standard 100% Whey Protein", weight="907 g (2 lbs)",
             retailer="optimum_nutrition")

    matched, score = match(on, hk)

    assert matched is not None
    assert score.reason == MatchReason.OK
    assert score.score == 1.0


def test_structured_classification_disagreement_alone_does_not_block():
    a = raw("Gold Standard 100% Whey Protein", protein_type="Whey Blend")
    b = raw("Gold Standard 100% Whey Protein", protein_type="Whey Protein Concentrate")

    matched, _ = match(a, b)

    assert matched is not None


@pytest.mark.parametrize(
    "left, right",
    [
        # Gold Standard Whey vs Gold Standard Isolate (different ON products)
        ("Gold Standard 100% Whey Protein", "Gold Standard 100% Isolate"),
        # Whey concentrate vs whey isolate from the same line
        ("MuscleBlaze Raw Whey Protein Concentrate", "MuscleBlaze Raw Whey Isolate"),
        ("Gold Standard 100% Whey Protein", "Gold Standard 100% Casein"),
        ("Platinum Hydrowhey", "Platinum Whey Isolate"),
    ],
)
def test_conflicting_name_forms_never_match(left, right):
    brand = "MuscleBlaze" if "MuscleBlaze" in left else "Optimum Nutrition"
    a, b = raw(left, brand=brand), raw(right, brand=brand)

    matched, score = match(a, b)
    assert matched is None

    # Holds even when a (wrong or noisy) structured attribute claims they agree.
    a = raw(left, brand=brand, protein_type="Whey Blend")
    b = raw(right, brand=brand, protein_type="Whey Blend")
    matched, score = match(a, b)
    assert matched is None


def test_form_conflict_reported_as_form_mismatch():
    from app.ingestion.matching.fingerprint import Fingerprinter
    from app.ingestion.matching.scorer import ProductScorer

    a = Fingerprinter.create(ProductNormalizer.normalize(raw("Gold Standard 100% Whey Protein")))
    b = Fingerprinter.create(ProductNormalizer.normalize(raw("Gold Standard 100% Isolate")))

    assert ProductScorer.score(a, b).reason == MatchReason.FORM_MISMATCH


def test_different_weight_stays_separate():
    a = raw("Gold Standard 100% Whey Protein", weight="907 g")
    b = raw("Gold Standard 100% Whey Protein", weight="454 g")

    matched, score = match(a, b)

    assert matched is None


@pytest.mark.parametrize(
    "left, right, brand",
    [
        ("Gold Standard 100% Whey Protein", "Gold Standard 100% Whey Isolate", "Optimum Nutrition"),
        ("MuscleBlaze Biozyme Performance Whey Concentrate",
         "MuscleBlaze Biozyme Performance Whey Isolate", "MuscleBlaze"),
        ("Gold Standard 100% Whey Protein", "Gold Standard 100% Whey Casein", "Optimum Nutrition"),
    ],
)
def test_form_rule_blocks_names_similar_enough_to_merge(left, right, brand):
    """Without the form rule these pairs would merge on name similarity alone."""
    from difflib import SequenceMatcher

    a = ProductNormalizer.normalize(raw(left, brand=brand))
    b = ProductNormalizer.normalize(raw(right, brand=brand))

    similarity = SequenceMatcher(None, a.name.lower(), b.name.lower()).ratio()
    assert similarity >= ProductMatcher.MATCH_THRESHOLD  # the rule is load-bearing

    matched, score = ProductMatcher.match(a, [b])

    assert matched is None
