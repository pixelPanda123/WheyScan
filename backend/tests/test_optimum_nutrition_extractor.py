import pytest

from app.ingestion.normalization.normalizer import ProductNormalizer
from app.ingestion.scraper.retailers.optimum_nutrition.extractor import (
    OptimumNutritionExtractor,
)

SKU_URL = (
    "https://www.optimumnutrition.co.in/products/"
    "gold-standard-100-whey-protein-powder-double-rich-chocolate-{}"
)

EXPECTED = {
    # sku: (raw weight tag, normalized grams, price)
    "1116202": ("152 g (5.36 oz)", 152, 1079.0),
    "1118948": ("454 g (1 lbs)", 454, 2759.0),
    "1118949": ("907 g (2 lbs)", 907, 4829.0),
    "1118950": ("2.27 kg (5 lbs)", 2270, 10759.0),
    "1139560": ("1.7 kg (3.7 lbs)", 1700, 8799.0),
}


@pytest.mark.parametrize("sku", sorted(EXPECTED))
def test_extracts_name_weight_flavour_into_separate_fields(on_client, sku):
    raw = OptimumNutritionExtractor(on_client).extract(SKU_URL.format(sku))
    weight, grams, price = EXPECTED[sku]

    # Name is only the first title segment; no "| flavour | size" in it.
    assert "|" not in raw.name
    assert raw.name.startswith("Gold Standard 100% Whey Protein")

    assert raw.weight == weight
    assert raw.flavour == "Double Rich Chocolate"
    assert raw.current_price == price
    assert raw.retailer_product_id.isdigit()

    normalized = ProductNormalizer.normalize(raw)

    assert normalized.name == "Gold Standard 100%"
    assert normalized.weight_g == grams
    assert normalized.flavour == "Chocolate"
    assert normalized.brand == "Optimum Nutrition"


def test_title_segment_order_does_not_matter(on_client, on_products):
    # 1118949 puts size before flavour; the others put flavour first.
    raw = OptimumNutritionExtractor(on_client).extract(SKU_URL.format("1118949"))

    assert raw.name == "Gold Standard 100% Whey Protein"
    assert raw.weight == "907 g (2 lbs)"
    assert raw.flavour == "Double Rich Chocolate"


@pytest.mark.parametrize(
    "tags, weight, flavour",
    [
        ("X-Mango, X-2 lb", "2 lb", "Mango"),  # "Mango" contains "g": used to count as a weight
        ("X-1 kg, X-Cafe Mocha", "1 kg", "Cafe Mocha"),
        ("X-Strawberry", None, "Strawberry"),
        ("Protein, whey_magic", None, None),
    ],
)
def test_x_tag_classification(tags, weight, flavour):
    assert OptimumNutritionExtractor._extract_metadata(tags) == {
        "weight": weight,
        "flavour": flavour,
    }


def test_falls_back_to_title_when_x_tags_missing(on_products):
    url = SKU_URL.format("1118948")
    product = dict(on_products[url]["product"], tags="Protein, Whey Protein")

    class Client:
        def get(self, url, **kwargs):
            class Response:
                def json(self):
                    return {"product": product}
            return Response()

    raw = OptimumNutritionExtractor(Client()).extract(url)

    assert raw.name == "Gold Standard 100% Whey Protein Powder"
    assert raw.weight == "1 lbs"
    assert raw.flavour == "Double Rich Chocolate"
