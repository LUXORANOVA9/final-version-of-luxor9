"""Initial LUXOR9 Schema Migration

Revision ID: 001
Revises: 
Create Date: 2026-03-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('slug', sa.String(50), unique=True, nullable=False),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('vp_name', sa.String(50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('revenue_target', sa.Float(), default=0.0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
    )
    
    # Create agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('agent_class', sa.String(30), nullable=False),
        sa.Column('tier', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(100), nullable=False),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('categories.id'), nullable=True),
        sa.Column('parent_agent_id', sa.String(50), sa.ForeignKey('agents.id'), nullable=True),
        sa.Column('model', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), default='idle'),
        sa.Column('personality', sa.Text(), nullable=True),
        sa.Column('config', postgresql.JSONB, default={}),
        sa.Column('tasks_completed', sa.Integer(), default=0),
        sa.Column('tasks_failed', sa.Integer(), default=0),
        sa.Column('revenue_generated', sa.Float(), default=0.0),
        sa.Column('success_rate', sa.Float(), default=100.0),
        sa.Column('think_cycle_seconds', sa.Integer(), default=30),
        sa.Column('authority_level', sa.Integer(), default=5),
        sa.Column('last_heartbeat', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
    )
    
    # Create streams table
    op.create_table(
        'streams',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('categories.id'), nullable=False),
        sa.Column('status', sa.String(20), default='idle'),
        sa.Column('assigned_vp_id', sa.String(50), sa.ForeignKey('agents.id'), nullable=True),
        sa.Column('revenue_today', sa.Float(), default=0.0),
        sa.Column('revenue_total', sa.Float(), default=0.0),
        sa.Column('revenue_yesterday', sa.Float(), default=0.0),
        sa.Column('customers', sa.Integer(), default=0),
        sa.Column('health_score', sa.Float(), default=100.0),
        sa.Column('error_count', sa.Integer(), default=0),
        sa.Column('config', postgresql.JSONB, default={}),
        sa.Column('deployed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
    )
    
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('assigned_to_id', sa.String(50), sa.ForeignKey('agents.id'), nullable=True),
        sa.Column('assigned_by_id', sa.String(50), sa.ForeignKey('agents.id'), nullable=True),
        sa.Column('stream_id', sa.Integer(), sa.ForeignKey('streams.id'), nullable=True),
        sa.Column('task_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(15), default='P2_MEDIUM'),
        sa.Column('status', sa.String(20), default='queued'),
        sa.Column('input_data', postgresql.JSONB, default={}),
        sa.Column('output_data', postgresql.JSONB, nullable=True),
        sa.Column('attempts', sa.Integer(), default=0),
        sa.Column('max_attempts', sa.Integer(), default=3),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
    )
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('from_agent_id', sa.String(50), sa.ForeignKey('agents.id'), nullable=False),
        sa.Column('to_agent_id', sa.String(50), sa.ForeignKey('agents.id'), nullable=False),
        sa.Column('msg_type', sa.String(20), nullable=False),
        sa.Column('priority', sa.String(15), default='P2_MEDIUM'),
        sa.Column('channel', sa.String(15), default='upward'),
        sa.Column('payload', postgresql.JSONB, nullable=False),
        sa.Column('response', postgresql.JSONB, nullable=True),
        sa.Column('status', sa.String(15), default='pending'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('responded_at', sa.DateTime(), nullable=True),
    )
    
    # Create metrics table
    op.create_table(
        'metrics',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('stream_id', sa.Integer(), sa.ForeignKey('streams.id'), nullable=True),
        sa.Column('agent_id', sa.String(50), sa.ForeignKey('agents.id'), nullable=True),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('categories.id'), nullable=True),
        sa.Column('metric_type', sa.String(50), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('recorded_at', sa.DateTime(), server_default=sa.text('now()')),
    )
    
    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('agent_id', sa.String(50), sa.ForeignKey('agents.id'), nullable=True),
        sa.Column('stream_id', sa.Integer(), sa.ForeignKey('streams.id'), nullable=True),
        sa.Column('data', postgresql.JSONB, default={}),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
    )
    
    # Create system_state table
    op.create_table(
        'system_state',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('key', sa.String(100), unique=True, nullable=False),
        sa.Column('value', postgresql.JSONB, nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
    )
    
    # Create indexes
    op.create_index('idx_metrics_stream_time', 'metrics', ['stream_id', 'recorded_at'])
    op.create_index('idx_metrics_agent_time', 'metrics', ['agent_id', 'recorded_at'])
    op.create_index('idx_events_time', 'events', ['created_at'])
    op.create_index('idx_agents_tier', 'agents', ['tier'])
    op.create_index('idx_agents_status', 'agents', ['status'])
    op.create_index('idx_streams_category', 'streams', ['category_id'])


def downgrade() -> None:
    op.drop_index('idx_streams_category')
    op.drop_index('idx_agents_status')
    op.drop_index('idx_agents_tier')
    op.drop_index('idx_events_time')
    op.drop_index('idx_metrics_agent_time')
    op.drop_index('idx_metrics_stream_time')
    
    op.drop_table('system_state')
    op.drop_table('events')
    op.drop_table('metrics')
    op.drop_table('messages')
    op.drop_table('tasks')
    op.drop_table('streams')
    op.drop_table('agents')
    op.drop_table('categories')
