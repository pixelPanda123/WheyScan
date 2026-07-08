from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.domains.products.repository import ProductRepository
from app.domains.products.schemas import (
    ProductCreate,
    ProductResponse,
)
from app.domains.products.service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post("/", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
):

    repository = ProductRepository(db)
    service = ProductService(repository)

    try:
        return service.create_product(product)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

@router.get("/", response_model=list[ProductResponse])
def list_products(
    db: Session = Depends(get_db),
):

    repository = ProductRepository(db)
    service = ProductService(repository)

    return service.list_products()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):

    repository = ProductRepository(db)
    service = ProductService(repository)

    product = service.get_product(product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product