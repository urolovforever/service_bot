"""Rating handlers"""

import logging
from typing import Optional
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings

from app.database.repositories import UserRepository, ProviderRepository, RatingRepository
from app.services.redis_service import redis_service
from app.keyboards.user import get_rating_keyboard, get_comment_keyboard
from app.utils.i18n import get_text

logger = logging.getLogger(__name__)
router = Router()


class RatingStates(StatesGroup):
    """Rating states"""

    waiting_for_comment = State()


@router.callback_query(F.data.startswith("rate:"))
async def callback_rate_provider(callback: CallbackQuery, session: AsyncSession):
    """Handle rate provider"""
    provider_id = int(callback.data.split(":")[1])

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    lang = user.language_code if user else "ru"

    # Check rate limit
    rating_repo = RatingRepository(session)
    rating_count = await rating_repo.count_user_ratings_today(callback.from_user.id)

    if rating_count >= settings.RATING_LIMIT_PER_DAY:
        await callback.answer(get_text("rating_limit", lang, limit=settings.RATING_LIMIT_PER_DAY), show_alert=True)
        return

    # Show rating keyboard
    text = get_text("rate_provider", lang)
    keyboard = get_rating_keyboard(provider_id, lang)

    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("rating:") & ~F.data.startswith("rating:cancel"))
async def callback_rating_select(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Handle rating selection"""
    parts = callback.data.split(":")
    provider_id = int(parts[1])
    rating_value = int(parts[2])

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    lang = user.language_code if user else "ru"

    # Store rating in state
    await state.update_data(provider_id=provider_id, rating=rating_value)
    await state.set_state(RatingStates.waiting_for_comment)

    # Ask for comment
    text = get_text("add_comment", lang)
    keyboard = get_comment_keyboard(provider_id, rating_value, lang)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("comment:skip:"))
async def callback_skip_comment(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Handle skip comment"""
    parts = callback.data.split(":")
    provider_id = int(parts[2])
    rating_value = int(parts[3])

    await save_rating(callback.from_user.id, provider_id, rating_value, None, session)
    await state.clear()

    await callback.message.delete()
    await callback.answer()


@router.message(RatingStates.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext, session: AsyncSession):
    """Process rating comment"""
    data = await state.get_data()
    provider_id = data.get("provider_id")
    rating_value = data.get("rating")

    await save_rating(message.from_user.id, provider_id, rating_value, message.text, session)
    await state.clear()


@router.callback_query(F.data == "rating:cancel")
async def callback_rating_cancel(callback: CallbackQuery, state: FSMContext):
    """Cancel rating"""
    await state.clear()
    await callback.message.delete()
    await callback.answer()


async def save_rating(
    user_id: int, provider_id: int, rating: int, comment: Optional[str], session: AsyncSession
):
    """Save rating to database"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(user_id)
    lang = user.language_code if user else "ru"

    # Save rating
    rating_repo = RatingRepository(session)
    existing_rating = await rating_repo.get_user_rating(user_id, provider_id)

    await rating_repo.create_or_update(user_id, provider_id, rating, comment)

    # Update provider average rating
    provider_repo = ProviderRepository(session)
    await provider_repo.update_rating(provider_id)

    # Send confirmation
    from aiogram import Bot
    from app.config import settings

    bot = Bot(token=settings.BOT_TOKEN)

    if existing_rating:
        text = get_text("rating_updated", lang)
    else:
        text = get_text("rating_saved", lang)

    await bot.send_message(user_id, text)

    logger.info(f"User {user_id} rated provider {provider_id} with {rating} stars")
