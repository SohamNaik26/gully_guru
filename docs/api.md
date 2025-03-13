# GullyGuru API Documentation

## Overview

The GullyGuru API is organized using a service-oriented architecture. Each service corresponds to a specific domain area of the application (users, gullies, players, fantasy, etc.) and provides methods for interacting with that domain. The API follows RESTful principles and uses JSON for data exchange.

## Architecture

The GullyGuru API follows a clean, layered architecture:

1. **Routes Layer**: Handles HTTP requests and responses
2. **Service Layer**: Contains business logic and database operations
3. **Factory Layer**: Creates response objects from database models or dictionaries
4. **Schema Layer**: Defines request and response data models using Pydantic
5. **Database Layer**: Manages database connections and models

This architecture ensures:
- Separation of concerns
- Consistent patterns across the codebase
- Type safety
- Testability
- Maintainability

## API Client Structure

The API client is organized as follows:

- `APIClientFactory`: A factory class that creates and manages service clients
- `BaseService`: A base class that provides common functionality for all service clients
- Service Clients: Domain-specific clients for interacting with different parts of the API

### Using the API Client

```python
from src.api.api_client_instance import api_client

# User-related operations
user = await api_client.users.get_user(telegram_id)
await api_client.users.create_user(user_data)

# Gully-related operations
gully = await api_client.gullies.get_gully(gully_id)
participants = await api_client.gullies.get_gully_participants(gully_id)

# Player-related operations
players = await api_client.players.get_players(limit=10)
player = await api_client.players.get_player(player_id)

# Fantasy-related operations
draft_squad = await api_client.fantasy.get_draft_squad(user_id, gully_id)
await api_client.fantasy.submit_squad(user_id, gully_id)

# Admin operations
await api_client.admin.assign_admin_role(user_id, gully_id)

# Always close the client when done
await api_client.close()
```

## Available Services

### UserService

Methods for managing users and their relationships with players.

- `get_user(user_id)`: Get a user by database ID
- `get_user_by_telegram_id(telegram_id)`: Get a user by Telegram ID
- `create_user(user_data)`: Create a new user
- `update_user(user_id, user_data)`: Update an existing user
- `delete_user(user_id)`: Delete a user
- `get_users_with_gullies(skip, limit, telegram_id)`: Get all users with their gully participations
- `get_user_players(user_id, gully_id)`: Get all players owned by a user, optionally filtered by gully
- `create_user_player(user_player_data)`: Create a new user player relationship

### GullyService

Methods for managing gullies (cricket communities) and their participants.

- `get_all_gullies(skip, limit)`: Get all gullies
- `get_gully(gully_id)`: Get a gully by ID
- `get_gully_by_group(telegram_group_id)`: Get a gully by Telegram group ID
- `create_gully(name, telegram_group_id)`: Create a new gully
- `get_participants(gully_id, user_id, skip, limit)`: Get participants with optional filtering by gully or user
- `get_participant(participant_id)`: Get a specific participant by ID
- `add_user_to_gully(user_id, gully_id, role)`: Add a user to a gully with a specific role
- `update_participant(participant_id, update_data)`: Update a participant's role or team name
- `get_user_gully_participations(user_id)`: Get all gullies a user participates in
- `get_user_gully_participation(user_id, gully_id)`: Get a user's participation in a specific gully

### PlayerService

Methods for managing cricket players.

- `get_players(skip, limit, team, player_type, search)`: Get players with optional filtering
- `get_player(player_id)`: Get a player by ID
- `create_player(player_data)`: Create a new player (admin only)
- `update_player(player_id, player_data)`: Update a player (admin only)
- `delete_player(player_id)`: Delete a player (admin only)
- `get_player_stats(player_id)`: Get statistics for a player

### FantasyService

Methods for managing fantasy cricket teams and drafts.

- `add_to_draft_squad(user_id, player_id, gully_id)`: Add a player to user's draft squad
- `remove_from_draft_squad(user_id, player_id, gully_id)`: Remove a player from user's draft squad
- `get_draft_squad(user_id, gully_id)`: Get user's draft squad
- `submit_squad(user_id, gully_id)`: Submit user's final squad
- `get_submission_status(gully_id)`: Check submission status for a Gully
- `start_auction(gully_id)`: Start auction for a Gully
- `get_contested_players(gully_id)`: Get contested players for a Gully
- `get_uncontested_players(gully_id)`: Get uncontested players for a Gully

### AdminService

Methods for administrative operations.

- `get_gully_admins(gully_id)`: Get all admins of a gully
- `assign_admin_role(user_id, gully_id)`: Assign admin role to a user
- `get_user_permissions(user_id, gully_id)`: Get a user's permissions in a gully
- `remove_admin_role(user_id, gully_id)`: Remove admin role from a user

## API Endpoints

### User Endpoints (`/api/users/`)
- `GET /api/users/` - Get all users with optional filtering
- `GET /api/users/{user_id}` - Get user by ID
- `GET /api/users/telegram/{telegram_id}` - Get user by Telegram ID
- `POST /api/users/` - Create a new user
- `DELETE /api/users/{user_id}` - Delete user by ID
- `DELETE /api/users/telegram/{telegram_id}` - Delete user by Telegram ID
- `GET /api/users/players/{user_id}` - Get all players owned by a user
- `POST /api/users/players` - Create a new user player relationship

### Gully Endpoints (`/api/gullies/`)
- `GET /api/gullies/` - Get all gullies
- `GET /api/gullies/{gully_id}` - Get gully by ID
- `GET /api/gullies/group/{telegram_group_id}` - Get gully by Telegram group ID
- `POST /api/gullies/` - Create a new gully

### Gully Participants Endpoints (`/api/gullies/participants/`)
- `GET /api/gullies/participants/` - Get participants with optional filtering
- `GET /api/gullies/participants/{participant_id}` - Get a specific participant
- `POST /api/gullies/participants/{gully_id}` - Add a user to a gully
- `PUT /api/gullies/participants/{participant_id}` - Update a participant's role or team name

### Player Endpoints (`/api/players/`)
- `GET /api/players/` - Get players with optional filtering
- `GET /api/players/{player_id}` - Get player by ID
- `POST /api/players/` - Create a new player (admin only)
- `PUT /api/players/{player_id}` - Update a player (admin only)
- `DELETE /api/players/{player_id}` - Delete a player (admin only)
- `GET /api/players/{player_id}/stats` - Get statistics for a player

### Fantasy Endpoints (`/api/fantasy/`)
- `POST /api/fantasy/draft-player` - Add a player to user's draft squad
- `DELETE /api/fantasy/draft-player/{player_id}` - Remove a player from user's draft squad
- `GET /api/fantasy/draft-squad` - Get user's draft squad
- `POST /api/fantasy/submit-squad` - Submit user's final squad
- `GET /api/fantasy/submission-status/{gully_id}` - Check submission status for a Gully
- `POST /api/fantasy/start-auction/{gully_id}` - Start auction for a Gully
- `GET /api/fantasy/contested-players/{gully_id}` - Get contested players for a Gully
- `GET /api/fantasy/uncontested-players/{gully_id}` - Get uncontested players for a Gully

### Admin Endpoints (`/api/admin/`)
- `GET /api/admin/gully/{gully_id}/admins` - Get all admins of a gully
- `POST /api/admin/gully/{gully_id}/admins/{user_id}` - Assign admin role to a user

## Setting Up New Routes

Creating a new feature in the GullyGuru API involves several steps. This section provides a comprehensive guide on how to set up new routes, schemas, services, and factories.

### Step 1: Define Schemas

First, define the request and response schemas using Pydantic models in the appropriate file under `src/api/schemas/`.

Example for a new feature called "matches":

```python
# src/api/schemas/match.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Request schema
class MatchCreate(BaseModel):
    home_team: str
    away_team: str
    venue: str
    match_date: datetime
    gully_id: int

# Response schema
class MatchResponse(BaseModel):
    id: int
    home_team: str
    away_team: str
    venue: str
    match_date: datetime
    gully_id: int
    created_at: datetime
    updated_at: datetime
```

### Step 2: Create Factory

Next, create a factory class to convert database models to response objects in `src/api/factories/`.

```python
# src/api/factories/match.py
from typing import Dict, Any, List, Union
from src.api.schemas.match import MatchResponse
from src.db.models.models import Match

class MatchFactory:
    @staticmethod
    def create_response(match: Union[Match, Dict[str, Any]]) -> MatchResponse:
        """Create a match response from a Match model or dictionary."""
        if isinstance(match, dict):
            return MatchResponse(**match)
        
        return MatchResponse(
            id=match.id,
            home_team=match.home_team,
            away_team=match.away_team,
            venue=match.venue,
            match_date=match.match_date,
            gully_id=match.gully_id,
            created_at=match.created_at,
            updated_at=match.updated_at
        )
    
    @staticmethod
    def create_response_list(matches: List[Union[Match, Dict[str, Any]]]) -> List[MatchResponse]:
        """Create a list of match responses from a list of Match models or dictionaries."""
        return [MatchFactory.create_response(match) for match in matches]
```

### Step 3: Create Service

Create a service class to handle business logic and database operations in `src/api/services/`.

```python
# src/api/services/match.py
from typing import Dict, Any, List, Optional
import logging
import httpx
from datetime import datetime
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.services.base import BaseService, BaseServiceClient
from src.db.models.models import Match, Gully

logger = logging.getLogger(__name__)

class MatchService(BaseService):
    """Client for interacting with match-related API endpoints."""
    
    def __init__(self, base_url: str, client: httpx.AsyncClient = None):
        """Initialize the match service client."""
        super().__init__(base_url, client)
        self.endpoint = f"{self.base_url}/matches"
    
    async def get_matches(self, gully_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get matches with optional filtering by gully."""
        params = {}
        if gully_id:
            params["gully_id"] = gully_id
            
        response = await self._make_request("GET", self.endpoint, params=params)
        if "error" in response:
            logger.error(f"Error getting matches: {response['error']}")
            return []
        return response
    
    async def get_match(self, match_id: int) -> Dict[str, Any]:
        """Get a match by ID."""
        response = await self._make_request("GET", f"{self.endpoint}/{match_id}")
        if "error" in response:
            logger.error(f"Error getting match: {response['error']}")
            return {}
        return response
    
    async def create_match(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new match."""
        response = await self._make_request("POST", self.endpoint, json=match_data)
        if "error" in response:
            logger.error(f"Error creating match: {response['error']}")
            return {}
        return response

class MatchServiceClient(BaseServiceClient):
    """Client for interacting with match-related database operations."""
    
    async def get_matches(self, gully_id: Optional[int] = None) -> List[Match]:
        """Get matches with optional filtering by gully."""
        query = select(Match)
        if gully_id:
            query = query.where(Match.gully_id == gully_id)
            
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_match(self, match_id: int) -> Optional[Match]:
        """Get a match by ID."""
        return await self.db.get(Match, match_id)
    
    async def create_match(self, match_data: Dict[str, Any]) -> Match:
        """Create a new match."""
        # First check if the gully exists
        gully = await self.db.get(Gully, match_data["gully_id"])
        if not gully:
            raise ValueError(f"Gully with ID {match_data['gully_id']} not found")
            
        # Create the match
        match = Match(**match_data)
        self.db.add(match)
        await self.db.commit()
        await self.db.refresh(match)
        return match
```

### Step 4: Update Service Exports

Add the new service to the exports in `src/api/services/__init__.py`:

```python
from src.api.services.match import MatchService, MatchServiceClient

__all__ = [
    # ... existing exports ...
    "MatchService",
    "MatchServiceClient",
]
```

### Step 5: Update Factory Exports

Add the new factory to the exports in `src/api/factories/__init__.py`:

```python
from src.api.factories.match import MatchFactory

__all__ = [
    # ... existing exports ...
    "MatchFactory",
]
```

### Step 6: Create Routes

Create a new route file in `src/api/routes/`:

```python
# src/api/routes/matches.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.db.session import get_session
from src.db.models import User
from src.api.schemas.match import MatchCreate, MatchResponse
from src.api.dependencies import get_current_user
from src.api.exceptions import NotFoundException
from src.api.factories import MatchFactory
from src.api.services import MatchServiceClient

router = APIRouter()

@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(
    match_data: MatchCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create a new match."""
    match_service = MatchServiceClient(session)
    match = await match_service.create_match(match_data.dict())
    return MatchFactory.create_response(match)

@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a match by ID."""
    match_service = MatchServiceClient(session)
    match = await match_service.get_match(match_id)
    if not match:
        raise NotFoundException(resource_type="Match", resource_id=match_id)
    return MatchFactory.create_response(match)

@router.get("/", response_model=List[MatchResponse])
async def get_matches(
    gully_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
):
    """Get all matches with optional filtering by gully."""
    match_service = MatchServiceClient(session)
    matches = await match_service.get_matches(gully_id=gully_id)
    return MatchFactory.create_response_list(matches)
```

### Step 7: Register Routes

Register the new routes in `src/api/routes/__init__.py`:

```python
from src.api.routes.matches import router as matches_router

# ... existing code ...

app.include_router(matches_router, prefix="/matches", tags=["matches"])
```

### Step 8: Update API Client Factory

Update the API client factory in `src/api/client_factory.py` to include the new service:

```python
from src.api.services import MatchService

class APIClientFactory:
    # ... existing code ...
    
    def __init__(self, base_url: str):
        # ... existing code ...
        self.matches = MatchService(base_url, self.client)
```

### Complete Example: User Flow

Let's walk through how the User feature is implemented in the GullyGuru API:

1. **Schema Definition** (`src/api/schemas/user.py`):
   ```python
   class UserCreate(BaseModel):
       username: str
       telegram_id: int
       is_admin: bool = False

   class UserResponse(BaseModel):
       id: int
       username: str
       telegram_id: int
       is_admin: bool
       created_at: datetime
       updated_at: datetime
   ```

2. **Factory Implementation** (`src/api/factories/user.py`):
   ```python
   class UserFactory:
       @staticmethod
       def create_response(user: Union[User, Dict[str, Any]]) -> UserResponse:
           if isinstance(user, dict):
               return UserResponse(**user)
           
           return UserResponse(
               id=user.id,
               username=user.username,
               telegram_id=user.telegram_id,
               is_admin=user.is_admin,
               created_at=user.created_at,
               updated_at=user.updated_at
           )
   ```

3. **Service Implementation** (`src/api/services/user.py`):
   ```python
   class UserServiceClient(BaseServiceClient):
       async def get_user(self, user_id: int) -> Optional[User]:
           return await self.db.get(User, user_id)
       
       async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
           query = select(User).where(User.telegram_id == telegram_id)
           result = await self.db.execute(query)
           return result.scalars().first()
       
       async def create_user(self, user_data: Dict[str, Any]) -> User:
           user = User(**user_data)
           self.db.add(user)
           await self.db.commit()
           await self.db.refresh(user)
           return user
   ```

4. **Route Implementation** (`src/api/routes/users.py`):
   ```python
   @router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
   async def create_user(
       user_data: UserCreate, session: AsyncSession = Depends(get_session)
   ):
       """Create a new user."""
       user_service = UserServiceClient(session)
       
       # Check if user with telegram_id already exists
       existing_user = await user_service.get_user_by_telegram_id(user_data.telegram_id)
       if existing_user:
           raise HTTPException(
               status_code=status.HTTP_409_CONFLICT,
               detail=f"User with telegram_id {user_data.telegram_id} already exists",
           )
       
       # Create new user
       user = await user_service.create_user(user_data.dict())
       return UserFactory.create_response(user)
   ```

This pattern ensures:
1. **Separation of concerns**: Routes handle HTTP, services handle business logic, factories handle response formatting
2. **Consistent pattern**: All features follow the same structure
3. **Type safety**: Pydantic models ensure type validation
4. **Testability**: Each layer can be tested independently
5. **Maintainability**: Changes to one layer don't affect others

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests:

- `200 OK`: The request was successful
- `201 Created`: A new resource was successfully created
- `204 No Content`: The request was successful but there is no content to return
- `400 Bad Request`: The request was invalid or cannot be served
- `401 Unauthorized`: Authentication is required and has failed or has not been provided
- `403 Forbidden`: The request is understood but it has been refused or access is not allowed
- `404 Not Found`: The requested resource could not be found
- `409 Conflict`: The request conflicts with the current state of the server
- `500 Internal Server Error`: An error occurred on the server

Custom exceptions are defined in `src.api.exceptions` to handle specific error cases:

- `NotFoundException`: Raised when a requested resource is not found
- `UnauthorizedException`: Raised when a user is not authorized to perform an action
- `ValidationException`: Raised when request data fails validation
- `ConflictException`: Raised when a request conflicts with the current state of the server

## Authentication

For development purposes, authentication is simplified and a test user is always returned. In production, proper JWT-based authentication will be implemented.

## Factories

The API uses factory classes to create response objects from database models:

- `UserFactory`: Creates user response objects
- `GullyFactory`: Creates gully response objects
- `GullyParticipantFactory`: Creates gully participant response objects
- `PlayerFactory`: Creates player response objects
- `AdminFactory`: Creates admin response objects
- `ContestPlayerResponseFactory`: Creates contested player response objects
- `DraftPlayerResponseFactory`: Creates draft player response objects
- `DraftSquadResponseFactory`: Creates draft squad response objects
- `SubmissionStatusResponseFactory`: Creates submission status response objects
- `AuctionStartResponseFactory`: Creates auction start response objects

## Closing the API Client

Always remember to close the API client when you're done using it to release resources:

```python
await api_client.close()
```

## Best Practices

1. **Service Layer Pattern**:
   - Services should contain all business logic
   - Services should return raw data (dictionaries or model instances)
   - Services should handle database operations

2. **Factory Pattern**:
   - Factories should create response objects from raw data
   - Factories should handle data transformation
   - Factories should be used in routes to format responses

3. **Route Pattern**:
   - Routes should handle HTTP requests and responses
   - Routes should use services for business logic
   - Routes should use factories to format responses
   - Routes should handle errors and exceptions

4. **Schema Pattern**:
   - Schemas should define request and response data models
   - Schemas should validate input data
   - Schemas should document API contracts

5. **Error Handling**:
   - Use custom exceptions for specific error cases
   - Handle errors at the route level
   - Return appropriate HTTP status codes
   - Provide meaningful error messages

## Improvements and TODOs

1. **Authentication and Authorization**
   - Implement JWT-based authentication
   - Add role-based access control
   - Secure endpoints with proper permission checks

2. **API Performance**
   - Add caching for frequently accessed data
   - Optimize database queries
   - Implement pagination for all list endpoints

3. **Documentation**
   - Add OpenAPI/Swagger documentation
   - Add more detailed examples for each endpoint
   - Document request and response schemas

4. **Testing**
   - Increase test coverage
   - Add integration tests for API endpoints
   - Add performance tests

5. **Error Handling**
   - Improve error messages and codes
   - Add more specific exception types
   - Implement consistent error response format

6. **Logging and Monitoring**
   - Add structured logging
   - Implement request/response logging
   - Add performance metrics

7. **Feature Enhancements**
   - Add endpoints for fantasy team management
   - Implement player statistics and scoring
   - Add auction management endpoints
   - Add match and tournament management 