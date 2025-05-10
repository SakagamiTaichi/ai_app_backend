from datetime import datetime
from typing import List
from uuid import UUID, uuid4
import re
from typing import List
from app.domain.practice.conversation_entity import ConversationEntity, MessageEntity
from app.domain.practice.practice_api_repotiroy import PracticeApiRepository
from app.domain.practice.practice_repository import PracticeRepository
from app.domain.practice.test_result_entity import MessageScore, TestResultEntity
from app.model.practice.practice import (
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
        self, repository: PracticeRepository, apiRepository: PracticeApiRepository
    ):
        # 何もしない
        self.dbRepository = repository
        self.apiRepository = apiRepository

    async def ai_registration(
        self, user_id: str, request: ConversationSetCreateRequest
    ) -> ConversationCreatedResponse:
        """AIによって会話を登録する"""

        # ユーザーの会話セットを取得
        conversation_set = await self.dbRepository.get_conversations(user_id)

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
            user_id=UUID(user_id),
            title=valueObject.title,
            order=order,
            created_at=now,
            messages=[
                MessageEntity(
                    conversation_id=conversation_id,
                    message_order=i + 1,
                    speaker_number=i % 2,
                    message_en=message.message_en,
                    message_ja=message.message_ja,
                    created_at=now,
                )
                for i, message in enumerate(valueObject.messages)  # type: ignore
            ],
        )

        # データベースに保存
        await self.dbRepository.create_conversation_set(conversation_set)
        # Pydanticモデルを返す
        return ConversationCreatedResponse(id=conversation_id)

    async def get_conversations(self, user_id: str) -> ConversationsResponse:
        """ユーザーの会話一覧を取得する"""

        entities: List[ConversationEntity] = await self.dbRepository.get_conversations(
            user_id
        )

        conversations = [
            Conversation(
                id=entity.id,
                user_id=entity.user_id,
                title=entity.title,
                order=entity.order,
                created_at=entity.created_at,
            )
            for entity in entities
        ]
        # ConversationResponseを作成して返す
        return ConversationsResponse(conversations=conversations)

    async def reorder_conversations(
        self, user_id: str, conversation_ids: List[UUID]
    ) -> None:
        """会話セットの順序を変更する"""
        # ユーザーの会話一覧を取得
        conversations = await self.dbRepository.get_conversations(user_id)

        # 指定された会話セットがユーザーの会話セットに存在するか確認
        for conversation_id in conversation_ids:
            if not any(
                conversation.id == conversation_id for conversation in conversations
            ):
                raise ValueError(
                    f"会話セット {conversation_id} はユーザーの会話セットに存在しません"
                )

        # 各会話セットの新しい順序を設定
        await self.dbRepository.reorder_conversations(user_id, conversation_ids)

    async def get_conversation(
        self, conversation_id: UUID, user_id: str
    ) -> ConversationResponse:
        """会話セットのメッセージ一覧を取得する"""
        entities: List[MessageResponse] = await self.dbRepository.get_conversation(
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
        diff_blocks = MessageScore.get_diff_blocks(user_tokens, correct_tokens)
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
        self, user_id: str, request: RecallTestRequest
    ) -> MessageTestResultSummary:
        """テスト結果を処理し、データベースに保存する"""
        try:
            # リクエストの会話IDから会話セットを取得
            conversation = await self.dbRepository.get_conversation(
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
                raise ValueError("会話セットのメッセージ数と回答数が一致しません")

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
                    score.get_tokenized_user_answer(),
                    score.get_tokenized_correct_answer(),
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
                        is_correct=score.is_correct,
                        similarity_to_correct=score.score,
                        last_similarity_to_correct=last_score,
                    )
                )

            return MessageTestResultSummary(
                correct_rate=test_result.overall_score(),
                last_correct_rate=(
                    last_test_result.overall_score() if last_test_result else None
                ),
                result=result_items,
            )

        except Exception as e:
            print(f"Error processing test results: {str(e)}")
            raise
