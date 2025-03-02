# from fastapi import APIRouter, HTTPException
# from app.services.memory_service import MemoryService

# router = APIRouter(prefix="/memory", tags=["memory"])
# service = MemoryService()
    
    
# @router.get("/memory")
# async def memory(question: str) -> str:
#     try:
#         return await service.getChat(question)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))