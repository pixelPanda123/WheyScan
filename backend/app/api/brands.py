from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.domains.products.repositories import BrandRepository
from app.domains.products.schemas import (
    BrandCreate,
    BrandResponse,
    BrandUpdate
)
from app.domains.products.services import BrandService

router = APIRouter(
    prefix="/brands",
    tags=["Brands"],
)


@router.post("/", response_model=BrandResponse)
def create_brand(
    brand: BrandCreate,
    db: Session = Depends(get_db),
):
    service = BrandService(BrandRepository(db))

    try:
        return service.create_brand(brand)

    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/", response_model=list[BrandResponse])
def list_brands(
    db: Session = Depends(get_db),
):
    return BrandService(
        BrandRepository(db)
    ).list_brands()


@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(
    brand_id: int,
    db: Session = Depends(get_db),
):
    brand = BrandService(
        BrandRepository(db)
    ).get_brand(brand_id)

    if not brand:
        raise HTTPException(404, "Brand not found")

    return brand

@router.patch("/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_id: int,
    data: BrandUpdate,
    db: Session = Depends(get_db),
):

    service = BrandService(
        BrandRepository(db)
    )

    try:
        return service.update_brand(
            brand_id,
            data,
        )

    except ValueError as e:
        raise HTTPException(
            404,
            str(e),
        )

@router.delete("/{brand_id}")
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
):

    service = BrandService(
        BrandRepository(db)
    )

    try:
        service.delete_brand(brand_id)

    except ValueError as e:
        raise HTTPException(
            404,
            str(e),
        )

    return {
        "message": "Brand deleted successfully."
    }
