from fastapi import APIRouter

from . import rank

routes = APIRouter()
routes.include_router(rank.app)
