from ..repositories.user_repository import UserRepository
from ..schemas.user_schema import UserCreate, UserUpdate
from bson import ObjectId

class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def _convert_to_response(self, user_doc: dict) -> dict:
        if not user_doc:
            return None
        user_doc["id"] = str(user_doc.pop("_id"))
        return user_doc

    async def get_all_users(self):
        users = await self.repository.find_all()
        return [self._convert_to_response(user) for user in users]

    async def get_user_by_id(self, user_id: str):
        try:
            user = await self.repository.get_by_id(user_id)
            if not user:
                return None
        except Exception:
            return None
        return self._convert_to_response(user)

    async def get_user_by_email(self, email: str):
        return await self.repository.get_by_email(email)

    async def create_user(self, user_data: UserCreate):
        existing = await self.repository.get_by_email(user_data.email)
        if existing:
            return None

        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["password"] = (user_data.password)

        created_user = await self.repository.create(user_dict)
        return self._convert_to_response(created_user)

    async def update_user(self, user_id: str, user_data: UserUpdate):
        user = await self.repository.get_by_id(user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        # if "password" in update_data:
        #     update_data["password"] = hash_password(update_data["password"])

        updated_user = await self.repository.update(user_id, update_data)
        return self._convert_to_response(updated_user)

    async def delete_user(self, user_id: str):
        return await self.repository.delete(user_id)