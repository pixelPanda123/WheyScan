from slugify import slugify

from app.domains.products.models import Product
from app.domains.products.schemas import ProductCreate, ProductUpdate
from app.domains.products.repository import ProductRepository


class ProductService:

    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def create_product(self, data: ProductCreate) -> Product:

        slug = slugify(data.name)

        existing = self.repository.get_by_slug(slug)

        if existing:
            raise ValueError("Product already exists.")

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

        return self.repository.get_by_id(product_id)

    def list_products(self):

        return self.repository.get_all()

    def update_product(self, product: Product):

        return self.repository.update(product)

    def delete_product(self, product_id: int):

        product = self.repository.get_by_id(product_id)

        if not product:
            raise ValueError("Product not found.")

        self.repository.delete(product)