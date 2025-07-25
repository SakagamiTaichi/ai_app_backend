from datetime import datetime
from typing import List
from uuid import UUID, uuid4
import re
from typing import List

from pydantic import ValidationError

from app.core.app_exception import BadRequestError, ConflictError, NotFoundError
from app.domain.practice.conversation_entity import ConversationEntity, MessageEntity
from app.domain.practice.practice_api_repotiroy import PracticeApiRepository
from app.domain.practice.practice_repository import PracticeRepository
from app.domain.practice.test_result_entity import (
    MessageScoreValueObject,
    TestResultEntity,
)
from app.domain.recall.reacall_card_entity import RecallCardEntity
from app.domain.recall.recall_card_repository import RecallCardrepository
from app.endpoint.practice.practice_model import (
    Conversation,
    ConversationCreatedResponse,
    ConversationResponse,
    ConversationSetCreateRequest,
    ConversationsResponse,
    MessageResponse,
    MessageTestResult,
    MessageTestResultSummary,
    RecallTestRequest,
)


class PracticeService:
    def __init__(
        self,
        practiceRepository: PracticeRepository,
        recallCardRepository: RecallCardrepository,
        apiRepository: PracticeApiRepository,
    ):
        # 何もしない
        self.dbRepository = practiceRepository
        self.dbRecallCardRepository = recallCardRepository
        self.apiRepository = apiRepository

    async def ai_registration(
        self, user_id: UUID, request: ConversationSetCreateRequest
    ) -> ConversationCreatedResponse:
        """AIによって会話を登録する"""
        try:
            # ユーザーの会話セットを取得
            conversation_set = await self.dbRepository.fetchAll(user_id)

            # 全ての会話セットの中から最大の順番を設定する
            order = conversation_set[0].order + 1 if conversation_set else 0

            # AIによるメッセージ一覧の取得
            valueObject = await self.apiRepository.get_generated_conversation(
                request.user_phrase
            )

            conversation_id = uuid4()
            now = datetime.now()

            conversation_set = ConversationEntity(
                id=conversation_id,
                userId=user_id,
                title=valueObject.title,
                order=order,
                createdAt=now,
                messages=[
                    MessageEntity(
                        conversationId=conversation_id,
                        messageOrder=i + 1,
                        speakerNumber=i % 2,
                        messageEn=message.messageEn,
                        messageJa=message.messageJa,
                        createdAt=now,
                    )
                    for i, message in enumerate(valueObject.messages)  # type: ignore
                ],
            )

            # データベースに保存
            await self.dbRepository.create(conversation_set)

            # 暗記カードに保存
            recall_cards = [
                RecallCardEntity(
                    recallCardId=uuid4(),
                    userId=user_id,
                    question=message.messageJa,
                    answer=message.messageEn,
                    correctPoint=0,
                    reviewDeadline=datetime.now(),
                )
                for message in valueObject.messages
            ]
            await self.dbRecallCardRepository.createAll(recall_cards)

            # Pydanticモデルを返す
            return ConversationCreatedResponse(id=conversation_id)
        except ValidationError as e:
            # バリデーションエラーの処理
            raise BadRequestError(detail=e.title)
        except Exception as e:
            # エラーハンドリング
            raise

    async def get_conversations(
        self, user_id: UUID, limit: int = 10, offset: int = 0
    ) -> ConversationsResponse:
        """ユーザーの会話一覧を取得する"""
        try:
            # ユーザーの会話一覧を取得
            entities: List[ConversationEntity] = await self.dbRepository.fetchAll(
                user_id, limit, offset
            )
            # 総数を取得
            total_count = await self.dbRepository.count_conversations(user_id)

            conversations = [
                Conversation(
                    id=entity.id,
                    user_id=entity.userId,
                    title=entity.title,
                    order=entity.order,
                    created_at=entity.createdAt,
                )
                for entity in entities
            ]
            # ConversationResponseを作成して返す
            return ConversationsResponse(
                conversations=conversations,
                total_count=total_count,
                limit=limit,
                offset=offset,
            )
        except ValidationError as e:
            # バリデーションエラーの処理
            raise BadRequestError(detail=e.title)
        except Exception as e:
            # エラーハンドリング
            raise

    async def reorder_conversations(
        self, user_id: UUID, conversation_ids: List[UUID]
    ) -> None:
        try:
            # ユーザーの会話一覧を取得
            conversations = await self.dbRepository.fetchAll(user_id)

            # 指定された会話セットがユーザーの会話セットに存在するか確認
            for conversation_id in conversation_ids:
                if not any(
                    conversation.id == conversation_id for conversation in conversations
                ):
                    raise NotFoundError(
                        detail=f"指定された会話はユーザーの会話セットに存在しません"
                    )
            # 各会話セットの新しい順序を設定
            await self.dbRepository.reorder_conversations(user_id, conversation_ids)
        except ValidationError as e:
            # バリデーションエラーの処理
            raise BadRequestError(detail=e.title)
        except Exception as e:
            # エラーハンドリング
            raise

    async def get_conversation(
        self, conversation_id: UUID, user_id: UUID
    ) -> ConversationResponse:
        """会話セットのメッセージ一覧を取得する"""
        try:
            entities: List[MessageResponse] = await self.dbRepository.fetch(
                conversation_id, user_id
            )
            messages = [
                MessageResponse(
                    conversation_id=entity.conversation_id,
                    message_order=entity.message_order,
                    speaker_number=entity.speaker_number,
                    message_en=entity.message_en,
                    message_ja=entity.message_ja,
                    created_at=entity.created_at,
                )
                for entity in entities
            ]
            # ConversationResponseを作成して返す
            return ConversationResponse(messages=messages)
        except ValidationError as e:
            # バリデーションエラーの処理
            raise BadRequestError(detail=e.title)
        except Exception as e:
            # エラーハンドリング
            raise

    # async def create_conversation_set(self, title: str, user_id: str) -> None:
    #     """新しい会話セットを作成する"""
    #     conversation_set = Conversation(
    #         id=uuid4(),
    #         user_id=UUID(user_id),
    #         title=title,
    #         order=0,  # デフォルトの順序を設定
    #         created_at=datetime.now()
    #     )

    #     return await self.dbRepository.create_conversation_set(conversation_set)

    async def create_message(
        self,
        conversation_id: UUID,
        message_order: int,
        speaker_number: int,
        message_en: str,
        message_ja: str,
    ) -> MessageResponse:
        """新しいメッセージを作成する"""
        message = MessageResponse(
            conversation_id=conversation_id,
            message_order=message_order,
            speaker_number=speaker_number,
            message_en=message_en,
            message_ja=message_ja,
            created_at=datetime.now(),
        )

        return await self.dbRepository.create_message(message)

    # トークンを連結する際に適切なスペースを入れる
    @staticmethod
    def join_tokens(tokens: List[str]) -> str:
        result = ""
        for i, token in enumerate(tokens):
            # 句読点の前にはスペースを入れない
            if i > 0 and not re.match(r"[.,;!?]", token):
                result += " "
            result += token
        return result

    def _generate_diff_html(self, user_tokens: List[str], correct_tokens: List[str]):
        """差分に基づいてHTMLマークアップを生成する"""
        diff_blocks = MessageScoreValueObject.get_diff_blocks(
            user_tokens, correct_tokens
        )
        user_html = []
        correct_html = []
        for tag, i1, i2, j1, j2 in diff_blocks:
            if tag == "equal":
                # 両方に存在するトークン
                for k in range(i1, i2):
                    user_html.append(user_tokens[k])
                for k in range(j1, j2):
                    correct_html.append(correct_tokens[k])
            elif tag == "delete":
                # ユーザーの解答にあって正解にないトークン（余分なトークン）
                for k in range(i1, i2):
                    user_html.append(f"<del>{user_tokens[k]}</del>")
            elif tag == "insert":
                # 正解にあってユーザーの解答にないトークン（不足しているトークン）
                for k in range(j1, j2):
                    correct_html.append(
                        f'<span style="color:red">{correct_tokens[k]}</span>'
                    )
            elif tag == "replace":
                # 置換されたトークン
                for k in range(i1, i2):
                    user_html.append(f"<del>{user_tokens[k]}</del>")
                for k in range(j1, j2):
                    correct_html.append(
                        f'<span style="color:red">{correct_tokens[k]}</span>'
                    )
        return self.join_tokens(user_html), self.join_tokens(correct_html)

    async def post_test_results(
        self, user_id: UUID, request: RecallTestRequest
    ) -> MessageTestResultSummary:
        """テスト結果を処理し、データベースに保存する"""
        try:
            # リクエストの会話IDから会話セットを取得
            conversation = await self.dbRepository.fetch(
                request.conversation_id, user_id
            )

            # 前回のテスト結果を取得
            last_test_result = await self.dbRepository.get_latest_test_result(
                request.conversation_id
            )

            # 前回のテスト結果から今回のテスト番号を取得
            test_number = 1
            if last_test_result:
                test_number = last_test_result.test_number + 1

            # 取得した会話セットとユーザーの会話セットのorderが完全一致するかを確認。しない場合はエラーを返す
            if len(conversation) != len(request.answers):
                raise ConflictError(
                    detail="会話セットのメッセージ数と回答数が一致しません"
                )

            # 取得してきた会話セットとリクエストのメッセージからanswersを作成
            answers = []
            for message in conversation:
                answers.append(
                    {
                        "message_order": message.message_order,
                        "user_answer": request.answers[
                            message.message_order - 1
                        ].user_answer,
                        "correct_answer": message.message_en,
                    }
                )

            # ドメインエンティティを作成
            test_result = TestResultEntity.factory(
                conversation_id=request.conversation_id,
                test_number=test_number,
                answers=answers,
            )

            # テスト結果をデータベースに保存
            saved_result = await self.dbRepository.save_test_result(test_result)

            result_items = []
            for score in test_result.message_scores:
                # ユーザーの解答と正解をHTMLとしてフォーマット
                user_html, correct_html = self._generate_diff_html(
                    score.get_tokenized_user_answer,
                    score.get_tokenized_correct_answer,
                )

                # 前回のスコアを検索
                last_score = None
                if last_test_result:
                    last_score = last_test_result.message_scores[
                        score.message_order - 1
                    ].score

                result_items.append(
                    MessageTestResult(
                        message_order=score.message_order,
                        user_answer=user_html,
                        correct_answer=correct_html,
                        is_correct=score.isCorrect,
                        similarity_to_correct=score.score,
                        last_similarity_to_correct=last_score,
                    )
                )

            return MessageTestResultSummary(
                correct_rate=test_result.overall_score,
                last_correct_rate=(
                    last_test_result.overall_score if last_test_result else None
                ),
                result=result_items,
            )

        except ValidationError as e:
            # バリデーションエラーの処理
            raise BadRequestError(detail=e.title)
        except Exception as e:
            # エラーハンドリング
            raise
