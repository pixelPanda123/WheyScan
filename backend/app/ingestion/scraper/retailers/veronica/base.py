from abc import ABC, abstractmethod
from typing import Iterator


from app.ingestion.scraper.base.types import RawProduct

from .parser import VeronicaParser


class VeronicaDiscoverer(ABC):

    RETAILER: str
    BASE_URL: str

    @abstractmethod
    def fetch_page(self, page: int) -> list[dict]:
        """
        Return one page of Veronica variants.
        """
        raise NotImplementedError

    def discover(self) -> Iterator[RawProduct]:

        page = 1

        while True:

            variants = self.fetch_page(page)

            if not variants:
                break

            for variant in variants:
                yield VeronicaParser.parse(
                    retailer=self.RETAILER,
                    base_url=self.BASE_URL,
                    product=variant,
                )

            page += 1