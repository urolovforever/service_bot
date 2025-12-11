"""Favorites handlers"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories import UserRepository, FavoriteRepository, ProviderRepository
from app.services.redis_service import redis_service
from app.keyboards.user import get_favorites_navigation_keyboard
from app.utils.i18n import get_text

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("favorite:"))
async def callback_add_favorite(callback: CallbackQuery, session: AsyncSession):
    """Add provider to favorites"""
    provider_id = int(callback.data.split(":")[1])

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    lang = user.language_code if user else "ru"

    # Add to favorites
    favorite_repo = FavoriteRepository(session)
    await favorite_repo.add(callback.from_user.id, provider_id)

    await callback.answer(get_text("favorite_added", lang))

    logger.info(f"User {callback.from_user.id} added provider {provider_id} to favorites")


@router.callback_query(F.data.startswith("unfavorite:"))
async def callback_remove_favorite(callback: CallbackQuery, session: AsyncSession):
    """Remove provider from favorites"""
    provider_id = int(callback.data.split(":")[1])

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    lang = user.language_code if user else "ru"

    # Remove from favorites
    favorite_repo = FavoriteRepository(session)
    await favorite_repo.remove(callback.from_user.id, provider_id)

    await callback.answer(get_text("favorite_removed", lang))

    logger.info(f"User {callback.from_user.id} removed provider {provider_id} from favorites")


@router.message(Command("myfavorites"))
@router.message(F.text.in_(["My Favorites", "Izbrannoe", "Sevimlilar"]))
async def cmd_favorites(message: Message, session: AsyncSession):
    """Show user favorites"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language_code if user else "ru"

    # Get favorites
    favorite_repo = FavoriteRepository(session)
    favorites = await favorite_repo.get_user_favorites(message.from_user.id)

    if not favorites:
        await message.answer(get_text("no_favorites", lang))
        return

    # Save to Redis for pagination
    provider_ids = [p.id for p in favorites]
    await redis_service.set_session(message.from_user.id, "favorite_ids", provider_ids)
    await redis_service.set_session(message.from_user.id, "favorite_index", 0)

    # Show first favorite
    await show_favorite(message, message.from_user.id, session, 0)


async def show_favorite(message: Message, user_id: int, session: AsyncSession, index: int):
    """Show favorite provider"""
    # Get favorite IDs
    favorite_ids = await redis_service.get_session(user_id, "favorite_ids")
    if not favorite_ids or index < 0 or index >= len(favorite_ids):
        return

    # Update index
    await redis_service.set_session(user_id, "favorite_index", index)

    # Get provider
    provider_repo = ProviderRepository(session)
    provider = await provider_repo.get_by_id(favorite_ids[index])

    if not provider:
        return

    # Get user info
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(user_id)
    lang = user.language_code if user else "ru"

    # Format provider info
    location_name = getattr(provider.location, f"name_{lang}", provider.location.name_en)
    category_name = getattr(provider.category, f"name_{lang}", provider.category.name_en)

    price_text = "N/A"
    if provider.price_min and provider.price_max:
        price_text = f"{provider.price_min}-{provider.price_max} {provider.currency}"
    elif provider.price_min:
        price_text = f"from {provider.price_min} {provider.currency}"

    text = get_text(
        "provider_info",
        lang,
        name=provider.name,
        description=provider.description,
        price=price_text,
        location=location_name,
        category=category_name,
        rating=f"{provider.average_rating:.1f}",
        count=provider.rating_count,
        views=provider.view_count,
        contacts=provider.contact_count,
    )

    # Get keyboard
    keyboard = get_favorites_navigation_keyboard(index, len(favorite_ids), provider.id, lang)

    # Send with photo or text
    if provider.photos:
        photo = provider.photos[0]
        await message.answer_photo(photo=photo.file_id, caption=text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "fav:next")
async def callback_fav_next(callback: CallbackQuery, session: AsyncSession):
    """Navigate to next favorite"""
    current_index = await redis_service.get_session(callback.from_user.id, "favorite_index")
    favorite_ids = await redis_service.get_session(callback.from_user.id, "favorite_ids")

    if favorite_ids and current_index < len(favorite_ids) - 1:
        await callback.message.delete()
        await show_favorite(callback.message, callback.from_user.id, session, current_index + 1)

    await callback.answer()


@router.callback_query(F.data == "fav:prev")
async def callback_fav_prev(callback: CallbackQuery, session: AsyncSession):
    """Navigate to previous favorite"""
    current_index = await redis_service.get_session(callback.from_user.id, "favorite_index")

    if current_index > 0:
        await callback.message.delete()
        await show_favorite(callback.message, callback.from_user.id, session, current_index - 1)

    await callback.answer()


@router.callback_query(F.data == "fav:back")
async def callback_fav_back(callback: CallbackQuery):
    """Go back from favorites"""
    await callback.message.delete()
    await callback.answer()
