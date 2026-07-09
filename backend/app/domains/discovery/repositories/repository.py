from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.domains.listings.models import Listing, Store
from app.domains.products.models import Brand, Product


class DiscoveryRepository:

    def __init__(self, db: Session):
        self.db = db

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
    ):
        stmt = (
            select(
                Product.id.label("product_id"),
                Product.brand_id,
                Brand.name.label("brand_name"),
                Product.name,
                Product.slug,
                Product.protein_type,
                Product.flavour,
                Product.weight,
                Product.weight_unit,
                Product.image_url,
                Listing.id.label("listing_id"),
                Listing.store_id,
                Store.name.label("store_name"),
                Listing.current_price,
                Listing.availability,
            )
            .join(Brand, Product.brand_id == Brand.id)
            .outerjoin(Listing, Listing.product_id == Product.id)
            .outerjoin(Store, Store.id == Listing.store_id)
        )

        if query:
            search = f"%{query}%"
            stmt = stmt.where(
                Product.name.ilike(search)
                | Product.slug.ilike(search)
                | Product.protein_type.ilike(search)
                | Product.flavour.ilike(search)
                | Brand.name.ilike(search)
                | Store.name.ilike(search)
            )

        if brand_id is not None:
            stmt = stmt.where(Product.brand_id == brand_id)

        if protein_type:
            stmt = stmt.where(Product.protein_type.ilike(protein_type))

        if weight is not None:
            stmt = stmt.where(Product.weight == weight)

        if availability is not None:
            stmt = stmt.where(Listing.availability == availability)

        if price_min is not None:
            stmt = stmt.where(Listing.current_price >= price_min)

        if price_max is not None:
            stmt = stmt.where(Listing.current_price <= price_max)

        if store_id is not None:
            stmt = stmt.where(Listing.store_id == store_id)

        sort_columns = {
            "name": Product.name,
            "price": Listing.current_price,
            "brand": Brand.name,
            "weight": Product.weight,
        }
        sort_column = sort_columns.get(sort_by, Product.name)
        sort_direction = desc if sort_order == "desc" else asc

        stmt = (
            stmt.order_by(sort_direction(sort_column), Product.id, Listing.id)
            .offset(skip)
            .limit(limit)
        )

        return self.db.execute(stmt).mappings().all()
