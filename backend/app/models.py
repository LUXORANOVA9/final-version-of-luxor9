"""LUXOR9 Database Models - Unified ORM Models

This module re-exports from app.database.models for consistency.
All database models should be imported from here.
"""
# Re-export all models from database.models for backward compatibility
from app.database.models import (
    Base,
    Agent,
    Category,
    Stream,
    Task,
    Message,
    Metric,
    Event,
    SystemState,
    get_engine,
    get_session,
    init_db as _init_db,
)

# For backward compatibility - init_db wrapper
def init_db():
    """Initialize database tables"""
    _init_db()


__all__ = [
    "Base",
    "Agent", 
    "Category",
    "Stream",
    "Task",
    "Message",
    "Metric",
    "Event",
    "SystemState",
    "get_engine",
    "get_session",
    "init_db",
]
