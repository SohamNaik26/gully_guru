# GullyGuru API Documentation

## Overview

The GullyGuru API is a RESTful service that provides endpoints for managing fantasy cricket leagues, players, and user interactions. The API follows a service-oriented architecture and adheres to RESTful principles.

## Architecture

The API is organized in a layered architecture:

1. **Routes Layer**: Defines the HTTP endpoints and handles request/response formatting
2. **Services Layer**: Contains business logic and orchestrates data operations
3. **Factories Layer**: Transforms database models into API response objects
4. **Schemas Layer**: Defines data validation and serialization/deserialization
5. **Database Layer**: Handles data persistence and retrieval
6. **Dependencies Layer**: Provides reusable dependencies for routes
7. **Exceptions Layer**: Defines custom exceptions and error handling

## Standardized Patterns

The GullyGuru API follows several standardized patterns to ensure consistency and maintainability:

### 1. Dependency Injection

All routes use FastAPI's dependency injection system to obtain database sessions and service instances:

```python
@router.get("/{user_id}")
async def get_user(
    user_id: int = Path(..., description="ID of the user"),
    db: AsyncSession = Depends(get_db)
):
    # ...
```

### 2. Exception Handling

The API uses a consistent exception handling pattern with custom exceptions:

```python
try:
    user = await user_service.get_user(user_id)
    if not user:
        raise NotFoundException(resource_type="User", resource_id=user_id)
    return user
except GullyGuruException:
    # Custom exceptions are handled automatically
    raise
except Exception as e:
    # Unexpected exceptions are logged and converted to 500 errors
    logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An internal server error occurred"
    )
```

The API also provides a `handle_exceptions` decorator that can be applied to route

## Standalone API

The GullyGuru API can be run as a standalone service, independent of the Telegram bot. This allows for:

1. **Direct Integration**: Other applications can directly integrate with the GullyGuru API
2. **Testing and Development**: Easier testing and development of new features
3. **Scalability**: The API can be scaled independently of the bot

### Running the Standalone API

The standalone API can be started using the provided script:

```bash
sh scripts/run_api.sh
```

By default, the API runs on `localhost:8000`. The health of the API can be checked at the `/health` endpoint:

```bash
curl http://localhost:8000/health
```

### API Response Structure

All API responses follow a consistent structure:

1. **Single Resource Responses**: Return the resource object directly
   ```json
   {
     "id": 1,
     "name": "Player Name",
     "player_type": "BAT",
     "team": "Team Name",
     "base_price": 100.00,
     "sold_price": 150.00,
     "season": 2025,
     "created_at": "2023-01-01T00:00:00",
     "updated_at": "2023-01-01T00:00:00"
   }
   ```

2. **Paginated List Responses**: Return a paginated response object
   ```json
   {
     "items": [
       {
         "id": 1,
         "name": "Player Name",
         "player_type": "BAT",
         // other fields...
       },
       // more items...
     ],
     "total": 228,
     "limit": 10,
     "offset": 0
   }
   ```

3. **Error Responses**: Return an error object with a detail message
   ```json
   {
     "detail": "Player with ID 999 not found"
   }
   ```

### Pagination

List endpoints support pagination with the following query parameters:

- `limit`: Maximum number of items to return (default: 10, max: 100)
- `offset`: Number of items to skip (default: 0)

Example:
```
GET /api/players/?limit=20&offset=40
```

This request would return items 41-60 from the collection.

### Schema Validation and Error Handling

The GullyGuru API uses Pydantic for schema validation, ensuring that all requests and responses conform to the defined schemas. This provides several benefits:

1. **Type Safety**: All data is validated against the expected types
2. **Required Fields**: The API enforces required fields and provides clear error messages when they are missing
3. **Field Constraints**: Fields can have constraints (e.g., minimum/maximum values) that are enforced by the API

When validation errors occur, the API returns a 422 Unprocessable Entity response with details about the validation errors:

```json
{
  "detail": [
    {
      "loc": ["body", "player_type"],
      "msg": "value is not a valid enumeration member; permitted: 'BAT', 'BOWL', 'ALL', 'WK'",
      "type": "type_error.enum",
      "ctx": {"enum_values": ["BAT", "BOWL", "ALL", "WK"]}
    }
  ]
}
```

Other common error responses include:

- **400 Bad Request**: The request was malformed
- **401 Unauthorized**: Authentication is required
- **404 Not Found**: The requested resource was not found
- **500 Internal Server Error**: An unexpected error occurred on the server

### Health Endpoint

The API provides a health endpoint that can be used to check the status of the service:

```
GET /health
```

The response includes:
- **status**: The overall status of the API ("ok" or "error")
- **database**: The status of the database connection ("healthy" or "unhealthy")
- **version**: The current version of the API

Example response:
```json
{
  "status": "ok",
  "database": "healthy",
  "version": "1.0.0"
}
```

This endpoint is useful for monitoring and health checks in production environments.

## API Endpoints

### User Endpoints

| Method | Endpoint | Description | Input | Output |
|--------|----------|-------------|-------|--------|
| POST | /users/ | Create a new user | UserCreate (telegram_id, username, full_name) | UserResponse |
| GET | /users/ | Get a paginated list of users | Query params: telegram_id, limit, offset | PaginatedResponse[UserResponse] |
| GET | /users/{user_id} | Get a user by ID | Path param: user_id | UserResponse |
| PUT | /users/{user_id} | Update a user | Path param: user_id, Body: UserUpdate | UserResponse |
| DELETE | /users/{user_id} | Delete a user | Path param: user_id | None (204 No Content) |

### Player Endpoints

| Method | Endpoint | Description | Input | Output |
|--------|----------|-------------|-------|--------|
| POST | /players/ | Create a new player | PlayerCreate, Query param: admin_user_id | PlayerResponse |
| GET | /players/ | Get a paginated list of players | Query params: name, team, player_type, limit, offset | PaginatedResponse[PlayerResponse] |
| GET | /players/{player_id} | Get a player by ID | Path param: player_id | PlayerResponse |
| PUT | /players/{player_id} | Update a player | Path param: player_id, Body: PlayerUpdate, Query param: admin_user_id | PlayerResponse |
| DELETE | /players/{player_id} | Delete a player | Path param: player_id, Query param: admin_user_id | None (204 No Content) |
| GET | /players/{player_id}/stats | Get statistics for a player | Path param: player_id | PlayerStatsResponse |

### Gully Endpoints

| Method | Endpoint | Description | Input | Output |
|--------|----------|-------------|-------|--------|
| GET | /gullies/ | Get a paginated list of gullies | Query params: name, status, user_id, telegram_group_id, limit, offset | PaginatedResponse[GullyResponse] |
| GET | /gullies/user/{user_id} | Get all gullies for a user | Path param: user_id | List[GullyResponse] |
| GET | /gullies/group/{telegram_group_id} | Get a gully by Telegram group ID | Path param: telegram_group_id | GullyResponse |
| POST | /gullies/ | Create a new gully | GullyCreate, Query param: creator_id | GullyResponse |
| GET | /gullies/{gully_id} | Get a gully by ID | Path param: gully_id | GullyResponse |
| PUT | /gullies/{gully_id} | Update a gully | Path param: gully_id, Body: GullyUpdate, Query param: user_id | GullyResponse |
| PUT | /gullies/{gully_id}/status | Update a gully's status | Path param: gully_id, Query params: status, user_id | SuccessResponse |
| DELETE | /gullies/{gully_id} | Delete a gully | Path param: gully_id, Query param: user_id | SuccessResponse |
| GET | /gullies/{gully_id}/submission-status | Get submission status for a gully | Path param: gully_id | SubmissionStatusResponse |

### Fantasy Endpoints

| Method | Endpoint | Description | Input | Output |
|--------|----------|-------------|-------|--------|
| GET | /fantasy/draft-squad/{participant_id} | Get a participant's draft squad | Path param: participant_id | SquadResponse |
| POST | /fantasy/draft-squad/{participant_id}/add | Add players to a participant's draft squad | Path param: participant_id, Body: BulkPlayerAddRequest | BulkDraftPlayerResponse |
| POST | /fantasy/draft-squad/{participant_id}/remove | Remove players from a participant's draft squad | Path param: participant_id, Body: BulkPlayerRemoveRequest | BulkDraftPlayerResponse |
| PUT | /fantasy/draft-squad/{participant_id} | Update a participant's entire draft squad | Path param: participant_id, Body: BulkPlayerAddRequest | BulkDraftPlayerResponse |

### Auction Endpoints

| Method | Endpoint | Description | Input | Output |
|--------|----------|-------------|-------|--------|
| POST | /auction/gullies/{gully_id}/start | Start auction for a gully | Path param: gully_id | AuctionStartResponse |
| POST | /auction/gullies/{gully_id}/mark-contested | Mark contested players in a gully | Path param: gully_id | Dict[str, Any] |
| GET | /auction/gullies/{gully_id}/contested-players | Get contested players for a gully | Path param: gully_id | List[ContestPlayerResponse] |
| GET | /auction/gullies/{gully_id}/uncontested-players | Get uncontested players for a gully | Path param: gully_id | List[ContestPlayerResponse] |
| PUT | /auction/queue/{auction_queue_id}/status | Update an auction's status | Path param: auction_queue_id, Query params: status, gully_id | SuccessResponse |
| POST | /auction/resolve-contested/{player_id}/{winning_participant_id} | Resolve a contested player | Path params: player_id, winning_participant_id | Dict[str, Any] |

### Admin Endpoints

| Method | Endpoint | Description | Input | Output |
|--------|----------|-------------|-------|--------|
| GET | /admin/gully/{gully_id}/admins | Get all admins for a gully | Path param: gully_id | List[AdminUserResponse] |
| POST | /admin/gully/{gully_id}/admins/{user_id} | Assign admin role to a user | Path params: gully_id, user_id, Query param: admin_user_id | AdminRoleResponse |
| DELETE | /admin/gully/{gully_id}/admins/{user_id} | Remove admin role from a user | Path params: gully_id, user_id, Query param: admin_user_id | None (204 No Content) |
| GET | /admin/user/{user_id}/permissions | Get a user's permissions in a gully | Path param: user_id, Query param: gully_id | Dict[str, Any] |

### Participant Endpoints

| Method | Endpoint | Description | Input | Output |
|--------|----------|-------------|-------|--------|
| GET | /participants/ | Get a paginated list of participants | Query params: gully_id, user_id, limit, offset | PaginatedResponse[ParticipantResponse] |
| GET | /participants/{participant_id} | Get a participant by ID | Path param: participant_id | ParticipantResponse |
| GET | /participants/user/{user_id}/gully/{gully_id} | Get a participant by user ID and gully ID | Path params: user_id, gully_id | ParticipantResponse |
| POST | /participants/ | Add a user to a gully | Body: ParticipantCreate | ParticipantResponse |
| PUT | /participants/{participant_id} | Update a participant | Path param: participant_id, Body: ParticipantUpdate | ParticipantResponse |
| DELETE | /participants/{participant_id} | Delete a participant | Path param: participant_id | None (204 No Content) |
| GET | /participants/user/{user_id} | Get all participations for a user | Path param: user_id | List[ParticipantResponse] |
| GET | /participants/gully/{gully_id} | Get all participants in a gully | Path param: gully_id | List[ParticipantResponse] |

## Bot-Friendly API Features

The GullyGuru API includes several features specifically designed to facilitate integration with the Telegram bot:

### No Admin Permission Requirements

The API has been designed to be bot-friendly by removing admin permission requirements for participant management:

1. **Adding Participants**: Any user can be added to a gully without requiring admin permissions
2. **Removing Participants**: Any participant can be removed without admin permission checks
3. **Updating Participants**: Participant information can be updated without admin permission checks
4. **Viewing Participants**: Anyone can view the list of participants in any gully without being a participant themselves

### Telegram ID Support

The API provides direct support for Telegram IDs:

1. **User Lookup by Telegram ID**: Users can be retrieved directly using their Telegram ID
2. **Gully Lookup by Telegram Group ID**: Gullies can be retrieved using the Telegram group ID
3. **Participant Lookup by Telegram ID**: The API supports finding participants by their Telegram ID

### Mock User Support

For bot operations, the API supports using mock users:

1. **Bot User**: A special bot user with ID 1 is automatically granted admin access to all gullies
2. **Mock Users**: The bot can create and use mock users for testing and development purposes

These features make it easier for the Telegram bot to interact with the API without requiring complex permission management or user authentication.