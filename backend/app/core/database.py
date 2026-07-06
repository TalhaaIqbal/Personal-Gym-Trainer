import asyncio
from pymongo.asynchronous.mongo_client import AsyncMongoClient
from .config import settings
from contextlib import asynccontextmanager
from fastapi import FastAPI

client = AsyncMongoClient(settings.MONGO_URL)
db = client[settings.MONGO_DB_NAME]

if __name__ == "__main__":
    asyncio.run(get_db())