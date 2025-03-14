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
| GET | /users/ | Get a paginated list of users | Query params: username, page, size | PaginatedResponse[UserResponse] |
| GET | /users/{user_id} | Get a user by ID | Path param: user_id | UserResponse |
| PUT | /users/{user_id} | Update a user | Path param: user_id, Body: UserUpdate | UserResponse |
| DELETE | /users/{user_id} | Delete a user | Path param: user_id | None (204 No Content) |

### Gully Endpoints

| Method | Endpoint | Description | Input | Output |
|--------|----------|-------------|-------|--------|
| POST | /gullies/ | Create a new gully | GullyCreate (name, telegram_group_id, creator_id) | GullyResponse |
| GET | /gullies/ | Get a paginated list of gullies | Query params: name, status, page, size | PaginatedResponse[GullyResponse] |
| GET | /gullies/{gully_id} | Get a gully by ID | Path param: gully_id | GullyResponse |
| PUT | /gullies/{gully_id} | Update a gully | Path param: gully_id, Body: GullyUpdate | GullyResponse |
| DELETE | /gullies/{gully_id} | Delete a gully | Path param: gully_id | None (204 No Content) |
| POST | /gullies/{gully_id}/participants | Add a participant to a gully | Path param: gully_id, Body: GullyParticipantCreate | GullyParticipantResponse |
| GET | /gullies/{gully_id}/participants | Get all participants in a gully | Path param: gully_id | List[GullyParticipantResponse] |
| PUT | /gullies/{gully_id}/participants/{user_id} | Update a participant's role | Path params: gully_id, user_id, Body: GullyParticipantUpdate | GullyParticipantResponse |
| DELETE | /gullies/{gully_id}/participants/{user_id} | Remove a participant from a gully | Path params: gully_id, user_id | None (204 No Content) |

### Player Endpoints

| Method | Endpoint | Description | Input | Output |
|--------|----------|-------------|-------|--------|
| POST | /players/ | Create a new player | PlayerCreate (name, player_type, team, etc.) | PlayerResponse |
| GET | /players/ | Get a paginated list of players | Query params: name, player_type, team, page, size | PaginatedResponse[PlayerResponse] |
| GET | /players/{player_id} | Get a player by ID | Path param: player_id | PlayerResponse |
| PUT | /players/{player_id} | Update a player | Path param: player_id, Body: PlayerUpdate | PlayerResponse |
| DELETE | /players/{player_id} | Delete a player | Path param: player_id | None (204 No Content) |
| GET | /players/{player_id}/stats | Get a player's statistics | Path param: player_id | PlayerStatsResponse |

### Fantasy Endpoints

| Method | Endpoint | Description | Input | Output |
|--------|----------|-------------|-------|--------|
| POST | /fantasy/contests/ | Create a new fantasy contest | ContestCreate (name, description, start_time, end_time, etc.) | ContestResponse |
| GET | /fantasy/contests/ | Get a paginated list of contests | Query params: name, status, page, size | PaginatedResponse[ContestResponse] |
| GET | /fantasy/contests/{contest_id} | Get a contest by ID | Path param: contest_id | ContestResponse |
| PUT | /fantasy/contests/{contest_id} | Update a contest | Path param: contest_id, Body: ContestUpdate | ContestResponse |
| DELETE | /fantasy/contests/{contest_id} | Delete a contest | Path param: contest_id | None (204 No Content) |
| POST | /fantasy/contests/{contest_id}/teams | Submit a team for a contest | Path param: contest_id, Body: TeamCreate | TeamResponse |
| GET | /fantasy/teams/ | Get a paginated list of teams | Query params: user_id, contest_id, page, size | PaginatedResponse[TeamResponse] |
| GET | /fantasy/teams/{team_id} | Get a team by ID | Path param: team_id | TeamResponse |
| PUT | /fantasy/teams/{team_id} | Update a team | Path param: team_id, Body: TeamUpdate | TeamResponse |
| DELETE | /fantasy/teams/{team_id} | Delete a team | Path param: team_id | None (204 No Content) |

### Admin Endpoints

| Method | Endpoint | Description | Input | Output |
|--------|----------|-------------|-------|--------|
| GET | /admin/gullies/{gully_id}/admins | Get all admins for a gully | Path param: gully_id | List[UserResponse] |

### Participant Endpoints

| Method | Endpoint | Description | Input | Output |
|--------|----------|-------------|-------|--------|
| GET | /participants/ | Get a paginated list of participants | Query params: user_id, gully_id, page, size | PaginatedResponse[ParticipantResponse] |
| GET | /participants/{participant_id} | Get a participant by ID | Path param: participant_id | ParticipantResponse |
| POST | /participants/ | Add a user to a gully | Body: ParticipantCreate (user_id, gully_id, role, team_name) | ParticipantResponse |
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