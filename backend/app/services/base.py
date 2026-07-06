from typing import Generic, TypeVar
from ..repositories.base import BaseRepository

ModelType = TypeVar("ModelType", bound=dict)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)

class BaseService(Generic[ModelType, RepositoryType]):
    def __init__(self, repository: RepositoryType) -> None:
        self.repository = repository

    async def get_by_id(self, id: str):
        return await self.repository.get_by_id(id)

    async def get_all(self):
        return await self.repository.find_all()

    async def create(self, obj: dict):
        return await self.repository.create(obj)

    async def delete(self, id: str):
        return await self.repository.delete(id)