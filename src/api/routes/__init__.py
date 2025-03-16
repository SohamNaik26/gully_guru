"""
Routes package for the GullyGuru API.
This package contains route modules that define the API endpoints.
"""

from fastapi import APIRouter

# Import routers individually to avoid circular imports
from src.api.routes.users import router as users_router
from src.api.routes.players import router as players_router
from src.api.routes.fantasy import router as fantasy_router
from src.api.routes.admin import router as admin_router
from src.api.routes.gully import router as gullies_router
from src.api.routes.participant import router as participant_router
from src.api.routes.auction import router as auction_router

# Create the main API router
api_router = APIRouter()

# Include all routers with appropriate prefixes and tags
api_router.include_router(users_router)
api_router.include_router(players_router)
api_router.include_router(fantasy_router)
api_router.include_router(admin_router)
api_router.include_router(gullies_router)
api_router.include_router(participant_router)
api_router.include_router(auction_router)
