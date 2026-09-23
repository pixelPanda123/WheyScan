import app.db.models

from fastapi import FastAPI

from app.api.analytics import router as analytics_router
from app.api.brands import router as brand_router
from app.api.discovery import router as discovery_router
from app.api.listings import router as listing_router
from app.api.products import router as product_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Project Protein API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router)
app.include_router(brand_router)
app.include_router(listing_router)
app.include_router(discovery_router)
app.include_router(analytics_router)


@app.get("/")
def root():
    return {"message": "Project Protein Backend"}
