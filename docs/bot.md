# Telegram Bot Service Documentation

## Overview

The GullyGuru Telegram Bot provides a user-friendly interface for interacting with the fantasy cricket platform through Telegram. It allows users to manage their teams, participate in auctions, view match data, and track their performance.

## Core Components

### 1. Bot Setup

- **Initialization**: Sets up the bot with Telegram API
- **Command Registration**: Registers available commands
- **Error Handling**: Manages and logs errors
- **Conversation Management**: Handles multi-step interactions

### 2. API Client

- **HTTP Requests**: Communicates with the backend API
- **Authentication**: Manages user authentication
- **Response Processing**: Parses API responses
- **Error Handling**: Handles API errors gracefully

### 3. Command Handlers

- **User Commands**: Processes user commands like /start, /help
- **Team Commands**: Handles team management commands
- **Auction Commands**: Manages auction-related commands
- **Match Commands**: Processes match-related commands
- **Leaderboard Commands**: Handles leaderboard viewing

### 4. Callback Handlers

- **Button Callbacks**: Processes inline button presses
- **Navigation**: Handles menu navigation
- **Actions**: Processes user actions like bidding, selecting players

### 5. Keyboards

- **Inline Keyboards**: Generates interactive button layouts
- **Navigation Menus**: Creates menu structures
- **Action Buttons**: Provides action-specific buttons

### 6. Utilities

- **Formatting**: Formats messages for display
- **Validation**: Validates user inputs
- **Pagination**: Handles paginated data display

## Available Commands

- `/start`: Register and start using the bot
- `/help`: Show available commands and help
- `/profile`: View user profile and budget
- `/players`: Browse available players
- `/search`: Search for specific players
- `/myteam`: View and manage your team
- `/captain`: Set team captain
- `/transfer`: Transfer players in/out
- `/auction`: View current auction status
- `/bid`: Place a bid in the auction
- `/matches`: View upcoming and live matches
- `/predict`: Make match predictions
- `/leaderboard`: View global rankings

## Interactive Features

### Inline Keyboards

The bot uses Telegram's inline keyboards for:
- Navigation between different sections
- Filtering player lists
- Placing bids in auctions
- Setting team captain
- Making match predictions

### Conversation Handlers

Multi-step interactions are managed through conversation handlers:
- Bidding process
- Player search
- Match predictions
- Team management

### Notifications

The bot sends proactive notifications for:
- New auction rounds
- Auction results
- Match start/end
- Points earned
- Team updates

## Workflows

### User Registration

1. User starts bot with `/start`
2. Bot checks if user exists in database
3. If new user, bot creates account and assigns initial budget
4. Bot sends welcome message with instructions

### Team Management

1. User views team with `/myteam`
2. Bot displays current team composition and value
3. User can set captain, transfer players, or view details
4. When adding players, budget constraints are enforced
5. Team composition rules are validated

### Auction Participation

1. User receives notification about new auction round
2. User views auction with `/auction`
3. User places bid via command or quick bid buttons
4. Bot validates bid against budget and minimum requirements
5. User receives notification about auction result

### Match Predictions

1. User views upcoming matches with `/matches`
2. User selects a match to predict
3. Bot shows prediction options
4. User makes prediction
5. After match, points are awarded based on accuracy

## Error Handling

The bot includes robust error handling:
- API request failures are caught and logged
- User input is validated before processing
- Appropriate error messages are shown to users
- Budget constraints are enforced for bids and transfers

## Integration with API

The bot communicates with the backend API through the `APIClient` class:
1. Makes HTTP requests to API endpoints
2. Handles authentication and error handling
3. Converts API responses to Python dictionaries
4. Provides methods for all required API operations

## Key Features

### User Management
- Registration with `/start`
- Profile viewing with `/profile`
- Budget tracking

### Team Management
- View team with `/myteam`
- Set captain with `/captain`
- Transfer players with `/transfer`
- Team composition rules enforcement

### Player Management
- Browse players with `/players`
- Filter by team, role, price
- View detailed player stats
- Add/remove players from team

### Auction System
- View live auctions with `/auction`
- Place bids on players
- Receive notifications for new auction rounds
- Get auction results
- View auction history

### Match and Prediction System
- View upcoming and live matches
- Make predictions on match outcomes
- Get live score updates
- Earn points based on correct predictions

### Leaderboard
- View global rankings
- Track points earned

## Auction Mechanism

The auction system is a key component of the bot:

1. **Auction Rounds**:
   - Each round features a single player
   - Users receive notifications when new rounds start
   - Base price is set for each player

2. **Bidding Process**:
   - Users can place bids via command or quick bid buttons
   - Minimum bid increments based on current price
   - System validates bids against user budget
   - Highest bidder wins when time expires

3. **Auction Results**:
   - All users receive notifications about auction outcomes
   - Winners get the player added to their team
   - Budget is automatically deducted

4. **Contested vs. Uncontested**:
   - Uncontested players are assigned at base price
   - Contested players go through bidding process

## Interactive UI

The bot uses Telegram's interactive features:

1. **Inline Keyboards**: Custom buttons for navigation and actions
2. **Callback Queries**: Handle button presses without requiring new commands
3. **Conversation Handlers**: Multi-step interactions (like bidding)

## API Integration

The bot communicates with the backend API through the `APIClient` class:

1. User data management (registration, profile updates)
2. Team management (adding/removing players, setting captain)
3. Auction participation (viewing status, placing bids)
4. Match data and predictions
5. Leaderboard and points tracking

## Error Handling

The bot includes robust error handling:
- API request failures are caught and logged
- User input is validated before processing
- Appropriate error messages are shown to users
- Budget constraints are enforced for bids and transfers

## Notifications

The bot sends proactive notifications for:
- New auction rounds
- Auction results
- Match start/end
- Points earned
- Team updates

## Example Workflows

### Auction Bidding
1. User receives notification about a new player being auctioned
2. User taps "View Auction" button or types `/auction`
3. Bot shows current auction status with player details and current bid
4. User taps "Place Bid" button
5. Bot shows bid options with quick bid buttons
6. User selects a bid amount
7. Bot confirms bid placement
8. When auction ends, user receives notification about the result

### Team Management
1. User navigates to team view with `/myteam`
2. Bot displays current team composition and value
3. User can set captain, transfer players, or view details
4. When adding players, budget constraints are enforced
5. Team composition rules (max players per role) are validated

## Deployment

The bot is designed to run as a Docker container alongside the API service:
- Both services share environment variables for configuration
- The bot connects to the API via internal Docker network
- Both use the same PostgreSQL database 