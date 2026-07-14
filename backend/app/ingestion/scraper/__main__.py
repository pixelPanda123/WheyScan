from app.ingestion.scraper.retailers.optimum_nutrition.discovery import (
    OptimumNutritionDiscoverer,
)
from app.ingestion.scraper.retailers.optimum_nutrition.extractor import (
    OptimumNutritionExtractor,
)


def main():
    discoverer = OptimumNutritionDiscoverer()
    extractor = OptimumNutritionExtractor()

    urls = discoverer.discover()

    print(f"Found {len(urls)} products\n")

    for i, url in enumerate(urls[:5], start=1):
        print(f"Product {i}")
        print(f"URL: {url}\n")

        product = extractor.extract(url)

        print(product)
        print("-" * 80)


if __name__ == "__main__":
    main()