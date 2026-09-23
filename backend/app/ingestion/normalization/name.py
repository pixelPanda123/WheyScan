import re


# Longest unit first, with a word boundary: with "lb|lbs" the regex matched
# "5 lb" inside "5 lbs" and left a stray "s" in the product name.
WEIGHT_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:kgs?|grams?|gms?|g|lbs?|oz)\b",
    re.IGNORECASE,
)

# Characters retailers use to separate "name | flavour | size" in titles.
SEPARATOR_PATTERN = re.compile(r"[|,]")


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
        raw_flavour: str | None = None,
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

        # Remove the retailer's flavour text first ("Double Rich Chocolate"),
        # then the normalized one ("Chocolate"). Removing only the normalized
        # flavour left fragments such as "Double Rich" in the name.
        for value in (raw_flavour, flavour):
            if value:
                text = re.sub(
                    re.escape(value),
                    "",
                    text,
                    flags=re.IGNORECASE,
                )

        text = WEIGHT_PATTERN.sub("", text)

        for word in cls.REMOVE_WORDS:
            text = re.sub(
                rf"\b{re.escape(word)}\b",
                "",
                text,
                flags=re.I,
            )

        text = re.sub(r"[()]+", "", text)

        # Drop separator segments emptied by the removals above
        # ("Gold Standard 100% | | " -> "Gold Standard 100%").
        parts = [
            re.sub(r"\s+", " ", part).strip()
            for part in SEPARATOR_PATTERN.split(text)
        ]
        text = " ".join(part for part in parts if part)

        return text.strip()
