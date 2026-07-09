from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.domains.analytics.exceptions import AnalyticsProductNotFoundError
from app.domains.analytics.repositories import AnalyticsRepository
from app.domains.analytics.schemas import ProductAnalyticsResponse
from app.domains.analytics.services import AnalyticsService

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/products/{product_id}", response_model=ProductAnalyticsResponse)
def get_product_analytics(
    product_id: int,
    db: Session = Depends(get_db),
):
    service = AnalyticsService(AnalyticsRepository(db))

    try:
        return service.get_product_analytics(product_id)

    except AnalyticsProductNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
