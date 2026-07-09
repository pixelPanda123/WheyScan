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

        return [DiscoveryResult.model_validate(row) for row in rows]
