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
- `participant_player`: One-to-many relationship with `ParticipantPlayer` (which participants own this player)
- `draft_selections`: One-to-many relationship with `DraftSelection` (which participants selected this player during draft)

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

### DraftSelection

Represents player selections during the draft phase, before they become owned players.

**Key Fields**:
- `id`: Primary key
- `gully_participant_id`: Reference to the GullyParticipant (link between User and Gully) (indexed)
- `player_id`: Reference to the Player (indexed)
- `selected_at`: When the player was selected
- `is_submitted`: Whether this selection has been submitted as part of the final draft squad

**Relationships**:
- `gully_participant`: Many-to-one relationship with `GullyParticipant` (back_populates="draft_selections")
- `player`: Many-to-one relationship with `Player` (back_populates="draft_selections")

**Constraints**:
- Composite index on the combination of `gully_participant_id` and `player_id` for efficient querying

### ParticipantPlayer

Represents the ownership relationship between a participant and a player after the draft phase.

**Key Fields**:
- `id`: Primary key
- `gully_participant_id`: Reference to the GullyParticipant (link between User and Gully) (indexed)
- `player_id`: Reference to the Player (indexed)
- `purchase_price`: Price paid for this player
- `purchase_date`: When the player was purchased
- `is_captain`: Whether this player is the team captain
- `is_vice_captain`: Whether this player is the team vice-captain
- `is_playing_xi`: Whether this player is in the playing XI
- `status`: Current status of player ownership (locked, contested, owned) (indexed, defaults to "locked")

**Relationships**:
- `gully_participant`: Many-to-one relationship with `GullyParticipant` (back_populates="participant_players")
- `player`: Many-to-one relationship with `Player` (back_populates="participant_player")

**Validations**:
- `purchase_price` must be non-negative
- `status` must be one of: "locked", "contested", "owned"

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
- `has_submitted_squad`: Whether user has submitted their initial squad (default: false)
- `submission_time`: When the user submitted their squad

**Relationships**:
- `gully`: Many-to-one relationship with `Gully` (back_populates="participants")
- `user`: Many-to-one relationship with `User` (back_populates="gully_participations")
- `bank_transactions`: One-to-many relationship with `BankTransaction` (transactions where this participant is the seller)
- `participant_players`: One-to-many relationship with `ParticipantPlayer` (players owned by this participant)
- `draft_selections`: One-to-many relationship with `DraftSelection` (players selected during draft by this participant)

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
- `seller_participant_id`: Reference to the GullyParticipant who is selling the player (for transfer auctions)
- `auction_type`: Type of auction ("new_player" or "transfer")
- `status`: Current status of the auction ("pending", "bidding", "completed")
- `listed_at`: When the player was listed for auction

**Relationships**:
- `gully`: Many-to-one relationship with `Gully` (back_populates="auction_queue_items")
- `player`: Many-to-one relationship with `Player`
- `seller_participant`: Many-to-one relationship with `GullyParticipant`
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
- `bid_amount` must be positive

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

Used in the `ParticipantPlayer.status` field to track the current state of player ownership.

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
                         | has_submitted_squad|               |
                         | submission_time   |               |
                         +-------------------+               |
                                  |                          |
                                  v                          v
+----------------+      +-------------------+      +-------------------+
|DraftSelection  |      |ParticipantPlayer  |      |   AuctionQueue    |
+----------------+      +-------------------+      +-------------------+
| id             |      | id                |      | id                |
| gully_participant_id | | gully_participant_id |  | gully_id          |
| player_id      |      | player_id         |      | player_id         |
| selected_at    |      | purchase_price    |      | seller_participant_id |
| is_submitted   |      | purchase_date     |      | auction_type      |
|                |      | is_captain        |      | status            |
|                |      | is_vice_captain   |      | listed_at         |
|                |      | is_playing_xi     |      +-------------------+
|                |      | status            |                |
+----------------+      +-------------------+                |
        |                        |                           |
        v                        v                           v
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
+-------------------+      +-------------------+
|  TransferMarket   |      | BankTransaction   |
+-------------------+      +-------------------+
| id                |      | id                |
| gully_id          |      | gully_id          |
| player_id         |      | player_id         |
| fair_price        |      | seller_participant_id |
| listed_at         |      | sale_price        |
+-------------------+      | sale_time         |
                           +-------------------+
```

## Validation Rules

The models implement several validation rules to ensure data integrity:

1. **Player Type Validation**: Player types must be one of: "BAT", "BOWL", "ALL", "WK"
2. **Role Validation**: GullyParticipant roles must be one of: "member", "admin"
3. **Auction Type Validation**: AuctionQueue auction_type must be one of: "new_player", "transfer"
4. **Auction Status Validation**: AuctionQueue status must be one of: "pending", "bidding", "completed"
5. **Gully Status Validation**: Gully status must be one of: "draft", "auction", "transfers", "completed"
6. **ParticipantPlayer Status Validation**: ParticipantPlayer status must be one of: "locked", "contested", "owned"
7. **Non-negative Values**: 
   - Purchase price must be non-negative
   - Budget must be non-negative
   - Points must be non-negative
   - Bid amount must be positive
   - Fair price must be non-negative
   - Sale price must be non-negative
8. **Unique Constraints**:
   - User's telegram_id must be unique
   - Gully's telegram_group_id must be unique
   - Player can only be owned by one participant per Gully (unique combination of player_id and gully_participant_id)
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

The GullyStatus and player ownership models define the possible states for Gullies and player ownership, respectively. This section describes the typical flow of states for these entities.

### Gully Status Flow

The Gully status represents the overall phase of the fantasy cricket league:

```
DRAFT  -->  AUCTION  -->  TRANSFERS  -->  COMPLETED
```

1. **DRAFT**:
   - Round 0 is in progress.
   - Participants can pick their initial squads using the DraftSelection model.
   - Players are tracked in the DraftSelection table during this phase.

2. **AUCTION**:
   - When everyone has submitted or the Round 0 deadline passes, the league enters Auction.
   - An auction round is live for any contested players from Round 0.
   - Bids occur, winners get their players as ParticipantPlayer records.

3. **TRANSFERS**:
   - When the auction concludes, the league moves into the Transfer window.
   - A mid-season transfer window is open.
   - Users can buy/sell players, pick up free agents, etc.

4. **COMPLETED**:
   - The league is finished.
   - No further actions are allowed.
   - This state is set at season's end or whenever the league is closed.

### Player Ownership Flow

The player ownership flow now involves two separate models:

1. **DraftSelection Model** (Draft Phase):
   - Players are initially selected and tracked in the DraftSelection table
   - `is_submitted` flag indicates whether the selection has been submitted as part of the final draft squad
   - Once the draft phase is complete, successful selections are converted to ParticipantPlayer records

2. **ParticipantPlayer Model** (Post-Draft Phase):
   - After the draft, player ownership is tracked in the ParticipantPlayer table
   - Status flow for ParticipantPlayer records:

```
LOCKED  -->  OWNED
CONTESTED  -->  OWNED (if won auction)
           \->  (deleted) (if lost auction)
```

1. **LOCKED**:
   - The user submitted their Round 0 squad for this player, and no other participant selected the same player.
   - In essence, the user's ownership is uncontested from Round 0.
   - This state is set when the user finalizes their Round 0 squad and no other user has selected the same player.

2. **CONTESTED**:
   - The user submitted their Round 0 squad, but another participant also selected this same player.
   - Ownership will be decided via an auction when the Gully transitions to AUCTION.
   - This state is set when the user finalizes their Round 0 squad and another user has also selected the same player.

3. **OWNED**:
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
| DraftSelection | Not Submitted | Submitted | User submits draft squad |
| DraftSelection | Submitted | ParticipantPlayer | Draft phase completes, selections are converted |
| ParticipantPlayer | LOCKED | OWNED | Round 0 is fully closed |
| ParticipantPlayer | CONTESTED | OWNED | User wins auction for player |
| ParticipantPlayer | CONTESTED | (deleted) | User loses auction for player |

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

## Implemented Changes

The following changes have been implemented to improve the data model:

1. **Separate Draft Selection Model**:
   - Created a new `DraftSelection` model to track player selections during the draft phase
   - This separates the draft phase from the post-draft ownership phase
   - Provides cleaner data model and simpler validation

2. **Updated UserPlayerStatus Enum**:
   - Removed the "draft" status from the UserPlayerStatus enum
   - Now only includes "locked", "contested", and "owned" statuses
   - Default status for ParticipantPlayer is now "locked"

3. **Migration for Existing Data**:
   - Created a migration to move existing draft data from ParticipantPlayer to DraftSelection
   - Updated the UserPlayerStatus enum to remove the "draft" status
   - Ensured backward compatibility for existing applications

## Implementation Action Items

The following action items should be completed to fully implement the new data model:

1. **API Updates**:
   - Update the fantasy API to use the new DraftSelection model for draft operations
   - Implement transition logic to convert DraftSelections to ParticipantPlayers when the draft phase completes
   - Update validation logic to reflect the new status flow

2. **Bot Updates**:
   - Update the Telegram bot to use the new DraftSelection model for draft operations
   - Update squad building commands to work with the new model
   - Ensure proper error handling for the transition between models

3. **Testing**:
   - Test the draft phase using the new DraftSelection model
   - Test the transition from draft to auction phase
   - Test the auction phase with the updated ParticipantPlayer model
   - Ensure data integrity throughout the entire process