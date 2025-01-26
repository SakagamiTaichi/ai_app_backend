import time
import json
from typing import AsyncGenerator, Dict, Any
from langsmith.client import Client
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import  RunnableLambda
from langchain_postgres import PGVector
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
from langchain_community.retrievers import TavilySearchAPIRetriever
class RagChatService:
    def __init__(self):
        # 基本的な初期化は変更なし
        self.client = Client()
        self.vector_store = PGVector(
            async_mode=True,
            connection=settings.ASYNC_DATABASE_URL,
            embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
            collection_metadata={"description": "Document embeddings"},
            use_jsonb=True,
            create_extension=False,
            engine_args = {
                "pool_size": 10,
                "max_overflow": 2,
                "pool_timeout": 30,
                "pool_recycle": 1800,
                "connect_args": {"statement_cache_size": 0}
            }
        )

        self.tavily_retriever = TavilySearchAPIRetriever(
            api_key=settings.TAVILY_API_KEY,
            k=3)

        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,    
            temperature=settings.TEMPERATURE,
            streaming=True
        )

        self.message_store: Dict[str, BaseChatMessageHistory] = {}

        # プロンプトテンプレートの定義（変更なし）
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""あなたは有能なAIアシスタントです。. 
            質問に答える際は以下の手順に従ってください:
            1. チャット履歴を確認してください
            2. 上の手順に答えが見つからない場合、コンテキストを使用して回答してください
            3. 上の手順に答えが見つからない場合、インターネットの情報を使用して回答してください
            3. 上の手順に答えが見つからない場合、できる範囲で回答してください"""),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("""
                ユーザーの質問: {input}
                コンテキスト: {context}
                インターネットの情報: {internet}
            """)
        ])

    def _format_docs(self, docs) -> str:
        """Format retrieved documents"""
        return "\n\n".join(doc.page_content for doc in docs)

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
            # レトリーバーのセットアップ
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": 4,
                    'score_threshold': 0.7,
                    "fetch_k": 20,
                    "lambda_mult": 0.3
                }
            )

            # 入力を処理する関数の定義
            async def process_input(input_dict: Dict[str, Any]) -> Dict[str, Any]:
                """
                入力とチャット履歴を処理し、必要な情報を組み合わせる
                チャット履歴はRunnableWithMessageHistoryによって自動的に提供される
                """
                # 入力文字列の取得
                user_question = input_dict["input"]
                # チャット履歴の取得（RunnableWithMessageHistoryにより提供）
                chat_history = input_dict.get("chat_history", [])
                
                # コンテキストの取得
                retrieved_docs = await retriever.ainvoke(user_question)

                # インターネットからの情報の取得
                internet = await self.tavily_retriever.ainvoke(user_question)
                
                # 必要な情報をすべて含む辞書を返す
                return {
                    "input": user_question,
                    "chat_history": chat_history,  # チャット履歴を含める
                    "context": self._format_docs(retrieved_docs),
                    "internet": internet
                }

            # 基本的なチェーンの構築
            retrieval_chain = RunnableLambda(process_input)
            response_chain = (
                self.prompt 
                | self.llm 
                | StrOutputParser()
            )
            rag_chain = retrieval_chain | response_chain

            # メッセージ履歴との統合
            chain_with_history = RunnableWithMessageHistory(
                rag_chain,
                self.get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
            )

            # レスポンスのストリーミング
            async for chunk in chain_with_history.astream(
                {"input": user_input},
                config={"configurable": {"session_id":session_id}}
            ):
                if chunk:
                    time.sleep(0.05)  # レート制限
                    yield self.format_sse_message(chunk)

            yield "event: close\ndata: Stream ended\n\n"
            
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            yield self.format_sse_message(error_message)
            yield "event: close\ndata: Stream ended with error\n\n"