# GullyGuru Database Models Documentation

This document provides a comprehensive overview of the database models used in the GullyGuru fantasy cricket application, including their relationships, validations, and design considerations.

## Table of Contents

1. [Base Components](#base-components)
2. [Core Models](#core-models)
3. [Relationship Models](#relationship-models)
4. [Entity Relationship Diagram](#entity-relationship-diagram)
5. [Validation Rules](#validation-rules)
6. [API Integration](#api-integration)
7. [Implemented Changes](#implemented-changes)

## Base Components

### TZDateTime

A custom DateTime type decorator that ensures all datetime values are timezone-aware.

**Purpose**: Ensures consistent timezone handling across the application by automatically converting naive datetime objects to UTC timezone.

### TimeStampedModel

A base model that provides created_at and updated_at timestamps for all models that inherit from it.

**Purpose**: Provides automatic timestamp tracking for all database models, ensuring consistent audit trails.

## Core Models

### User

Represents a fantasy cricket manager (user of the application).

**Key Fields**:
- `id`: Primary key
- `telegram_id`: Unique identifier from Telegram (indexed for performance)
- `username`: User's Telegram username (indexed for performance)
- `full_name`: User's full name

**Relationships**:
- `user_players`: One-to-many relationship with `UserPlayer` (players owned by this user)
- `gully_participations`: One-to-many relationship with `GullyParticipant` (participations in gullies)
- `gullies`: Many-to-many relationship with `Gully` through the `GullyParticipant` link model

**Properties**:
- `gully_ids`: A property that returns a list of gully IDs that the user is a part of, derived from the `gully_participations` relationship

### Player

Represents an IPL cricket player.

**Key Fields**:
- `id`: Primary key
- `name`: Player's full name (indexed)
- `team`: IPL team name (indexed)
- `player_type`: Type of player (BAT, BOWL, ALL, WK) (indexed)
- `base_price`: Base auction price
- `sold_price`: Final auction price
- `season`: IPL season year (indexed, defaults to 2025)

**Relationships**:
- `user_player`: One-to-one relationship with `UserPlayer` (which user owns this player)

**Validations**:
- `player_type` must be one of: "BAT", "BOWL", "ALL", "WK"

### Gully

Represents a fantasy cricket league (called a "Gully").

**Key Fields**:
- `id`: Primary key
- `name`: Name of the Gully (indexed)
- `telegram_group_id`: Telegram group ID associated with this Gully (unique, indexed)

**Relationships**:
- `participants`: One-to-many relationship with `GullyParticipant` (users participating in this Gully)
- `user_players`: One-to-many relationship with `UserPlayer` (players assigned to this Gully)
- `users`: Many-to-many relationship with `User` through the `GullyParticipant` link model

## Relationship Models

### UserPlayer

Represents the ownership relationship between a user and a player in a specific Gully.

**Key Fields**:
- `id`: Primary key
- `user_id`: Reference to the User (indexed)
- `player_id`: Reference to the Player (indexed)
- `gully_id`: Reference to the Gully context (indexed)
- `purchase_price`: Price paid for this player
- `purchase_date`: When the player was purchased
- `is_captain`: Whether this player is the team captain
- `is_vice_captain`: Whether this player is the team vice-captain
- `is_playing_xi`: Whether this player is in the playing XI

**Relationships**:
- `user`: Many-to-one relationship with `User` (back_populates="user_players")
- `player`: One-to-one relationship with `Player` (back_populates="user_player")
- `gully`: Many-to-one relationship with `Gully` (back_populates="user_players")

**Validations**:
- `purchase_price` must be non-negative

**Constraints**:
- Unique constraint on the combination of `player_id` and `gully_id` to ensure a player can only be owned by one user per Gully

### GullyParticipant

Represents a user's participation in a specific Gully.

**Key Fields**:
- `id`: Primary key
- `gully_id`: Reference to the Gully
- `user_id`: Reference to the User
- `team_name`: Name of the user's team in this Gully
- `budget`: Available budget for this Gully (default: 120.0)
- `points`: Total points earned in this Gully (default: 0)
- `role`: User's role in this Gully (default: "member")

**Relationships**:
- `gully`: Many-to-one relationship with `Gully` (back_populates="participants")
- `user`: Many-to-one relationship with `User` (back_populates="gully_participations")

**Validations**:
- `role` must be one of: "member", "admin"
- `budget` must be non-negative
- `points` must be non-negative

**Constraints**:
- Unique constraint on the combination of `user_id` and `gully_id` to ensure a user can only participate once in a Gully

## Entity Relationship Diagram

```
+----------------+       +-------------------+       +----------------+
|      User      |       | GullyParticipant  |       |     Gully      |
+----------------+       +-------------------+       +----------------+
| id             |<----->| user_id           |<----->| id             |
| telegram_id    |       | gully_id          |       | name           |
| username       |       | team_name         |       | telegram_group_|
| full_name      |       | budget            |       +----------------+
+----------------+       | points            |               |
        |                | role              |               |
        |                +-------------------+               |
        |                                                    |
        v                                                    v
+----------------+                                  +----------------+
|   UserPlayer   |                                  |                |
+----------------+                                  |                |
| id             |                                  |                |
| user_id        |<---------------------------------+                |
| player_id      |                                                   |
| gully_id       |<--------------------------------------------------+
| purchase_price |
| purchase_date  |
| is_captain     |
| is_vice_captain|
| is_playing_xi  |
+----------------+
        |
        v
+----------------+
|     Player     |
+----------------+
| id             |
| name           |
| team           |
| player_type    |
| base_price     |
| sold_price     |
| season         |
+----------------+
```

## Validation Rules

The models implement several validation rules to ensure data integrity:

1. **Player Type Validation**: Player types must be one of: "BAT", "BOWL", "ALL", "WK"
2. **Role Validation**: GullyParticipant roles must be one of: "member", "admin"
3. **Non-negative Values**: 
   - Purchase price must be non-negative
   - Budget must be non-negative
   - Points must be non-negative
4. **Unique Constraints**:
   - User's telegram_id must be unique
   - Gully's telegram_group_id must be unique
   - Player can only be owned by one user per Gully (unique combination of player_id and gully_id)
   - User can only participate once in a Gully (unique combination of user_id and gully_id)

## API Integration

The database models are integrated with the API using Pydantic schemas for request and response validation. Key aspects of this integration include:

### Schema Design

1. **Base Schemas**: Each model has a base schema that defines common fields
2. **Create Schemas**: Extend base schemas for creation operations
3. **Response Schemas**: Extend base schemas for response operations, including additional computed fields

### Computed Properties

For properties that are computed from relationships, we use two approaches:

1. **Model Properties**: Properties defined on the SQLModel classes using Python's property decorator
   ```python
   def get_gully_ids(self) -> list[int]:
       """Return a list of gully IDs that the user is a part of."""
       return [participation.gully_id for participation in self.gully_participations]
   
   User.gully_ids = property(get_gully_ids)
   ```

2. **API-Level Computation**: For more complex scenarios, we compute values at the API level
   ```python
   # Get gully_ids for each user
   user_responses = []
   for user in users:
       # Get the gully_ids for this user
       gully_query = select(GullyParticipant.gully_id).where(GullyParticipant.user_id == user.id)
       gully_result = await session.execute(gully_query)
       gully_ids = gully_result.scalars().all()
       
       # Create a response with the user data and gully_ids
       user_response = UserResponseWithGullies(
           id=user.id,
           telegram_id=user.telegram_id,
           username=user.username,
           full_name=user.full_name,
           created_at=user.created_at,
           updated_at=user.updated_at,
           gully_ids=gully_ids
       )
       user_responses.append(user_response)
   ```

### Response Schema Extensions

We create extended response schemas for specific use cases:

```python
class UserResponse(UserBase):
    """Response model for user data."""
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserResponseWithGullies(UserResponse):
    """Response model for user data with gully IDs."""
    gully_ids: List[int] = []
    model_config = ConfigDict(from_attributes=True)
```

## Implemented Changes

The following changes have been implemented to improve the database model:

1. **Removed PlayerStats Model**: The PlayerStats model has been removed as it was no longer needed.

2. **Removed Status Field from Gully Model**: The status field has been removed from the Gully model as it was not needed.

3. **Added Relationship in User Model**: Added the `user_players` relationship to the User model to properly link users to their owned players.

4. **Updated Relationship Definitions**: Updated the relationship definitions to use the Relationship class with appropriate back_populates references to ensure proper bidirectional relationships.

5. **Fixed GullyParticipant Relationships**: Fixed the relationships between GullyParticipant, User, and Gully to ensure proper navigation between these models.

6. **Added Unique Constraint for User-Gully Combination**: Added a unique constraint on the combination of user_id and gully_id in the GullyParticipant model to ensure a user can only participate once in a Gully.

7. **Changed Player Ownership Constraint**: Changed the unique constraint on player_id in UserPlayer to be on the combination of player_id and gully_id instead, allowing the same player to be owned by different users in different Gullies.

8. **Added Relationship in Gully Model**: Added the `users` relationship to the Gully model to properly link gullies to their users.

9. **Added Event Listener for Updated_at Field**: Implemented a SQLAlchemy event listener to automatically update the `updated_at` field when a record is modified.

10. **Fixed Forward References**: Implemented proper forward references to avoid circular import issues between models.

11. **Added Gully IDs Property**: Added a property to the User model that returns a list of gully IDs that the user is a part of, making it easier to access this information.

12. **Created Extended Response Schemas**: Created extended response schemas for specific use cases, such as including gully IDs in user responses. 