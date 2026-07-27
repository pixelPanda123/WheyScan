class BrandNormalizer:

    BRAND_MAP = {
        "on": "Optimum Nutrition",
        "optimum nutrition": "Optimum Nutrition",

        "muscleblaze": "MuscleBlaze",
        "muscle blaze": "MuscleBlaze",

        "myprotein": "MyProtein",

        "gnc": "GNC",

        "nakpro": "Nakpro",

        "as-it-is": "AS-IT-IS",
        "as it is": "AS-IT-IS",

        "dymatize": "Dymatize",

        "isopure": "Isopure",

        "avvatar": "Avvatar",
    }

    @classmethod
    def normalize(cls, brand: str | None) -> str | None:
        if not brand:
            return None

        key = brand.strip().lower()

        return cls.BRAND_MAP.get(key, brand.strip())