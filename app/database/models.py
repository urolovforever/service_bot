"""Database models"""

from datetime import datetime
from sqlalchemy import (
    BigInteger,
    String,
    Text,
    Float,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List, Optional


class Base(DeclarativeBase):
    """Base class for all models"""

    pass


class User(Base):
    """User model"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("locations.id"), nullable=True)
    language_code: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    location: Mapped[Optional["Location"]] = relationship("Location")
    ratings: Mapped[List["Rating"]] = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite", back_populates="user", cascade="all, delete-orphan"
    )
    contacts: Mapped[List["UserProviderContact"]] = relationship(
        "UserProviderContact", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"


class Location(Base):
    """Location model"""

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    name_uz: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    providers: Mapped[List["Provider"]] = relationship("Provider", back_populates="location")

    def __repr__(self) -> str:
        return f"<Location(id={self.id}, name_en={self.name_en})>"


class Category(Base):
    """Category model"""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(255), nullable=False)
    name_uz: Mapped[str] = mapped_column(String(255), nullable=False)
    description_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_ru: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_uz: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    providers: Mapped[List["Provider"]] = relationship("Provider", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name_en={self.name_en})>"


class Provider(Base):
    """Provider model"""

    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    telegram_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    price_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="UZS", nullable=False)

    # Location and Category
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False, index=True)

    # Optional geolocation
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Status and availability
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Statistics
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contact_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    location: Mapped["Location"] = relationship("Location", back_populates="providers")
    category: Mapped["Category"] = relationship("Category", back_populates="providers")
    photos: Mapped[List["ProviderPhoto"]] = relationship(
        "ProviderPhoto", back_populates="provider", cascade="all, delete-orphan"
    )
    ratings: Mapped[List["Rating"]] = relationship(
        "Rating", back_populates="provider", cascade="all, delete-orphan"
    )
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite", back_populates="provider", cascade="all, delete-orphan"
    )
    contacts: Mapped[List["UserProviderContact"]] = relationship(
        "UserProviderContact", back_populates="provider", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_provider_location_category", "location_id", "category_id"),
        Index("idx_provider_active_approved", "is_active", "is_approved"),
        CheckConstraint("price_min >= 0", name="check_price_min_positive"),
        CheckConstraint("price_max >= price_min", name="check_price_max_gte_min"),
        CheckConstraint("average_rating >= 0 AND average_rating <= 5", name="check_avg_rating_range"),
    )

    def __repr__(self) -> str:
        return f"<Provider(id={self.id}, name={self.name}, rating={self.average_rating})>"


class ProviderPhoto(Base):
    """Provider photo model"""

    __tablename__ = "provider_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("providers.id"), nullable=False, index=True)
    file_id: Mapped[str] = mapped_column(String(255), nullable=False)
    file_unique_id: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    provider: Mapped["Provider"] = relationship("Provider", back_populates="photos")

    __table_args__ = (Index("idx_provider_photo_order", "provider_id", "order"),)

    def __repr__(self) -> str:
        return f"<ProviderPhoto(id={self.id}, provider_id={self.provider_id})>"


class Rating(Base):
    """Rating model"""

    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False, index=True)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("providers.id"), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_moderated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="ratings")
    provider: Mapped["Provider"] = relationship("Provider", back_populates="ratings")

    __table_args__ = (
        Index("idx_rating_user_provider", "user_id", "provider_id", unique=True),
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    def __repr__(self) -> str:
        return f"<Rating(id={self.id}, user_id={self.user_id}, provider_id={self.provider_id}, rating={self.rating})>"


class Favorite(Base):
    """Favorite model"""

    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False, index=True)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("providers.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="favorites")
    provider: Mapped["Provider"] = relationship("Provider", back_populates="favorites")

    __table_args__ = (Index("idx_favorite_user_provider", "user_id", "provider_id", unique=True),)

    def __repr__(self) -> str:
        return f"<Favorite(id={self.id}, user_id={self.user_id}, provider_id={self.provider_id})>"


class UserProviderContact(Base):
    """User-Provider contact tracking model"""

    __tablename__ = "user_provider_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False, index=True)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("providers.id"), nullable=False, index=True)
    contacted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="contacts")
    provider: Mapped["Provider"] = relationship("Provider", back_populates="contacts")

    __table_args__ = (Index("idx_contact_user_provider_date", "user_id", "provider_id", "contacted_at"),)

    def __repr__(self) -> str:
        return f"<UserProviderContact(id={self.id}, user_id={self.user_id}, provider_id={self.provider_id})>"
