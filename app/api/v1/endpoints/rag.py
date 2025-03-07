# from fastapi import APIRouter, HTTPException
# from app.schemas.rag import InformationRequest, InformationsResponse
# from app.services.rag_service import RagService

# router = APIRouter(prefix="/rag", tags=["rag"])
# rag_service = RagService()

# @router.post("/")
# async def embedding_model(infromation: InformationRequest) -> str:
#     try:
#         return rag_service.embedding_model(infromation.information)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @router.get("/", response_model=InformationsResponse)
# async def rag() -> InformationsResponse:
#     try:
#         return rag_service.get_information()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @router.get("/retriver")
# async def retriver(question: str) -> str:
#     try:
#         return rag_service.retriver(question)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))