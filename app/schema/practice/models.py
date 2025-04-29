import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKeyConstraint, String, Integer, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class ConversationModel(Base):
    __tablename__ = "en_conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    

    # リレーションシップ
    messages = relationship("MessageModel", back_populates="conversation")
    test_scores = relationship("ConversationTestScoreModel", back_populates="conversation")
    user = relationship("UserModel", back_populates="conversations")


class MessageModel(Base):
    __tablename__ = "en_messages"
    
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("en_conversations.id"), primary_key=True)
    message_order = Column(Integer, primary_key=True)
    speaker_number = Column(Integer, nullable=False)
    message_en = Column(String, nullable=False)
    message_ja = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # リレーションシップ
    conversation = relationship("ConversationModel", back_populates="messages")


class ConversationTestScoreModel(Base):
    __tablename__ = "en_conversation_test_scores"
    
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("en_conversations.id"), primary_key=True)
    test_number = Column(Integer, primary_key=True)
    test_score = Column(Float, nullable=False)
    is_pass = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # リレーションシップ
    conversation = relationship("ConversationModel", back_populates="test_scores")
    message_scores = relationship("MessageTestScoreModel", back_populates="test")


class MessageTestScoreModel(Base):
    __tablename__ = "en_message_test_scores"
    
    conversation_id = Column(UUID(as_uuid=True), primary_key=True)
    test_number = Column(Integer, primary_key=True)
    message_order = Column(Integer, primary_key=True)
    score = Column(Float, nullable=False)
    
    __table_args__ = (
        ForeignKeyConstraint(
            ["conversation_id", "test_number"],
            ["en_conversation_test_scores.conversation_id", "en_conversation_test_scores.test_number"]
        ),
    )
    
    # リレーションシップ
    test = relationship("ConversationTestScoreModel", back_populates="message_scores")