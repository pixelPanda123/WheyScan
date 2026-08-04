from datetime import datetime

from app.ingestion.scraper.base.types import RawProduct
from app.ingestion.scraper.http.client import HTTPClient


class OptimumNutritionExtractor:

    def __init__(self):
        self.client = HTTPClient()

    def extract(self, product_url: str) -> RawProduct:

        json_url = f"{product_url}.json"

        response = self.client.get(json_url)

        try:
            data = response.json()["product"]
        except Exception:
            raise ValueError(f"Invalid Shopify JSON returned for {json_url}")

        variant = data["variants"][0]
        image = data.get("image")

        metadata = self._extract_metadata(
            data.get("tags", "")
        )

        return RawProduct(
            retailer="optimum_nutrition",
            retailer_product_id=str(data["id"]),

            name=data["title"],
            brand=data["vendor"],

            weight=metadata["weight"],
            flavour=metadata["flavour"],
            protein_type=self._extract_protein_type(
                data.get("tags", "")
            ),

            current_price=float(variant["price"]),

            original_price=(
                float(variant["compare_at_price"])
                if variant["compare_at_price"]
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

    def _extract_metadata(self, tags: str) -> dict:

        metadata = {
            "weight": None,
            "flavour": None,
        }

        for tag in tags.split(","):

            tag = tag.strip()

            if not tag.startswith("X-"):
                continue

            value = tag[2:].strip()

            lower = value.lower()

            if any(unit in lower for unit in ("kg", "lb", "lbs", "g")):
                metadata["weight"] = value
            else:
                metadata["flavour"] = value

        return metadata

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