from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.domains.discovery.repositories import DiscoveryRepository
from app.domains.discovery.schemas import DiscoveryResult
from app.domains.discovery.services import DiscoveryService

router = APIRouter(
    prefix="/discovery",
    tags=["Discovery"],
)


@router.get("/search", response_model=list[DiscoveryResult])
def search(
    query: str | None = None,
    brand_id: int | None = None,
    protein_type: str | None = None,
    weight: float | None = None,
    availability: bool | None = None,
    price_min: float | None = None,
    price_max: float | None = None,
    store_id: int | None = None,
    sort_by: Literal["name", "price", "brand", "weight"] = "name",
    sort_order: Literal["asc", "desc"] = "asc",
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = DiscoveryService(DiscoveryRepository(db))

    return service.search(
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
