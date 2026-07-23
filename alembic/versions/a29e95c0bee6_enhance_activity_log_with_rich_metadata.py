"""enhance_activity_log_with_rich_metadata

Add rich metadata fields to ActivityLog for enterprise audit trail:
- previous_value: JSON field for previous value before change
- new_value: JSON field for new value after change  
- user_name: String field for user who performed action
- user_id: UUID field for user reference (nullable, for future auth)
- entity_type: String field for related entity type (quotation, payment, etc.)
- entity_id: UUID field for related entity reference
- metadata: JSON/JSONB field for additional structured data (JSONB in PostgreSQL, JSON in SQLite)

These fields enable change comparison, user tracking, and entity navigation.
All fields are nullable for backward compatibility.

Revision ID: a29e95c0bee6
Revises: c3f8a2d91e04
Create Date: 2026-07-22 13:22:52.136963

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a29e95c0bee6'
down_revision: Union[str, None] = 'c3f8a2d91e04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add rich metadata fields to activity_logs table
    op.add_column('activity_logs', sa.Column('previous_value', sa.Text(), nullable=True))
    op.add_column('activity_logs', sa.Column('new_value', sa.Text(), nullable=True))
    op.add_column('activity_logs', sa.Column('user_name', sa.String(length=200), nullable=True))
    op.add_column('activity_logs', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('activity_logs', sa.Column('entity_type', sa.String(length=50), nullable=True))
    op.add_column('activity_logs', sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True))
    # Use JSON type that works with both PostgreSQL (as JSONB) and SQLite (as JSON)
    op.add_column('activity_logs', sa.Column('metadata', sa.JSON(), nullable=True))
    
    # Add indexes for common query patterns
    op.create_index('ix_activity_logs_entity_type', 'activity_logs', ['entity_type'], unique=False)
    op.create_index('ix_activity_logs_entity_id', 'activity_logs', ['entity_id'], unique=False)
    op.create_index('ix_activity_logs_user_id', 'activity_logs', ['user_id'], unique=False)


def downgrade() -> None:
    # Remove indexes
    op.drop_index('ix_activity_logs_user_id', table_name='activity_logs')
    op.drop_index('ix_activity_logs_entity_id', table_name='activity_logs')
    op.drop_index('ix_activity_logs_entity_type', table_name='activity_logs')
    
    # Remove columns
    op.drop_column('activity_logs', 'metadata')
    op.drop_column('activity_logs', 'entity_id')
    op.drop_column('activity_logs', 'entity_type')
    op.drop_column('activity_logs', 'user_id')
    op.drop_column('activity_logs', 'user_name')
    op.drop_column('activity_logs', 'new_value')
    op.drop_column('activity_logs', 'previous_value')
