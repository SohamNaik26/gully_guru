# API Schema Documentation

## Overview

GullyGuru uses Pydantic models for API request validation and response serialization. These models are organized in the `src/api/schemas/` directory by domain to improve code organization and maintainability.

## Schema Organization

The API schemas are organized into the following files:

### User Schemas (`src/api/schemas/user.py`)

Models related to user data, authentication, and profiles.

| Model | Purpose | Description |
|-------|---------|-------------|
| `UserBase` | Base model | Common user fields (telegram_id, username, etc.) |
| `UserCreate` | Request model | Used for creating new users |
| `UserResponse` | Response model | User data returned by the API |
| `UserWithPlayers` | Response model | User data with owned players |

### Player Schemas (`src/api/schemas/player.py`)

Models related to cricket players and their statistics.

| Model | Purpose | Description |
|-------|---------|-------------|
| `PlayerBase` | Base model | Common player fields (name, team, type, etc.) |
| `PlayerCreate` | Request model | Used for creating new players |
| `PlayerRead` | Response model | Basic player data returned by the API |
| `PlayerResponse` | Response model | Complete player data returned by the API |
| `PlayerStatsResponse` | Response model | Player statistics data |

### Match Schemas (`src/api/schemas/match.py`)

Models related to cricket matches and player performances.

| Model | Purpose | Description |
|-------|---------|-------------|
| `MatchBase` | Base model | Common match fields (date, venue, teams, etc.) |
| `MatchCreate` | Request model | Used for creating new matches |
| `MatchResponse` | Response model | Match data returned by the API |
| `MatchPerformanceResponse` | Response model | Player performance in a match |

### Game Mechanics Schemas (`src/api/schemas/game.py`)

Models related to game mechanics like auctions, bids, and leaderboards.

| Model | Purpose | Description |
|-------|---------|-------------|
| `UserSquadResponse` | Response model | User's squad data |
| `AuctionBidCreate` | Request model | Used for creating auction bids |
| `AuctionBidResponse` | Response model | Auction bid data returned by the API |
| `LeaderboardEntry` | Component model | Single entry in a leaderboard |
| `LeaderboardResponse` | Response model | Complete leaderboard data |
| `UserPlayerBase` | Base model | User-player relationship data |
| `UserPlayerCreate` | Request model | Used for creating user-player relationships |
| `UserPlayerRead` | Response model | Basic user-player relationship data |
| `UserPlayerWithDetails` | Response model | User-player data with detailed player info |

## Schema Inheritance Pattern

GullyGuru follows a consistent inheritance pattern for API schemas:

1. **Base Models**: Define common fields shared by request and response models
2. **Create Models**: Extend base models for creation requests, often adding validation
3. **Response Models**: Extend base models with additional fields for API responses

This pattern reduces code duplication and ensures consistency across the API.

### Example: Player Schema Inheritance

```python
# Base model with common fields
class PlayerBase(BaseModel):
    name: str
    team: str
    player_type: str  # BAT, BOWL, ALL, WK
    base_price: Optional[Decimal] = None
    sold_price: Optional[Decimal] = None
    season: int = 2025

# Create model for requests
class PlayerCreate(PlayerBase):
    pass

# Response model with additional fields
class PlayerResponse(PlayerBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

## Using Schemas in API Endpoints

### Importing Schemas

All schemas can be imported from the central `schemas` module:

```python
from src.api.schemas import UserResponse, PlayerResponse, MatchResponse
```

### Example: Using Schemas in FastAPI Endpoints

```python
from fastapi import APIRouter, Depends
from src.api.schemas import PlayerCreate, PlayerResponse
from src.services.player_service import PlayerService

router = APIRouter()

@router.post("/players/", response_model=PlayerResponse)
async def create_player(
    player: PlayerCreate,
    player_service: PlayerService = Depends()
):
    """Create a new player."""
    return await player_service.create_player(player)

@router.get("/players/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: int,
    player_service: PlayerService = Depends()
):
    """Get a player by ID."""
    return await player_service.get_player(player_id)
```

## Best Practices

1. **Use Inheritance**: Leverage schema inheritance to reduce code duplication
2. **Validate Input**: Add field validators to ensure data integrity
3. **Document Fields**: Add docstrings and comments to explain field purposes
4. **Use Type Hints**: Always use proper type hints for better IDE support
5. **Keep Schemas Focused**: Each schema should have a single responsibility
6. **Use Forward References**: For circular dependencies between schemas 