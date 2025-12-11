"""User keyboards"""

from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from app.database.models import Location, Category, Provider


def get_main_menu_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    texts = {
        "en": {
            "browse": "= Browse Services",
            "favorites": "d My Favorites",
            "language": "< Language",
        },
        "ru": {
            "browse": "= >8A: CA;C3",
            "favorites": "d 71@0==>5",
            "language": "< /7K:",
        },
        "uz": {
            "browse": "= Xizmatlarni ko'rish",
            "favorites": "d Sevimlilar",
            "language": "< Til",
        },
    }

    t = texts.get(lang, texts["en"])

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["browse"])],
            [KeyboardButton(text=t["favorites"]), KeyboardButton(text=t["language"])],
        ],
        resize_keyboard=True,
    )
    return keyboard


def get_locations_keyboard(locations: List[Location], lang: str = "en") -> InlineKeyboardMarkup:
    """Get locations selection keyboard"""
    buttons = []

    for location in locations:
        name = getattr(location, f"name_{lang}", location.name_en)
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"location:{location.id}")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_categories_keyboard(categories: List[Category], lang: str = "en") -> InlineKeyboardMarkup:
    """Get categories selection keyboard"""
    buttons = []

    for category in categories:
        name = getattr(category, f"name_{lang}", category.name_en)
        icon = category.icon or "=Ë"
        buttons.append([InlineKeyboardButton(text=f"{icon} {name}", callback_data=f"category:{category.id}")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_provider_keyboard(
    provider: Provider,
    current_index: int,
    total: int,
    is_favorite: bool = False,
    has_rated: bool = False,
    lang: str = "en",
) -> InlineKeyboardMarkup:
    """Get provider details keyboard with navigation"""
    texts = {
        "en": {
            "contact": "=Þ Contact",
            "rate": "P Rate",
            "save": "d Save",
            "unsave": "=” Remove",
            "prev": "À Previous",
            "next": "Next ¶",
            "back": "= Back to Categories",
            "already_rated": " Rated",
        },
        "ru": {
            "contact": "=Þ !2O70BLAO",
            "rate": "P F5=8BL",
            "save": "d !>E@0=8BL",
            "unsave": "=” #40;8BL",
            "prev": "À 0704",
            "next": "?5@54 ¶",
            "back": "=  :0B53>@8O<",
            "already_rated": " F5=5=>",
        },
        "uz": {
            "contact": "=Þ Bog'lanish",
            "rate": "P Baholash",
            "save": "d Saqlash",
            "unsave": "=” O'chirish",
            "prev": "À Oldingi",
            "next": "Keyingi ¶",
            "back": "= Kategoriyalarga",
            "already_rated": " Baholangan",
        },
    }

    t = texts.get(lang, texts["en"])

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


def get_rating_keyboard(provider_id: int, lang: str = "en") -> InlineKeyboardMarkup:
    """Get rating selection keyboard"""
    buttons = []

    # Stars row
    stars_row = []
    for i in range(1, 6):
        stars_row.append(InlineKeyboardButton(text=f"{'P' * i}", callback_data=f"rating:{provider_id}:{i}"))

    buttons.append(stars_row)

    # Cancel button
    texts = {"en": "L Cancel", "ru": "L B<5=0", "uz": "L Bekor qilish"}
    buttons.append([InlineKeyboardButton(text=texts.get(lang, texts["en"]), callback_data="rating:cancel")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_comment_keyboard(provider_id: int, rating: int, lang: str = "en") -> InlineKeyboardMarkup:
    """Get comment options keyboard"""
    texts = {
        "en": {"skip": "í Skip Comment", "cancel": "L Cancel"},
        "ru": {"skip": "í 57 :><<5=B0@8O", "cancel": "L B<5=0"},
        "uz": {"skip": "í Sharh yozmaslik", "cancel": "L Bekor qilish"},
    }

    t = texts.get(lang, texts["en"])

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
            InlineKeyboardButton(text="<ì<ç English", callback_data="lang:en"),
            InlineKeyboardButton(text="<÷<ú  CAA:89", callback_data="lang:ru"),
        ],
        [InlineKeyboardButton(text="<ú<ÿ O'zbek", callback_data="lang:uz")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_favorites_navigation_keyboard(current: int, total: int, provider_id: int, lang: str = "en") -> InlineKeyboardMarkup:
    """Get favorites navigation keyboard"""
    texts = {
        "en": {"remove": "=” Remove", "contact": "=Þ Contact", "prev": "À", "next": "¶", "back": "= Back"},
        "ru": {"remove": "=” #40;8BL", "contact": "=Þ !2O70BLAO", "prev": "À", "next": "¶", "back": "= 0704"},
        "uz": {"remove": "=” O'chirish", "contact": "=Þ Bog'lanish", "prev": "À", "next": "¶", "back": "= Ortga"},
    }

    t = texts.get(lang, texts["en"])

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
