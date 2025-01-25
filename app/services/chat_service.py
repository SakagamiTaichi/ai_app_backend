
import time
import json
from typing import AsyncGenerator
from langsmith.client import Client
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_postgres import PGVector
from app.core.config import settings

class RagChatService:
    def __init__(self):
        # Initialize LangSmith client
        self.client = Client()

        # Initialize vector store
        self.vector_store = PGVector(
            async_mode=True,
            connection=settings.ASYNC_DATABASE_URL,
            embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
            collection_metadata={"description": "Document embeddings"},
            use_jsonb=True,
            create_extension=False,
            engine_args = {
                           "pool_size": 10,  # 最大接続数
                           "max_overflow": 2,  # 追加で許可する接続数
                           "pool_timeout": 30,  # 接続待ちのタイムアウト（秒）
                           "pool_recycle": 1800,  # 接続を再利用する時間（秒）
                           "connect_args": {"statement_cache_size": 0}  # prepared statementsのキャッシュを無効化

                          }
        )

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,    
            temperature=settings.TEMPERATURE,
            streaming=True
        )

        self.rag_prompt = ChatPromptTemplate.from_template('''
            以下の文脈を踏まえて、システムプロンプトに従って質問に回答してください。

            文脈: {context}

            質問：{question}
        ''')

    def _format_docs(self, docs):
        """Retrieved documents をフォーマットする"""
        return "\n\n".join(doc.page_content for doc in docs)

    def format_sse_message(self, data: str) -> str:
        return f"data: {json.dumps({'content': data})}\n\n"

    async def stream_response(self, user_input: str) -> AsyncGenerator[str, None]:

        # Setup retriever with MMR search
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 4,
                'score_threshold': 0.7,
                "fetch_k": 20,
                "lambda_mult": 0.3
            }
        )


        # Create RAG chain
        rag_chain = (
            {
                "context": retriever | self._format_docs,
                "question": RunnablePassthrough()
            }
            | self.rag_prompt
            | self.llm
        )

        # Stream the response
        async for chunk in rag_chain.astream(user_input):
            if chunk.content:
                time.sleep(0.05)  # Rate limiting
                yield self.format_sse_message(chunk.content)

        yield "event: close\ndata: Stream ended\n\n"