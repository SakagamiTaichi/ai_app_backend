import time
from typing import AsyncGenerator
import json
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from app.core.config import settings
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser

class ChatService:
    def __init__(self):
        self.SYSTEM_MESSAGE = """あなたは「ずんだもん」という名前の妖精です。
緑色の髪をした小さな妖精のような見た目で、「ずんだ餅」がモチーフとなっています。
以下のルールに従って応答してください：
1. 語尾に「なのだ」や「のだ」を付けることが多い。
2. 可愛らしくて元気な性格
3. 自然な日本語になるように気をつけてください"""

        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,    
            temperature=settings.TEMPERATURE,
            streaming=True
        )
        self.output_parser = StrOutputParser()

    def format_sse_message(self, data: str) -> str:
        return f"data: {json.dumps({'content': data})}\n\n"

    async def stream_response(self, user_input: str) -> AsyncGenerator[str, None]:
        messages = [
            SystemMessage(content=self.SYSTEM_MESSAGE),
            HumanMessage(content=user_input)
        ]

        async for chunk in self.llm.astream(messages):
            if chunk.content:
                # 0.1秒待機
                time.sleep(0.1)
                yield self.format_sse_message(chunk.content)
              
        yield "event: close\ndata: Stream ended\n\n"
