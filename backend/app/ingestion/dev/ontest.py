from app.ingestion.scraper.retailers.optimum_nutrition.discovery import OptimumNutritionDiscoverer
from app.ingestion.scraper.retailers.optimum_nutrition.extractor import OptimumNutritionExtractor
from app.ingestion.normalization.normalizer import ProductNormalizer

discoverer = OptimumNutritionDiscoverer(client)
extractor = OptimumNutritionExtractor(client)

for i, url in enumerate(discoverer.discover()):

    raw = extractor.extract(url)
    normalized = ProductNormalizer.normalize(raw)

    print("=" * 80)
    print(raw.name)
    print(f"Brand    : {raw.brand} -> {normalized.brand}")
    print(f"Weight   : {raw.weight} -> {normalized.weight_g}")
    print(f"Flavour  : {raw.flavour} -> {normalized.flavour}")
    print(f"Protein  : {raw.protein_type} -> {normalized.protein_type}")
    print(f"Name     : {normalized.name}")

    if i == 9:
        break