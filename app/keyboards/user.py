"""User keyboards"""

from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from app.database.models import Location, Category, Provider


def get_main_menu_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    texts = {
        "en": {
            "browse": "Browse Services",
            "favorites": "My Favorites",
            "language": "Language",
        },
        "ru": {
            "browse": "Poisk uslug",
            "favorites": "Izbrannoe",
            "language": "Yazyk",
        },
        "uz": {
            "browse": "Xizmatlarni korish",
            "favorites": "Sevimlilar",
            "language": "Til",
        },
    }

    t = texts.get(lang, texts["ru"])

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["browse"])],
            [KeyboardButton(text=t["favorites"]), KeyboardButton(text=t["language"])],
        ],
        resize_keyboard=True,
    )
    return keyboard


def get_locations_keyboard(locations: List[Location], lang: str = "ru") -> InlineKeyboardMarkup:
    """Get locations selection keyboard"""
    buttons = []

    for location in locations:
        name = getattr(location, f"name_{lang}", location.name_en)
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"location:{location.id}")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_categories_keyboard(categories: List[Category], lang: str = "ru") -> InlineKeyboardMarkup:
    """Get categories selection keyboard"""
    buttons = []

    for category in categories:
        name = getattr(category, f"name_{lang}", category.name_en)
        icon = category.icon or ""
        buttons.append([InlineKeyboardButton(text=f"{icon} {name}", callback_data=f"category:{category.id}")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_provider_keyboard(
    provider: Provider,
    current_index: int,
    total: int,
    is_favorite: bool = False,
    has_rated: bool = False,
    lang: str = "ru",
) -> InlineKeyboardMarkup:
    """Get provider details keyboard with navigation"""
    texts = {
        "en": {
            "contact": "Contact",
            "rate": "Rate",
            "save": "Save",
            "unsave": "Remove",
            "prev": "< Previous",
            "next": "Next >",
            "back": "< Back to Categories",
            "already_rated": "Rated",
        },
        "ru": {
            "contact": "Svyazatsya",
            "rate": "Otsenitsya",
            "save": "Sohranit",
            "unsave": "Udalit",
            "prev": "< Nazad",
            "next": "Vpered >",
            "back": "< K kategoriyam",
            "already_rated": "Otseneno",
        },
        "uz": {
            "contact": "Boglanish",
            "rate": "Baholash",
            "save": "Saqlash",
            "unsave": "Ochirish",
            "prev": "< Oldingi",
            "next": "Keyingi >",
            "back": "< Kategoriyalarga",
            "already_rated": "Baholangan",
        },
    }

    t = texts.get(lang, texts["ru"])

    buttons = []

    # Contact and rating row
    row1 = [InlineKeyboardButton(text=t["contact"], callback_data=f"contact:{provider.id}")]

    if has_rated:
        row1.append(InlineKeyboardButton(text=t["already_rated"], callback_data="noop"))
    else:
        row1.append(InlineKeyboardButton(text=t["rate"], callback_data=f"rate:{provider.id}"))

    buttons.append(row1)

    # Favorite row
    if is_favorite:
        buttons.append([InlineKeyboardButton(text=t["unsave"], callback_data=f"unfavorite:{provider.id}")])
    else:
        buttons.append([InlineKeyboardButton(text=t["save"], callback_data=f"favorite:{provider.id}")])

    # Navigation row
    nav_row = []
    if current_index > 0:
        nav_row.append(InlineKeyboardButton(text=t["prev"], callback_data=f"browse:prev"))
    nav_row.append(InlineKeyboardButton(text=f"{current_index + 1}/{total}", callback_data="noop"))
    if current_index < total - 1:
        nav_row.append(InlineKeyboardButton(text=t["next"], callback_data=f"browse:next"))

    buttons.append(nav_row)

    # Back button
    buttons.append([InlineKeyboardButton(text=t["back"], callback_data="browse:back")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_rating_keyboard(provider_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Get rating selection keyboard"""
    buttons = []

    # Stars row
    stars_row = []
    for i in range(1, 6):
        stars_row.append(InlineKeyboardButton(text=f"{i}", callback_data=f"rating:{provider_id}:{i}"))

    buttons.append(stars_row)

    # Cancel button
    texts = {"en": "Cancel", "ru": "Otmena", "uz": "Bekor qilish"}
    buttons.append([InlineKeyboardButton(text=texts.get(lang, texts["ru"]), callback_data="rating:cancel")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_comment_keyboard(provider_id: int, rating: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Get comment options keyboard"""
    texts = {
        "en": {"skip": "Skip Comment", "cancel": "Cancel"},
        "ru": {"skip": "Bez kommentariya", "cancel": "Otmena"},
        "uz": {"skip": "Sharh yozmaslik", "cancel": "Bekor qilish"},
    }

    t = texts.get(lang, texts["ru"])

    buttons = [
        [InlineKeyboardButton(text=t["skip"], callback_data=f"comment:skip:{provider_id}:{rating}")],
        [InlineKeyboardButton(text=t["cancel"], callback_data="rating:cancel")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text="Russkiy", callback_data="lang:ru"),
            InlineKeyboardButton(text="Ozbekcha", callback_data="lang:uz"),
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_favorites_navigation_keyboard(current: int, total: int, provider_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Get favorites navigation keyboard"""
    texts = {
        "en": {"remove": "Remove", "contact": "Contact", "prev": "<", "next": ">", "back": "Back"},
        "ru": {"remove": "Udalit", "contact": "Svyazatsya", "prev": "<", "next": ">", "back": "Nazad"},
        "uz": {"remove": "Ochirish", "contact": "Boglanish", "prev": "<", "next": ">", "back": "Ortga"},
    }

    t = texts.get(lang, texts["ru"])

    buttons = []

    # Action buttons
    buttons.append(
        [
            InlineKeyboardButton(text=t["remove"], callback_data=f"unfavorite:{provider_id}"),
            InlineKeyboardButton(text=t["contact"], callback_data=f"contact:{provider_id}"),
        ]
    )

    # Navigation
    if total > 1:
        nav_row = []
        if current > 0:
            nav_row.append(InlineKeyboardButton(text=t["prev"], callback_data="fav:prev"))
        nav_row.append(InlineKeyboardButton(text=f"{current + 1}/{total}", callback_data="noop"))
        if current < total - 1:
            nav_row.append(InlineKeyboardButton(text=t["next"], callback_data="fav:next"))
        buttons.append(nav_row)

    # Back button
    buttons.append([InlineKeyboardButton(text=t["back"], callback_data="fav:back")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
