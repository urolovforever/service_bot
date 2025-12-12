"""Start and basic handlers"""

import logging
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.repositories import UserRepository, LocationRepository
from app.keyboards.user import (
    get_main_menu_keyboard,
    get_language_keyboard,
    get_phone_request_keyboard,
    get_location_selection_keyboard,
)
from app.utils.i18n import get_text
from app.states import RegistrationStates

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, state: FSMContext):
    """Handle /start command"""
    user_repo = UserRepository(session)

    # Check if user already exists
    existing_user = await user_repo.get_by_telegram_id(message.from_user.id)

    if existing_user:
        # User already registered, show main menu
        lang = existing_user.language_code
        welcome_text = get_text("welcome", lang)
        keyboard = get_main_menu_keyboard(lang)
        await message.answer(welcome_text, reply_markup=keyboard)
        logger.info(f"Existing user {existing_user.telegram_id} started the bot")
    else:
        # New user, start registration process
        # Create user with minimal information
        lang_code = message.from_user.language_code or "ru"
        # Check if user is an admin
        is_admin = message.from_user.id in settings.admin_list
        user = await user_repo.create(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            language_code=lang_code,
            is_admin=is_admin,
        )

        if is_admin:
            logger.info(f"New ADMIN user {user.telegram_id} started registration")
        else:
            logger.info(f"New user {user.telegram_id} started registration")

        # Start registration flow
        registration_texts = {
            "en": "👋 Welcome! Let's get you registered.\n\n📝 Please enter your first name:",
            "ru": "👋 Dobro pozhalovat! Davay zaregistriruem vas.\n\n📝 Vvedite vashe imya:",
            "uz": "👋 Xush kelibsiz! Keling, ro'yxatdan o'tamiz.\n\n📝 Ismingizni kiriting:",
        }

        await message.answer(
            registration_texts.get(lang_code, registration_texts["ru"]),
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(RegistrationStates.waiting_for_first_name)


@router.message(RegistrationStates.waiting_for_first_name)
async def process_first_name(message: Message, session: AsyncSession, state: FSMContext):
    """Process first name input"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language_code if user else "ru"

    first_name = message.text.strip()

    if not first_name or len(first_name) < 2:
        error_texts = {
            "en": "❌ First name is too short. Please enter at least 2 characters:",
            "ru": "❌ Imya slishkom korotkoe. Vvedite minimum 2 simvola:",
            "uz": "❌ Ism juda qisqa. Kamida 2 ta belgi kiriting:",
        }
        await message.answer(error_texts.get(lang, error_texts["ru"]))
        return

    # Save first name to state
    await state.update_data(first_name=first_name)

    # Ask for last name
    last_name_texts = {
        "en": "📝 Great! Now please enter your last name:",
        "ru": "📝 Otlichno! Teper vvedite vashu familiyu:",
        "uz": "📝 Ajoyib! Endi familiyangizni kiriting:",
    }

    await message.answer(last_name_texts.get(lang, last_name_texts["ru"]))
    await state.set_state(RegistrationStates.waiting_for_last_name)


@router.message(RegistrationStates.waiting_for_last_name)
async def process_last_name(message: Message, session: AsyncSession, state: FSMContext):
    """Process last name input"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language_code if user else "ru"

    last_name = message.text.strip()

    if not last_name or len(last_name) < 2:
        error_texts = {
            "en": "❌ Last name is too short. Please enter at least 2 characters:",
            "ru": "❌ Familiya slishkom korotkaya. Vvedite minimum 2 simvola:",
            "uz": "❌ Familiya juda qisqa. Kamida 2 ta belgi kiriting:",
        }
        await message.answer(error_texts.get(lang, error_texts["ru"]))
        return

    # Save last name to state
    await state.update_data(last_name=last_name)

    # Ask for phone number
    phone_texts = {
        "en": "📱 Please share your phone number using the button below:",
        "ru": "📱 Podelit vashim nomerom telefona, ispolzuya knopku nizhe:",
        "uz": "📱 Telefon raqamingizni quyidagi tugma orqali yuboring:",
    }

    keyboard = get_phone_request_keyboard(lang)
    await message.answer(phone_texts.get(lang, phone_texts["ru"]), reply_markup=keyboard)
    await state.set_state(RegistrationStates.waiting_for_phone)


@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def process_phone(message: Message, session: AsyncSession, state: FSMContext):
    """Process phone number"""
    user_repo = UserRepository(session)
    location_repo = LocationRepository(session)

    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language_code if user else "ru"

    phone_number = message.contact.phone_number

    # Save phone number to state
    await state.update_data(phone_number=phone_number)

    # Get all locations
    locations = await location_repo.get_all_active()

    if not locations:
        # No locations available, skip this step
        await complete_registration(message, session, state)
        return

    # Ask for location
    location_texts = {
        "en": "📍 Great! Now please select your location:",
        "ru": "📍 Otlichno! Teper vyberite vashe mestopolozhenie:",
        "uz": "📍 Ajoyib! Endi joylashuvingizni tanlang:",
    }

    keyboard = get_location_selection_keyboard(locations, lang)
    await message.answer(
        location_texts.get(lang, location_texts["ru"]),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(RegistrationStates.waiting_for_location)


@router.message(RegistrationStates.waiting_for_phone)
async def process_phone_text(message: Message, session: AsyncSession, state: FSMContext):
    """Handle text message when expecting phone number"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language_code if user else "ru"

    error_texts = {
        "en": "❌ Please use the button below to share your phone number:",
        "ru": "❌ Ispolzuyte knopku nizhe, chtoby podelit nomerom telefona:",
        "uz": "❌ Telefon raqamingizni yuborish uchun quyidagi tugmani bosing:",
    }

    keyboard = get_phone_request_keyboard(lang)
    await message.answer(error_texts.get(lang, error_texts["ru"]), reply_markup=keyboard)


@router.callback_query(F.data.startswith("reg_location:"))
async def process_location(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    """Process location selection"""
    location_id = int(callback.data.split(":")[1])

    # Save location to state
    await state.update_data(location_id=location_id)

    # Complete registration
    await complete_registration(callback.message, session, state)
    await callback.answer()


async def complete_registration(message: Message, session: AsyncSession, state: FSMContext):
    """Complete the registration process"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    lang = user.language_code if user else "ru"

    # Get data from state
    data = await state.get_data()

    # Update user information
    await user_repo.update_user_info(
        telegram_id=message.from_user.id,
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        phone_number=data.get("phone_number"),
        location_id=data.get("location_id"),
    )

    # Clear state
    await state.clear()

    # Send success message
    success_texts = {
        "en": "✅ Registration completed successfully!\n\nYou can now browse services and providers.",
        "ru": "✅ Registratsiya uspeshno zavershena!\n\nTeper vy mozhete iskat uslugi i postavshchikov.",
        "uz": "✅ Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!\n\nEndi siz xizmatlar va provayderlarni ko'rishingiz mumkin.",
    }

    await message.answer(success_texts.get(lang, success_texts["ru"]))

    # Send welcome message with main menu
    welcome_text = get_text("welcome", lang)
    keyboard = get_main_menu_keyboard(lang)
    await message.answer(welcome_text, reply_markup=keyboard)

    logger.info(f"User {message.from_user.id} completed registration")


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
@router.message(F.text.in_(["🌐 Language", "🌐 Yazyk", "🌐 Til"]))
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
