# API Service Documentation

## Overview

The GullyGuru API is a FastAPI-based backend service that provides all the data and business logic for the fantasy cricket platform. It handles user management, team management, player data, auctions, match data, and scoring.

This document provides a high-level overview of the API architecture. For detailed information about specific components, please refer to the following documents:
- [User Management System](user_management.md#api-system) - For user, group, and gully management APIs
- [Auction Management System](auction_management.md#api-system) - For auction and bidding APIs

## Architecture

The GullyGuru API follows a modular architecture with clear separation of concerns:

1. **API Layer** - FastAPI endpoints for handling HTTP requests
2. **Service Layer** - Business logic encapsulated in service classes
3. **Database Layer** - SQLModel-based models with proper relationships

## Core Components

### 1. User Management

- **Registration**: Creates new user accounts with initial budget
- **Authentication**: JWT-based authentication system
- **Profile Management**: Updates user profiles and tracks budgets

For detailed information, see [User Management API](user_management.md#api-system).

### 2. Team Management

- **Team Creation**: Allows users to build their fantasy teams
- **Player Addition/Removal**: Manages team composition with budget constraints
- **Captain Selection**: Handles captain designation (for bonus points)
- **Team Validation**: Enforces team composition rules (max players per role, etc.)

### 3. Player Management

- **Player Database**: Stores all player information and statistics
- **Player Filtering**: Provides search and filter capabilities
- **Player Statistics**: Tracks and updates player performance data

### 4. Auction System

- **Auction Rounds**: Manages sequential player auctions
- **Bidding Process**: Handles bid placement and validation
- **Auction Results**: Processes auction outcomes and updates teams
- **Notifications**: Triggers notifications for auction events

For detailed information, see [Auction Management API](auction_management.md#api-system).

### 5. Match Management

- **Match Scheduling**: Tracks upcoming and live matches
- **Live Scores**: Updates match scores and statistics
- **Player Performance**: Records player performance in matches
- **Points Calculation**: Calculates fantasy points based on real performance

### 6. Leaderboard System

- **Points Tracking**: Aggregates user points
- **Rankings**: Generates leaderboards
- **Historical Data**: Maintains historical performance data

## Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. User logs in with credentials
2. API returns a JWT token
3. Subsequent requests include the token in the Authorization header
4. API validates the token and identifies the user

For detailed information, see [User Management Authentication](user_management.md#authentication).

## Error Handling

The API provides standardized error responses:

- 400: Bad Request (invalid input)
- 401: Unauthorized (authentication required)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (resource doesn't exist)
- 409: Conflict (resource already exists)
- 422: Unprocessable Entity (invalid data format)
- 500: Internal Server Error (server-side issue)

Each error response includes:
- Error code
- Error message
- Optional details for debugging

For component-specific error handling, see:
- [User Management Error Handling](user_management.md#error-handling)
- [Auction Management Error Handling](auction_management.md#error-handling)

## Scheduled Tasks

The API includes background tasks for:

- Updating player statistics
- Processing auction rounds
- Calculating match points
- Updating leaderboards
- Managing user sessions and tokens

For component-specific scheduled tasks, see:
- [User Management Scheduled Tasks](user_management.md#scheduled-tasks)
- [Auction Management Scheduled Tasks](auction_management.md#scheduled-tasks)

## API Models

The API uses Pydantic models for request validation and response serialization. These models are organized in the `src/api/schemas/` directory by domain:

### Schema Organization

- **User Schemas** (`src/api/schemas/user.py`): Models for user data, authentication, and profiles
- **Player Schemas** (`src/api/schemas/player.py`): Models for player data and statistics
- **Match Schemas** (`src/api/schemas/match.py`): Models for match data and performance
- **Game Schemas** (`src/api/schemas/game.py`): Models for game mechanics like auctions, bids, and leaderboards

For detailed schema examples, see:
- [User Management API Schemas](user_management.md#api-schemas)
- [Auction Management API Schemas](auction_management.md#api-schemas)

### Schema Inheritance

Schemas follow a consistent inheritance pattern:

1. **Base Models**: Define common fields (e.g., `UserBase`, `PlayerBase`)
2. **Create Models**: Extend base models for creation requests (e.g., `UserCreate`, `PlayerCreate`)
3. **Response Models**: Extend base models with additional fields for responses (e.g., `UserResponse`, `PlayerResponse`)

## API Endpoints

For a complete list of API endpoints, see:
- [User Management API Endpoints](user_management.md#api-endpoints)
- [Auction Management API Endpoints](auction_management.md#api-endpoints)

## Database Models

For detailed information about database models, see:
- [User Management Database Models](user_management.md#database-models)
- [Auction Management Database Models](auction_management.md#database-models) 