"""Bootstrap database and add node agent credentials.

Revision ID: 20261114_01
Revises:
"""

from alembic import op
import sqlalchemy as sa

from app.database import Base
from app import models


revision = "20261114_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()

    # Create missing tables on a fresh installation.
    Base.metadata.create_all(bind=connection)

    inspector = sa.inspect(connection)

    if "nodes" not in inspector.get_table_names():
        raise RuntimeError(
            "Failed to create or locate nodes table"
        )

    columns = {
        column["name"]
        for column in inspector.get_columns("nodes")
    }

    if "agent_port" not in columns:
        op.add_column(
            "nodes",
            sa.Column(
                "agent_port",
                sa.Integer(),
                nullable=False,
                server_default="9000",
            ),
        )

    if "agent_token_encrypted" not in columns:
        op.add_column(
            "nodes",
            sa.Column(
                "agent_token_encrypted",
                sa.Text(),
                nullable=True,
            ),
        )


def downgrade():
    # Keep columns to avoid accidental data loss.
    pass
