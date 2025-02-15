from datetime import datetime
import time
import json
from typing import AsyncGenerator, Dict, Any, List
from uuid import UUID
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from supabase import create_client
from app.core.config import settings
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

from app.schemas.english_chat import ConversationSet, Message

class EnglishChatService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,    
            temperature=settings.TEMPERATURE,
            streaming=True
        )

        self.message_store: Dict[str, BaseChatMessageHistory] = {}
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        # Define system prompt for English teaching assistant
        SYSTEM_PROMPT = """You are an English chat AI."""
#         SYSTEM_PROMPT = """You are an English learning support AI designed to help non-native speakers improve their English communication skills. Your role is to engage with users naturally while helping them develop more native-like English expression.

# Core Functions:
# 1. Always respond in English, regardless of the input language
# 2. Analyze the user's input and provide a more natural English version
# 3. Explain the reasons for your suggested improvements

# For each response, follow this format:
# 1. First, respond naturally to the content of the user's message
# 2. Then say "Here's a more natural way to express your message:" and provide the improved version
# 3. Finally, say "Here's why I suggested these changes:" and explain your improvements

# Guidelines for corrections:
# - Focus on making the language more idiomatic and native-like
# - Consider context-appropriate vocabulary and expressions
# - Preserve the user's intended tone and style
# - Explain idioms and colloquialisms when introducing them
# - Note when expressions are region-specific (US, UK, etc.)
# - Maintain a supportive and encouraging tone

# Remember to:
# - Focus on practical, high-frequency improvements
# - Provide alternatives when multiple natural expressions are possible
# - Maintain user confidence while suggesting improvements
# - Keep explanations clear and concise"""

        # Updated prompt template with the system prompt
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("""Please responde to :{input}""")
            # HumanMessagePromptTemplate.from_template("""Please analyze and improve the following English expression, providing both corrections and explanations:{input}""")
        ])

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get or create chat history for a session"""
        if session_id not in self.message_store:
            self.message_store[session_id] = ChatMessageHistory()
        return self.message_store[session_id]

    def format_sse_message(self, data: str) -> str:
        """Format message for Server-Sent Events"""
        return f"data: {json.dumps({'content': data})}\n\n"

    async def stream_response(self, user_input: str, session_id: str) -> AsyncGenerator[str, None]:
        """Generate streaming response with conversation history"""
        try:
            async def process_input(input_dict: Dict[str, Any]) -> Dict[str, Any]:
                """Process input and chat history"""
                user_question = input_dict["input"]
                chat_history = input_dict.get("chat_history", [])
                
                return {
                    "input": user_question,
                    "chat_history": chat_history,
                }

            retrieval_chain = RunnableLambda(process_input)
            response_chain = (
                self.prompt 
                | self.llm 
                | StrOutputParser()
            )
            rag_chain = retrieval_chain | response_chain

            chain_with_history = RunnableWithMessageHistory(
                rag_chain,
                self.get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
            )

            async for chunk in chain_with_history.astream(
                {"input": user_input},
                config={"configurable": {"session_id": session_id}}
            ):
                if chunk:
                    time.sleep(0.05)  # Rate limiting
                    yield self.format_sse_message(chunk)

            yield "event: close\ndata: Stream ended\n\n"
            
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            yield self.format_sse_message(error_message)
            yield "event: close\ndata: Stream ended with error\n\n"

    def get_conversation_sets(self) -> List[ConversationSet]:

        """Get chat histories for all sessions"""
        try:
            response = self.client.table('en_conversation_sets') \
                .select('*') \
                .order('created_at', desc=True) \
                .execute()
    
            # レスポンスから履歴リストを作成
            sets = [
                ConversationSet(
                    id=UUID(record['id']),
                    title=record['title'],
                    created_at=datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
                )
                for record in response.data
            ]

            return sets
    
        except Exception as e:
            print(f"Error fetching chat histories: {str(e)}")
            raise

    def get_messages(self, set_id: UUID) -> List[Message]:
        """Get chat history for a conversation set"""
        try:
            response = self.client.table('en_messages') \
                .select('*') \
                .eq('set_id', str(set_id)) \
                .order('message_order') \
                .execute()
    
            # レスポンスからメッセージリストを作成
            messages = [
                Message(
                    set_id=UUID(record['set_id']),
                    message_order=record['message_order'],
                    speaker_number=record['speaker_number'],
                    message_en=record['message_en'],
                    message_ja=record['message_ja'],
                    created_at=datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
                )
                for record in response.data
            ]

            return messages
        
        except Exception as e:
            print(f"Error fetching chat history: {str(e)}")
            raise
    