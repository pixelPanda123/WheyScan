class FlavourNormalizer:

    FLAVOUR_MAP = {

        "double rich chocolate": "Chocolate",
        "rich chocolate": "Chocolate",
        "milk chocolate": "Chocolate",
        "chocolate": "Chocolate",

        "cookies & cream": "Cookies and Cream",
        "cookies and creme": "Cookies and Cream",
        "cookies and cream": "Cookies and Cream",

        "vanilla ice cream": "Vanilla",
        "french vanilla": "Vanilla",
        "vanilla": "Vanilla",

        "banana": "Banana",
        "mango": "Mango",
        "strawberry": "Strawberry",

        "cafe mocha": "Mocha",
        "mocha": "Mocha",
    }

    @classmethod
    def normalize(cls, flavour: str | None) -> str | None:

        if not flavour:
            return None

        text = flavour.strip().lower()

        return cls.FLAVOUR_MAP.get(text, flavour.strip())