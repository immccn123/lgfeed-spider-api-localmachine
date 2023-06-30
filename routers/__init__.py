from fastapi import APIRouter

from . import rank
from . import black_history
from . import tools

routes = APIRouter()
routes.include_router(rank.app)
routes.include_router(black_history.app)
routes.include_router(tools.app)
