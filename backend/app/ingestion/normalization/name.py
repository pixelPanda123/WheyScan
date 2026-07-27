import re


class NameNormalizer:

    REMOVE_WORDS = {
        "protein",
        "powder",
        "100%",
        "whey",
        "isolate",
        "concentrate",
        "blend",
    }

    @classmethod
    def normalize(
        cls,
        name: str | None,
        brand: str | None,
        flavour: str | None,
    ) -> str:
        if not name: 
            return ""

        text = name

        if brand:
            text = re.sub(
                re.escape(brand),
                "",
                text,
                flags=re.IGNORECASE,
            )

        if flavour:
            text = re.sub(
                re.escape(flavour),
                "",
                text,
                flags=re.IGNORECASE,
            )

        text = re.sub(r"\d+(\.\d+)?\s?(kg|g|gm|lb|lbs)", "", text, flags=re.I)

        for word in cls.REMOVE_WORDS:
            text = re.sub(
                rf"\b{re.escape(word)}\b",
                "",
                text,
                flags=re.I,
            )

        text = re.sub(r"[()]+", "", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text.strip()