from fastapi import APIRouter
from app.schemas.text_to_sql import TableData
from app.services.text_to_sql import TextToSQLService

router = APIRouter(prefix="/text-to-sql", tags=["text-to-sql"])
text_to_sql_service = TextToSQLService()

@router.get("/", response_model=TableData)
def get_text_to_sql(input: str) -> TableData:
    return text_to_sql_service.get_text_to_sql(input)
