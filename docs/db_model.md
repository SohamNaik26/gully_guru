# GullyGuru Database Models Documentation

This document provides a comprehensive overview of the database models used in the GullyGuru fantasy cricket application, including their relationships, validations, and design considerations.

## Table of Contents

1. [Base Components](#base-components)
2. [Core Models](#core-models)
3. [Relationship Models](#relationship-models)
4. [Auction & Transfer Models](#auction--transfer-models)
5. [Enums & Constants](#enums--constants)
6. [Entity Relationship Diagram](#entity-relationship-diagram)
7. [Validation Rules](#validation-rules)
8. [Security Loopholes & Fixes](#security-loopholes--fixes)
9. [State Flow](#state-flow)
10. [API Integration](#api-integration)
11. [Implemented Changes](#implemented-changes)
12. [Implementation Action Items](#implementation-action-items)

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
- `status`: Current status of the Gully (draft, auction, transfers, completed) (indexed, defaults to "draft")

**Relationships**:
- `participants`: One-to-many relationship with `GullyParticipant` (users participating in this Gully)
- `users`: Many-to-many relationship with `User` through the `GullyParticipant` link model
- `auction_queue_items`: One-to-many relationship with `AuctionQueue` (players in auction queue for this Gully)
- `transfer_market_items`: One-to-many relationship with `TransferMarket` (players in transfer market for this Gully)
- `bank_transactions`: One-to-many relationship with `BankTransaction` (transactions in this Gully)

**Validations**:
- `status` must be one of: "draft", "auction", "transfers", "completed"

## Relationship Models

### ParticipantPlayer

Represents the ownership relationship between a participant and a player.

**Key Fields**:
- `id`: Primary key
- `gully_participant_id`: Reference to the GullyParticipant (link between User and Gully) (indexed)
- `player_id`: Reference to the Player (indexed)
- `purchase_price`: Price paid for this player
- `purchase_date`: When the player was purchased
- `is_captain`: Whether this player is the team captain
- `is_vice_captain`: Whether this player is the team vice-captain
- `is_playing_xi`: Whether this player is in the playing XI
- `status`: Current status of player ownership (draft, locked, contested, owned) (indexed, defaults to "draft")

**Relationships**:
- `gully_participant`: Many-to-one relationship with `GullyParticipant` (back_populates="participant_players")
- `player`: One-to-one relationship with `Player` (back_populates="participant_player")

**Validations**:
- `purchase_price` must be non-negative
- `status` must be one of: "draft", "locked", "contested", "owned"

**Constraints**:
- Unique constraint on the combination of `player_id` and `gully_participant_id` to ensure a player can only be owned by one participant

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
- `bank_transactions`: One-to-many relationship with `BankTransaction` (transactions where this participant is the seller)
- `participant_players`: One-to-many relationship with `ParticipantPlayer` (players owned by this participant)

**Validations**:
- `role` must be one of: "member", "admin"
- `budget` must be non-negative
- `points` must be non-negative

**Constraints**:
- Unique constraint on the combination of `user_id` and `gully_id` to ensure a user can only participate once in a Gully

## Auction & Transfer Models

### AuctionQueue

Represents players that are queued for auction or transfer in a specific Gully.

**Key Fields**:
- `id`: Primary key
- `gully_id`: Reference to the Gully (indexed)
- `player_id`: Reference to the Player (indexed)
- `auction_type`: Type of auction ("new_player" or "transfer")
- `status`: Current status of the auction ("pending", "bidding", "completed")
- `listed_at`: When the player was listed for auction

**Relationships**:
- `gully`: Many-to-one relationship with `Gully` (back_populates="auction_queue_items")
- `player`: Many-to-one relationship with `Player`
- `bids`: One-to-many relationship with `Bid` (bids placed on this auction item)

**Validations**:
- `auction_type` must be one of: "new_player", "transfer"
- `status` must be one of: "pending", "bidding", "completed"

### TransferMarket

Represents players available for purchase in the transfer market for a specific Gully.

**Key Fields**:
- `id`: Primary key
- `gully_id`: Reference to the Gully (indexed)
- `player_id`: Reference to the Player (indexed)
- `fair_price`: Fair price for the player
- `listed_at`: When the player was listed in the transfer market

**Relationships**:
- `gully`: Many-to-one relationship with `Gully` (back_populates="transfer_market_items")
- `player`: Many-to-one relationship with `Player`

**Validations**:
- `fair_price` must be non-negative

### BankTransaction

Represents financial transactions related to player transfers in a specific Gully.

**Key Fields**:
- `id`: Primary key
- `gully_id`: Reference to the Gully (indexed)
- `player_id`: Reference to the Player (indexed)
- `seller_participant_id`: Reference to the GullyParticipant who sold the player
- `sale_price`: Price at which the player was sold
- `sale_time`: When the transaction occurred

**Relationships**:
- `gully`: Many-to-one relationship with `Gully` (back_populates="bank_transactions")
- `player`: Many-to-one relationship with `Player`
- `seller_participant`: Many-to-one relationship with `GullyParticipant` (back_populates="bank_transactions")

**Validations**:
- `sale_price` must be non-negative

### Bid

Represents a bid placed by a user on a player in the auction queue.

**Key Fields**:
- `id`: Primary key
- `auction_queue_id`: Reference to the AuctionQueue item (indexed)
- `gully_participant_id`: Reference to the GullyParticipant who placed the bid (indexed)
- `bid_amount`: Amount of the bid
- `bid_time`: When the bid was placed

**Relationships**:
- `auction_queue_item`: Many-to-one relationship with `AuctionQueue` (back_populates="bids")
- `gully_participant`: Many-to-one relationship with `GullyParticipant`

**Validations**:
- `bid_amount` must be non-negative

**Constraints**:
- Unique constraint on the combination of `auction_queue_id` and `gully_participant_id` to ensure a participant can only place one bid per auction item

## Enums & Constants

To ensure data consistency and validation, we define the following enums for type-related columns in our models:

### PlayerType Enum

Used in the `Player.player_type` field to categorize cricket players by their role.

- `BATSMAN` = "BAT"
- `BOWLER` = "BOWL"
- `ALL_ROUNDER` = "ALL"
- `WICKET_KEEPER` = "WK"

### ParticipantRole Enum

Used in the `GullyParticipant.role` field to define a user's role within a Gully.

- `MEMBER` = "member"
- `ADMIN` = "admin"

### AuctionType Enum

Used in the `AuctionQueue.auction_type` field to distinguish between different types of auctions.

- `NEW_PLAYER` = "new_player" (Initial auction for new players)
- `TRANSFER` = "transfer" (Weekly transfer window auction)

### AuctionStatus Enum

Used in the `AuctionQueue.status` field to track the current state of an auction item.

- `DRAFT` = "draft" (Player in draft stage before submission)
- `PENDING` = "pending" (Waiting for auction to start)
- `BIDDING` = "bidding" (Active bidding phase)
- `COMPLETED` = "completed" (Auction has concluded)

### GullyStatus Enum

Used in the `Gully.status` field to track the current state of a fantasy cricket league.

- `DRAFT` = "draft" (Round 0 in progress, participants picking initial squads)
- `AUCTION` = "auction" (Auction round is live for contested players from Round 0)
- `TRANSFERS` = "transfers" (Mid-season transfer window is open)
- `COMPLETED` = "completed" (League is finished, no further actions allowed)

### UserPlayerStatus Enum

Used in the `UserPlayer.status` field to track the current state of player ownership.

- `DRAFT` = "draft" (User selected this player in Round 0, squad not yet finalized)
- `LOCKED` = "locked" (User submitted Round 0 squad, player is uncontested)
- `CONTESTED` = "contested" (User submitted Round 0 squad, player is contested by others)
- `OWNED` = "owned" (User definitively owns this player, won auction or uncontested)

## Entity Relationship Diagram

```
+----------------+       +-------------------+       +----------------+
|      User      |       | GullyParticipant  |       |     Gully      |
+----------------+       +-------------------+       +----------------+
| id             |<----->| user_id           |<----->| id             |
| telegram_id    |       | gully_id          |       | name           |
| username       |       | team_name         |       | telegram_group_|
| full_name      |       | budget            |       | status         |
+----------------+       | points            |       +----------------+
                         | role              |               |
                         +-------------------+               |
                                  |                          |
                                  v                          v
+----------------+      +-------------------+      +-------------------+
|ParticipantPlayer|     | BankTransaction   |      |   AuctionQueue    |
+----------------+      +-------------------+      +-------------------+
| id             |      | id                |      | id                |
| gully_participant_id |<| seller_participant_id |  | gully_id          |
| player_id      |      | player_id         |      | player_id         |
| purchase_price |      | gully_id          |<-----| auction_type      |
| purchase_date  |      | sale_price        |      | status            |
| is_captain     |      | sale_time         |      | listed_at         |
| is_vice_captain|      +-------------------+      +-------------------+
| is_playing_xi  |                                          |
| status         |                                          |
+----------------+                                          |
        |                                                   |
        v                                                   v
+----------------+                                 +-------------------+
|     Player     |                                 |       Bid         |
+----------------+                                 +-------------------+
| id             |<--------------------------------| auction_queue_id  |
| name           |                                 | gully_participant_id |
| team           |                                 | bid_amount        |
| player_type    |                                 | bid_time          |
| base_price     |                                 +-------------------+
| sold_price     |
| season         |
+----------------+
        |
        v
+-------------------+
|  TransferMarket   |
+-------------------+
| id                |
| gully_id          |
| player_id         |
| fair_price        |
| listed_at         |
+-------------------+
```

## Validation Rules

The models implement several validation rules to ensure data integrity:

1. **Player Type Validation**: Player types must be one of: "BAT", "BOWL", "ALL", "WK"
2. **Role Validation**: GullyParticipant roles must be one of: "member", "admin"
3. **Auction Type Validation**: AuctionQueue auction_type must be one of: "new_player", "transfer"
4. **Auction Status Validation**: AuctionQueue status must be one of: "draft", "pending", "bidding", "completed"
5. **Gully Status Validation**: Gully status must be one of: "draft", "auction", "transfers", "completed"
6. **UserPlayer Status Validation**: UserPlayer status must be one of: "draft", "locked", "contested", "owned"
7. **Non-negative Values**: 
   - Purchase price must be non-negative
   - Budget must be non-negative
   - Points must be non-negative
   - Bid amount must be non-negative
   - Fair price must be non-negative
   - Sale price must be non-negative
8. **Unique Constraints**:
   - User's telegram_id must be unique
   - Gully's telegram_group_id must be unique
   - Player can only be owned by one user per Gully (unique combination of player_id and gully_id)
   - User can only participate once in a Gully (unique combination of user_id and gully_id)
   - Participant can only place one bid per auction item (unique combination of auction_queue_id and gully_participant_id)

## Security Loopholes & Fixes

The following security loopholes have been identified and fixed to ensure fair play in the auction and transfer system:

### 1. Users Re-Buying Their Own Listed Players

**Issue**:
- A user could list a player for sale and then re-buy them at a lower price, gaining an unfair advantage
- This creates a potential for price manipulation and gaming the system

**Fix**:
- Restrict users from bidding on their own listed players
- Add a CHECK constraint in the Bid model to prevent bids from the seller:
  - Ensure the bidder (gully_participant_id) is not the same as the seller of the player
  - Track the seller_id in the AuctionQueue model for transfer-type auctions
  - Implement application-level validation to reject bids from the seller

**Implementation**:
- Add seller_participant_id field to AuctionQueue model for transfer auctions
- Add validation in the Bid creation endpoint to check if the bidder is the seller
- Add database-level constraint to enforce this rule even if application validation is bypassed

**Impact**:
- Ensures fair play by preventing price manipulation
- Maintains market integrity in the transfer system
- Prevents users from exploiting the system to increase their budget

## State Flow

The GullyStatus and UserPlayerStatus enums define the possible states for Gullies and UserPlayers, respectively. This section describes the typical flow of states for these entities.

### Gully Status Flow

The Gully status represents the overall phase of the fantasy cricket league:

```
DRAFT  -->  AUCTION  -->  TRANSFERS  -->  COMPLETED
```

1. **DRAFT**:
   - Round 0 is in progress.
   - Participants can pick their initial squads.
   - UserPlayers are created with status DRAFT.

2. **AUCTION**:
   - When everyone has submitted or the Round 0 deadline passes, the league enters Auction.
   - An auction round is live for any contested players from Round 0.
   - Bids occur, winners get their players.

3. **TRANSFERS**:
   - When the auction concludes, the league moves into the Transfer window.
   - A mid-season transfer window is open.
   - Users can buy/sell players, pick up free agents, etc.

4. **COMPLETED**:
   - The league is finished.
   - No further actions are allowed.
   - This state is set at season's end or whenever the league is closed.

### UserPlayer Status Flow

The UserPlayer status represents the ownership state of a player by a user:

```
DRAFT  -->  LOCKED  -->  OWNED
       \->  CONTESTED  -->  OWNED (if won auction)
                       \->  (deleted) (if lost auction)
```

1. **DRAFT**:
   - The user has selected this player in Round 0, but the user's squad is not yet finalized.
   - The user can still remove this player or continue adding more.

2. **LOCKED**:
   - The user submitted their Round 0 squad for this player, and no other participant selected the same player.
   - In essence, the user's ownership is uncontested from Round 0.
   - This state is set when the user finalizes their Round 0 squad and no other user has selected the same player.

3. **CONTESTED**:
   - The user submitted their Round 0 squad, but another participant also selected this same player.
   - Ownership will be decided via an auction when the Gully transitions to AUCTION.
   - This state is set when the user finalizes their Round 0 squad and another user has also selected the same player.

4. **OWNED**:
   - The user definitively owns this player.
   - This state is reached either by:
     - Being uncontested from the start (LOCKED → OWNED after Round 0 is fully done)
     - Winning the auction if it was CONTESTED
   - Once set to OWNED, that record stays unless the user sells or transfers the player.

### State Transitions

The following table summarizes the key state transitions and their triggers:

| Entity | From State | To State | Trigger |
|--------|------------|----------|---------|
| Gully | DRAFT | AUCTION | All participants submit squads or deadline passes |
| Gully | AUCTION | TRANSFERS | All auctions are completed |
| Gully | TRANSFERS | COMPLETED | Season ends or league is closed |
| UserPlayer | DRAFT | LOCKED | User submits squad and player is uncontested |
| UserPlayer | DRAFT | CONTESTED | User submits squad and player is contested |
| UserPlayer | LOCKED | OWNED | Round 0 is fully closed |
| UserPlayer | CONTESTED | OWNED | User wins auction for player |
| UserPlayer | CONTESTED | (deleted) | User loses auction for player |

## API Integration

The database models are integrated with the API using Pydantic schemas for request and response validation. Key aspects of this integration include:

### Schema Design

1. **Base Schemas**: Each model has a base schema that defines common fields
2. **Create Schemas**: Extend base schemas for creation operations
3. **Response Schemas**: Extend base schemas for response operations, including additional computed fields

### Computed Properties

For properties that are computed from relationships, we use two approaches:

1. **Model Properties**: Properties defined on the SQLModel classes using Python's property decorator
   - **Example**: The `gully_ids` property on the User model returns a list of gully IDs the user is part of
   - **Implementation**: Uses a simple list comprehension to extract gully_id values from the user's gully_participations

2. **API-Level Computation**: For more complex scenarios, we compute values at the API level
   - **Example**: Computing gully IDs for each user in a list response
   - **Implementation**: Executes a database query to get gully IDs for each user and includes them in the response