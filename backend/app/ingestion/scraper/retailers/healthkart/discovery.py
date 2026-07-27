from app.ingestion.scraper.http.client import HTTPClient
from app.ingestion.scraper.retailers.veronica.base import VeronicaDiscoverer


class HealthKartDiscoverer(VeronicaDiscoverer):

    BASE_URL = "https://www.healthkart.com"
    RETAILER = "healthkart"

    def __init__(self, client: HTTPClient):
        self.client = client

    def fetch_page(self, page: int) -> list[dict]:

        response = self.client.get(
            f"{self.BASE_URL}/veronica/catalog/results",
            params={
                "catPrefix": "snt-pt-wp",
                "parentCatPrefix": "snt-pt-wp",
                "navKey": "SCT-snt-pt-wp",
                "pageNo": page,
                "perPage": 24,
                "excludeOOS": "true",
                "plt": 1,
                "st": 1,
            },
        )

        response.raise_for_status()

        data = response.json()

        return data.get("results", {}).get("variants", [])