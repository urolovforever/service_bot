"""Script to populate initial data for testing"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.session import async_session_maker, init_db
from app.database.repositories import LocationRepository, CategoryRepository, ProviderRepository


async def populate_locations(session):
    """Populate sample locations"""
    location_repo = LocationRepository(session)

    locations = [
        {"name_en": "Tashkent", "name_ru": ""0H:5=B", "name_uz": "Toshkent"},
        {"name_en": "Samarkand", "name_ru": "!0<0@:0=4", "name_uz": "Samarqand"},
        {"name_en": "Bukhara", "name_ru": "CE0@0", "name_uz": "Buxoro"},
        {"name_en": "Khiva", "name_ru": "%820", "name_uz": "Xiva"},
    ]

    for loc in locations:
        await location_repo.create(**loc)
        print(f" Created location: {loc['name_en']}")


async def populate_categories(session):
    """Populate sample categories"""
    category_repo = CategoryRepository(session)

    categories = [
        {
            "name_en": "Plumbing",
            "name_ru": "!0=B5E=8:0",
            "name_uz": "Santexnika",
            "icon": "='",
            "description_en": "Plumbing and water system services",
        },
        {
            "name_en": "Electrical",
            "name_ru": "-;5:B@8:0",
            "name_uz": "Elektr",
            "icon": "¡",
            "description_en": "Electrical installation and repair",
        },
        {
            "name_en": "Cleaning",
            "name_ru": "#1>@:0",
            "name_uz": "Tozalash",
            "icon": ">ù",
            "description_en": "Professional cleaning services",
        },
        {
            "name_en": "Carpentry",
            "name_ru": "!B>;O@=K5 @01>BK",
            "name_uz": "Duradgorlik",
            "icon": ">š",
            "description_en": "Carpentry and woodwork",
        },
        {
            "name_en": "Painting",
            "name_ru": ">:@0A:0",
            "name_uz": "Bo'yash",
            "icon": "<¨",
            "description_en": "Painting and decorating",
        },
    ]

    for cat in categories:
        await category_repo.create(**cat)
        print(f" Created category: {cat['name_en']}")


async def populate_providers(session):
    """Populate sample providers"""
    provider_repo = ProviderRepository(session)

    providers = [
        {
            "name": "John's Plumbing Services",
            "description": "Professional plumbing services with 10 years experience. We handle all types of plumbing issues including leaks, installations, and repairs.",
            "location_id": 1,
            "category_id": 1,
            "phone": "+998901234567",
            "telegram_username": "johns_plumbing",
            "price_min": 50000,
            "price_max": 500000,
            "currency": "UZS",
        },
        {
            "name": "ElectroMaster",
            "description": "Expert electrical services for homes and businesses. Licensed and insured electricians available 24/7.",
            "location_id": 1,
            "category_id": 2,
            "phone": "+998901234568",
            "telegram_username": "electromaster",
            "price_min": 100000,
            "price_max": 1000000,
            "currency": "UZS",
        },
        {
            "name": "CleanPro Services",
            "description": "Professional cleaning company offering residential and commercial cleaning. Eco-friendly products.",
            "location_id": 1,
            "category_id": 3,
            "phone": "+998901234569",
            "telegram_username": "cleanpro",
            "price_min": 80000,
            "price_max": 300000,
            "currency": "UZS",
        },
        {
            "name": "Wood Masters",
            "description": "Custom furniture and carpentry services. Quality woodwork for your home and office.",
            "location_id": 2,
            "category_id": 4,
            "phone": "+998901234570",
            "telegram_username": "woodmasters",
            "price_min": 200000,
            "price_max": 2000000,
            "currency": "UZS",
        },
        {
            "name": "Perfect Paint",
            "description": "Professional painting services for interior and exterior. High-quality paints and expert application.",
            "location_id": 2,
            "category_id": 5,
            "phone": "+998901234571",
            "telegram_username": "perfectpaint",
            "price_min": 150000,
            "price_max": 1500000,
            "currency": "UZS",
        },
    ]

    for prov in providers:
        provider = await provider_repo.create(**prov)
        # Auto-approve for testing
        await provider_repo.approve(provider.id)
        print(f" Created and approved provider: {prov['name']}")


async def main():
    """Main function"""
    print("=€ Populating database with sample data...")

    # Initialize database
    await init_db()
    print(" Database initialized")

    async with async_session_maker() as session:
        print("\n=Í Creating locations...")
        await populate_locations(session)

        print("\n=Â Creating categories...")
        await populate_categories(session)

        print("\n=T Creating providers...")
        await populate_providers(session)

    print("\n Database populated successfully!")
    print("\nYou can now:")
    print("1. Start the bot with: python main.py")
    print("2. Open Telegram and start chatting with your bot")
    print("3. Browse providers by location and category")
    print("4. Use /admin command if you're an admin")


if __name__ == "__main__":
    asyncio.run(main())
