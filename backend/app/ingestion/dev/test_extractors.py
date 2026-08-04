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


def print_product(raw):
    print("=" * 80)
    print(f"Name      : {raw.name}")
    print(f"Brand     : {raw.brand}")
    print(f"Weight    : {raw.weight}")
    print(f"Flavour   : {raw.flavour}")
    print(f"Protein   : {raw.protein_type}")
    print(f"Price     : {raw.current_price}")
    print(f"Available : {raw.availability}")
    print(f"URL       : {raw.product_url}")


def summary(products):
    print("\nSummary")
    print("-" * 40)

    print(f"Products           : {len(products)}")
    print(f"Missing Name       : {sum(p.name is None for p in products)}")
    print(f"Missing Brand      : {sum(p.brand is None for p in products)}")
    print(f"Missing Weight     : {sum(p.weight is None for p in products)}")
    print(f"Missing Flavour    : {sum(p.flavour is None for p in products)}")
    print(f"Missing Protein    : {sum(p.protein_type is None for p in products)}")
    print(f"Missing Price      : {sum(p.current_price is None for p in products)}")


def test_healthkart(client):

    print("\n")
    print("=" * 80)
    print("HEALTHKART")
    print("=" * 80)

    discoverer = HealthKartDiscoverer(client)

    products = list(discoverer.discover())

    for product in products[:10]:
        print_product(product)

    summary(products)


def test_muscleblaze(client):

    print("\n")
    print("=" * 80)
    print("MUSCLEBLAZE")
    print("=" * 80)

    discoverer = MuscleBlazeDiscoverer(client)

    products = list(discoverer.discover())

    for product in products[:10]:
        print_product(product)

    summary(products)


def test_on():

    print("\n")
    print("=" * 80)
    print("OPTIMUM NUTRITION")
    print("=" * 80)

    discoverer = OptimumNutritionDiscoverer()

    extractor = OptimumNutritionExtractor()

    urls = discoverer.discover()

    products = []

    for url in urls:

        try:
            raw = extractor.extract(url)
            products.append(raw)

        except Exception as e:
            print(f"Failed: {url}")
            print(e)

    for product in products[:10]:
        print_product(product)

    summary(products)


def main():

    client = HTTPClient()

    test_healthkart(client)

    test_muscleblaze(client)

    test_on()


if __name__ == "__main__":
    main()