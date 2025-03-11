from fastapi import APIRouter

# Import routers individually to avoid circular imports
from src.api.routes.users import router as users_router
from src.api.routes.players import router as players_router
from src.api.routes.fantasy import router as fantasy_router
from src.api.routes.admin import router as admin_router
from src.api.routes.gullies import router as gullies_router
from src.api.routes.gullies import participants_router

# Create the main API router
api_router = APIRouter()

# Include all routers with appropriate prefixes and tags
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(players_router, prefix="/players", tags=["players"])
api_router.include_router(fantasy_router, prefix="/fantasy", tags=["fantasy"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(gullies_router, prefix="/gullies", tags=["gullies"])

# Include the participants router as a sub-router of gullies
api_router.include_router(
    participants_router, prefix="/gullies/participants", tags=["participants"]
)
