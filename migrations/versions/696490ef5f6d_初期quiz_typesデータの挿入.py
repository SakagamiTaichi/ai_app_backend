"""初期quiz_typesデータの挿入

Revision ID: 696490ef5f6d
Revises: d113f7a5f42f
Create Date: 2025-07-13 03:17:46.272529

"""

from typing import Sequence, Union
import uuid
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = "696490ef5f6d"
down_revision: Union[str, None] = "d113f7a5f42f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # quiz_typesテーブルのメタデータを定義
    quiz_types_table = sa.table(
        "quiz_types",
        sa.column("quiz_type_id", UUID),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    # 現在時刻を取得
    now = datetime.now(timezone.utc)

    # 初期データを定義
    initial_quiz_types = [
        {
            "quiz_type_id": uuid.uuid4(),
            "name": "シチュエーション対応",
            "description": "日常生活で起こりそうなシチュエーションに対して、適切な英語で対応する練習をします。",
            "created_at": now,
            "updated_at": now,
        },
        {
            "quiz_type_id": uuid.uuid4(),
            "name": "英文法",
            "description": "英語の文法ルールを学習するクイズです",
            "created_at": now,
            "updated_at": now,
        },
        {
            "quiz_type_id": uuid.uuid4(),
            "name": "リスニング",
            "description": "英語の聞き取り能力を向上させるクイズです",
            "created_at": now,
            "updated_at": now,
        },
        {
            "quiz_type_id": uuid.uuid4(),
            "name": "長文読解",
            "description": "英語の長文を読んで理解力を鍛えるクイズです",
            "created_at": now,
            "updated_at": now,
        },
        {
            "quiz_type_id": uuid.uuid4(),
            "name": "発音",
            "description": "正しい英語の発音を身につけるクイズです",
            "created_at": now,
            "updated_at": now,
        },
    ]

    # データを挿入
    op.bulk_insert(quiz_types_table, initial_quiz_types)


def downgrade() -> None:
    """Downgrade schema."""
    # 挿入したデータを削除（ダウングレード時）
    op.execute(
        "DELETE FROM quiz_types WHERE name IN ('シチュエーション対応', '英文法', 'リスニング', '長文読解', '発音')"
    )
