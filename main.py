"""Main entry point for the Telegram Service Marketplace Bot"""

import asyncio
import logging
import sys
from pathlib import Path
from aiogram import Bot, Dispatcher

from app.config import settings
from app.bot import create_bot, create_dispatcher
from app.database.session import init_db
from app.services.redis_service import redis_service

# Create logs directory if it doesn't exist
Path("logs").mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/bot.log"),
    ],
)

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, dp: Dispatcher):
    """Actions on bot startup"""
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_db()

        # Connect to Redis
        logger.info("Connecting to Redis...")
        await redis_service.connect()

        # Get bot info
        bot_info = await bot.get_me()
        logger.info(f"Bot @{bot_info.username} started successfully!")

        # Notify admins
        for admin_id in settings.admin_list:
            try:
                await bot.send_message(admin_id, "🤖 Bot has been started!")
            except Exception as e:
                logger.warning(f"Failed to notify admin {admin_id}: {e}")

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


async def on_shutdown(bot: Bot):
    """Actions on bot shutdown"""
    logger.info("Shutting down bot...")

    # Disconnect from Redis
    await redis_service.disconnect()

    # Notify admins
    for admin_id in settings.admin_list:
        try:
            await bot.send_message(admin_id, "🔴 Bot has been stopped!")
        except Exception as e:
            logger.warning(f"Failed to notify admin {admin_id}: {e}")

    logger.info("Bot stopped successfully")


async def main():
    """Main function"""
    # Create bot and dispatcher
    bot = create_bot()
    dp = create_dispatcher()

    # Run startup actions
    await on_startup(bot, dp)

    try:
        # Start polling
        logger.info("Starting bot polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Error during polling: {e}")
    finally:
        # Run shutdown actions
        await on_shutdown(bot)
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
