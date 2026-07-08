import app.db.models

from fastapi import FastAPI
from app.api.products import router as product_router

app = FastAPI(
    title="Project Protein API"
)

app.include_router(product_router)


@app.get("/")
def root():
    return {"message": "Project Protein Backend"}