# from fastapi import APIRouter, HTTPException
# from fastapi.responses import StreamingResponse
# from app.services.chat_service import RagChatService

# router = APIRouter(prefix="/chat", tags=["chat"])
# chat_service = RagChatService()

# @router.get("/stream")
# async def chat_stream(message: str,session_id : str) -> StreamingResponse:
#     try:
#         return StreamingResponse(
#             chat_service.stream_response(message,session_id),
#             media_type="text/event-stream"
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))