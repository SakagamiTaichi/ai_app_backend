from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.item import ItemCreate, ItemResponse
from app.services.item_service import ItemService

router = APIRouter(prefix="/items", tags=["items"])
item_service = ItemService()

@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate) -> ItemResponse:
    return item_service.create_item(item)

@router.get("/", response_model=List[ItemResponse])
def get_items() -> List[ItemResponse]:
    return item_service.get_items()

@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int) -> ItemResponse:
    item = item_service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item