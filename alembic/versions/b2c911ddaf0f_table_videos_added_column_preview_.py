"""table videos: added column preview_storage_key

Revision ID: b2c911ddaf0f
Revises: 6524df9ee467
Create Date: 2026-10-27 17:11:52.199785

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "b2c911ddaf0f"
down_revision: Union[str, Sequence[str], None] = "6524df9ee467"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # тип нужно создать до колонки, op.add_column его сам не создаёт
    postgresql.ENUM(
        "processing", "success", "failed", name="videostatus"
    ).create(op.get_bind(), checkfirst=True)

    op.alter_column("videos", "storage_key", new_column_name="video_storage_key")

    # server_default нужен только чтобы заполнить уже существующие строки
    op.add_column(
        "videos",
        sa.Column(
            "preview_storage_key", sa.String(), nullable=False, server_default=""
        ),
    )
    op.add_column(
        "videos",
        sa.Column(
            "status",
            postgresql.ENUM(
                "processing",
                "success",
                "failed",
                name="videostatus",
                create_type=False,
            ),
            nullable=False,
            server_default="success",
        ),
    )

    # в модели значений по умолчанию нет, убираем их из БД
    op.alter_column("videos", "preview_storage_key", server_default=None)
    op.alter_column("videos", "status", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("videos", "status")
    op.drop_column("videos", "preview_storage_key")
    op.alter_column("videos", "video_storage_key", new_column_name="storage_key")

    postgresql.ENUM(name="videostatus").drop(op.get_bind(), checkfirst=True)
