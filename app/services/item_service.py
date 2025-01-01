from typing import List, Optional
from app.schemas.item import ItemCreate, ItemResponse

class ItemService:
    def __init__(self):
        # メモリ内でデータを保持する簡易的な実装
        self._items = []
        self._counter = 0

        # デモデータの作成
        self.create_item(ItemCreate(name="item1", price=100))
        self.create_item(ItemCreate(name="item2", price=200))


    def create_item(self, item: ItemCreate) -> ItemResponse:
        self._counter += 1
        item_dict = item.model_dump()
        item_dict["id"] = self._counter
        self._items.append(item_dict)
        return ItemResponse(**item_dict)

    def get_items(self) -> List[ItemResponse]:
        return [ItemResponse(**item) for item in self._items]

    def get_item(self, item_id: int) -> Optional[ItemResponse]:
        for item in self._items:
            if item["id"] == item_id:
                return ItemResponse(**item)
        return None