"""Script to fix admin status for existing users"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.session import async_session_maker, init_db
from app.database.models import User
from app.config import settings
from sqlalchemy import select, update


async def fix_admin_status():
    """Fix admin status for existing users"""
    print("🔧 Fixing admin status for existing users...")
    print(f"Admin IDs from config: {settings.admin_list}")

    async with async_session_maker() as session:
        # Get all users who should be admins
        result = await session.execute(
            select(User).where(User.telegram_id.in_(settings.admin_list))
        )
        users = result.scalars().all()

        if not users:
            print("⚠️  No users found with the configured admin IDs")
            return

        # Update admin status
        updated_count = 0
        for user in users:
            if not user.is_admin:
                user.is_admin = True
                updated_count += 1
                print(f"✅ Updated admin status for user {user.telegram_id} (@{user.username})")
            else:
                print(f"ℹ️  User {user.telegram_id} (@{user.username}) already has admin status")

        if updated_count > 0:
            await session.commit()
            print(f"\n✅ Successfully updated {updated_count} user(s)")
        else:
            print("\n✅ All admin users already have correct status")

        # Also check for users who have admin status but are not in the admin list
        result = await session.execute(
            select(User).where(User.is_admin == True)
        )
        admin_users = result.scalars().all()

        invalid_admins = [u for u in admin_users if u.telegram_id not in settings.admin_list]
        if invalid_admins:
            print(f"\n⚠️  Warning: Found {len(invalid_admins)} user(s) with admin status not in config:")
            for user in invalid_admins:
                print(f"   - User {user.telegram_id} (@{user.username})")


async def main():
    """Main function"""
    # Initialize database
    await init_db()
    print("✅ Database initialized\n")

    await fix_admin_status()

    print("\n✅ Done!")


if __name__ == "__main__":
    asyncio.run(main())
