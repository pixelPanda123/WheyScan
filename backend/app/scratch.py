from app.ingestion.scraper.http.client import HTTPClient
from app.ingestion.scraper.retailers.healthkart.discovery import HealthKartDiscoverer

client = HTTPClient()
discoverer = HealthKartDiscoverer(client)

count = 0

for product in discoverer.discover():
    count += 1

    print(product)

    if count == 5:
        break

print(f"\nDiscovered {count} products.")