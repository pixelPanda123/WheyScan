class ProteinNormalizer:

    @classmethod
    def normalize(
        cls,
        protein_type: str | None,
        name: str,
    ) -> str | None:

        text = f"{protein_type or ''} {name}".lower()

        if "isolate" in text or "iso100" in text:
            return "ISOLATE"

        if "hydro" in text:
            return "HYDROLYSED"

        if "concentrate" in text:
            return "CONCENTRATE"

        if "blend" in text:
            return "BLEND"

        if "whey" in text:
            return "WHEY"

        return None