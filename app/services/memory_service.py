# from app.core.config import settings
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI
# from supabase import create_client
# from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain_core.messages import SystemMessage
# from langchain_core.prompts.chat import (
#     ChatPromptTemplate,
#     HumanMessagePromptTemplate,
#     MessagesPlaceholder,
# )
# from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain_core.chat_history import BaseChatMessageHistory
# from langchain_core.runnables.history import RunnableWithMessageHistory



# class MemoryService:

#     def __init__(self):

#         self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
#         self.llm = ChatOpenAI(
#             model=settings.OPENAI_MODEL,
#             temperature=settings.TEMPERATURE,
#             streaming=True
#         )
        
#         self.store = {}
    
#     def get_session_history(self,session_id: str) -> BaseChatMessageHistory:
#         if session_id not in self.store:
#             self.store[session_id] = ChatMessageHistory()
#         return self.store[session_id]


#     async def  getChat(self, question: str) -> str:
        
#         template_messages = [
#             SystemMessage(content="You are a helpful assistant."),
#             MessagesPlaceholder(variable_name="chat_history"),
#             HumanMessagePromptTemplate.from_template("{question}"),
#         ]

#         prompt_template = ChatPromptTemplate.from_messages(template_messages)

#         chain = prompt_template|self.llm|StrOutputParser()

#         with_message_history = RunnableWithMessageHistory(
#                     chain,
#                     self.get_session_history,
#                     input_messages_key="question",
#                     history_messages_key="chat_history",
#                     #output_messages_key="output",
#                   )
        
#         output = with_message_history.invoke(input={"question":question},
#                               config={"configurable": {"session_id": "123"}})


#         return output