"""Add is_edited flag to generated_files."""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260613_0002"
down_revision = "20260418_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "generated_files",
        sa.Column(
            "is_edited",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("generated_files", "is_edited")
