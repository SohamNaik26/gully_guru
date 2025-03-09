# GullyGuru API

## Overview

The GullyGuru API is organized using a service-oriented architecture. This directory contains the client code for interacting with the API server.

## Directory Structure

```
src/api/
├── services/                  # Service-specific client implementations
│   ├── users/                 # User service client
│   │   ├── __init__.py
│   │   └── client.py          # UserService implementation
│   ├── gullies/               # Gully service client
│   │   ├── __init__.py
│   │   └── client.py          # GullyService implementation
│   ├── players/               # Player service client
│   │   ├── __init__.py
│   │   └── client.py          # PlayerService implementation
│   ├── transfers/             # Transfer service client
│   │   ├── __init__.py
│   │   └── client.py          # TransferService implementation
│   ├── fantasy/               # Fantasy service client
│   │   ├── __init__.py
│   │   └── client.py          # FantasyService implementation
│   ├── admin/                 # Admin service client
│   │   ├── __init__.py
│   │   └── client.py          # AdminService implementation
│   └── base.py                # Base service class with common functionality
├── routes/                    # API route definitions
│   ├── __init__.py            # Router registration
│   ├── users.py               # User endpoints
│   ├── gullies.py             # Gully endpoints
│   ├── players.py             # Player endpoints
│   ├── transfers.py           # Transfer endpoints
│   ├── fantasy.py             # Fantasy endpoints
│   └── admin.py               # Admin endpoints
├── schemas/                   # Pydantic models for request/response validation
│   ├── __init__.py
│   ├── user.py                # User schemas
│   ├── gully.py               # Gully schemas
│   ├── player.py              # Player schemas
│   ├── transfer.py            # Transfer schemas
│   ├── fantasy.py             # Fantasy schemas
│   └── admin.py               # Admin schemas
├── client_factory.py          # Factory class for creating and managing service clients
├── api_client_instance.py     # Global API client instance
├── dependencies.py            # FastAPI dependency injection utilities
├── exceptions.py              # Custom exception classes
└── __init__.py                # Package initialization
```

## API Endpoints

### User Endpoints (`/api/users/`)
- `GET /api/users/telegram/{telegram_id}` - Get user by Telegram ID
- `GET /api/users/{user_id}` - Get user by ID
- `POST /api/users/` - Create a new user
- `PUT /api/users/telegram/{telegram_id}` - Update user by Telegram ID
- `DELETE /api/users/telegram/{telegram_id}` - Delete user by Telegram ID

### Gully Endpoints (`/api/gullies/`)
- `GET /api/gullies/` - Get all gullies
- `GET /api/gullies/{gully_id}` - Get gully by ID
- `GET /api/gullies/group/{group_id}` - Get gully by Telegram group ID
- `POST /api/gullies/` - Create a new gully
- `GET /api/gullies/participants/{gully_id}` - Get participants of a gully
- `GET /api/gullies/user-gullies/{user_id}` - Get all gullies a user participates in
- `POST /api/gullies/participants/{gully_id}/{user_id}` - Add a user to a gully
- `PUT /api/gullies/participants/{gully_id}/{user_id}/activate` - Set a gully as active for a user

### Player Endpoints (`/api/players/`)
- `GET /api/players/` - Get players with optional filtering
- `GET /api/players/{player_id}` - Get player by ID
- `GET /api/players/{player_id}/stats` - Get statistics for a player

### Transfer Endpoints (`/api/transfers/`)
- `GET /api/transfers/listings` - Get transfer listings
- `GET /api/transfers/listings/{listing_id}` - Get a specific transfer listing
- `GET /api/transfers/user/{user_id}/listings` - Get listings created by a user
- `POST /api/transfers/listings` - Create a new transfer listing
- `POST /api/transfers/listings/{listing_id}/bid` - Place a bid on a transfer listing
- `POST /api/transfers/bids/{bid_id}/accept` - Accept a transfer bid
- `POST /api/transfers/listings/{listing_id}/cancel` - Cancel a transfer listing
- `GET /api/transfers/window/current` - Get the current transfer window

### Fantasy Endpoints (`/api/fantasy/`)
- `GET /api/fantasy/teams/user/{user_id}` - Get a user's fantasy team
- `POST /api/fantasy/teams/user/{user_id}/buy` - Buy a player for a user's team
- `POST /api/fantasy/teams/user/{user_id}/captain` - Set a player as captain
- `GET /api/fantasy/teams/user/{user_id}/validate` - Validate a user's team

### Admin Endpoints (`/api/admin/`)
- `GET /api/admin/permissions/{gully_id}/{user_id}` - Get a user's permissions in a gully
- `GET /api/admin/gully/{gully_id}/admins` - Get all admins of a gully
- `POST /api/admin/gully/{gully_id}/admins/{user_id}` - Assign admin role to a user
- `DELETE /api/admin/gully/{gully_id}/admins/{user_id}` - Remove admin role from a user
- `POST /api/admin/permissions/{gully_id}/{user_id}/{permission_type}` - Assign a specific permission to an admin
- `DELETE /api/admin/permissions/{gully_id}/{user_id}/{permission_type}` - Remove a specific permission from an admin
- `POST /api/admin/gully/{gully_id}/nominate/{nominee_id}` - Nominate a user as admin
- `POST /api/admin/gully/{gully_id}/invite` - Generate an invite link for a gully

## Usage

```python
from src.api.api_client_instance import api_client

# User operations
user = await api_client.users.get_user(telegram_id)

# Gully operations
gully = await api_client.gullies.get_gully(gully_id)

# Player operations
players = await api_client.players.get_players(limit=10)

# Always close the client when done
await api_client.close()
```

## Service Architecture

Each service client is responsible for a specific domain area of the application:

1. **UserService**: User management
2. **GullyService**: Gully (cricket community) management
3. **PlayerService**: Cricket player data
4. **TransferService**: Player transfer market
5. **FantasyService**: Fantasy team management
6. **AdminService**: Administrative operations

For detailed documentation of available methods, see the [API Documentation](../../docs/api.md). 