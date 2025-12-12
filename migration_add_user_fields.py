"""Migration script to add phone_number and location_id to users table

Run this script from your local environment:
    python migration_add_user_fields.py

Or use the migration.sql file with psql:
    psql -h localhost -U marketplace_user -d marketplace_bot -f migration.sql
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def migrate():
    """Add phone_number and location_id columns to users table"""
    engine = create_async_engine(settings.database_url)

    try:
        async with engine.begin() as conn:
            # Check if columns exist
            logger.info("Checking if columns already exist...")

            # Add phone_number column
            try:
                await conn.execute(text(
                    "ALTER TABLE users ADD COLUMN phone_number VARCHAR(50)"
                ))
                logger.info("✅ Added phone_number column")
            except Exception as e:
                if "already exists" in str(e):
                    logger.info("ℹ️  phone_number column already exists")
                else:
                    raise

            # Add location_id column
            try:
                await conn.execute(text(
                    "ALTER TABLE users ADD COLUMN location_id INTEGER"
                ))
                logger.info("✅ Added location_id column")
            except Exception as e:
                if "already exists" in str(e):
                    logger.info("ℹ️  location_id column already exists")
                else:
                    raise

            # Add foreign key constraint
            try:
                await conn.execute(text(
                    "ALTER TABLE users ADD CONSTRAINT users_location_id_fkey "
                    "FOREIGN KEY (location_id) REFERENCES locations(id)"
                ))
                logger.info("✅ Added foreign key constraint")
            except Exception as e:
                if "already exists" in str(e):
                    logger.info("ℹ️  Foreign key constraint already exists")
                else:
                    raise

        logger.info("✅ Migration completed successfully!")

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(migrate())
