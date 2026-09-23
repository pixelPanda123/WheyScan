from sqlalchemy import asc, desc, distinct, func, select
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
    ) -> list[dict]:
        qualified_products = (
            select(Listing.product_id)
            .group_by(Listing.product_id)
            .having(func.count(distinct(Listing.store_id)) >= 2)
        )

        product_name = Product.name.label("product_name")
        brand_name = Brand.name.label("brand_name")
        product_weight = Product.weight.label("product_weight")
        min_price = func.min(Listing.current_price).label("min_price")

        product_stmt = (
            select(
                Product.id.label("product_id"),
                product_name,
                brand_name,
                product_weight,
                min_price,
            )
            .join(Brand, Product.brand_id == Brand.id)
            .join(Listing, Listing.product_id == Product.id)
            .join(Store, Store.id == Listing.store_id)
            .where(Product.id.in_(qualified_products))
        )

        if query:
            search = f"%{query}%"
            product_stmt = product_stmt.where(
                Product.name.ilike(search)
                | Product.slug.ilike(search)
                | Product.protein_type.ilike(search)
                | Product.flavour.ilike(search)
                | Brand.name.ilike(search)
                | Store.name.ilike(search)
            )

        if brand_id is not None:
            product_stmt = product_stmt.where(Product.brand_id == brand_id)

        if protein_type:
            product_stmt = product_stmt.where(Product.protein_type.ilike(protein_type))

        if weight is not None:
            product_stmt = product_stmt.where(Product.weight == weight)

        if availability is not None:
            product_stmt = product_stmt.where(Listing.availability == availability)

        if price_min is not None:
            product_stmt = product_stmt.where(Listing.current_price >= price_min)

        if price_max is not None:
            product_stmt = product_stmt.where(Listing.current_price <= price_max)

        if store_id is not None:
            product_stmt = product_stmt.where(Listing.store_id == store_id)

        product_stmt = product_stmt.group_by(
            Product.id,
            Product.name,
            Brand.name,
            Product.weight,
        )

        sort_columns = {
            "name": product_name,
            "price": min_price,
            "brand": brand_name,
            "weight": product_weight,
        }
        sort_column = sort_columns.get(sort_by, product_name)
        sort_direction = desc if sort_order == "desc" else asc

        product_stmt = (
            product_stmt.order_by(sort_direction(sort_column), Product.id)
            .offset(skip)
            .limit(limit)
        )

        product_ids = [
            row.product_id
            for row in self.db.execute(product_stmt).all()
        ]

        if not product_ids:
            return []

        rows = self.db.execute(
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
                Listing.url.label("product_url"),
            )
            .join(Brand, Product.brand_id == Brand.id)
            .join(Listing, Listing.product_id == Product.id)
            .join(Store, Store.id == Listing.store_id)
            .where(Product.id.in_(product_ids))
            .order_by(Product.id, Listing.current_price, Listing.id)
        ).mappings().all()

        order = {product_id: index for index, product_id in enumerate(product_ids)}
        return sorted(rows, key=lambda row: (order[row["product_id"]], row["listing_id"]))
