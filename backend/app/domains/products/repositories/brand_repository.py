from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.products.models import Brand


class BrandRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, brand: Brand):
        self.db.add(brand)
        self.db.commit()
        self.db.refresh(brand)
        return brand

    def get_all(self):
        return list(self.db.scalars(select(Brand)).all())

    def get_by_id(self, brand_id: int):
        return self.db.get(Brand, brand_id)

    def get_by_name(self, name: str):
        stmt = select(Brand).where(Brand.name == name)
        return self.db.scalar(stmt)
    def update(self, brand: Brand):
        self.db.commit()
        self.db.refresh(brand)
        return brand

    def delete(self, brand: Brand):
        self.db.delete(brand)
        self.db.commit()