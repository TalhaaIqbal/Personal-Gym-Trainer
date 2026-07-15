from typing import Any, Dict, List
from bson.objectid import ObjectId, InvalidId
from motor.motor_asyncio import AsyncIOMotorCollection

def _validate_object_id(id: str) -> ObjectId | None:
    if not ObjectId.is_valid(id):
        return None
    try:
        return ObjectId(id)
    except (InvalidId, ValueError, TypeError):
        return None

class BaseRepository[ModelType: dict]:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def find_one(self, filter: Dict[str, Any]) -> ModelType | None:
        result = await self.collection.find_one(filter)
        return result

    async def find_all(self) -> List[ModelType]:
        result = self.collection.find()
        all_results = await result.to_list(length=None)
        return all_results
    
    async def get_by_id(self, id: str) -> ModelType | None:
        object_id = _validate_object_id(id)
        if object_id is None:
            return None
        result = await self.collection.find_one({"_id": object_id})
        return result

    async def create(self, data: ModelType) -> ModelType:
        result = await self.collection.insert_one(data)
        created_doc = await self.collection.find_one({"_id": result.inserted_id})
        return created_doc
    
    async def delete(self, item_id: str) -> bool:
        object_id = _validate_object_id(item_id)
        if object_id is None:
            return False
        result = await self.collection.delete_one({"_id": object_id})
        return result.deleted_count > 0

    async def update(self, item_id: str, data: dict) -> ModelType | None:
        object_id = _validate_object_id(item_id)
        if object_id is None:
            return None
        result = await self.collection.update_one(
            {"_id": object_id},
            {"$set": data}
        )
        if result.modified_count == 0:
            return None
        return await self.get_by_id(item_id)