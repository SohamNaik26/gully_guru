# API Service Documentation

## Overview

The GullyGuru API is a FastAPI-based backend service that provides all the data and business logic for the fantasy cricket platform. It handles user management, team management, player data, auctions, match data, and scoring.

## Core Components

### 1. User Management

- **Registration**: Creates new user accounts with initial budget
- **Authentication**: JWT-based authentication system
- **Profile Management**: Updates user profiles and tracks budgets

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

### 5. Match Management

- **Match Scheduling**: Tracks upcoming and live matches
- **Live Scores**: Updates match scores and statistics
- **Player Performance**: Records player performance in matches
- **Points Calculation**: Calculates fantasy points based on real performance

### 6. Leaderboard System

- **Points Tracking**: Aggregates user points
- **Rankings**: Generates leaderboards
- **Historical Data**: Maintains historical performance data

## API Endpoints

### User Endpoints

- `POST /users/register`: Register a new user
- `POST /users/login`: Authenticate a user
- `GET /users/me`: Get current user profile
- `PUT /users/me`: Update user profile
- `GET /users/{user_id}/team`: Get a user's team

### Team Endpoints

- `GET /teams/my`: Get current user's team
- `POST /teams/players/{player_id}`: Add player to team
- `DELETE /teams/players/{player_id}`: Remove player from team
- `PUT /teams/captain/{player_id}`: Set team captain

### Player Endpoints

- `GET /players`: List all players (with filtering)
- `GET /players/{player_id}`: Get player details
- `GET /players/search`: Search for players

### Auction Endpoints

- `GET /auctions/current`: Get current auction status
- `GET /auctions/history`: Get auction history
- `POST /auctions/bid`: Place a bid
- `GET /auctions/rounds/{round_id}`: Get auction round details

### Match Endpoints

- `GET /matches/upcoming`: Get upcoming matches
- `GET /matches/live`: Get live matches
- `GET /matches/{match_id}`: Get match details
- `POST /matches/{match_id}/predict`: Make match prediction

### Leaderboard Endpoints

- `GET /leaderboard`: Get global leaderboard
- `GET /leaderboard/weekly`: Get weekly leaderboard

## Database Models

- **User**: User accounts and budgets
- **Player**: Player information and statistics
- **UserPlayerLink**: Many-to-many relationship between users and players
- **Team**: Team composition and captain
- **Auction**: Auction rounds and status
- **AuctionBid**: Bids placed in auctions
- **Match**: Match details and scores
- **Prediction**: User predictions for matches
- **PointsLog**: Record of points earned by users

## Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. User logs in with credentials
2. API returns a JWT token
3. Subsequent requests include the token in the Authorization header
4. API validates the token and identifies the user

## Error Handling

The API provides standardized error responses:

- 400: Bad Request (invalid input)
- 401: Unauthorized (authentication required)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (resource doesn't exist)
- 409: Conflict (resource already exists)
- 500: Internal Server Error (server-side issue)

Each error response includes:
- Error code
- Error message
- Optional details for debugging

## Scheduled Tasks

The API includes background tasks for:

- Updating player statistics
- Processing auction rounds
- Calculating match points
- Updating leaderboards 