# GullyGuru API Documentation

## Overview

The GullyGuru API is organized using a service-oriented architecture. Each service corresponds to a specific domain area of the application (users, gullies, players, etc.) and provides methods for interacting with that domain.

## API Client Structure

The API client is organized as follows:

- `APIClientFactory`: A factory class that creates and manages service clients
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

# Transfer-related operations
listings = await api_client.transfers.get_transfer_listings()
window = await api_client.transfers.get_current_transfer_window()

# Fantasy-related operations
team = await api_client.fantasy.get_user_team(user_id)
await api_client.fantasy.set_captain(user_id, player_id)

# Admin operations
await api_client.admin.assign_admin_role(user_id, gully_id)
```

## Available Services

### UserService

Methods for managing users.

- `get_user(telegram_id)`: Get a user by Telegram ID
- `create_user(user_data)`: Create a new user
- `update_user(telegram_id, user_data)`: Update an existing user
- `delete_user(telegram_id)`: Delete a user
- `get_user_by_id(user_id)`: Get a user by database ID

### GullyService

Methods for managing gullies (cricket communities).

- `get_all_gullies()`: Get all gullies
- `get_gully(gully_id)`: Get a gully by ID
- `get_gully_by_group(group_id)`: Get a gully by Telegram group ID
- `create_gully(name, telegram_group_id)`: Create a new gully
- `get_gully_participants(gully_id, skip, limit)`: Get participants of a gully
- `get_user_gully_participations(user_id)`: Get all gullies a user participates in
- `add_user_to_gully(user_id, gully_id, role)`: Add a user to a gully
- `set_active_gully(user_id, gully_id)`: Set a gully as active for a user

### PlayerService

Methods for managing cricket players.

- `get_players(skip, limit, team, player_type, search)`: Get players with optional filtering
- `get_player(player_id)`: Get a player by ID
- `get_player_stats(player_id)`: Get statistics for a player

### TransferService

Methods for managing player transfers.

- `get_transfer_listings(status, window_id)`: Get transfer listings
- `get_transfer_listing(listing_id)`: Get a specific transfer listing
- `get_user_listings(user_id, status)`: Get listings created by a user
- `create_transfer_listing(player_id, min_price, transfer_window_id)`: Create a new transfer listing
- `place_transfer_bid(listing_id, bid_amount)`: Place a bid on a transfer listing
- `accept_transfer_bid(bid_id)`: Accept a transfer bid
- `cancel_transfer_listing(listing_id)`: Cancel a transfer listing
- `get_current_transfer_window()`: Get the current transfer window

### FantasyService

Methods for managing fantasy cricket teams.

- `get_user_team(user_id, game_id)`: Get a user's fantasy team
- `buy_player(user_id, player_id, price)`: Buy a player for a user's team
- `set_captain(user_id, player_id)`: Set a player as captain
- `validate_user_team(user_id)`: Validate a user's team

### AdminService

Methods for administrative operations.

- `get_user_permissions(user_id, gully_id)`: Get a user's permissions in a gully
- `get_gully_admins(gully_id)`: Get all admins of a gully
- `assign_admin_role(user_id, gully_id)`: Assign admin role to a user
- `remove_admin_role(user_id, gully_id)`: Remove admin role from a user
- `assign_admin_permission(user_id, gully_id, permission_type)`: Assign a specific permission to an admin
- `remove_admin_permission(user_id, gully_id, permission_type)`: Remove a specific permission from an admin
- `nominate_admin(nominee_id, gully_id)`: Nominate a user as admin
- `generate_invite_link(gully_id, expiration_hours)`: Generate an invite link for a gully 