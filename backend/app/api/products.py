from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.domains.products.exceptions import (
    ProductAlreadyExistsError,
    ProductBrandNotFoundError,
    ProductNotFoundError,
)
from app.domains.products.repositories import ProductRepository
from app.domains.products.schemas import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.domains.products.services import ProductService

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

    except ProductBrandNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ProductAlreadyExistsError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get("/", response_model=list[ProductResponse])
def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):

    repository = ProductRepository(db)
    service = ProductService(repository)

    return service.list_products(
        skip=skip,
        limit=limit,
    )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):

    repository = ProductRepository(db)
    service = ProductService(repository)

    try:
        return service.get_product(product_id)

    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
):

    repository = ProductRepository(db)
    service = ProductService(repository)

    try:
        return service.update_product(
            product_id,
            data,
        )

    except (ProductNotFoundError, ProductBrandNotFoundError) as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ProductAlreadyExistsError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):

    repository = ProductRepository(db)
    service = ProductService(repository)

    try:
        service.delete_product(product_id)

    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    return {
        "message": "Product deleted successfully."
    }
