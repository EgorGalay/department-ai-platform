"""Add password hashes for local accounts.

Revision ID: 0002_add_password_hash
Revises: 0001_initial_identity
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_add_password_hash"
down_revision = "0001_initial_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "password_hash")
