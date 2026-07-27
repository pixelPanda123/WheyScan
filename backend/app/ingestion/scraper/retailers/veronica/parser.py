from datetime import datetime

from app.ingestion.scraper.base.types import RawProduct


class VeronicaParser:

    @staticmethod
    def attributes(groups: list[dict]) -> dict[str, str]:
        attrs = {}

        for group in groups or []:
            for value in group.get("values", []):
                name = value.get("dis_nm")
                val = value.get("val")

                if name and val:
                    attrs[name] = val

        return attrs

    @classmethod
    def parse(
        cls,
        retailer: str,
        base_url: str,
        product: dict,
    ) -> RawProduct:

        attrs = cls.attributes(product.get("grps", []))

        return RawProduct(
            retailer=retailer,
            retailer_product_id=str(product.get("id")),

            name=product.get("spName", ""),
            brand=product.get("brName", ""),

            weight=attrs.get("Weight"),
            flavour=attrs.get("Flavour"),
            protein_type=attrs.get("Protein Type"),

            current_price=float(product.get("offer_pr", 0)),
            original_price=product.get("mrp"),
            discount=product.get("discount"),

            product_url=base_url + product.get("urlFragment", ""),
            image_url=product.get("m_img"),

            availability="In Stock"
            if not product.get("oos", False)
            else "Out of Stock",

            rating=product.get("rating"),
            review_count=product.get("nrvw"),

            scraped_at=datetime.utcnow(),
        )