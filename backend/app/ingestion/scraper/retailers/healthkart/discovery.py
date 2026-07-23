from __future__ import annotations

from datetime import datetime
from typing import Iterator

from app.ingestion.scraper.base.types import RawProduct
from app.ingestion.scraper.http.client import HTTPClient


class HealthKartDiscoverer:
    RETAILER = "healthkart"
    BASE_URL = "https://www.healthkart.com"
    API_URL = f"{BASE_URL}/veronica/catalog/results"

    DEFAULT_PARAMS = {
        "catPrefix": "snt-pt-wp",
        "parentCatPrefix": "snt-pt-wp",
        "perPage": 24,
        "excludeOOS": "true",
        "navKey": "SCT-snt-pt-wp",
        "plt": 1,
        "st": 1,
    }

    def __init__(self, client: HTTPClient):
        self.client = client

    def discover(self) -> Iterator[RawProduct]:
        page = 1

        while True:
            variants = self._fetch_page(page)

            if not variants:
                break

            for variant in variants:
                yield self._to_raw_product(variant)

            page += 1

    def _fetch_page(self, page: int) -> list[dict]:
        params = self.DEFAULT_PARAMS.copy()
        params["pageNo"] = page

        response = self.client.get(
            self.API_URL,
            params=params,
        )

        response.raise_for_status()

        data = response.json()

        return data["results"]["variants"]

    @staticmethod
    def _get_attributes(variant: dict) -> dict[str, str]:
        attributes = {}

        for group in variant.get("grps", []):
            for value in group.get("values", []):
                attributes[value["dis_nm"]] = value["val"]

        return attributes

    def _to_raw_product(self, variant: dict) -> RawProduct:
        attributes = self._get_attributes(variant)

        image = variant.get("m_img") or {}

        return RawProduct(
            retailer=self.RETAILER,
            retailer_product_id=str(variant["id"]),
            name=variant["spName"],
            brand=variant["brName"],
            weight=attributes.get("Weight"),
            flavour=attributes.get("Flavour"),
            protein_type=None,
            current_price=float(variant["offer_pr"]),
            original_price=float(variant["mrp"]) if variant.get("mrp") else None,
            discount=float(variant["currDisPercent"])
            if variant.get("currDisPercent") is not None
            else None,
            product_url=self.BASE_URL + variant["urlFragment"],
            image_url=image.get("o_link"),
            availability="In Stock" if not variant.get("oos") else "Out of Stock",
            rating=float(variant["rating"]) if variant.get("rating") else None,
            review_count=int(variant["nrvw"]) if variant.get("nrvw") else None,
            scraped_at=datetime.utcnow(),
        )