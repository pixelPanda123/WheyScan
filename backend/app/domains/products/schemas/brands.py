from pydantic import BaseModel, ConfigDict


class BrandCreate(BaseModel):
    name: str


class BrandResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class BrandUpdate(BaseModel):
    name: str | None = None