from app.domains.products.models import Brand
from app.domains.products.repositories import BrandRepository
from app.domains.products.schemas import BrandCreate, BrandUpdate


class BrandService:

    def __init__(self, repository: BrandRepository):
        self.repository = repository

    def create_brand(self, data: BrandCreate):

        if self.repository.get_by_name(data.name):
            raise ValueError("Brand already exists.")

        brand = Brand(name=data.name)

        return self.repository.create(brand)

    def list_brands(self):
        return self.repository.get_all()

    def get_brand(self, brand_id: int):
        return self.repository.get_by_id(brand_id)

    def update_brand(
        self,
        brand_id: int,
        data: BrandUpdate,
    ):

        brand = self.repository.get_by_id(brand_id)

        if not brand:
            raise ValueError("Brand not found.")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(brand, key, value)

        return self.repository.update(brand)

    def delete_brand(
        self,
        brand_id: int,
    ):

        brand = self.repository.get_by_id(brand_id)

        if not brand:
            raise ValueError("Brand not found.")

        self.repository.delete(brand)
