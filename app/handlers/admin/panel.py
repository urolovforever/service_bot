"""Admin panel handlers"""

import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.config import settings
from app.database.repositories import (
    LocationRepository,
    CategoryRepository,
    ProviderRepository,
    ContactRepository,
)
from app.database.models import User, Provider, Rating
from app.keyboards.admin import (
    get_admin_main_keyboard,
    get_locations_manage_keyboard,
    get_location_actions_keyboard,
    get_categories_manage_keyboard,
    get_category_actions_keyboard,
    get_providers_manage_keyboard,
    get_provider_actions_keyboard,
    get_approve_providers_keyboard,
    get_statistics_keyboard,
)

logger = logging.getLogger(__name__)
router = Router()


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in settings.admin_list


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Show admin panel"""
    if not is_admin(message.from_user.id):
        await message.answer("Ô Access denied")
        return

    text = "=' <b>Admin Panel</b>\n\nSelect an action:"
    keyboard = get_admin_main_keyboard()

    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "admin:back")
async def callback_admin_back(callback: CallbackQuery):
    """Back to admin main menu"""
    text = "=' <b>Admin Panel</b>\n\nSelect an action:"
    keyboard = get_admin_main_keyboard()

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


# LOCATIONS MANAGEMENT
@router.callback_query(F.data == "admin:locations")
async def callback_admin_locations(callback: CallbackQuery, session: AsyncSession):
    """Show locations management"""
    location_repo = LocationRepository(session)
    locations = await location_repo.get_all_active()

    text = "=Í <b>Manage Locations</b>\n\nClick on a location to manage it:"
    keyboard = get_locations_manage_keyboard(locations)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:location:view:"))
async def callback_admin_location_view(callback: CallbackQuery, session: AsyncSession):
    """View location details"""
    location_id = int(callback.data.split(":")[-1])

    location_repo = LocationRepository(session)
    location = await location_repo.get_by_id(location_id)

    if not location:
        await callback.answer("Location not found")
        return

    text = (
        f"=Í <b>Location Details</b>\n\n"
        f"ID: {location.id}\n"
        f"English: {location.name_en}\n"
        f"Russian: {location.name_ru}\n"
        f"Uzbek: {location.name_uz}\n"
        f"Status: {' Active' if location.is_active else 'L Inactive'}"
    )

    keyboard = get_location_actions_keyboard(location_id, location.is_active)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:location:toggle:"))
async def callback_admin_location_toggle(callback: CallbackQuery, session: AsyncSession):
    """Toggle location active status"""
    location_id = int(callback.data.split(":")[-1])

    location_repo = LocationRepository(session)
    location = await location_repo.toggle_active(location_id)

    if location:
        await callback.answer(f"Location {'activated' if location.is_active else 'deactivated'}")
        # Refresh view
        await callback_admin_location_view(callback, session)
    else:
        await callback.answer("Error")


# CATEGORIES MANAGEMENT
@router.callback_query(F.data == "admin:categories")
async def callback_admin_categories(callback: CallbackQuery, session: AsyncSession):
    """Show categories management"""
    category_repo = CategoryRepository(session)
    categories = await category_repo.get_all_active()

    text = "=Â <b>Manage Categories</b>\n\nClick on a category to manage it:"
    keyboard = get_categories_manage_keyboard(categories)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:category:view:"))
async def callback_admin_category_view(callback: CallbackQuery, session: AsyncSession):
    """View category details"""
    category_id = int(callback.data.split(":")[-1])

    category_repo = CategoryRepository(session)
    category = await category_repo.get_by_id(category_id)

    if not category:
        await callback.answer("Category not found")
        return

    text = (
        f"=Â <b>Category Details</b>\n\n"
        f"ID: {category.id}\n"
        f"English: {category.name_en}\n"
        f"Russian: {category.name_ru}\n"
        f"Uzbek: {category.name_uz}\n"
        f"Icon: {category.icon or 'None'}\n"
        f"Status: {' Active' if category.is_active else 'L Inactive'}"
    )

    keyboard = get_category_actions_keyboard(category_id, category.is_active)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:category:toggle:"))
async def callback_admin_category_toggle(callback: CallbackQuery, session: AsyncSession):
    """Toggle category active status"""
    category_id = int(callback.data.split(":")[-1])

    category_repo = CategoryRepository(session)
    category = await category_repo.toggle_active(category_id)

    if category:
        await callback.answer(f"Category {'activated' if category.is_active else 'deactivated'}")
        await callback_admin_category_view(callback, session)
    else:
        await callback.answer("Error")


# PROVIDERS MANAGEMENT
@router.callback_query(F.data == "admin:providers")
async def callback_admin_providers(callback: CallbackQuery, session: AsyncSession):
    """Show providers management"""
    provider_repo = ProviderRepository(session)
    providers, _ = await provider_repo.get_filtered(approved_only=False, limit=50)

    text = "=T <b>Manage Providers</b>\n\nClick on a provider to manage it:"
    keyboard = get_providers_manage_keyboard(providers)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:provider:view:"))
async def callback_admin_provider_view(callback: CallbackQuery, session: AsyncSession):
    """View provider details"""
    provider_id = int(callback.data.split(":")[-1])

    provider_repo = ProviderRepository(session)
    provider = await provider_repo.get_by_id(provider_id)

    if not provider:
        await callback.answer("Provider not found")
        return

    text = (
        f"=T <b>Provider Details</b>\n\n"
        f"ID: {provider.id}\n"
        f"Name: {provider.name}\n"
        f"Description: {provider.description[:100]}...\n"
        f"Location: {provider.location.name_en}\n"
        f"Category: {provider.category.name_en}\n"
        f"Price: {provider.price_min}-{provider.price_max} {provider.currency}\n"
        f"Rating: {provider.average_rating:.1f}/5.0 ({provider.rating_count} reviews)\n"
        f"Views: {provider.view_count}\n"
        f"Contacts: {provider.contact_count}\n"
        f"Status: {' Active' if provider.is_active else 'L Inactive'}\n"
        f"Approved: {' Yes' if provider.is_approved else 'ó Pending'}"
    )

    keyboard = get_provider_actions_keyboard(provider_id, provider.is_active, provider.is_approved)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:provider:approve:"))
async def callback_admin_provider_approve(callback: CallbackQuery, session: AsyncSession):
    """Approve provider"""
    provider_id = int(callback.data.split(":")[-1])

    provider_repo = ProviderRepository(session)
    provider = await provider_repo.approve(provider_id)

    if provider:
        await callback.answer(" Provider approved")
        await callback_admin_provider_view(callback, session)
    else:
        await callback.answer("Error")


@router.callback_query(F.data.startswith("admin:provider:toggle:"))
async def callback_admin_provider_toggle(callback: CallbackQuery, session: AsyncSession):
    """Toggle provider active status"""
    provider_id = int(callback.data.split(":")[-1])

    provider_repo = ProviderRepository(session)
    provider = await provider_repo.toggle_active(provider_id)

    if provider:
        await callback.answer(f"Provider {'activated' if provider.is_active else 'deactivated'}")
        await callback_admin_provider_view(callback, session)
    else:
        await callback.answer("Error")


@router.callback_query(F.data == "admin:approve")
async def callback_admin_approve(callback: CallbackQuery, session: AsyncSession):
    """Show unapproved providers"""
    provider_repo = ProviderRepository(session)
    providers = await provider_repo.get_unapproved()

    text = f" <b>Approve Providers</b>\n\n{len(providers)} pending approval"
    keyboard = get_approve_providers_keyboard(providers)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


# STATISTICS
@router.callback_query(F.data == "admin:stats")
async def callback_admin_stats(callback: CallbackQuery):
    """Show statistics menu"""
    text = "=Ê <b>Statistics</b>\n\nSelect a report:"
    keyboard = get_statistics_keyboard()

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "admin:stats:users")
async def callback_admin_stats_users(callback: CallbackQuery, session: AsyncSession):
    """Show user statistics"""
    result = await session.execute(select(func.count()).select_from(User))
    total_users = result.scalar_one()

    result = await session.execute(select(func.count()).select_from(User).where(User.is_active == True))
    active_users = result.scalar_one()

    text = (
        f"=e <b>User Statistics</b>\n\n"
        f"Total Users: {total_users}\n"
        f"Active Users: {active_users}\n"
    )

    await callback.answer()
    await callback.message.answer(text)


@router.callback_query(F.data == "admin:stats:providers")
async def callback_admin_stats_providers(callback: CallbackQuery, session: AsyncSession):
    """Show provider statistics"""
    result = await session.execute(select(func.count()).select_from(Provider))
    total_providers = result.scalar_one()

    result = await session.execute(
        select(func.count()).select_from(Provider).where(Provider.is_active == True)
    )
    active_providers = result.scalar_one()

    result = await session.execute(
        select(func.count()).select_from(Provider).where(Provider.is_approved == False)
    )
    pending_providers = result.scalar_one()

    text = (
        f"=T <b>Provider Statistics</b>\n\n"
        f"Total Providers: {total_providers}\n"
        f"Active Providers: {active_providers}\n"
        f"Pending Approval: {pending_providers}\n"
    )

    await callback.answer()
    await callback.message.answer(text)


@router.callback_query(F.data == "admin:stats:toprated")
async def callback_admin_stats_toprated(callback: CallbackQuery, session: AsyncSession):
    """Show top rated providers"""
    provider_repo = ProviderRepository(session)
    providers, _ = await provider_repo.get_filtered(approved_only=True, limit=10)

    text = "P <b>Top Rated Providers</b>\n\n"
    for i, provider in enumerate(providers[:10], 1):
        text += f"{i}. {provider.name} - {provider.average_rating:.1f}P ({provider.rating_count} reviews)\n"

    await callback.answer()
    await callback.message.answer(text)


@router.callback_query(F.data == "admin:stats:contacted")
async def callback_admin_stats_contacted(callback: CallbackQuery, session: AsyncSession):
    """Show most contacted providers"""
    contact_repo = ContactRepository(session)
    most_contacted = await contact_repo.get_most_contacted_providers(limit=10)

    text = "=Þ <b>Most Contacted Providers</b>\n\n"
    for i, (provider, count) in enumerate(most_contacted, 1):
        text += f"{i}. {provider.name} - {count} contacts\n"

    await callback.answer()
    await callback.message.answer(text)


@router.callback_query(F.data == "admin:cancel")
async def callback_admin_cancel(callback: CallbackQuery):
    """Cancel admin action"""
    await callback.message.delete()
    await callback.answer()
