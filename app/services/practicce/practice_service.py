import time
import json
from datetime import datetime
from typing import AsyncGenerator, Dict, List
from uuid import UUID, uuid4

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
import re
from typing import List
from app.core.config import settings
from app.domain.practice.conversation import ConversationEntity
from app.domain.practice.practice_repository import PracticeRepository
from app.domain.practice.test_result import MessageScore, TestResult
from app.model.practice.practice import Conversation, ConversationsResponse, Message, MessageTestResult, MessageTestResultSummary, RecallTestRequest


class PracticeService:
    def __init__(self, repository: PracticeRepository):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,    
            temperature=settings.TEMPERATURE,
            streaming=True
        )

        self.message_store: Dict[str, BaseChatMessageHistory] = {}
        self.repository = repository
        
        # Define system prompt for English teaching assistant
        SYSTEM_PROMPT = """You are an English chat AI."""
        # より詳細なプロンプトは元のコードと同じように記述できます
        
        # プロンプトテンプレートの定義
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("""Please responde to :{input}""")
        ])

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """セッション用のチャット履歴を取得または作成する"""
        if session_id not in self.message_store:
            self.message_store[session_id] = ChatMessageHistory()
        return self.message_store[session_id]

    def format_sse_message(self, data: str) -> str:
        """Server-Sent Events用にメッセージをフォーマットする"""
        return f"data: {json.dumps({'content': data})}\n\n"
    
    async def stream_response(self, user_input: str, session_id: str) -> AsyncGenerator[str, None]:
        """会話履歴付きのストリーミングレスポンスを生成する"""
        try:
            # 1. まずプロンプトとLLMを組み合わせる（メッセージ形式を保持）
            prompt_and_llm = self.prompt | self.llm
        
            # 2. 履歴管理を追加
            chain_with_history = RunnableWithMessageHistory(
                prompt_and_llm,
                self.get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
            )
        
            # 3. 最後に文字列出力パーサーを追加
            final_chain = chain_with_history | StrOutputParser()

            # レスポンスをストリーミング
            async for chunk in final_chain.astream(
                {"input": user_input},
                config={"configurable": {"session_id": session_id}}
            ):
                if chunk:
                    time.sleep(0.05)  # レート制限
                    yield self.format_sse_message(chunk)

            yield "event: close\ndata: Stream ended\n\n"
        
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            yield self.format_sse_message(error_message)
            yield "event: close\ndata: Stream ended with error\n\n"

    async def get_conversations(self, user_id: str) -> ConversationsResponse:
        """ユーザーの会話一覧を取得する"""
        
        entities: List[ConversationEntity]= await self.repository.get_conversations(user_id)
        
        conversations = [
        Conversation(
            id=entity.id,
            user_id=entity.user_id,
            title=entity.title,
            created_at=entity.created_at
        )
        for entity in entities
    ]
        # ConversationResponseを作成して返す
        return ConversationsResponse(conversations=conversations)

    
    async def get_conversation(self, conversation_id: UUID, user_id: str) -> List[Message]:
        """会話セットのメッセージ一覧を取得する"""
        return await self.repository.get_conversation(conversation_id, user_id)
    
    async def create_conversation_set(self, title: str, user_id: str) -> Conversation:
        """新しい会話セットを作成する"""
        conversation_set = Conversation(
            id=uuid4(),
            user_id=UUID(user_id),
            title=title,
            created_at=datetime.now()
        )
        
        return await self.repository.create_conversation_set(conversation_set)
    
    async def create_message(self, conversation_id: UUID, message_order: int, 
                             speaker_number: int, message_en: str, 
                             message_ja: str) -> Message:
        """新しいメッセージを作成する"""
        message = Message(
            conversation_id=conversation_id,
            message_order=message_order,
            speaker_number=speaker_number,
            message_en=message_en,
            message_ja=message_ja,
            created_at=datetime.now()
        )

        return await self.repository.create_message(message)
    
    # トークンを連結する際に適切なスペースを入れる
    @staticmethod
    def join_tokens(tokens :List[str]) -> str:
        result = ""
        for i, token in enumerate(tokens):
            # 句読点の前にはスペースを入れない
            if i > 0 and not re.match(r'[.,;!?]', token):
                result += " "
            result += token
        return result

    def _generate_diff_html(self, user_tokens : List[str], correct_tokens :List[str]):
        """差分に基づいてHTMLマークアップを生成する"""
        diff_blocks = MessageScore.get_diff_blocks(user_tokens, correct_tokens)
        user_html = []
        correct_html = []
        for tag, i1, i2, j1, j2 in diff_blocks:
            if tag == 'equal':
                # 両方に存在するトークン
                for k in range(i1, i2):
                    user_html.append(user_tokens[k])
                for k in range(j1, j2):
                    correct_html.append(correct_tokens[k])
            elif tag == 'delete':
                # ユーザーの解答にあって正解にないトークン（余分なトークン）
                for k in range(i1, i2):
                    user_html.append(f'<del>{user_tokens[k]}</del>')
            elif tag == 'insert':
                # 正解にあってユーザーの解答にないトークン（不足しているトークン）
                for k in range(j1, j2):
                    correct_html.append(f'<span style="color:red">{correct_tokens[k]}</span>')
            elif tag == 'replace':
                    # 置換されたトークン
                    for k in range(i1, i2):
                        user_html.append(f'<del>{user_tokens[k]}</del>')
                    for k in range(j1, j2):
                        correct_html.append(f'<span style="color:red">{correct_tokens[k]}</span>')
        return self.join_tokens(user_html), self.join_tokens(correct_html)
    
    async def post_test_results(self, user_id: str, request: RecallTestRequest) -> MessageTestResultSummary:
        """テスト結果を処理し、データベースに保存する"""
        try:
            # リクエストの会話IDから会話セットを取得
            conversation = await self.repository.get_conversation(request.conversation_id, user_id)

            # 前回のテスト結果を取得
            last_test_result = await self.repository.get_latest_test_result(request.conversation_id)

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
                answers.append({
                'message_order': message.message_order,
                'user_answer': request.answers[message.message_order - 1].user_answer,
                'correct_answer': message.message_en
            })
            
            # ドメインエンティティを作成
            test_result = TestResult.factory(
                conversation_id=request.conversation_id,
                test_number=test_number,
                answers=answers
            )
            
            # テスト結果をデータベースに保存
            saved_result = await self.repository.save_test_result(test_result)
            
            result_items = []
            for score in test_result.message_scores:
                # ユーザーの解答と正解をHTMLとしてフォーマット
                user_html, correct_html =  self._generate_diff_html( score.get_tokenized_user_answer(), score.get_tokenized_correct_answer())
                
                # 前回のスコアを検索
                last_score = None
                if last_test_result:
                    last_score = last_test_result.message_scores[score.message_order - 1].score
                
                result_items.append(
                    MessageTestResult(
                        message_order=score.message_order,
                        user_answer=user_html,
                        correct_answer=correct_html,
                        is_correct=score.is_correct,
                        similarity_to_correct=score.score,
                        last_similarity_to_correct=last_score
                    )
                )
            
            return MessageTestResultSummary(
                correct_rate=test_result.overall_score(),
                last_correct_rate=last_test_result.overall_score() if last_test_result else None,
                result=result_items
            )
            
        except Exception as e:
            print(f"Error processing test results: {str(e)}")
            raise