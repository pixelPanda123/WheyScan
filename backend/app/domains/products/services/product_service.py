from slugify import slugify

from app.domains.products.exceptions import (
    ProductAlreadyExistsError,
    ProductBrandNotFoundError,
    ProductNotFoundError,
)
from app.domains.products.models import Product
from app.domains.products.repositories import ProductRepository
from app.domains.products.schemas import ProductCreate, ProductUpdate


class ProductService:

    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def create_product(self, data: ProductCreate) -> Product:

        slug = slugify(data.name)

        if not self.repository.brand_exists(data.brand_id):
            raise ProductBrandNotFoundError("Brand not found.")

        if self.repository.get_by_slug(slug):
            raise ProductAlreadyExistsError("Product already exists.")

        product = Product(
            brand_id=data.brand_id,
            name=data.name,
            slug=slug,
            protein_type=data.protein_type,
            flavour=data.flavour,
            weight=data.weight,
            weight_unit=data.weight_unit,
            image_url=data.image_url,
        )

        return self.repository.create(product)

    def get_product(self, product_id: int):

        product = self.repository.get_by_id(product_id)

        if not product:
            raise ProductNotFoundError("Product not found.")

        return product

    def list_products(
        self,
        skip: int = 0,
        limit: int = 20,
    ):

        return self.repository.list(
            skip=skip,
            limit=limit,
        )

    def update_product(
        self,
        product_id: int,
        data: ProductUpdate,
    ):

        product = self.repository.get_by_id(product_id)

        if not product:
            raise ProductNotFoundError("Product not found.")

        update_data = data.model_dump(exclude_unset=True)

        if "brand_id" in update_data:
            brand_id = update_data["brand_id"]
            if brand_id is not None and not self.repository.brand_exists(brand_id):
                raise ProductBrandNotFoundError("Brand not found.")

        if "name" in update_data and update_data["name"] is not None:
            slug = slugify(update_data["name"])
            existing = self.repository.get_by_slug(slug)

            if existing and existing.id != product.id:
                raise ProductAlreadyExistsError("Product already exists.")

            update_data["slug"] = slug

        for key, value in update_data.items():
            setattr(product, key, value)

        return self.repository.update(product)

    def delete_product(self, product_id: int):

        product = self.repository.get_by_id(product_id)

        if not product:
            raise ProductNotFoundError("Product not found.")

        self.repository.delete(product)
