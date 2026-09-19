from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Backend.app.api.routes import executions, health, workflows
from Backend.app.core.config import settings
from Backend.app.core.logging import setup_logging
from Backend.app.db.database import init_db, close_db
from Backend.app.api.routes import nodes
from Backend.app.nodes import register_nodes
from Backend.app.workflow.registry import registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    register_nodes(registry)
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(workflows.router)
app.include_router(executions.router)
app.include_router(nodes.router)


@app.get("/")
async def root():
    return {"message": "Workflow Engine API", "version": "0.1.0"}