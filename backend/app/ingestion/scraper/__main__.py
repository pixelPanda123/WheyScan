from app.ingestion.scraper.http.client import HTTPClient
from app.ingestion.scraper.retailers.healthkart.discovery import HealthKartDiscoverer


def main():
    client = HTTPClient()

    discoverer = HealthKartDiscoverer(client)

    count = 0

    for product in discoverer.discover():
        print(product)
        print("-" * 100)

        count += 1

        # Only print the first few products while developing
        if count == 5:
            break

    print(f"\nDiscovered {count} products.")


if __name__ == "__main__":
    main()