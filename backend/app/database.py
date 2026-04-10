"""LUXOR9 - Database Setup with Connection Pooling"""
import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from app.config import get_settings

logger = logging.getLogger("luxor9.database")

Base = declarative_base()

_settings = get_settings()


def get_database_url() -> str:
    db_url = os.environ.get("DATABASE_URL", _settings.database_url)
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("sqlite://"):
        db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return db_url


def get_sync_database_url() -> str:
    return os.environ.get("DATABASE_URL", _settings.database_url)


is_postgres = _settings.database_url.startswith("postgresql")


if is_postgres:
    async_engine = create_async_engine(
        get_database_url(),
        echo=_settings.debug,
        pool_size=_settings.db_pool_size,
        max_overflow=_settings.db_max_overflow,
        pool_timeout=_settings.db_pool_timeout,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    sync_engine = create_engine(
        get_sync_database_url(),
        echo=_settings.debug,
        pool_size=_settings.db_pool_size,
        max_overflow=_settings.db_max_overflow,
        pool_timeout=_settings.db_pool_timeout,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
else:
    async_engine = create_async_engine(
        "sqlite+aiosqlite:///luxor9.db",
        echo=_settings.debug,
        poolclass=NullPool,
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    sync_engine = create_engine(
        "sqlite:///luxor9.db",
        echo=_settings.debug,
        connect_args={"check_same_thread": False},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with get_async_db() as session:
        yield session


def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_async_db():
    """Initialize async database and create all tables"""
    from app.database.models import Base
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Async database tables created")


def init_db():
    """Initialize database and create all tables (sync version)"""
    from app.database.models import Base
    Base.metadata.create_all(bind=sync_engine)
    _seed_categories_sync()


def _seed_categories_sync():
    """Seed categories and streams using sync session"""
    db = SessionLocal()
    try:
        from app.database.models import Category, Stream
        existing = db.query(Category).first()
        if not existing:
            categories = [
                Category(id=1, name="AI Agency", vp_name="FORGE", color="#3b82f6"),
                Category(id=2, name="SaaS", vp_name="NEXUS", color="#8b5cf6"),
                Category(id=3, name="Creative", vp_name="MUSE", color="#ec4899"),
                Category(id=4, name="Digital", vp_name="ATLAS", color="#f59e0b"),
                Category(id=5, name="Finance", vp_name="VAULT", color="#10b981"),
                Category(id=6, name="E-commerce", vp_name="MARKET", color="#06b6d4"),
                Category(id=7, name="Real Estate", vp_name="TERRA", color="#f97316"),
                Category(id=8, name="Marketing", vp_name="SIGNAL", color="#ef4444"),
                Category(id=9, name="Enterprise", vp_name="TITAN", color="#6366f1"),
                Category(id=10, name="Consulting", vp_name="ORACLE", color="#64748b"),
            ]
            db.add_all(categories)

            for cat_id in range(1, 11):
                for stream_num in range(1, 11):
                    stream = Stream(
                        id=(cat_id - 1) * 10 + stream_num,
                        title=f"Stream {(cat_id - 1) * 10 + stream_num}",
                        category_id=cat_id,
                        status="idle"
                    )
                    db.add(stream)

            db.commit()
            logger.info("Database seeded with categories and streams")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


async def seed_categories_async():
    """Seed categories and streams using async session"""
    async with AsyncSessionLocal() as session:
        try:
            from app.database.models import Category, Stream
            result = await session.execute(text("SELECT id FROM categories LIMIT 1"))
            existing = result.fetchone()
            
            if not existing:
                categories = [
                    Category(id=1, name="AI Agency", vp_name="FORGE", color="#3b82f6"),
                    Category(id=2, name="SaaS", vp_name="NEXUS", color="#8b5cf6"),
                    Category(id=3, name="Creative", vp_name="MUSE", color="#ec4899"),
                    Category(id=4, name="Digital", vp_name="ATLAS", color="#f59e0b"),
                    Category(id=5, name="Finance", vp_name="VAULT", color="#10b981"),
                    Category(id=6, name="E-commerce", vp_name="MARKET", color="#06b6d4"),
                    Category(id=7, name="Real Estate", vp_name="TERRA", color="#f97316"),
                    Category(id=8, name="Marketing", vp_name="SIGNAL", color="#ef4444"),
                    Category(id=9, name="Enterprise", vp_name="TITAN", color="#6366f1"),
                    Category(id=10, name="Consulting", vp_name="ORACLE", color="#64748b"),
                ]
                session.add_all(categories)
                await session.flush()

                streams = []
                for cat_id in range(1, 11):
                    for stream_num in range(1, 11):
                        streams.append(Stream(
                            id=(cat_id - 1) * 10 + stream_num,
                            title=f"Stream {(cat_id - 1) * 10 + stream_num}",
                            category_id=cat_id,
                            status="idle"
                        ))
                session.add_all(streams)
                await session.commit()
                logger.info("Async database seeded with categories and streams")
        except Exception as e:
            logger.error(f"Error seeding async database: {e}")
            await session.rollback()
            raise


async def close_async_db():
    """Close async database connections"""
    await async_engine.dispose()
    logger.info("Async database connections closed")


def close_db():
    """Close sync database connections"""
    sync_engine.dispose()
    logger.info("Sync database connections closed")


@event.listens_for(sync_engine, "connect")
def set_search_path(dbapi_connection, connection_record):
    """Set PostgreSQL search_path for multi-tenant support"""
    if is_postgres:
        cursor = dbapi_connection.cursor()
        cursor.execute("SELECT current_setting('search_path')")
        current = cursor.fetchone()[0]
        if "luxor9" not in current:
            cursor.execute("SET search_path TO public")
        cursor.close()
