"""Browse providers handlers"""

import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories import (
    UserRepository,
    LocationRepository,
    CategoryRepository,
    ProviderRepository,
    RatingRepository,
    FavoriteRepository,
)
from app.services.redis_service import redis_service
from app.keyboards.user import get_locations_keyboard, get_categories_keyboard, get_provider_keyboard
from app.utils.i18n import get_text

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text.in_(["= Browse Services", "= >8A: CA;C3", "= Xizmatlarni ko'rish"]))
async def browse_start(message: Message, session: AsyncSession):
    """Start browsing - select location"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language_code if user else "en"

    # Get active locations
    location_repo = LocationRepository(session)
    locations = await location_repo.get_all_active()

    if not locations:
        await message.answer(get_text("error", lang))
        return

    # Clear previous browsing state
    await redis_service.delete_session(message.from_user.id, "browsing_state")

    # Show location selection
    text = get_text("select_location", lang)
    keyboard = get_locations_keyboard(locations, lang)

    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("location:"))
async def callback_location_select(callback: CallbackQuery, session: AsyncSession):
    """Handle location selection"""
    location_id = int(callback.data.split(":")[1])

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    lang = user.language_code if user else "en"

    # Save location to session
    await redis_service.set_session(callback.from_user.id, "selected_location", location_id)

    # Get active categories
    category_repo = CategoryRepository(session)
    categories = await category_repo.get_all_active()

    if not categories:
        await callback.answer(get_text("error", lang))
        return

    # Show category selection
    text = get_text("select_category", lang)
    keyboard = get_categories_keyboard(categories, lang)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("category:"))
async def callback_category_select(callback: CallbackQuery, session: AsyncSession):
    """Handle category selection and show providers"""
    category_id = int(callback.data.split(":")[1])

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    lang = user.language_code if user else "en"

    # Get selected location
    location_id = await redis_service.get_session(callback.from_user.id, "selected_location")

    if not location_id:
        await callback.answer(get_text("error", lang))
        return

    # Get providers
    provider_repo = ProviderRepository(session)
    providers, total = await provider_repo.get_filtered(
        location_id=location_id, category_id=category_id, approved_only=True
    )

    if not providers:
        await callback.message.edit_text(get_text("no_providers", lang))
        await callback.answer()
        return

    # Save browsing state
    provider_ids = [p.id for p in providers]
    await redis_service.set_browsing_state(
        user_id=callback.from_user.id,
        location_id=location_id,
        category_id=category_id,
        provider_ids=provider_ids,
        current_index=0,
    )

    # Show first provider
    await show_provider(callback.message, callback.from_user.id, session, 0, edit=True)
    await callback.answer()


async def show_provider(message: Message, user_id: int, session: AsyncSession, index: int, edit: bool = False):
    """Show provider details"""
    # Get browsing state
    state = await redis_service.get_browsing_state(user_id)
    if not state:
        return

    provider_ids = state["provider_ids"]
    if index < 0 or index >= len(provider_ids):
        return

    # Update current index
    await redis_service.update_browsing_index(user_id, index)

    # Get provider
    provider_repo = ProviderRepository(session)
    provider = await provider_repo.get_by_id(provider_ids[index])

    if not provider:
        return

    # Increment view count
    await provider_repo.increment_view_count(provider.id)

    # Get user info
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(user_id)
    lang = user.language_code if user else "en"

    # Check if user has rated
    rating_repo = RatingRepository(session)
    user_rating = await rating_repo.get_user_rating(user_id, provider.id)
    has_rated = user_rating is not None

    # Check if favorite
    favorite_repo = FavoriteRepository(session)
    is_favorite = await favorite_repo.is_favorite(user_id, provider.id)

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
    keyboard = get_provider_keyboard(
        provider=provider,
        current_index=index,
        total=len(provider_ids),
        is_favorite=is_favorite,
        has_rated=has_rated,
        lang=lang,
    )

    # Send with photos or text only
    if provider.photos:
        photo = provider.photos[0]
        if edit:
            try:
                await message.delete()
            except Exception:
                pass
            await message.answer_photo(photo=photo.file_id, caption=text, reply_markup=keyboard)
        else:
            await message.answer_photo(photo=photo.file_id, caption=text, reply_markup=keyboard)
    else:
        if edit:
            try:
                await message.edit_text(text, reply_markup=keyboard)
            except Exception:
                await message.answer(text, reply_markup=keyboard)
        else:
            await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "browse:next")
async def callback_browse_next(callback: CallbackQuery, session: AsyncSession):
    """Navigate to next provider"""
    state = await redis_service.get_browsing_state(callback.from_user.id)
    if not state:
        await callback.answer()
        return

    current_index = state["current_index"]
    total = len(state["provider_ids"])

    if current_index < total - 1:
        await show_provider(callback.message, callback.from_user.id, session, current_index + 1, edit=True)

    await callback.answer()


@router.callback_query(F.data == "browse:prev")
async def callback_browse_prev(callback: CallbackQuery, session: AsyncSession):
    """Navigate to previous provider"""
    state = await redis_service.get_browsing_state(callback.from_user.id)
    if not state:
        await callback.answer()
        return

    current_index = state["current_index"]

    if current_index > 0:
        await show_provider(callback.message, callback.from_user.id, session, current_index - 1, edit=True)

    await callback.answer()


@router.callback_query(F.data == "browse:back")
async def callback_browse_back(callback: CallbackQuery, session: AsyncSession):
    """Go back to category selection"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    lang = user.language_code if user else "en"

    # Get active categories
    category_repo = CategoryRepository(session)
    categories = await category_repo.get_all_active()

    # Show category selection
    text = get_text("select_category", lang)
    keyboard = get_categories_keyboard(categories, lang)

    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "noop")
async def callback_noop(callback: CallbackQuery):
    """No operation callback"""
    await callback.answer()
