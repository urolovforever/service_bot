"""Bot initialization and setup"""

import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.middlewares.database import DatabaseMiddleware
from app.middlewares.logging_middleware import LoggingMiddleware
from app.handlers.user import start, browse, contact, rating, favorites
from app.handlers.admin import panel

logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    """Create bot instance"""
    return Bot(token=settings.BOT_TOKEN, parse_mode="HTML")


def create_dispatcher() -> Dispatcher:
    """Create dispatcher with routers and middlewares"""
    dp = Dispatcher(storage=MemoryStorage())

    # Register middlewares
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # Register routers
    # User handlers
    dp.include_router(start.router)
    dp.include_router(browse.router)
    dp.include_router(contact.router)
    dp.include_router(rating.router)
    dp.include_router(favorites.router)

    # Admin handlers
    dp.include_router(panel.router)

    logger.info("Dispatcher configured successfully")

    return dp
