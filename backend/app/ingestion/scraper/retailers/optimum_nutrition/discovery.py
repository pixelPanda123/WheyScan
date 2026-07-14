from xml.etree import ElementTree

from app.ingestion.scraper.http.client import HTTPClient


class OptimumNutritionDiscoverer:
    """
    Discovers all product URLs from the Optimum Nutrition Shopify sitemap.
    """

    SITEMAP_INDEX = "https://www.optimumnutrition.co.in/sitemap.xml"

    def __init__(self):
        self.client = HTTPClient()

    def discover(self) -> list[str]:
        """
        Returns every product URL from all Shopify product sitemaps.
        """
        product_urls = []

        for sitemap in self._get_product_sitemaps():
            product_urls.extend(self._parse_product_sitemap(sitemap))

        return product_urls

    def _get_product_sitemaps(self) -> list[str]:
        """
        Reads sitemap.xml and returns only product sitemap URLs.
        """

        response = self.client.get(self.SITEMAP_INDEX)

        root = ElementTree.fromstring(response.content)

        namespace = {
            "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
        }

        sitemaps = []

        for sitemap in root.findall("sm:sitemap", namespace):
            loc = sitemap.find("sm:loc", namespace)

            if loc is None:
                continue

            if "sitemap_products" in loc.text:
                sitemaps.append(loc.text)

        return sitemaps

    def _parse_product_sitemap(self, sitemap_url: str) -> list[str]:
        """
        Reads a product sitemap and extracts every product URL.
        """

        response = self.client.get(sitemap_url)

        root = ElementTree.fromstring(response.content)

        namespace = {
            "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
        }

        product_urls = []

        for url in root.findall("sm:url", namespace):
            loc = url.find("sm:loc", namespace)

            if loc is None:
                continue

            if "/products/" in loc.text:
                product_urls.append(loc.text)

        return product_urls