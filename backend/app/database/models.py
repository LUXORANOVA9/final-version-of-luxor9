"""LUXOR9 Database Models - Cross-Database Compatible"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.types import CHAR, JSON as SA_JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class GUID(TypeDecorator):
    """Platform-independent GUID type using CHAR(36) for storage"""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid4().__class__):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid4().__class__):
            return value
        return uuid4(value)


class JSONType(TypeDecorator):
    """Cross-database JSON type"""
    impl = SA_JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(SA_JSON())


class Agent(Base):
    """Agent table - stores all agents in the hierarchy"""
    __tablename__ = "agents"

    id = Column(GUID(), primary_key=True, default=uuid4)
    name = Column(String(50), nullable=False, unique=True)
    agent_class = Column(String(30), nullable=False)
    tier = Column(Integer, nullable=False)
    role = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    parent_agent_id = Column(GUID(), ForeignKey("agents.id"), nullable=True)

    model = Column(String(50), nullable=False)
    status = Column(String(20), default="idle")
    personality = Column(Text, nullable=True)
    config = Column(JSONType, default={})

    tasks_completed = Column(Integer, default=0)
    tasks_failed = Column(Integer, default=0)
    revenue_generated = Column(Float, default=0.0)
    success_rate = Column(Float, default=100.0)

    think_cycle_seconds = Column(Integer, default=30)
    authority_level = Column(Integer, default=5)
    last_heartbeat = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    children = relationship("Agent", backref="parent", remote_side=[id])
    category = relationship("Category", backref="agents")
    tasks = relationship("Task", backref="assigned_agent", foreign_keys="Task.assigned_to")
    messages = relationship("Message", backref="from_agent", foreign_keys="Message.from_agent_id")


class Category(Base):
    """Product/Service Categories"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    color = Column(String(20), nullable=True)
    vp_name = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    revenue_target = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)


class Stream(Base):
    """Income Streams"""
    __tablename__ = "streams"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    status = Column(String(20), default="idle")

    revenue_today = Column(Float, default=0.0)
    revenue_total = Column(Float, default=0.0)
    revenue_yesterday = Column(Float, default=0.0)

    customers = Column(Integer, default=0)
    health_score = Column(Float, default=100.0)
    error_count = Column(Integer, default=0)

    assigned_vp_id = Column(GUID(), ForeignKey("agents.id"), nullable=True)

    config = Column(JSONType, default={})
    deployed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", backref="streams")
    assigned_vp = relationship("Agent", backref="assigned_streams")
    tasks = relationship("Task", backref="stream")


class Task(Base):
    """Tasks assigned to agents"""
    __tablename__ = "tasks"

    id = Column(GUID(), primary_key=True, default=uuid4)
    assigned_to_id = Column(GUID(), ForeignKey("agents.id"), nullable=True)
    assigned_by_id = Column(GUID(), ForeignKey("agents.id"), nullable=True)
    stream_id = Column(Integer, ForeignKey("streams.id"), nullable=True)

    task_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(15), default="P2_MEDIUM")

    status = Column(String(20), default="queued")

    input_data = Column(JSONType, default={})
    output_data = Column(JSONType, default={})

    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)

    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    """Inter-agent messages"""
    __tablename__ = "messages"

    id = Column(GUID(), primary_key=True, default=uuid4)
    from_agent_id = Column(GUID(), ForeignKey("agents.id"), nullable=False)
    to_agent_id = Column(GUID(), ForeignKey("agents.id"), nullable=False)

    msg_type = Column(String(20), nullable=False)
    priority = Column(String(15), default="P2_MEDIUM")
    channel = Column(String(15), default="upward")

    payload = Column(JSONType, nullable=False)
    response = Column(JSONType, nullable=True)

    status = Column(String(15), default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)


class Metric(Base):
    """Time-series metrics"""
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True)
    stream_id = Column(Integer, ForeignKey("streams.id"), nullable=True)
    agent_id = Column(GUID(), ForeignKey("agents.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    metric_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    metadata = Column(JSONType, default={})

    recorded_at = Column(DateTime, default=datetime.utcnow)


class Event(Base):
    """Audit trail"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    event_type = Column(String(50), nullable=False)
    source = Column(String(100), nullable=True)
    agent_id = Column(GUID(), ForeignKey("agents.id"), nullable=True)
    stream_id = Column(Integer, ForeignKey("streams.id"), nullable=True)

    data = Column(JSONType, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemState(Base):
    """System-wide state"""
    __tablename__ = "system_state"

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSONType, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
