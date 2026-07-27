import re


class WeightNormalizer:

    LB_TO_G = 453.592

    @classmethod
    def normalize(cls, weight: str | None) -> int | None:

        if not weight:
            return None

        text = weight.lower().replace(" ", "")

        match = re.search(r"([\d.]+)(kg|g|gm|grams|lb|lbs)", text)

        if not match:
            return None

        value = float(match.group(1))
        unit = match.group(2)

        if unit == "kg":
            return round(value * 1000)

        if unit in {"g", "gm", "grams"}:
            return round(value)

        if unit in {"lb", "lbs"}:
            return round(value * cls.LB_TO_G)

        return None