"""Contact provider handlers"""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings

from app.database.repositories import UserRepository, ProviderRepository, ContactRepository
from app.services.redis_service import redis_service
from app.utils.i18n import get_text

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("contact:"))
async def callback_contact_provider(callback: CallbackQuery, session: AsyncSession):
    """Handle contact provider"""
    provider_id = int(callback.data.split(":")[1])

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    lang = user.language_code if user else "en"

    # Check rate limit
    contact_count = await redis_service.get_rate_limit(callback.from_user.id, "contact")
    if contact_count >= settings.CONTACT_LIMIT_PER_HOUR:
        await callback.answer(
            get_text("contact_limit", lang, limit=settings.CONTACT_LIMIT_PER_HOUR), show_alert=True
        )
        return

    # Get provider
    provider_repo = ProviderRepository(session)
    provider = await provider_repo.get_by_id(provider_id)

    if not provider:
        await callback.answer(get_text("error", lang))
        return

    # Build contact info
    contact_text = get_text("contact_info", lang)

    if provider.phone:
        contact_text += get_text("contact_phone", lang, phone=provider.phone)

    if provider.telegram_username:
        contact_text += get_text("contact_telegram", lang, username=provider.telegram_username)

    # Save contact record
    contact_repo = ContactRepository(session)
    await contact_repo.create(callback.from_user.id, provider_id)

    # Increment provider contact count
    await provider_repo.increment_contact_count(provider_id)

    # Increment rate limit
    await redis_service.increment_rate_limit(callback.from_user.id, "contact", 3600)

    # Send contact info
    await callback.message.answer(contact_text)
    await callback.answer(get_text("contact_saved", lang))

    logger.info(f"User {callback.from_user.id} contacted provider {provider_id}")
