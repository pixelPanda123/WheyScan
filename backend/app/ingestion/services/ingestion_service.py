from app.ingestion.scraper.base.types import RawProduct


class IngestionService:

    def ingest(self, product: RawProduct):

        print("=" * 80)
        print("INGESTING PRODUCT")
        print("=" * 80)

        print(f"Retailer : {product.retailer}")
        print(f"Brand    : {product.brand}")
        print(f"Product  : {product.name}")
        print(f"Price    : ₹{product.current_price}")

        print("=" * 80)