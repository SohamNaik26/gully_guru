from fastapi import APIRouter

# Import routers individually to avoid circular imports
from src.api.routes.users import router as users_router
from src.api.routes.players import router as players_router
from src.api.routes.games import router as games_router
from src.api.routes.transfers import router as transfers_router
from src.api.routes.fantasy import router as fantasy_router
from src.api.routes.admin import router as admin_router

api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(players_router, prefix="/players", tags=["players"])
api_router.include_router(games_router, prefix="/games", tags=["games"])
api_router.include_router(transfers_router, prefix="/transfers", tags=["transfers"])
api_router.include_router(fantasy_router, prefix="/fantasy", tags=["fantasy"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
