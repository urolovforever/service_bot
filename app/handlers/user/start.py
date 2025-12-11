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
        language_code=message.from_user.language_code or "ru",
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
    lang = user.language_code if user else "ru"

    help_text = {
        "en": (
            "Help\n\n"
            "Browse Services - Find service providers\n"
            "My Favorites - View your saved providers\n"
            "Language - Change bot language\n\n"
            "Commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/myfavorites - View your favorites\n"
            "/language - Change language"
        ),
        "ru": (
            "Pomosh\n\n"
            "Poisk uslug - Nayti postavshchikov uslug\n"
            "Izbrannoe - Prosmotr sohranennyh postavshchikov\n"
            "Yazyk - Izmenit yazyk bota\n\n"
            "Komandy:\n"
            "/start - Zapustit bota\n"
            "/help - Pokazat eto soobshenie\n"
            "/myfavorites - Prosmotr izbrannogo\n"
            "/language - Izmenit yazyk"
        ),
        "uz": (
            "Yordam\n\n"
            "Xizmatlarni korish - Xizmat korsatuvchilarni topish\n"
            "Sevimlilar - Saqlangan provayderlarni korish\n"
            "Til - Bot tilini ozgartirish\n\n"
            "Buyruqlar:\n"
            "/start - Botni ishga tushirish\n"
            "/help - Ushbu xabarni korsatish\n"
            "/myfavorites - Sevimlilarni korish\n"
            "/language - Tilni ozgartirish"
        ),
    }

    await message.answer(help_text.get(lang, help_text["ru"]))


@router.message(Command("language"))
@router.message(F.text.in_(["Yazyk", "Til", "Language"]))
async def cmd_language(message: Message):
    """Handle language change"""
    keyboard = get_language_keyboard()

    texts = {
        "en": "Choose your language:",
        "ru": "Vyberite vash yazyk:",
        "uz": "Tilingizni tanlang:",
    }

    await message.answer(texts.get("ru"), reply_markup=keyboard)


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
