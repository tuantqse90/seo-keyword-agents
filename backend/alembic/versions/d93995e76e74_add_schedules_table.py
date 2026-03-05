"""add_schedules_table

Revision ID: d93995e76e74
Revises: ed3c0eec8c2d
Create Date: 2026-03-05 22:36:49.540904
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd93995e76e74'
down_revision: Union[str, None] = 'ed3c0eec8c2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE schedules (
            id UUID PRIMARY KEY,
            project_id UUID REFERENCES projects(id),
            module reportmodule NOT NULL,
            query VARCHAR(2048) NOT NULL,
            interval_hours INTEGER NOT NULL DEFAULT 168,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            last_run_at TIMESTAMP,
            next_run_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)


def downgrade() -> None:
    op.drop_table('schedules')
