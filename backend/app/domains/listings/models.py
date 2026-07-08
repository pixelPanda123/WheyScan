from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from app.db.base import Base






class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    base_url: Mapped[str] = mapped_column(String)

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    listings = relationship(
        "Listing",
        back_populates="store",
    )


class Listing(Base):
    __tablename__ = "listings"

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "store_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id")
    )

    url: Mapped[str] = mapped_column(String)

    current_price: Mapped[float] = mapped_column(
        Numeric(10, 2)
    )

    availability: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    last_scraped: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    product = relationship(
        "Product",
        back_populates="listings",
    )

    store = relationship(
        "Store",
        back_populates="listings",
    )

    price_history = relationship(
        "PriceHistory",
        back_populates="listing",
        cascade="all, delete-orphan",
    )

    
class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True)

    listing_id: Mapped[int] = mapped_column(
        ForeignKey("listings.id"),
        nullable=False,
    )

    price: Mapped[float] = mapped_column(
        Numeric(10, 2)
    )

    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    valid_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    listing = relationship(
        "Listing",
        back_populates="price_history",
    )