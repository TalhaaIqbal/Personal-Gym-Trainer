from ast import Dict, List
from typing import Any, Generic, TypeVar
from bson import ObjectId 
from motor.motor_asyncio import AsyncIOMotorCollection

ModelType = TypeVar('ModelType', bound=dict)

class BaseRepository(Generic[ModelType]):
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
        result = await self.collection.find_one({"_id": ObjectId(id)})
        return result

    async def create(self, data: ModelType) -> ModelType:
        result = await self.collection.insert_one(data)
        created_doc = await self.collection.find_one({"_id": result.inserted_id})
        return created_doc
    
    async def delete(self, item_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count > 0

    async def update(self, item_id: str, data: dict) -> ModelType | None:
        result = await self.collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": data}
        )
        if result.modified_count == 0:
            return None
        return await self.get_by_id(item_id)