"""Add per-node CA certificate for secure HTTPS connections.

Revision ID: 20261114_02
Revises: 20261114_01
"""

from alembic import op
import sqlalchemy as sa


revision = "20261114_02"
down_revision = "20261114_01"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "nodes",
        sa.Column(
            "agent_ca_certificate",
            sa.Text(),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column(
        "nodes",
        "agent_ca_certificate",
    )
