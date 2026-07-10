from .routers import base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .core.database import client

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await client.aconnect()
        print("Connected to MongoDB")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
    yield
    await client.aclose()


app = FastAPI(
    title="Personal Gym Trainer API",
    description="Personal Gym Trainer platform",
    version="1.0.0",
    lifespan=lifespan,
    debug=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(base.router)

@app.get("/")
def root():
    return {"message": "Welcome to Personal Gym Trainer API"}