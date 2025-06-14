import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class RecallCardModel(Base):
    """復習カードモデル"""

    __tablename__ = "en_recall_cards"

    recall_card_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    question = Column(String, nullable=False, comment="質問")
    answer = Column(String, nullable=False, comment="答案")
    correct_point = Column(Integer, nullable=False, default=0, comment="正解ポイント")
    review_deadline = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
        comment="復習期限",
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
        comment="作成日時",
    )

    # リレーションシップ
    user = relationship("UserModel", back_populates="recall_cards")
