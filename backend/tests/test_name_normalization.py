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

    assert normalized.name == "Gold Standard 100%"
    assert normalized.flavour == "Chocolate"


@pytest.mark.parametrize(
    "name, expected",
    [
        ("Some Whey 5 lbs", "Some"),        # used to leave a stray "s"
        ("Some Whey 2lbs", "Some"),
        ("Some Whey 1000 gm", "Some"),      # used to leave a stray "m"
        ("Some Whey 2.27 kg", "Some"),
        ("Some Whey 152 g (5.36 oz)", "Some"),
    ],
)
def test_weight_units_removed_completely(name, expected):
    assert NameNormalizer.normalize(name, None, None) == expected


def test_raw_flavour_removed_before_normalized_flavour():
    # Normalized flavour is "Chocolate"; removing only that left "Double Rich".
    assert (
        NameNormalizer.normalize(
            "Gold Standard 100% Double Rich Chocolate",
            "Optimum Nutrition",
            "Chocolate",
            raw_flavour="Double Rich Chocolate",
        )
        == "Gold Standard 100%"
    )


def test_empty_separator_segments_dropped():
    assert NameNormalizer.normalize("Biozyme Performance, 1 kg, ", None, None) == (
        "Biozyme Performance"
    )


# HealthKart names must normalize exactly as before (these match the product
# names already stored from HealthKart runs).
@pytest.mark.parametrize(
    "name, brand, flavour, expected",
    [
        ("MuscleBlaze Biozyme Performance Whey", "MuscleBlaze", "Rich Chocolate", "Biozyme Performance"),
        ("Ronnie Coleman Pro-Antium Whey Protein", "Ronnie Coleman", "Chocolate", "Pro-Antium"),
        ("MuscleBlaze Biozyme Gold 100% Whey", "MuscleBlaze", "Rich Milk Chocolate", "Biozyme Gold 100%"),
        ("MuscleBlaze Biozyme Whey PR", "MuscleBlaze", "Rich Chocolate", "Biozyme PR"),
        ("Optimum Nutrition Gold Standard 100% Whey Protein", "ON", "Double Rich Chocolate", "Gold Standard 100%"),
    ],
)
def test_healthkart_names_unchanged(name, brand, flavour, expected):
    normalized = ProductNormalizer.normalize(raw(name, brand, flavour=flavour))

    assert normalized.name == expected
