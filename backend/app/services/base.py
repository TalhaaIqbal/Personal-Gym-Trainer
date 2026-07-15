from ..repositories.base import BaseRepository
from ..helper.datetime_to_string import convert_datetime_to_string

class BaseService[ModelType: dict, RepositoryType: BaseRepository]:
    def __init__(self, repository: RepositoryType) -> None:
        self.repository = repository

    async def get_by_id(self, id: str) -> ModelType | None:
        item = await self.repository.get_by_id(id)
        return self._convert_to_response(item)
        
    async def get_all(self) -> list[ModelType]:
        items = await self.repository.find_all()
        return [self._convert_to_response(item) for item in items]

    async def create(self, obj: ModelType):
        return await self.repository.create(obj)

    async def delete(self, id: str):
        return await self.repository.delete(id)
    
    def _convert_to_response(self, availability_doc: ModelType) -> ModelType | None:
        if not availability_doc:
            return None
        if "_id" in availability_doc:
            availability_doc["id"] = str(availability_doc.pop("_id"))
        return availability_doc

    def _convert_datetime_to_string(self, data: ModelType) -> ModelType:
        return convert_datetime_to_string(data)