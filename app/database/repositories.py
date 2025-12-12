"""Database repositories"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy import select, func, update, delete, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database.models import (
    User,
    Location,
    Category,
    Provider,
    ProviderPhoto,
    Rating,
    Favorite,
    UserProviderContact,
)


class UserRepository:
    """User repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: str = "en",
    ) -> User:
        """Create new user"""
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_language(self, telegram_id: int, language_code: str) -> None:
        """Update user language"""
        await self.session.execute(
            update(User).where(User.telegram_id == telegram_id).values(language_code=language_code)
        )
        await self.session.commit()

    async def update_user_info(
        self,
        telegram_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        location_id: Optional[int] = None,
    ) -> None:
        """Update user information"""
        values = {}
        if first_name is not None:
            values["first_name"] = first_name
        if last_name is not None:
            values["last_name"] = last_name
        if phone_number is not None:
            values["phone_number"] = phone_number
        if location_id is not None:
            values["location_id"] = location_id

        if values:
            await self.session.execute(update(User).where(User.telegram_id == telegram_id).values(**values))
            await self.session.commit()

    async def get_or_create(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: str = "en",
    ) -> User:
        """Get or create user"""
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            user = await self.create(telegram_id, username, first_name, last_name, language_code)
        return user


class LocationRepository:
    """Location repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_active(self) -> List[Location]:
        """Get all active locations"""
        result = await self.session.execute(select(Location).where(Location.is_active == True).order_by(Location.id))
        return list(result.scalars().all())

    async def get_by_id(self, location_id: int) -> Optional[Location]:
        """Get location by ID"""
        result = await self.session.execute(select(Location).where(Location.id == location_id))
        return result.scalar_one_or_none()

    async def create(self, name_en: str, name_ru: str, name_uz: str) -> Location:
        """Create new location"""
        location = Location(name_en=name_en, name_ru=name_ru, name_uz=name_uz)
        self.session.add(location)
        await self.session.commit()
        await self.session.refresh(location)
        return location

    async def update(
        self, location_id: int, name_en: Optional[str] = None, name_ru: Optional[str] = None, name_uz: Optional[str] = None
    ) -> Optional[Location]:
        """Update location"""
        location = await self.get_by_id(location_id)
        if location:
            if name_en:
                location.name_en = name_en
            if name_ru:
                location.name_ru = name_ru
            if name_uz:
                location.name_uz = name_uz
            await self.session.commit()
            await self.session.refresh(location)
        return location

    async def delete(self, location_id: int) -> bool:
        """Delete location"""
        result = await self.session.execute(delete(Location).where(Location.id == location_id))
        await self.session.commit()
        return result.rowcount > 0

    async def toggle_active(self, location_id: int) -> Optional[Location]:
        """Toggle location active status"""
        location = await self.get_by_id(location_id)
        if location:
            location.is_active = not location.is_active
            await self.session.commit()
            await self.session.refresh(location)
        return location


class CategoryRepository:
    """Category repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_active(self) -> List[Category]:
        """Get all active categories"""
        result = await self.session.execute(select(Category).where(Category.is_active == True).order_by(Category.id))
        return list(result.scalars().all())

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        result = await self.session.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        name_en: str,
        name_ru: str,
        name_uz: str,
        description_en: Optional[str] = None,
        description_ru: Optional[str] = None,
        description_uz: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> Category:
        """Create new category"""
        category = Category(
            name_en=name_en,
            name_ru=name_ru,
            name_uz=name_uz,
            description_en=description_en,
            description_ru=description_ru,
            description_uz=description_uz,
            icon=icon,
        )
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def update(self, category_id: int, **kwargs) -> Optional[Category]:
        """Update category"""
        category = await self.get_by_id(category_id)
        if category:
            for key, value in kwargs.items():
                if hasattr(category, key) and value is not None:
                    setattr(category, key, value)
            await self.session.commit()
            await self.session.refresh(category)
        return category

    async def delete(self, category_id: int) -> bool:
        """Delete category"""
        result = await self.session.execute(delete(Category).where(Category.id == category_id))
        await self.session.commit()
        return result.rowcount > 0

    async def toggle_active(self, category_id: int) -> Optional[Category]:
        """Toggle category active status"""
        category = await self.get_by_id(category_id)
        if category:
            category.is_active = not category.is_active
            await self.session.commit()
            await self.session.refresh(category)
        return category


class ProviderRepository:
    """Provider repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, provider_id: int) -> Optional[Provider]:
        """Get provider by ID with relationships"""
        result = await self.session.execute(
            select(Provider)
            .options(selectinload(Provider.photos), selectinload(Provider.location), selectinload(Provider.category))
            .where(Provider.id == provider_id)
        )
        return result.scalar_one_or_none()

    async def get_filtered(
        self,
        location_id: Optional[int] = None,
        category_id: Optional[int] = None,
        min_rating: Optional[float] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        available_only: bool = False,
        approved_only: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[Provider], int]:
        """Get filtered providers with pagination"""
        query = select(Provider).options(
            selectinload(Provider.photos), selectinload(Provider.location), selectinload(Provider.category)
        )

        conditions = [Provider.is_active == True]

        if approved_only:
            conditions.append(Provider.is_approved == True)

        if location_id:
            conditions.append(Provider.location_id == location_id)

        if category_id:
            conditions.append(Provider.category_id == category_id)

        if min_rating:
            conditions.append(Provider.average_rating >= min_rating)

        if price_min is not None:
            conditions.append(Provider.price_min >= price_min)

        if price_max is not None:
            conditions.append(Provider.price_max <= price_max)

        if available_only:
            conditions.append(Provider.is_available == True)

        query = query.where(and_(*conditions)).order_by(desc(Provider.average_rating), desc(Provider.contact_count))

        # Get total count
        count_query = select(func.count()).select_from(Provider).where(and_(*conditions))
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        providers = list(result.scalars().all())

        return providers, total

    async def create(
        self,
        name: str,
        description: str,
        location_id: int,
        category_id: int,
        phone: Optional[str] = None,
        telegram_username: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        currency: str = "UZS",
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Provider:
        """Create new provider"""
        provider = Provider(
            name=name,
            description=description,
            location_id=location_id,
            category_id=category_id,
            phone=phone,
            telegram_username=telegram_username,
            price_min=price_min,
            price_max=price_max,
            currency=currency,
            latitude=latitude,
            longitude=longitude,
        )
        self.session.add(provider)
        await self.session.commit()
        await self.session.refresh(provider)
        return provider

    async def update(self, provider_id: int, **kwargs) -> Optional[Provider]:
        """Update provider"""
        provider = await self.get_by_id(provider_id)
        if provider:
            for key, value in kwargs.items():
                if hasattr(provider, key) and value is not None:
                    setattr(provider, key, value)
            await self.session.commit()
            await self.session.refresh(provider)
        return provider

    async def delete(self, provider_id: int) -> bool:
        """Delete provider"""
        result = await self.session.execute(delete(Provider).where(Provider.id == provider_id))
        await self.session.commit()
        return result.rowcount > 0

    async def approve(self, provider_id: int) -> Optional[Provider]:
        """Approve provider"""
        provider = await self.get_by_id(provider_id)
        if provider:
            provider.is_approved = True
            await self.session.commit()
            await self.session.refresh(provider)
        return provider

    async def toggle_active(self, provider_id: int) -> Optional[Provider]:
        """Toggle provider active status"""
        provider = await self.get_by_id(provider_id)
        if provider:
            provider.is_active = not provider.is_active
            await self.session.commit()
            await self.session.refresh(provider)
        return provider

    async def increment_view_count(self, provider_id: int) -> None:
        """Increment provider view count"""
        await self.session.execute(
            update(Provider).where(Provider.id == provider_id).values(view_count=Provider.view_count + 1)
        )
        await self.session.commit()

    async def increment_contact_count(self, provider_id: int) -> None:
        """Increment provider contact count"""
        await self.session.execute(
            update(Provider).where(Provider.id == provider_id).values(contact_count=Provider.contact_count + 1)
        )
        await self.session.commit()

    async def update_rating(self, provider_id: int) -> None:
        """Update provider average rating"""
        result = await self.session.execute(
            select(func.avg(Rating.rating), func.count(Rating.id))
            .where(and_(Rating.provider_id == provider_id, Rating.is_moderated == True))
        )
        avg_rating, count = result.one()

        await self.session.execute(
            update(Provider)
            .where(Provider.id == provider_id)
            .values(average_rating=float(avg_rating or 0), rating_count=count or 0)
        )
        await self.session.commit()

    async def get_unapproved(self, limit: int = 50) -> List[Provider]:
        """Get unapproved providers"""
        result = await self.session.execute(
            select(Provider)
            .options(selectinload(Provider.location), selectinload(Provider.category))
            .where(Provider.is_approved == False)
            .order_by(Provider.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())


class RatingRepository:
    """Rating repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_rating(self, user_id: int, provider_id: int) -> Optional[Rating]:
        """Get user rating for provider"""
        result = await self.session.execute(
            select(Rating).where(and_(Rating.user_id == user_id, Rating.provider_id == provider_id))
        )
        return result.scalar_one_or_none()

    async def create_or_update(
        self, user_id: int, provider_id: int, rating: int, comment: Optional[str] = None
    ) -> Rating:
        """Create or update rating"""
        existing_rating = await self.get_user_rating(user_id, provider_id)

        if existing_rating:
            existing_rating.rating = rating
            existing_rating.comment = comment
            existing_rating.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(existing_rating)
            return existing_rating
        else:
            new_rating = Rating(user_id=user_id, provider_id=provider_id, rating=rating, comment=comment)
            self.session.add(new_rating)
            await self.session.commit()
            await self.session.refresh(new_rating)
            return new_rating

    async def get_provider_ratings(self, provider_id: int, limit: int = 20) -> List[Rating]:
        """Get provider ratings"""
        result = await self.session.execute(
            select(Rating)
            .options(selectinload(Rating.user))
            .where(and_(Rating.provider_id == provider_id, Rating.is_moderated == True))
            .order_by(desc(Rating.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_user_ratings_today(self, user_id: int) -> int:
        """Count user ratings today"""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.session.execute(
            select(func.count()).select_from(Rating).where(and_(Rating.user_id == user_id, Rating.created_at >= today_start))
        )
        return result.scalar_one()


class FavoriteRepository:
    """Favorite repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_favorite(self, user_id: int, provider_id: int) -> Optional[Favorite]:
        """Get user favorite"""
        result = await self.session.execute(
            select(Favorite).where(and_(Favorite.user_id == user_id, Favorite.provider_id == provider_id))
        )
        return result.scalar_one_or_none()

    async def add(self, user_id: int, provider_id: int) -> Favorite:
        """Add to favorites"""
        existing = await self.get_user_favorite(user_id, provider_id)
        if existing:
            return existing

        favorite = Favorite(user_id=user_id, provider_id=provider_id)
        self.session.add(favorite)
        await self.session.commit()
        await self.session.refresh(favorite)
        return favorite

    async def remove(self, user_id: int, provider_id: int) -> bool:
        """Remove from favorites"""
        result = await self.session.execute(
            delete(Favorite).where(and_(Favorite.user_id == user_id, Favorite.provider_id == provider_id))
        )
        await self.session.commit()
        return result.rowcount > 0

    async def get_user_favorites(self, user_id: int) -> List[Provider]:
        """Get user favorites"""
        result = await self.session.execute(
            select(Provider)
            .join(Favorite, Favorite.provider_id == Provider.id)
            .options(selectinload(Provider.photos), selectinload(Provider.location), selectinload(Provider.category))
            .where(Favorite.user_id == user_id)
            .order_by(desc(Favorite.created_at))
        )
        return list(result.scalars().all())

    async def is_favorite(self, user_id: int, provider_id: int) -> bool:
        """Check if provider is in favorites"""
        favorite = await self.get_user_favorite(user_id, provider_id)
        return favorite is not None


class ContactRepository:
    """Contact repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, provider_id: int) -> UserProviderContact:
        """Create contact record"""
        contact = UserProviderContact(user_id=user_id, provider_id=provider_id)
        self.session.add(contact)
        await self.session.commit()
        await self.session.refresh(contact)
        return contact

    async def count_user_contacts_last_hour(self, user_id: int) -> int:
        """Count user contacts in last hour"""
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        result = await self.session.execute(
            select(func.count())
            .select_from(UserProviderContact)
            .where(and_(UserProviderContact.user_id == user_id, UserProviderContact.contacted_at >= hour_ago))
        )
        return result.scalar_one()

    async def get_most_contacted_providers(self, limit: int = 10) -> List[Tuple[Provider, int]]:
        """Get most contacted providers"""
        result = await self.session.execute(
            select(Provider, func.count(UserProviderContact.id).label("contact_count"))
            .join(UserProviderContact, UserProviderContact.provider_id == Provider.id)
            .group_by(Provider.id)
            .order_by(desc("contact_count"))
            .limit(limit)
        )
        return list(result.all())
