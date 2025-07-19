import uuid
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    Integer,
    Boolean,
    DateTime,
)


class Users(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # リレーションシップ
    conversations = relationship("Conversations", back_populates="user")
    learning_histories = relationship("LearningHistories", back_populates="user")
    recall_cards = relationship("RecallCards", back_populates="user")
    study_record = relationship("StudyRecords", uselist=False, back_populates="user")
    user_answers = relationship("UserAnswers", back_populates="user")
    review_schedules = relationship("ReviewSchedules", back_populates="user")


class VerificationCodes(Base):
    __tablename__ = "verification_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, index=True)
    code = Column(String(6), nullable=False)
    is_used = Column(Boolean, default=False)
    verification_attempts = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class PasswordResetTokens(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, index=True)
    token = Column(String, nullable=False, unique=True, index=True)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    used_at = Column(DateTime(timezone=True), nullable=True)


class StudyRecords(Base):
    __tablename__ = "study_records"

    study_record_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # リレーションシップ
    user = relationship("Users", back_populates="study_record")
    daily_study_records = relationship("DailyStudyRecords", back_populates="study_record")


class DailyStudyRecords(Base):
    __tablename__ = "daily_study_records"

    study_record_id = Column(
        UUID(as_uuid=True),
        ForeignKey("study_records.study_record_id"),
        nullable=False,
        primary_key=True,
        index=True,
    )
    date = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    study_time = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # 外部キー制約
    __table_args__ = (
        ForeignKeyConstraint(
            ["study_record_id"],
            ["study_records.study_record_id"],
            ondelete="CASCADE",
        ),
    )

    # リレーションシップ
    study_record = relationship("StudyRecords", back_populates="daily_study_records")


class Quiz(Base):
    __tablename__ = "quizzes"

    quiz_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(String(300), nullable=False)
    quiz_type_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quiz_types.quiz_type_id"),
        nullable=False,
        index=True,
    )  # クイズの種類ID
    difficulty = Column(Integer, nullable=False, default=1)
    model_answer = Column(String(300), nullable=False, comment="模範解答")
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # リレーションシップ
    quiz_type = relationship("QuizType", back_populates="quizzes")
    user_answers = relationship("UserAnswers", back_populates="quiz")
    review_schedules = relationship("ReviewSchedules", back_populates="quiz")


class QuizType(Base):
    __tablename__ = "quiz_types"

    quiz_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(300), nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # リレーションシップ
    quizzes = relationship("Quiz", back_populates="quiz_type")


class UserAnswers(Base):
    __tablename__ = "user_answers"

    user_answer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    quiz_id = Column(
        UUID(as_uuid=True), ForeignKey("quizzes.quiz_id"), nullable=False, index=True
    )
    answer = Column(String(300), nullable=False)
    score = Column(Integer, nullable=False)
    feedback = Column(String(500), nullable=True)
    model_answer = Column(String(300), nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # リレーションシップ
    quiz = relationship("Quiz", back_populates="user_answers")
    user = relationship("Users", back_populates="user_answers")


class ReviewSchedules(Base):
    __tablename__ = "review_schedules"

    review_schedule_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    quiz_id = Column(
        UUID(as_uuid=True), ForeignKey("quizzes.quiz_id"), nullable=False, index=True
    )
    review_deadline = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # リレーションシップ
    quiz = relationship("Quiz", back_populates="review_schedules")
    user = relationship("Users", back_populates="review_schedules")


class Conversations(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    title = Column(String(200), nullable=False)
    order = Column(Integer, default=0)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # リレーションシップ
    messages = relationship("Messages", back_populates="conversation")
    test_scores = relationship("ConversationTestScores", back_populates="conversation")
    user = relationship("Users", back_populates="conversations")


class Messages(Base):
    __tablename__ = "messages"

    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), primary_key=True
    )
    message_order = Column(Integer, primary_key=True)
    speaker_number = Column(Integer, nullable=False)
    message_en = Column(String, nullable=False)
    message_ja = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # リレーションシップ
    conversation = relationship("Conversations", back_populates="messages")


class ConversationTestScores(Base):
    __tablename__ = "conversation_test_scores"

    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), primary_key=True
    )
    test_number = Column(Integer, primary_key=True)
    test_score = Column(Float, nullable=False)
    is_pass = Column(Boolean, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # リレーションシップ
    conversation = relationship("Conversations", back_populates="test_scores")
    message_scores = relationship("MessageTestScores", back_populates="test")


class MessageTestScores(Base):
    __tablename__ = "message_test_scores"

    conversation_id = Column(UUID(as_uuid=True), primary_key=True)
    test_number = Column(Integer, primary_key=True)
    message_order = Column(Integer, primary_key=True)
    score = Column(Float, nullable=False)
    user_answer = Column(String, nullable=False)  # P7653

    __table_args__ = (
        ForeignKeyConstraint(
            ["conversation_id", "test_number"],
            [
                "conversation_test_scores.conversation_id",
                "conversation_test_scores.test_number",
            ],
        ),
    )

    # リレーションシップ
    test = relationship("ConversationTestScores", back_populates="message_scores")


class LearningHistories(Base):
    __tablename__ = "learning_histories"

    date = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
        primary_key=True,
    )
    learning_time = Column(Integer, nullable=False, default=0.0)

    # リレーションシップ
    user = relationship("Users", back_populates="learning_histories")


class RecallCards(Base):
    """復習カードモデル"""

    __tablename__ = "recall_cards"

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
    user = relationship("Users", back_populates="recall_cards")
