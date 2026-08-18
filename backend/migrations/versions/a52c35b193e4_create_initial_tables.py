"""Create initial tables

Revision ID: a52c35b193e4
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import JSON

# revision identifiers, used by Alembic.
revision = 'a52c35b193e4'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create actions table
    op.create_table(
        'actions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('agent_id', sa.String(100), nullable=False),
        sa.Column('operation', sa.String(50), nullable=False),
        sa.Column('target_table', sa.String(100), nullable=True),
        sa.Column('condition', sa.String(500), nullable=True),
        sa.Column('record_count', sa.Integer, default=0),
        sa.Column('data_category', sa.String(50), nullable=True),
        sa.Column('parameters', JSON, nullable=True),
        sa.Column('llm_confidence', sa.Float, default=0.5),
        sa.Column('validation_score', sa.Float, default=0.5),
        sa.Column('reversibility_score', sa.Integer, default=0),
        sa.Column('data_scope_score', sa.Integer, default=0),
        sa.Column('regulatory_score', sa.Integer, default=0),
        sa.Column('confidence_score', sa.Integer, default=0),
        sa.Column('total_risk', sa.Integer, default=0),
        sa.Column('autonomy_level', sa.String(20), default='PENDING'),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('execution_status', sa.String(20), nullable=True),
        sa.Column('execution_result', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('action_id', sa.String(36), nullable=False),
        sa.Column('reviewer', sa.String(100), nullable=True),
        sa.Column('review_status', sa.String(20), default='pending'),
        sa.Column('decision', sa.String(20), nullable=True),
        sa.Column('comment', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('reviewed_at', sa.DateTime, nullable=True),
        sa.Column('assigned_at', sa.DateTime, nullable=True),
        sa.Column('sla_deadline', sa.DateTime, nullable=True),
        sa.Column('escalation_level', sa.Integer, default=0),
        sa.ForeignKeyConstraint(['action_id'], ['actions.id'])
    )
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('action_id', sa.String(36), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_data', JSON, nullable=True),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('risk_breakdown', JSON, nullable=True),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['action_id'], ['actions.id'])
    )
    
    # Create indexes
    op.create_index('idx_actions_agent_id', 'actions', ['agent_id'])
    op.create_index('idx_actions_created_at', 'actions', ['created_at'])
    op.create_index('idx_audit_timestamp', 'audit_logs', ['timestamp'])

def downgrade() -> None:
    op.drop_index('idx_audit_timestamp', table_name='audit_logs')
    op.drop_index('idx_actions_created_at', table_name='actions')
    op.drop_index('idx_actions_agent_id', table_name='actions')
    op.drop_table('audit_logs')
    op.drop_table('reviews')
    op.drop_table('actions')