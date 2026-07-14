from typing import Generic, TypeVar
from ..repositories.base import BaseRepository
from datetime import date, time
from ..helper.datetime_to_string import convert_datetime_to_string

ModelType = TypeVar("ModelType", bound=dict)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)

class BaseService(Generic[ModelType, RepositoryType]):
    def __init__(self, repository: RepositoryType) -> None:
        self.repository = repository

    async def get_by_id(self, id: str):
        item = await self.repository.get_by_id(id)
        return self._convert_to_response(item)
        
    async def get_all(self):
        items = await self.repository.find_all()
        return [self._convert_to_response(item) for item in items]

    async def create(self, obj: dict):
        return await self.repository.create(obj)

    async def delete(self, id: str):
        return await self.repository.delete(id)
    
    def _convert_to_response(self, availability_doc: dict) -> dict:
        if not availability_doc:
            return None
        if "_id" in availability_doc:
            availability_doc["id"] = str(availability_doc.pop("_id"))
        return availability_doc

    def _convert_datetime_to_string(self, data: dict) -> dict:
        return convert_datetime_to_string(data)