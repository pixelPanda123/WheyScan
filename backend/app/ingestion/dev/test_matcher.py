from app.ingestion.matching.matcher import ProductMatcher
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

from app.ingestion.filtering.catalog_filter import CatalogFilter
from app.ingestion.filtering.classifier import ProductClassifier


def process_product(raw, catalog):

    if not CatalogFilter.accept(raw):
        kind = ProductClassifier.classify(raw.name)

        print(f"[SKIP] {kind.value:12} | {raw.name}")

        return False

    normalized = ProductNormalizer.normalize(raw)

    match, score = ProductMatcher.match(
        normalized,
        catalog,
    )

    if match is None:
        catalog.append(normalized)

        print(
            f"[NEW]   {normalized.brand} | "
            f"{normalized.name} | "
            f"{normalized.weight_g}g"
        )

    else:
        print(
            f"[MATCH] {normalized.brand} | "
            f"{normalized.name}"
        )

        print(
            f"        -> {match.brand} | "
            f"{match.name}"
        )

        print(
            f"        Score : {score.score:.3f}"
        )

    return match is not None


def main():

    client = HTTPClient()

    catalog = []

    matched = 0

    total = 0

    # -----------------------------
    # HealthKart
    # -----------------------------

    print("\n====================")
    print("HEALTHKART")
    print("====================")

    hk = HealthKartDiscoverer(client)

    for raw in hk.discover():

        total += 1

        if process_product(raw, catalog):
            matched += 1

    # -----------------------------
    # MuscleBlaze
    # -----------------------------

    print("\n====================")
    print("MUSCLEBLAZE")
    print("====================")

    mb = MuscleBlazeDiscoverer(client)

    for raw in mb.discover():

        total += 1

        if process_product(raw, catalog):
            matched += 1

    # -----------------------------
    # Optimum Nutrition
    # -----------------------------

    print("\n====================")
    print("OPTIMUM NUTRITION")
    print("====================")

    discoverer = OptimumNutritionDiscoverer()

    extractor = OptimumNutritionExtractor()

    for url in discoverer.discover():

        total += 1

        try:

            raw = extractor.extract(url)

            if process_product(raw, catalog):
                matched += 1

        except Exception as e:

            print(f"Skipped {url}")

            print(e)

    print("\n")
    print("=" * 70)

    print(f"Total Products      : {total}")
    print(f"Canonical Products  : {len(catalog)}")
    print(f"Matched Products    : {matched}")
    print(f"New Products        : {len(catalog)}")

    print("=" * 70)


if __name__ == "__main__":
    main()