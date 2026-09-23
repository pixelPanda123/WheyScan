import re
from datetime import datetime

from app.ingestion.scraper.base.types import RawProduct
from app.ingestion.scraper.http.client import HTTPClient


# "907 g (2 lbs)", "1.7 kg", "5 lbs", "152 g (5.36 oz)"
WEIGHT_PATTERN = re.compile(
    r"^\s*\d+(?:\.\d+)?\s*(?:kgs?|grams?|gms?|g|lbs?|oz)\b",
    re.IGNORECASE,
)


class OptimumNutritionExtractor:
    """
    Extracts one product from ON India's Shopify store.

    Each size/flavour is its own Shopify product with a title like
    "Gold Standard 100% Whey Protein Powder | Double Rich Chocolate | 5 lbs"
    and one "Default Title" variant, so Shopify's variant options/weight are
    empty. Size and flavour come from the "X-" tags (e.g. "X-907 g (2 lbs)",
    "X-Double Rich Chocolate"), falling back to the title segments.
    Only the first title segment is the product name.
    """

    def __init__(self, client: HTTPClient | None = None):
        self.client = client or HTTPClient()

    def extract(self, product_url: str) -> RawProduct:

        json_url = f"{product_url}.json"

        response = self.client.get(json_url)

        try:
            data = response.json()["product"]
        except Exception:
            raise ValueError(f"Invalid Shopify JSON returned for {json_url}")

        variant = data["variants"][0]
        image = data.get("image")
        tags = data.get("tags", "")

        name, title_details = self._split_title(data["title"])

        metadata = self._extract_metadata(tags)

        # Fall back to the title's "| flavour | size" segments if tags lack them
        fallback = self._classify(title_details)
        weight = metadata["weight"] or fallback["weight"]
        flavour = metadata["flavour"] or fallback["flavour"]

        return RawProduct(
            retailer="optimum_nutrition",
            retailer_product_id=str(data["id"]),

            name=name,
            brand=data["vendor"],

            weight=weight,
            flavour=flavour,
            protein_type=self._extract_protein_type(tags),

            current_price=float(variant["price"]),

            original_price=(
                float(variant["compare_at_price"])
                if variant.get("compare_at_price")
                else None
            ),

            discount=None,

            product_url=product_url,

            image_url=image["src"] if image else None,

            availability="In Stock",

            rating=None,
            review_count=None,

            scraped_at=datetime.now(),
        )

    @staticmethod
    def _split_title(title: str) -> tuple[str, list[str]]:
        """
        "Gold Standard 100% Whey Protein | 907 g (2 lbs) | Double Rich Chocolate"
        -> ("Gold Standard 100% Whey Protein", ["907 g (2 lbs)", "Double Rich Chocolate"])
        """
        parts = [part.strip() for part in title.split("|")]
        parts = [part for part in parts if part]

        if not parts:
            return title.strip(), []

        return parts[0], parts[1:]

    @staticmethod
    def _is_weight(value: str) -> bool:
        return bool(WEIGHT_PATTERN.match(value))

    @classmethod
    def _classify(cls, values: list[str]) -> dict:

        metadata = {
            "weight": None,
            "flavour": None,
        }

        for value in values:
            key = "weight" if cls._is_weight(value) else "flavour"

            if metadata[key] is None:
                metadata[key] = value

        return metadata

    @classmethod
    def _extract_metadata(cls, tags: str) -> dict:

        values = [
            tag.strip()[2:].strip()
            for tag in tags.split(",")
            if tag.strip().startswith("X-")
        ]

        return cls._classify([value for value in values if value])

    def _extract_protein_type(self, tags: str):

        tags = tags.lower()

        if "mass gainer" in tags:
            return "MASS_GAINER"

        if "casein" in tags:
            return "CASEIN"

        if "plant protein" in tags:
            return "PLANT"

        if "whey isolate" in tags:
            return "WHEY_ISOLATE"

        if "whey concentrate" in tags:
            return "WHEY_CONCENTRATE"

        if "whey protein" in tags:
            return "WHEY"

        return None
