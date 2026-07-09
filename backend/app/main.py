import app.db.models

from fastapi import FastAPI

from app.api.analytics import router as analytics_router
from app.api.brands import router as brand_router
from app.api.discovery import router as discovery_router
from app.api.listings import router as listing_router
from app.api.products import router as product_router

app = FastAPI(
    title="Project Protein API"
)

app.include_router(product_router)
app.include_router(brand_router)
app.include_router(listing_router)
app.include_router(discovery_router)
app.include_router(analytics_router)


@app.get("/")
def root():
    return {"message": "Project Protein Backend"}
