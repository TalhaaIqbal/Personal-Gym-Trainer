from pymongo.asynchronous.mongo_client import AsyncMongoClient
from .config import settings

client = AsyncMongoClient(settings.MONGO_URL)
db = client[settings.MONGO_DB_NAME]