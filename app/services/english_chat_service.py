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
import difflib
import re
from typing import List
from app.core.config import settings
from app.repositories.english_repository import EnglishRepository
from app.schemas.english_chat import ConversationSet, Message, MessageTestResult, MessageTestResultSummary, RecallTestRequestModel

class EnglishChatService:
    def __init__(self, repository: EnglishRepository):
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

    async def get_conversation_sets(self, user_id: str) -> List[ConversationSet]:
        """ユーザーの会話セットを取得する"""
        return await self.repository.get_conversation_sets(user_id)
    
    async def get_messages(self, set_id: UUID, user_id: str) -> List[Message]:
        """会話セットのチャット履歴を取得する（アクセス権の確認あり）"""
        return await self.repository.get_messages(set_id, user_id)
    
    async def create_conversation_set(self, title: str, user_id: str) -> ConversationSet:
        """新しい会話セットを作成する"""
        conversation_set = ConversationSet(
            id=uuid4(),
            user_id=UUID(user_id),
            title=title,
            created_at=datetime.now()
        )
        
        return await self.repository.create_conversation_set(conversation_set)
    
    async def create_message(self, set_id: UUID, message_order: int, 
                             speaker_number: int, message_en: str, 
                             message_ja: str) -> Message:
        """新しいメッセージを作成する"""
        message = Message(
            set_id=set_id,
            message_order=message_order,
            speaker_number=speaker_number,
            message_en=message_en,
            message_ja=message_ja,
            created_at=datetime.now()
        )
        
        return await self.repository.create_message(message)
    
    async def post_test_results(self, user_id: str, request: RecallTestRequestModel) -> MessageTestResultSummary:
        """
        ユーザーの英語解答と正解を比較して結果を返す
        - 余分な単語には取り消し線を付ける
        - 不足している単語は赤文字で表示する
        - 類似度を計算する
        """
        result :List[MessageTestResult] = []
        for req in request.answers:
            # ユーザーの解答と正解を取得
            user_answer = req.user_answer.strip()
            correct_answer = req.correct_answer.strip()
        
            # 単語とトークン(句読点など)に分割
            def tokenize(text : str) -> List[str]:
                return re.findall(r'\b[\w\']+\b|[.,;!?]|\S', text)
            
            user_tokens = tokenize(user_answer)
            correct_tokens = tokenize(correct_answer)
        
            # トークンレベルでの差分を取得
            matcher = difflib.SequenceMatcher(None, user_tokens, correct_tokens)
            diff_blocks = matcher.get_opcodes()
        
            # HTMLにマークアップ
            user_html, correct_html = self._generate_diff_html(diff_blocks, user_tokens, correct_tokens)
        
            # 類似度を計算
            similarity = matcher.ratio()
        
            # 正解かどうかを判定（類似度が0.9以上なら正解）
            is_correct = similarity >= 0.9
        
            # 結果を作成
            result.append(
                MessageTestResult(
                    user_answer=user_html,  # スキーマ定義のとおりuser_anserという名前
                    correct_answer=correct_html,
                    is_correct=is_correct,
                    similarity_to_correct=round(similarity, 2)*100
                )
            )
        
        # サマリーを作成
        summary = MessageTestResultSummary(
            # 正解率の平均
            correct_rate = sum(r.similarity_to_correct for r in result) / len(result) if len(result) else 0,
            result=result,
            last_correct_rate=0.0  # 固定値
        )
    
        return summary

    def _generate_diff_html(self, diff_blocks : List, user_tokens : List, correct_tokens :List):
        """差分に基づいてHTMLマークアップを生成する"""
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
    
        # トークンを連結する際に適切なスペースを入れる
        def join_tokens(tokens :List[str]) -> str:
            result = ""
            for i, token in enumerate(tokens):
                # 句読点の前にはスペースを入れない
                if i > 0 and not re.match(r'[.,;!?]', token):
                    result += " "
                result += token
            return result
    
        return join_tokens(user_html), join_tokens(correct_html)