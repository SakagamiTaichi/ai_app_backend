from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from sqlalchemy.orm import selectinload

from app.domain.practice.conversation_entity import ConversationEntity
from app.domain.practice.test_result_entity import (
    MessageScoreValueObject,
    TestResultEntity,
)
from app.domain.practice.practice_repository import PracticeRepository
from app.endpoint.practice.practice_model import MessageResponse
from app.schema.models import (
    Conversations,
    Messages,
    ConversationTestScores,
    MessageTestScores,
)


class PracticePostgresRepository(PracticeRepository):
    """PostgreSQLを使用した練習機能のリポジトリ実装"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetchAll(
        self, user_id: UUID, limit: int = 10, offset: int = 0
    ) -> List[ConversationEntity]:
        """特定ユーザーの会話セットの一覧を取得する"""
        try:
            result = await self.db.execute(
                select(Conversations)
                .options(selectinload(Conversations.messages))
                .where(Conversations.user_id == user_id)
                .order_by(desc(Conversations.created_at))
                .limit(limit)
                .offset(offset)
            )

            conversations = result.scalars().all()

            return [
                ConversationEntity(
                    id=conversation.id,  # type: ignore
                    userId=conversation.user_id,  # type: ignore
                    title=conversation.title,  # type: ignore
                    order=conversation.order,  # type: ignore
                    createdAt=conversation.created_at,  # type: ignore
                    messages=[],  # 空のリストを設定
                )
                for conversation in conversations
            ]

        except Exception as e:
            raise

    async def count_conversations(self, user_id: UUID) -> int:
        """特定ユーザーの会話セット総数を取得する"""
        try:
            from sqlalchemy import func

            result = await self.db.execute(
                select(func.count(Conversations.id)).where(
                    Conversations.user_id == user_id
                )
            )
            return result.scalar() or 0
        except Exception as e:
            raise

    async def reorder_conversations(
        self, user_id: UUID, conversation_ids: List[UUID]
    ) -> None:
        """会話セットの順序を変更する"""
        try:
            for order, conversation_id in enumerate(conversation_ids):
                await self.db.execute(
                    update(Conversations)
                    .where(Conversations.user_id == user_id)
                    .where(Conversations.id == conversation_id)
                    .values(order=order)
                )

            await self.db.commit()

        except Exception as e:
            await self.db.rollback()
            raise

    async def fetch(
        self, conversation_id: UUID, user_id: UUID
    ) -> List[MessageResponse]:
        """特定の会話セットに属するメッセージを取得する（アクセス権の確認あり）"""
        try:
            # まず会話セットの所有者を確認
            result = await self.db.execute(
                select(Conversations).where(Conversations.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()

            if not conversation or str(conversation.user_id) != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="このリソースにアクセスする権限がありません",
                )

            # メッセージを取得
            result = await self.db.execute(
                select(Messages)
                .where(Messages.conversation_id == conversation_id)
                .order_by(Messages.message_order)
            )
            messages = result.scalars().all()

            return [
                MessageResponse(
                    conversation_id=message.conversation_id,  # type: ignore
                    message_order=message.message_order,  # type: ignore
                    speaker_number=message.speaker_number,  # type: ignore
                    message_en=message.message_en,  # type: ignore
                    message_ja=message.message_ja,  # type: ignore
                    created_at=message.created_at,  # type: ignore
                )
                for message in messages
            ]

        except Exception as e:
            raise

    async def create_message(self, message: MessageResponse) -> MessageResponse:
        """メッセージを作成する"""
        try:
            new_message = Messages(
                conversation_id=message.conversation_id,
                message_order=message.message_order,
                speaker_number=message.speaker_number,
                message_en=message.message_en,
                message_ja=message.message_ja,
                created_at=message.created_at,
            )

            self.db.add(new_message)
            await self.db.commit()
            await self.db.refresh(new_message)

            return message

        except Exception as e:
            await self.db.rollback()
            raise

    async def create(self, conversation_set: ConversationEntity) -> None:
        """会話セットを作成する"""
        try:
            # 同時にメッセージも保存する
            messages = [
                Messages(
                    conversation_id=message.conversationId,
                    message_order=message.messageOrder,
                    speaker_number=message.speakerNumber,
                    message_en=message.messageEn,
                    message_ja=message.messageJa,
                    created_at=message.createdAt,
                )
                for message in conversation_set.messages  # type: ignore
            ]

            new_conversation = Conversations(
                id=conversation_set.id,
                user_id=conversation_set.userId,
                title=conversation_set.title,
                order=conversation_set.order,
                created_at=conversation_set.createdAt,
                messages=messages,
            )

            self.db.add(new_conversation)
            await self.db.commit()

        except Exception as e:
            await self.db.rollback()
            raise

    async def save_test_result(self, test_result: TestResultEntity) -> TestResultEntity:
        """テスト結果をデータベースに保存する"""
        try:
            # 会話テストスコアを保存
            conversation_score = ConversationTestScores(
                conversation_id=test_result.conversation_id,
                test_number=test_result.test_number,
                test_score=test_result.overall_score,
                is_pass=test_result.is_passing,
                created_at=test_result.created_at,
            )

            self.db.add(conversation_score)

            # メッセージごとのスコアを保存
            for score in test_result.message_scores:
                message_score = MessageTestScores(
                    conversation_id=test_result.conversation_id,
                    test_number=test_result.test_number,
                    message_order=score.message_order,
                    score=score.score,
                    user_answer=score.userAnswer,  # Save user answer
                )
                self.db.add(message_score)

            await self.db.commit()
            return test_result

        except Exception as e:
            await self.db.rollback()
            raise

    async def get_latest_test_result(
        self, conversation_id: UUID
    ) -> Optional[TestResultEntity]:
        """指定された会話の最新のテスト結果を取得する"""
        try:
            # 最新のテスト結果を取得（メッセージスコアも含めて）
            result = await self.db.execute(
                select(ConversationTestScores)
                .options(selectinload(ConversationTestScores.message_scores))
                .where(ConversationTestScores.conversation_id == conversation_id)
                .order_by(desc(ConversationTestScores.test_number))
                .limit(1)
            )
            latest_test = result.scalar_one_or_none()

            if not latest_test:
                return None

            # メッセージスコアのリストを作成
            message_scores = []
            for item in latest_test.message_scores:
                # メッセージの詳細を取得
                msg_result = await self.db.execute(
                    select(Messages)
                    .where(Messages.conversation_id == conversation_id)
                    .where(Messages.message_order == item.message_order)
                )
                msg = msg_result.scalar_one_or_none()

                if msg:
                    score = MessageScoreValueObject(
                        message_order=item.message_order,
                        score=item.score,
                        isCorrect=item.score >= 90.0,
                        userAnswer=item.user_answer,  # Retrieve user answer
                        correctAnswer=msg.message_en,  # type: ignore
                    )
                    message_scores.append(score)

            # TestResultエンティティを作成して返す
            return TestResultEntity(
                conversation_id=latest_test.conversation_id,  # type: ignore
                test_number=latest_test.test_number,  # type: ignore
                message_scores=message_scores,
                created_at=latest_test.created_at,  # type: ignore
            )

        except Exception as e:
            raise
