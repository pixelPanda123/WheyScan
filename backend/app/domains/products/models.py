from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    products = relationship(
        "Product",
        back_populates="brand",
        cascade="all, delete-orphan",
    )



class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    brand_id: Mapped[int] = mapped_column(
        ForeignKey("brands.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(255))

    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    # Scraped data often lacks these, so they are optional.
    protein_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    flavour: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    weight: Mapped[float | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    weight_unit: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    image_url: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    brand = relationship(
        "Brand",
        back_populates="products",
    )

    listings = relationship(
        "Listing",
        back_populates="product",
        cascade="all, delete-orphan",
    )