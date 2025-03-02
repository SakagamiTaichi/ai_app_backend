import time
import json
from datetime import datetime
from typing import AsyncGenerator, Dict, List
from uuid import UUID

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

from app.core.config import settings
from app.repositories.english_repository import EnglishRepository
from app.schemas.english_chat import ConversationSet, Message

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

    async def get_conversation_sets(self) -> List[ConversationSet]:
        """全セッションのチャット履歴を取得する"""
        return await self.repository.get_conversation_sets()
    
    async def get_messages(self, set_id: UUID) -> List[Message]:
        """会話セットのチャット履歴を取得する"""
        return await self.repository.get_messages(set_id)
    
    async def create_conversation_set(self, title: str) -> ConversationSet:
        """新しい会話セットを作成する"""
        from uuid import uuid4
        
        conversation_set = ConversationSet(
            id=uuid4(),
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