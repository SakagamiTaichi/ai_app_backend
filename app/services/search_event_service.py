# from unittest import result
# from langgraph.checkpoint.memory import MemorySaver
# from open_deep_research.graph import builder
# import uuid
# from app.core.config import settings
# from langgraph.types import Command
# from pydantic import BaseModel, Field
# from typing import List, Optional
# from datetime import datetime
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI

# # Pydanticモデルで出力構造を定義
# class EventInfo(BaseModel):
#     name: str = Field(description="イベント名")
#     date: str = Field(description="イベントの日付")
#     location: str = Field(description="イベントの開催場所")
#     description: str = Field(description="イベントの概要")

# class MediaCoverage(BaseModel):
#     publication: str = Field(description="掲載メディア名")
#     date: str = Field(description="掲載日")
#     url: Optional[str] = Field(description="掲載URL（利用可能な場合）")
#     summary: str = Field(description="掲載内容の概要")

# class HANAEventData(BaseModel):
#     events: List[EventInfo] = Field(description="HANAのイベント情報リスト")
#     media_coverage: List[MediaCoverage] = Field(description="メディア掲載情報リスト")

# class SearchEventService:
#     def __init__(self):
#         self.llm = ChatOpenAI(
#              model="gpt-4o",
#              temperature=0.2
#         )

#     async def get_search_event(self, event_id: str):
#         # まず通常の方法でレポートを取得
#         memory = MemorySaver()
#         graph = builder.compile(checkpointer=memory)
#         thread = {"configurable": {
#                            "thread_id": str(uuid.uuid4()),
#                            "search_api": "tavily",
#                            "planner_provider": "openai",
#                            "planner_model": "gpt-4o",
#                            "writer_provider": "openai",
#                            "writer_model": "gpt-4o",
#                            "max_search_depth": 1,
#                           }}

#         topic = "HANAという日本の音楽ガールズグループの最新のイベントの概要と日時と場所、およびメディア掲載情報を詳細に調査してください。"

#         # レポートを取得
#         result = await graph.ainvoke(
#             {"topic": topic},
#             thread,
#             stream_mode="updates",
#         )

#         # 最終的なレポートを取得
#         final_result = await graph.ainvoke(
#             Command(resume=True),
#             thread,
#         )

#         raw_report = ""
#         if isinstance(final_result, dict) and 'final_report' in final_result:
#             raw_report = final_result['final_report']
#         else:
#             # 他の可能性を確認
#             for key in final_result:
#                 if isinstance(final_result[key], dict) and 'final_report' in final_result[key]:
#                     raw_report = final_result[key]['final_report']

#         # 生のレポートからPydanticモデルにパース
#         prompt = ChatPromptTemplate.from_template(
#             """
#             以下のレポートから、HANAという日本の音楽ガールズグループに関する情報を構造化データとして抽出してください。
#             イベント情報とメディア掲載情報を分けて整理してください。

#             レポート:
#             {report}

#             必要な出力形式は以下の通りです:
#             - events: イベント情報のリスト（名前、日付、場所、概要）
#             - media_coverage: メディア掲載情報のリスト（掲載メディア、掲載日、URL、概要）
#             """
#         )

#         # 構造化出力を取得
#         chain = prompt | self.llm.with_structured_output(HANAEventData)
#         structured_data = await chain.ainvoke({"report": raw_report})

#         return structured_data
