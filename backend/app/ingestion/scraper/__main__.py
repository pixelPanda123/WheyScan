# # from app.ingestion.scraper.retailers.optimum_nutrition.discovery import (
# #     OptimumNutritionDiscoverer,
# # )
# # from app.ingestion.scraper.retailers.optimum_nutrition.extractor import (
# #     OptimumNutritionExtractor,
# # )
# # from app.ingestion.services.ingestion_service import IngestionService


# # def main():
# #     discoverer = OptimumNutritionDiscoverer()
# #     extractor = OptimumNutritionExtractor()
# #     ingestion = IngestionService()

# #     urls = discoverer.discover()

# #     print(f"Found {len(urls)} products\n")

# #     for i, url in enumerate(urls[:5], start=1):
# #         print(f"Product {i}")
# #         print(f"URL: {url}\n")

# #         product = extractor.extract(url)
# #         ingestion.ingest(product)

# # from app.ingestion.scraper.retailers.healthkart.discovery import (
# #     HealthKartDiscoverer,
# # )


# # def main():
# #     discoverer = HealthKartDiscoverer()

# #     urls = discoverer.discover()

# #     print(f"Found {len(urls)} products\n")

# #     for url in urls[:10]:
# #         print(url)



# # if __name__ == "__main__":
# #     main()

# from app.ingestion.scraper.retailers.healthkart.discovery import (
#     HealthKartDiscoverer,
# )


# def main():
#     discoverer = HealthKartDiscoverer()

#     urls = discoverer.discover()

#     print(f"\nFound {len(urls)} products\n")

#     for url in urls:
#         print(url)


# if __name__ == "__main__":
#     main()

from app.ingestion.scraper.retailers.healthkart.discovery import (
    HealthKartDiscoverer
)


def main():

    discoverer = HealthKartDiscoverer()

    urls = discoverer.discover()

    print(f"\nFound {len(urls)} products\n")

    for url in urls:
        print(url)


if __name__ == "__main__":
    main()