from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.products.models import Brand, Product


class ProductRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_by_id(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def brand_exists(self, brand_id: int) -> bool:
        return self.db.get(Brand, brand_id) is not None

    def get_by_slug(self, slug: str) -> Product | None:
        stmt = select(Product).where(Product.slug == slug)
        return self.db.scalar(stmt)

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Product]:
        stmt = select(Product)
        stmt = stmt.order_by(Product.id).offset(skip).limit(limit)

        return list(self.db.scalars(stmt).all())

    def update(self, product: Product) -> Product:
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()
