from datetime import datetime

import pytest

from app.ingestion.normalization.name import NameNormalizer
from app.ingestion.normalization.normalizer import ProductNormalizer
from app.ingestion.scraper.base.types import RawProduct


def raw(name, brand, weight=None, flavour=None, protein_type=None):
    return RawProduct(
        retailer="test",
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


# Full ON Shopify titles as they appear on optimumnutrition.co.in. Before the
# fix these produced "Gold Standard 100% | Double Rich | s" and similar.
@pytest.mark.parametrize(
    "title",
    [
        "Gold Standard 100% Whey Protein Powder | Double Rich Chocolate | 152 g",
        "Gold Standard 100% Whey Protein Powder | Double Rich Chocolate | 1 lbs",
        "Gold Standard 100% Whey Protein | 907 g (2 lbs) | Double Rich Chocolate",
        "Gold Standard 100% Whey Protein Powder | Double Rich Chocolate | 5 lbs",
        "Gold Standard 100% Whey Protein Powder | Double Rich Chocolate | 1.7 kg",
    ],
)
def test_full_on_title_normalizes_to_product_name(title):
    normalized = ProductNormalizer.normalize(
        raw(title, "Optimum Nutrition", flavour="Double Rich Chocolate")
    )

    # Protein-form words ("Whey") are kept; filler ("Protein", "Powder") is not.
    assert normalized.name == "Gold Standard 100% Whey"
    assert normalized.flavour == "Chocolate"


@pytest.mark.parametrize(
    "name, expected",
    [
        ("Some Whey 5 lbs", "Some Whey"),        # used to leave a stray "s"
        ("Some Whey 2lbs", "Some Whey"),
        ("Some Whey 1000 gm", "Some Whey"),      # used to leave a stray "m"
        ("Some Whey 2.27 kg", "Some Whey"),
        ("Some Whey 152 g (5.36 oz)", "Some Whey"),
    ],
)
def test_weight_units_removed_completely(name, expected):
    assert NameNormalizer.normalize(name, None, None) == expected


def test_raw_flavour_removed_before_normalized_flavour():
    # Normalized flavour is "Chocolate"; removing only that left "Double Rich".
    assert (
        NameNormalizer.normalize(
            "Gold Standard 100% Whey Double Rich Chocolate",
            "Optimum Nutrition",
            "Chocolate",
            raw_flavour="Double Rich Chocolate",
        )
        == "Gold Standard 100% Whey"
    )


def test_empty_separator_segments_dropped():
    assert NameNormalizer.normalize("Biozyme Performance, 1 kg, ", None, None) == (
        "Biozyme Performance"
    )


# HealthKart names: same cleanup as before, but protein-form words are now
# kept, so existing HealthKart products need re-ingesting (see cleanup steps).
@pytest.mark.parametrize(
    "name, brand, flavour, expected",
    [
        ("MuscleBlaze Biozyme Performance Whey", "MuscleBlaze", "Rich Chocolate", "Biozyme Performance Whey"),
        ("Ronnie Coleman Pro-Antium Whey Protein", "Ronnie Coleman", "Chocolate", "Pro-Antium Whey"),
        ("MuscleBlaze Biozyme Gold 100% Whey", "MuscleBlaze", "Rich Milk Chocolate", "Biozyme Gold 100% Whey"),
        ("MuscleBlaze Biozyme Whey PR", "MuscleBlaze", "Rich Chocolate", "Biozyme Whey PR"),
        ("Optimum Nutrition Gold Standard 100% Whey Protein", "ON", "Double Rich Chocolate", "Gold Standard 100% Whey"),
    ],
)
def test_healthkart_names(name, brand, flavour, expected):
    normalized = ProductNormalizer.normalize(raw(name, brand, flavour=flavour))

    assert normalized.name == expected


@pytest.mark.parametrize(
    "name, expected",
    [
        ("Gold Standard 100% Isolate", "Gold Standard 100% Isolate"),
        ("MuscleBlaze Raw Whey Protein Concentrate 80%", "Raw Whey Concentrate 80%"),
        ("Gold Standard 100% Casein Protein", "Gold Standard 100% Casein"),
        ("Dymatize ISO 100 Hydrolyzed Whey Protein Isolate", "ISO 100 Hydrolyzed Whey Isolate"),
    ],
)
def test_protein_form_words_kept_in_name(name, expected):
    brand = name.split()[0] if name.startswith(("MuscleBlaze", "Dymatize")) else "Optimum Nutrition"
    assert ProductNormalizer.normalize(raw(name, brand)).name == expected
