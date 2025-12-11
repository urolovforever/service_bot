"""Admin keyboards"""

from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.database.models import Location, Category, Provider


def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Get admin main menu keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text="=Í Manage Locations", callback_data="admin:locations"),
            InlineKeyboardButton(text="=Â Manage Categories", callback_data="admin:categories"),
        ],
        [
            InlineKeyboardButton(text="=T Manage Providers", callback_data="admin:providers"),
            InlineKeyboardButton(text=" Approve Providers", callback_data="admin:approve"),
        ],
        [
            InlineKeyboardButton(text="=Ê Statistics", callback_data="admin:stats"),
            InlineKeyboardButton(text="=â Send Announcement", callback_data="admin:announce"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_locations_manage_keyboard(locations: List[Location]) -> InlineKeyboardMarkup:
    """Get locations management keyboard"""
    buttons = []

    for location in locations:
        status = "" if location.is_active else "L"
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{status} {location.name_en}", callback_data=f"admin:location:view:{location.id}"
                )
            ]
        )

    buttons.append([InlineKeyboardButton(text="• Add Location", callback_data="admin:location:add")])
    buttons.append([InlineKeyboardButton(text="= Back", callback_data="admin:back")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_location_actions_keyboard(location_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Get location actions keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text=" Edit", callback_data=f"admin:location:edit:{location_id}"),
            InlineKeyboardButton(
                text="= Toggle" if is_active else " Activate", callback_data=f"admin:location:toggle:{location_id}"
            ),
        ],
        [InlineKeyboardButton(text="=Ñ Delete", callback_data=f"admin:location:delete:{location_id}")],
        [InlineKeyboardButton(text="= Back", callback_data="admin:locations")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_categories_manage_keyboard(categories: List[Category]) -> InlineKeyboardMarkup:
    """Get categories management keyboard"""
    buttons = []

    for category in categories:
        status = "" if category.is_active else "L"
        icon = category.icon or "=Ë"
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{status} {icon} {category.name_en}", callback_data=f"admin:category:view:{category.id}"
                )
            ]
        )

    buttons.append([InlineKeyboardButton(text="• Add Category", callback_data="admin:category:add")])
    buttons.append([InlineKeyboardButton(text="= Back", callback_data="admin:back")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_category_actions_keyboard(category_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """Get category actions keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text=" Edit", callback_data=f"admin:category:edit:{category_id}"),
            InlineKeyboardButton(
                text="= Toggle" if is_active else " Activate", callback_data=f"admin:category:toggle:{category_id}"
            ),
        ],
        [InlineKeyboardButton(text="=Ñ Delete", callback_data=f"admin:category:delete:{category_id}")],
        [InlineKeyboardButton(text="= Back", callback_data="admin:categories")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_providers_manage_keyboard(providers: List[Provider], offset: int = 0) -> InlineKeyboardMarkup:
    """Get providers management keyboard with pagination"""
    buttons = []

    for provider in providers[:10]:  # Show 10 per page
        status = "" if provider.is_active else "L"
        approved = "" if provider.is_approved else "ó"
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{status} {approved} {provider.name[:30]}", callback_data=f"admin:provider:view:{provider.id}"
                )
            ]
        )

    # Pagination
    nav_row = []
    if offset > 0:
        nav_row.append(InlineKeyboardButton(text="À Previous", callback_data=f"admin:providers:page:{offset - 10}"))
    if len(providers) > 10:
        nav_row.append(InlineKeyboardButton(text="Next ¶", callback_data=f"admin:providers:page:{offset + 10}"))

    if nav_row:
        buttons.append(nav_row)

    buttons.append([InlineKeyboardButton(text="• Add Provider", callback_data="admin:provider:add")])
    buttons.append([InlineKeyboardButton(text="= Back", callback_data="admin:back")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_provider_actions_keyboard(provider_id: int, is_active: bool, is_approved: bool) -> InlineKeyboardMarkup:
    """Get provider actions keyboard"""
    buttons = []

    row1 = [InlineKeyboardButton(text=" Edit", callback_data=f"admin:provider:edit:{provider_id}")]

    if not is_approved:
        row1.append(InlineKeyboardButton(text=" Approve", callback_data=f"admin:provider:approve:{provider_id}"))

    buttons.append(row1)

    buttons.append(
        [
            InlineKeyboardButton(
                text="= Toggle Active" if is_active else " Activate",
                callback_data=f"admin:provider:toggle:{provider_id}",
            )
        ]
    )

    buttons.append([InlineKeyboardButton(text="=Ñ Delete", callback_data=f"admin:provider:delete:{provider_id}")])
    buttons.append([InlineKeyboardButton(text="= Back", callback_data="admin:providers")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_approve_providers_keyboard(providers: List[Provider]) -> InlineKeyboardMarkup:
    """Get unapproved providers keyboard"""
    buttons = []

    if not providers:
        buttons.append([InlineKeyboardButton(text=" No pending approvals", callback_data="noop")])
    else:
        for provider in providers[:10]:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"ó {provider.name[:30]}", callback_data=f"admin:provider:approve:{provider.id}"
                    )
                ]
            )

    buttons.append([InlineKeyboardButton(text="= Back", callback_data="admin:back")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_statistics_keyboard() -> InlineKeyboardMarkup:
    """Get statistics menu keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text="=e User Stats", callback_data="admin:stats:users"),
            InlineKeyboardButton(text="=T Provider Stats", callback_data="admin:stats:providers"),
        ],
        [
            InlineKeyboardButton(text="P Top Rated", callback_data="admin:stats:toprated"),
            InlineKeyboardButton(text="=Þ Most Contacted", callback_data="admin:stats:contacted"),
        ],
        [InlineKeyboardButton(text="= Back", callback_data="admin:back")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_confirm_keyboard(action: str, item_id: int) -> InlineKeyboardMarkup:
    """Get confirmation keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text=" Confirm", callback_data=f"admin:confirm:{action}:{item_id}"),
            InlineKeyboardButton(text="L Cancel", callback_data="admin:cancel"),
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Get cancel keyboard"""
    buttons = [[InlineKeyboardButton(text="L Cancel", callback_data="admin:cancel")]]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
