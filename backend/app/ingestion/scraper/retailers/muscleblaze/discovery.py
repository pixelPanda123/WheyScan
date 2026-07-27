from app.ingestion.scraper.http.client import HTTPClient
from app.ingestion.scraper.retailers.veronica.base import VeronicaDiscoverer


class MuscleBlazeDiscoverer(VeronicaDiscoverer):

    BASE_URL = "https://www.muscleblaze.com"
    RETAILER = "muscleblaze"

    CATEGORY_ID = "CL-1703"
    PER_PAGE = 24

    def __init__(self, client: HTTPClient):
        self.client = client

    def fetch_page(self, page: int) -> list[dict]:

        response = self.client.get(
            f"{self.BASE_URL}/veronica/catalog/results/{self.CATEGORY_ID}",
            params={
                "pageNo": page,
                "perPage": self.PER_PAGE,
                "excludeOOS": "true",
                "plt": 1,
                "st": 9,
            },
        )

        response.raise_for_status()

        data = response.json()

        return data.get("results", {}).get("variants", [])