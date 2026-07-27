# from app.ingestion.scraper.http.client import HTTPClient
# from app.ingestion.scraper.retailers.healthkart.discovery import HealthKartDiscoverer
# # from app.ingestion.scraper.retailers.optimum_nutrition.discovery import ONDiscoverer
# # from app.ingestion.scraper.retailers.muscleblaze.discovery import MuscleBlazeDiscoverer


# def run(discoverer):
#     count = 0

#     for product in discoverer.discover():
#         print(product)
#         print("-" * 100)

#         count += 1

#         if count == 5:
#             break

#     print(f"\nDiscovered {count} products.")


# def main():
#     client = HTTPClient()

#     # Change this line while developing
#     discoverer = HealthKartDiscoverer(client)

#     run(discoverer)


# if __name__ == "__main__":
#     main()


from itertools import islice

from app.ingestion.scraper.http.client import HTTPClient

from app.ingestion.scraper.retailers.healthkart.discovery import (
    HealthKartDiscoverer,
)
from app.ingestion.scraper.retailers.muscleblaze.discovery import (
    MuscleBlazeDiscoverer,
)


def test_discoverer(name: str, discoverer):
    print("=" * 80)
    print(f"Testing {name}")
    print("=" * 80)

    count = 0

    for product in discoverer.discover():

        count += 1

        if count <= 5:
            print(product)
            print()

    print(f"Total products discovered: {count}")
    print()


def main():

    client = HTTPClient()

    healthkart = HealthKartDiscoverer(client)
    muscleblaze = MuscleBlazeDiscoverer(client)

    test_discoverer("HealthKart", healthkart)
    test_discoverer("MuscleBlaze", muscleblaze)


if __name__ == "__main__":
    main()