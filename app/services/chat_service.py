import time
import json
from typing import AsyncGenerator
from langsmith.client import Client
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings

class ChatService:
    def __init__(self):
        # Initialize LangSmith client
        self.client = Client()
        
        # Pull the prompt from LangSmith
        self.system_prompt = self.client.pull_prompt(
            "chat_prompt"  # Replace with your actual prompt identifier
        )
        
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,    
            temperature=settings.TEMPERATURE,
            streaming=True
        )

    def format_sse_message(self, data: str) -> str:
        return f"data: {json.dumps({'content': data})}\n\n"

    async def stream_response(self, user_input: str) -> AsyncGenerator[str, None]:
        # Use the pulled prompt template to format the system message
        system_message = self.system_prompt.format()
        
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=user_input)
        ]

        async for chunk in self.llm.astream(messages):
            if chunk.content:
                # 0.1秒待機
                time.sleep(0.1)
                yield self.format_sse_message(chunk.content)
              
        yield "event: close\ndata: Stream ended\n\n"