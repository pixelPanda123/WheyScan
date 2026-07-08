from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    brand_id: int
    name: str
    slug: str
    protein_type: str
    flavour: str
    weight: float
    weight_unit: str
    image_url: str | None = None


class ProductResponse(BaseModel):
    id: int
    brand_id: int
    name: str
    slug: str
    protein_type: str
    flavour: str
    weight: float
    weight_unit: str
    image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    brand_id: int | None = None
    name: str | None = None
    slug: str | None = None
    protein_type: str | None = None
    flavour: str | None = None
    weight: float | None = None
    weight_unit: str | None = None
    image_url: str | None = None