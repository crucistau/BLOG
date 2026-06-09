"""Seed script to create the initial admin user."""

import asyncio

from sqlalchemy import select

from app.database import async_session, engine
from app.dependencies.auth import hash_password
from app.models import User


async def seed() -> None:
    from app.database import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none() is None:
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
            )
            session.add(admin)
            await session.commit()
            print("Admin user created: admin / admin123")
        else:
            print("Admin user already exists, skipping.")


if __name__ == "__main__":
    asyncio.run(seed())
