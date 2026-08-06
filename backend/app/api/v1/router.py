from fastapi import APIRouter
from app.api.v1.routes import query, verify, replay, graph

api_router = APIRouter()

api_router.include_router(
    query.router,
    tags=["Query"],
)

api_router.include_router(
    verify.router,
    tags=["Verification"],
)

api_router.include_router(
    replay.router,
    tags=["Replay"],
)

api_router.include_router(
    graph.router,
    tags=["Graph"],
)