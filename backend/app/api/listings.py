from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.domains.listings.exceptions import (
    ListingAlreadyExistsError,
    ListingNotFoundError,
    ListingProductNotFoundError,
    ListingStoreNotFoundError,
    StoreAlreadyExistsError,
    StoreHasListingsError,
    StoreNotFoundError,
)
from app.domains.listings.repositories import (
    ListingRepository,
    PriceHistoryRepository,
    StoreRepository,
)
from app.domains.listings.schemas import (
    ListingCreate,
    ListingResponse,
    ListingUpdate,
    PriceHistoryResponse,
    StoreCreate,
    StoreResponse,
    StoreUpdate,
)
from app.domains.listings.services import ListingService, StoreService

router = APIRouter(
    tags=["Listings"],
)


def get_store_service(db: Session) -> StoreService:
    return StoreService(StoreRepository(db))


def get_listing_service(db: Session) -> ListingService:
    return ListingService(
        ListingRepository(db),
        PriceHistoryRepository(db),
    )


@router.post("/stores", response_model=StoreResponse)
def create_store(
    store: StoreCreate,
    db: Session = Depends(get_db),
):
    service = get_store_service(db)

    try:
        return service.create_store(store)

    except StoreAlreadyExistsError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get("/stores", response_model=list[StoreResponse])
def list_stores(
    db: Session = Depends(get_db),
):
    return get_store_service(db).list_stores()


@router.get("/stores/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_store_service(db).get_store(store_id)

    except StoreNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@router.patch("/stores/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    data: StoreUpdate,
    db: Session = Depends(get_db),
):
    try:
        return get_store_service(db).update_store(
            store_id,
            data,
        )

    except StoreNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except StoreAlreadyExistsError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.delete("/stores/{store_id}")
def delete_store(
    store_id: int,
    db: Session = Depends(get_db),
):
    try:
        get_store_service(db).delete_store(store_id)

    except StoreNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except StoreHasListingsError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return {
        "message": "Store deleted successfully."
    }


@router.post("/listings", response_model=ListingResponse)
def create_listing(
    listing: ListingCreate,
    db: Session = Depends(get_db),
):
    service = get_listing_service(db)

    try:
        return service.create_listing(listing)

    except (ListingProductNotFoundError, ListingStoreNotFoundError) as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ListingAlreadyExistsError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get("/listings", response_model=list[ListingResponse])
def list_listings(
    db: Session = Depends(get_db),
):
    return get_listing_service(db).list_listings()


@router.get("/products/{product_id}/listings", response_model=list[ListingResponse])
def get_product_listings(
    product_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_listing_service(db).get_product_listings(product_id)

    except ListingProductNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@router.get("/listings/{listing_id}", response_model=ListingResponse)
def get_listing(
    listing_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_listing_service(db).get_listing(listing_id)

    except ListingNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@router.get("/listings/{listing_id}/history", response_model=list[PriceHistoryResponse])
def get_listing_history(
    listing_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_listing_service(db).listing_history(listing_id)

    except ListingNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@router.patch("/listings/{listing_id}", response_model=ListingResponse)
def update_listing(
    listing_id: int,
    data: ListingUpdate,
    db: Session = Depends(get_db),
):
    service = get_listing_service(db)

    try:
        return service.update_listing(
            listing_id,
            data,
        )

    except (
        ListingNotFoundError,
        ListingProductNotFoundError,
        ListingStoreNotFoundError,
    ) as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except ListingAlreadyExistsError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.delete("/listings/{listing_id}")
def delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
):
    try:
        get_listing_service(db).delete_listing(listing_id)

    except ListingNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    return {
        "message": "Listing deleted successfully."
    }
