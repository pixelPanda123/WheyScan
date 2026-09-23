"""
Scrape retailers and write the results to the database.

Usage (from backend/):

    python -m app.ingestion.run                         # all retailers
    python -m app.ingestion.run -r healthkart -l 20     # one retailer, first 20 items
    python -m app.ingestion.run --dry-run               # run everything, then roll back

Each product is ingested inside its own savepoint, so one bad product is
logged and skipped without losing the rest of the run.
"""

import argparse
import logging
import time
from collections import Counter
from dataclasses import dataclass
from itertools import islice
from typing import Callable, Iterator

from sqlalchemy.orm import Session

import app.db.models  # noqa: F401  (register all mappers)
from app.db.session import SessionLocal, engine
from app.domains.listings.models import Store
from app.ingestion.scraper.base.types import RawProduct
from app.ingestion.scraper.http.client import HTTPClient
from app.ingestion.scraper.retailers.healthkart.discovery import HealthKartDiscoverer
from app.ingestion.scraper.retailers.muscleblaze.discovery import MuscleBlazeDiscoverer
from app.ingestion.scraper.retailers.optimum_nutrition.discovery import (
    OptimumNutritionDiscoverer,
)
from app.ingestion.scraper.retailers.optimum_nutrition.extractor import (
    OptimumNutritionExtractor,
)
from app.ingestion.services.ingestion_service import IngestionService

log = logging.getLogger("ingestion")


@dataclass(frozen=True)
class RetailerSource:
    store_name: str  # must equal RawProduct.retailer
    base_url: str
    iter_products: Callable[[HTTPClient, Counter, float], Iterator[RawProduct]]


def _healthkart(client: HTTPClient, stats: Counter, delay: float):
    yield from HealthKartDiscoverer(client).discover()


def _muscleblaze(client: HTTPClient, stats: Counter, delay: float):
    yield from MuscleBlazeDiscoverer(client).discover()


def _optimum_nutrition(client: HTTPClient, stats: Counter, delay: float):
    extractor = OptimumNutritionExtractor()

    for url in OptimumNutritionDiscoverer().discover():
        try:
            yield extractor.extract(url)
        except Exception as exc:  # one broken product page shouldn't stop the run
            stats["scrape_failed"] += 1
            log.warning("scrape failed %s: %s", url, exc)

        if delay:
            time.sleep(delay)


SOURCES: dict[str, RetailerSource] = {
    "healthkart": RetailerSource(
        "healthkart", "https://www.healthkart.com", _healthkart
    ),
    "muscleblaze": RetailerSource(
        "muscleblaze", "https://www.muscleblaze.com", _muscleblaze
    ),
    "optimum_nutrition": RetailerSource(
        "optimum_nutrition", "https://www.optimumnutrition.co.in", _optimum_nutrition
    ),
}


def seed_stores(db: Session, names: list[str], *, dry_run: bool = False) -> None:
    for name in names:
        source = SOURCES[name]

        if db.query(Store).filter_by(name=source.store_name).first() is None:
            db.add(Store(name=source.store_name, base_url=source.base_url, active=True))
            log.info("seeded store %s", source.store_name)

    if dry_run:
        db.flush()
    else:
        db.commit()


def ingest_retailer(
    db: Session,
    service: IngestionService,
    source: RetailerSource,
    client: HTTPClient,
    *,
    limit: int | None,
    delay: float,
    dry_run: bool,
) -> Counter:

    stats: Counter = Counter()
    products = source.iter_products(client, stats, delay)

    if limit:
        products = islice(products, limit)

    for raw in products:
        stats["seen"] += 1

        try:
            with db.begin_nested():
                result = service.ingest(raw)

        except Exception as exc:
            service.reset_cache()
            stats["failed"] += 1
            log.warning("ingest failed [%s] %s: %s", source.store_name, raw.name, exc)
            continue

        if result is None:
            stats["filtered_out"] += 1
            continue

        stats["ingested"] += 1
        stats["new_products"] += result.created_product
        stats["matched_existing"] += not result.created_product
        stats["new_listings"] += result.created_listing
        stats["price_changes"] += result.price_changed

        if not dry_run:
            db.commit()

    return stats


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "-r", "--retailer",
        action="append",
        choices=sorted(SOURCES),
        help="retailer to scrape (repeatable, default: all)",
    )
    parser.add_argument("-l", "--limit", type=int, help="max products per retailer")
    parser.add_argument(
        "--delay",
        type=float,
        default=0.3,
        help="seconds between per-product requests (Optimum Nutrition only)",
    )
    parser.add_argument("--dry-run", action="store_true", help="roll back at the end")
    parser.add_argument("-v", "--verbose", action="store_true", help="log SQL")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    engine.echo = args.verbose

    names = args.retailer or list(SOURCES)
    client = HTTPClient()

    with SessionLocal() as db:
        seed_stores(db, names, dry_run=args.dry_run)
        service = IngestionService(db)

        for name in names:
            log.info("=== %s ===", name)
            stats = ingest_retailer(
                db,
                service,
                SOURCES[name],
                client,
                limit=args.limit,
                delay=args.delay,
                dry_run=args.dry_run,
            )
            log.info("%s: %s", name, dict(stats))

        if args.dry_run:
            db.rollback()
            log.info("dry run: all changes rolled back")


if __name__ == "__main__":
    main()
