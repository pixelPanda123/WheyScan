from app.domains.discovery.repositories import DiscoveryRepository
from app.domains.discovery.schemas import DiscoveryResult


class DiscoveryService:

    def __init__(self, repository: DiscoveryRepository):
        self.repository = repository

    def search(
        self,
        query: str | None = None,
        brand_id: int | None = None,
        protein_type: str | None = None,
        weight: float | None = None,
        availability: bool | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        store_id: int | None = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        skip: int = 0,
        limit: int = 20,
    ) -> list[DiscoveryResult]:
        rows = self.repository.search(
            query=query,
            brand_id=brand_id,
            protein_type=protein_type,
            weight=weight,
            availability=availability,
            price_min=price_min,
            price_max=price_max,
            store_id=store_id,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit,
        )

        products: dict[int, dict] = {}

        for row in rows:
            product_id = row["product_id"]
            product = products.setdefault(
                product_id,
                {
                    "id": product_id,
                    "product_id": product_id,
                    "name": row["name"],
                    "brand": row["brand_name"],
                    "brand_id": row["brand_id"],
                    "brand_name": row["brand_name"],
                    "slug": row["slug"],
                    "protein_type": row["protein_type"],
                    "flavour": row["flavour"],
                    "weight": row["weight"],
                    "weight_unit": row["weight_unit"],
                    "image_url": row["image_url"],
                    "listings": [],
                },
            )

            product["listings"].append(
                {
                    "listing_id": row["listing_id"],
                    "store_id": row["store_id"],
                    "store_name": row["store_name"],
                    "current_price": row["current_price"],
                    "price_per_100g": self._price_per_100g(
                        row["current_price"],
                        row["weight"],
                        row["weight_unit"],
                    ),
                    "availability": row["availability"],
                    "product_url": row["product_url"],
                }
            )

        return [
            DiscoveryResult.model_validate(product)
            for product in products.values()
        ]

    @staticmethod
    def _price_per_100g(
        price: float | None,
        weight: float | None,
        weight_unit: str | None,
    ) -> float | None:
        if price is None or weight is None or not weight_unit:
            return None

        unit = weight_unit.strip().lower()
        grams_by_unit = {
            "g": 1,
            "gm": 1,
            "gram": 1,
            "grams": 1,
            "kg": 1000,
            "kgs": 1000,
            "lb": 453.59237,
            "lbs": 453.59237,
        }
        grams_multiplier = grams_by_unit.get(unit)

        if grams_multiplier is None:
            return None

        grams = float(weight) * grams_multiplier
        if grams <= 0:
            return None

        return round(float(price) / grams * 100, 2)
