"""Start and basic handlers"""

import logging
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories import UserRepository
from app.keyboards.user import get_main_menu_keyboard, get_language_keyboard
from app.utils.i18n import get_text

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    """Handle /start command"""
    user_repo = UserRepository(session)

    # Get or create user
    user = await user_repo.get_or_create(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        language_code=message.from_user.language_code or "en",
    )

    logger.info(f"User {user.telegram_id} started the bot")

    # Get user language
    lang = user.language_code

    # Send welcome message
    welcome_text = get_text("welcome", lang)
    keyboard = get_main_menu_keyboard(lang)

    await message.answer(welcome_text, reply_markup=keyboard)


@router.message(Command("help"))
async def cmd_help(message: Message, session: AsyncSession):
    """Handle /help command"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language_code if user else "en"

    help_text = {
        "en": (
            "=Ö <b>Help</b>\n\n"
            "= <b>Browse Services</b> - Find service providers\n"
            "d <b>My Favorites</b> - View your saved providers\n"
            "< <b>Language</b> - Change bot language\n\n"
            "<b>Commands:</b>\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/myfavorites - View your favorites\n"
            "/language - Change language"
        ),
        "ru": (
            "=Ö <b>><>IL</b>\n\n"
            "= <b>>8A: CA;C3</b> - 09B8 ?>AB02I8:>2 CA;C3\n"
            "d <b>71@0==>5</b> - @>A<>B@ A>E@0=5==KE ?>AB02I8:>2\n"
            "< <b>/7K:</b> - 7<5=8BL O7K: 1>B0\n\n"
            "<b>><0=4K:</b>\n"
            "/start - 0?CAB8BL 1>B0\n"
            "/help - >:070BL MB> A>>1I5=85\n"
            "/myfavorites - @>A<>B@ 871@0==>3>\n"
            "/language - 7<5=8BL O7K:"
        ),
        "uz": (
            "=Ö <b>Yordam</b>\n\n"
            "= <b>Xizmatlarni ko'rish</b> - Xizmat ko'rsatuvchilarni topish\n"
            "d <b>Sevimlilar</b> - Saqlangan provayderlarni ko'rish\n"
            "< <b>Til</b> - Bot tilini o'zgartirish\n\n"
            "<b>Buyruqlar:</b>\n"
            "/start - Botni ishga tushirish\n"
            "/help - Ushbu xabarni ko'rsatish\n"
            "/myfavorites - Sevimlilarni ko'rish\n"
            "/language - Tilni o'zgartirish"
        ),
    }

    await message.answer(help_text.get(lang, help_text["en"]))


@router.message(Command("language"))
@router.message(F.text.in_(["< Language", "< /7K:", "< Til"]))
async def cmd_language(message: Message):
    """Handle language change"""
    keyboard = get_language_keyboard()

    texts = {
        "en": "< Choose your language:",
        "ru": "< K15@8B5 20H O7K::",
        "uz": "< Tilingizni tanlang:",
    }

    await message.answer(texts.get("en"), reply_markup=keyboard)


@router.callback_query(F.data.startswith("lang:"))
async def callback_language(callback: CallbackQuery, session: AsyncSession):
    """Handle language selection callback"""
    lang_code = callback.data.split(":")[1]

    user_repo = UserRepository(session)
    await user_repo.update_language(callback.from_user.id, lang_code)

    # Send confirmation
    await callback.answer(get_text("language_changed", lang_code))

    # Update keyboard
    keyboard = get_main_menu_keyboard(lang_code)
    await callback.message.answer(get_text("welcome", lang_code), reply_markup=keyboard)

    await callback.message.delete()
