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

        return RawProduct(
            retailer="optimum_nutrition",
            retailer_product_id=str(data["id"]),

            name=data["title"],
            brand=data["vendor"],

            weight=f"{variant['weight']} {variant['weight_unit']}",
            flavour=self._extract_tag(data.get("tags", ""), "X-"),
            protein_type=self._extract_protein_type(data.get("tags", "")),

            current_price=float(variant["price"]),
            original_price=float(variant["compare_at_price"]) if variant["compare_at_price"] else None,
            discount=None,

            product_url=product_url,
            image_url=image["src"] if image else None,

            availability="In Stock",   # We'll improve this later.

            rating=None,
            review_count=None,

            scraped_at=datetime.now(),
        )

    def _extract_tag(self, tags: str, prefix: str):
        for tag in tags.split(","):
            tag = tag.strip()

            if tag.startswith(prefix):
                return tag.replace(prefix, "").strip()

        return None

    def _extract_protein_type(self, tags: str):
        protein_types = [
            "Whey Isolate",
            "Whey Concentrate",
            "Mass Gainer",
            "Casein",
            "Plant Protein",
            "Protein Blend",
        ]

        for protein in protein_types:
            if protein in tags:
                return protein

        return None