from app.ingestion.filtering.classifier import ProductClassifier

tests = [
    "Gold Standard 100% Whey",
    "Micronized Creatine",
    "Fish Oil 60 Capsules",
    "Gym Bag",
    "Opti Lock Shaker",
    "Gold Standard Whey + Fish Oil",
]

for t in tests:
    print(t, "->", ProductClassifier.classify(t))