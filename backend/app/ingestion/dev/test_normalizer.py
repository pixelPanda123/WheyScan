from app.ingestion.normalization.normalizer import ProductNormalizer

from app.ingestion.scraper.http.client import HTTPClient

from app.ingestion.scraper.retailers.healthkart.discovery import (
    HealthKartDiscoverer,
)
from app.ingestion.scraper.retailers.muscleblaze.discovery import (
    MuscleBlazeDiscoverer,
)

from app.ingestion.scraper.retailers.optimum_nutrition.discovery import (
    OptimumNutritionDiscoverer,
)
from app.ingestion.scraper.retailers.optimum_nutrition.extractor import (
    OptimumNutritionExtractor,
)


def print_product(raw, normalized):
    print("=" * 80)
    print(raw.name)
    print(f"Brand    : {raw.brand} -> {normalized.brand}")
    print(f"Weight   : {raw.weight} -> {normalized.weight_g}")
    print(f"Flavour  : {raw.flavour} -> {normalized.flavour}")
    print(f"Protein  : {raw.protein_type} -> {normalized.protein_type}")
    print(f"Name     : {normalized.name}")


def main():
    client = HTTPClient()

    # Veronica retailers
    discoverers = [
        HealthKartDiscoverer(client),
        MuscleBlazeDiscoverer(client),
    ]

    for discoverer in discoverers:
        print(f"\n===== {discoverer.RETAILER} =====")

        for i, raw in enumerate(discoverer.discover()):
            normalized = ProductNormalizer.normalize(raw)

            print_product(raw, normalized)

            if i == 9:
                break

    # Optimum Nutrition
    print("\n===== optimum_nutrition =====")

    discoverer = OptimumNutritionDiscoverer()
    extractor = OptimumNutritionExtractor()

    for i, url in enumerate(discoverer.discover()):
        try:
            raw = extractor.extract(url)
            normalized = ProductNormalizer.normalize(raw)

            print_product(raw, normalized)

            if i == 9:
                break

        except Exception as e:
            print(f"Failed to process {url}: {e}")


if __name__ == "__main__":
    main()