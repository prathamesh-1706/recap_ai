from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="RECAP API",
    description="Revenue Intelligence & Recovery Agent",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(router)
