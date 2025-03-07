from fastapi import APIRouter
from src.api.routes import users, players, games, transfers, auction, admin

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(transfers.router, prefix="/transfers", tags=["transfers"])
api_router.include_router(auction.router, prefix="/auction", tags=["auction"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
