# GullyGuru Fantasy Cricket

A Telegram bot for fantasy cricket with auction, transfers, and live scoring.

## Features

- User registration and team management
- Player auctions with real-time bidding
- Weekly transfer windows
- Match predictions and polls
- Live scoring and leaderboards
- Multi-group support with separate gully leagues
- Admin controls for gully management

## Documentation

For detailed documentation, see the [Documentation Index](docs/README.md) which includes:

- [User Management System](docs/user_management.md)
- [Auction Management System](docs/auction_management.md)
- [Database Migration](docs/db_migration.md)
- [API Documentation](docs/api.md)
- [Gully Management](docs/gully_management.md)

## System Architecture & Setup

### Architecture Overview

GullyGuru follows a layered architecture pattern:

```mermaid
graph TD
    A[Telegram Bot Layer] --> B[API Layer]
    B --> C[Service Layer]
    C --> D[Database Layer]
    E[Background Tasks] --> C
```

#### Components

1. **Database Layer**
   - PostgreSQL database with SQLModel ORM
   - Alembic for migrations
   - Core models for users, gullies, players, and auctions

2. **Service Layer**
   - Business logic encapsulation
   - Transaction management
   - Data validation and processing

3. **API Layer**
   - FastAPI endpoints with OpenAPI documentation
   - JWT authentication
   - Request/response validation with Pydantic

4. **Telegram Bot Layer**
   - Python-Telegram-Bot framework
   - Command handlers and conversation flows
   - Inline keyboards and callback handlers
   - Notification system

5. **Background Tasks**
   - Scheduled jobs for data updates
   - Asynchronous processing
   - Notification delivery

### Development Setup

#### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Pipenv
- Telegram Bot Token (from BotFather)

#### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/GullyGuru.git
   cd GullyGuru
   ```

2. **Install dependencies**
   ```bash
   pipenv install
   pipenv install --dev  # For development tools
   ```

3. **Configure environment variables**
   Create a `.env` file with:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/gullyguru
   TELEGRAM_BOT_TOKEN=your_bot_token
   JWT_SECRET=your_jwt_secret
   ENVIRONMENT=development
   ```

4. **Initialize the database**
   ```bash
   pipenv run alembic upgrade head
   ```

5. **Run the application**
   ```bash
   pipenv run python -m src.main
   ```

### Deployment to Cloud Run

GullyGuru is deployed to Google Cloud Run for scalable, serverless container execution:

1. **Build and tag the Docker image**
   ```bash
   docker build -t gcr.io/[PROJECT_ID]/gullyguru:latest .
   ```

2. **Push the image to Google Container Registry**
   ```bash
   docker push gcr.io/[PROJECT_ID]/gullyguru:latest
   ```

3. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy gullyguru \
     --image gcr.io/[PROJECT_ID]/gullyguru:latest \
     --platform managed \
     --region [REGION] \
     --allow-unauthenticated \
     --set-env-vars="DATABASE_URL=postgresql://[USER]:[PASSWORD]@[HOST]/[DB_NAME],TELEGRAM_BOT_TOKEN=[TOKEN]"
   ```

#### Cloud Infrastructure

The application is deployed with the following cloud components:

- **Cloud Run**: Hosts the containerized application with automatic scaling
- **Cloud SQL**: PostgreSQL database for persistent storage
- **Secret Manager**: Securely stores sensitive configuration like API tokens
- **Cloud Storage**: Stores static assets and backup files
- **Cloud Scheduler**: Triggers scheduled tasks and maintenance jobs

#### Continuous Deployment

The deployment process is automated using Cloud Build:

1. Code is pushed to the main branch
2. Cloud Build automatically builds the Docker image
3. The image is pushed to Container Registry
4. Cloud Run service is updated with the new image
5. Health checks verify the deployment

#### Environment Configuration

Environment variables are managed through Cloud Run's configuration:

- Production environment variables are set during deployment
- Secrets are injected from Secret Manager
- Database connection uses private VPC connector for security

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make database changes**
   - Update models in `src/db/models/`
   - Generate migration:
     ```bash
     pipenv run alembic revision --autogenerate -m "Description of changes"
     ```
   - Apply migration:
     ```bash
     pipenv run alembic upgrade head
     ```

3. **Implement services**
   - Add business logic in `src/services/`
   - Write unit tests in `src/tests/services/`

4. **Create API endpoints**
   - Implement endpoints in `src/api/routes/`
   - Define schemas in `src/api/schemas/`

5. **Develop bot commands**
   - Add command handlers in `src/bot/handlers/`
   - Create keyboards in `src/bot/keyboards/`
   - Implement callbacks in `src/bot/callbacks/`

6. **Run tests**
   ```bash
   pipenv run pytest
   ```

## Basic Usage

### Admin Commands
- `/join_gully` - Join a gully and start playing
- `/create_gully` - Create a new gully in a group
- `/gully_settings` - Configure gully settings
- `/add_admin` - Add an admin to the current gully

### User Commands
- `/join_gully` - Join a gully in the current group
- `/my_gullies` - View all gullies you're participating in
- `/switch_gully` - Switch between different gullies
- `/myteam` - View your current team
- `/players` - Browse available players

For a complete list of commands and detailed usage instructions, see the [User Management Documentation](docs/user_management.md).

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[MIT License](LICENSE)

## Recent Updates

### Documentation Reorganization
We've completely restructured our documentation for better clarity:
- Created comprehensive guides for [User Management](docs/user_management.md) and [Auction System](docs/auction_management.md)
- Organized documentation by functional areas and technical layers
- Added detailed implementation plans with clear sequences
- Improved database schema documentation with relationships
- See the [Documentation Index](docs/README.md) for a complete overview

### API Schema Reorganization
We've improved the organization of our API models:
- Moved all API schemas from `src/db/models/api.py` to a dedicated `src/api/schemas/` directory
- Separated schemas by domain (user, player, match, game)
- Implemented proper inheritance patterns for cleaner code
- Added comprehensive documentation for all schema models
- Removed unused API database tables to optimize the database

### Gully Management System
We've implemented a comprehensive gully management system that allows:
- Creating multiple fantasy cricket gullies across different Telegram groups
- Users can participate in multiple gullies simultaneously
- Each gully has its own auction, transfers, and leaderboard
- Automatic context switching based on group interactions
- Easy navigation between different gullies

For detailed documentation on the gully system, see [Gully Management Documentation](docs/gully_management.md).

## TODO

### API Services Implementation

The following API services need to be implemented to complete the bot refactoring:

#### 1. GullyService
- `get_user_gully_participation(user_id, gully_id)`: Get a user's participation in a gully
- `get_members_without_teams(gully_id)`: Get members who haven't created teams yet

#### 2. FantasyService
- `get_auction_status(gully_id)`: Get the current auction status
- `start_auction(gully_id)`: Start an auction
- `next_auction_player(gully_id)`: Move to the next player in the auction
- `end_auction(gully_id)`: End the auction
- `place_bid(gully_id, user_id, bid_amount)`: Place a bid in an auction
- `get_user_team(user_id, gully_id)`: Get a user's team
- `get_team_stats(user_id, gully_id)`: Get statistics for a user's team

#### 3. UserService
- `get_user_credits(user_id, gully_id)`: Get a user's available credits
- `set_active_gully(user_id, gully_id)`: Set a user's active gully
- `get_active_gully(user_id)`: Get a user's active gully

### High Priority
1. **Playing XI Selection**
   - Implement daily lineup selection (11 players + Captain + Vice-Captain)
   - Add vice-captain designation functionality
   - Create UI for easy team selection before match deadlines
   - Add validation for team composition rules

2. **Scoring System**
   - Implement Dream11-style scoring rules
   - Add point calculations for batting (runs, boundaries, strike rate)
   - Add point calculations for bowling (wickets, economy rate, dot balls)
   - Implement captain (2×) and vice-captain (1.5×) point multipliers
   - Create daily and match-wise point summaries

3. **Auction System Implementation**
   - **Database & Models**
     - Complete AuctionRound model with proper status tracking
     - Implement AuctionBid model with validation rules
     - Create AuctionTimer model for tracking auction timers
     - Add AuctionLog model for audit trail
     - Implement PlayerAuctionStatus model to track player auction status

   - **API Endpoints**
     - Create auction round management endpoints (create, start, end)
     - Implement bid placement and validation endpoints
     - Add auction status query endpoints
     - Create auction history endpoints
     - Implement auction timer management endpoints

   - **Services**
     - Develop AuctionService for business logic
     - Implement BidValidationService for bid rules
     - Create AuctionTimerService for timer management
     - Develop PlayerAllocationService for post-auction allocation

   - **Telegram Bot Commands**
     - Implement `/auction_status` command
     - Add `/bid <amount>` command
     - Create `/auction_history` command
     - Implement admin commands for auction management
     - Add inline keyboard for quick bidding

   - **Bot Handlers & Callbacks**
     - Develop auction status handler
     - Implement bid placement handler
     - Create auction notification system
     - Implement auction timer callbacks
     - Add auction result announcement

   - **User Experience**
     - Design player cards with auction information
     - Implement bid confirmation dialogs
     - Create auction countdown timer display
     - Add current highest bidder indicators
     - Implement budget tracking during auction

### Medium Priority
1. **Notifications**
   - Add match start/end notifications
   - Create reminders for lineup submission deadlines
   - Implement transfer window opening/closing alerts
   - Add auction start notifications
   - Implement outbid notifications during auction

2. **Leaderboards**
   - Develop daily, weekly, and season-long leaderboards
   - Add tie-breaking logic based on total wickets, runs, etc.
   - Create head-to-head comparison between users

### Low Priority
1. **UI Improvements**
   - Enhance player cards with more statistics
   - Add graphical elements for team performance
   - Improve navigation in the bot interface

## Installation

[Installation instructions here]

## Usage

### Basic Commands
- `/join_gully` - Join a gully and start playing
- `/create_gully` - Create a new gully in a group (admin only)
- `/join_gully` - Join a gully in the current group
- `/my_gullies` - View all gullies you're participating in
- `/switch_gully` - Switch between different gullies
- `/gully_info` - View information about the current gully

### Team Management
- `/myteam` - View your current team
- `/players` - Browse available players
- `/captain` - Set your team captain

### Auction Commands
- `/bid` - Place a bid in an active auction
- `/auction_status` - Check the status of the current auction

## Contributing

[Contribution guidelines here]

## License

[License information here]

## Remaining Questions

The following questions need to be addressed in future development:

### Auction & Transfer System

1. **Bid Management**
   - How should we handle bid cancellations? Currently, the plan is to not allow cancellations once a bid is placed.
   - Should we implement a minimum bid increment? If so, what should it be?
   - How should we handle tie-breaking for bids with the same amount? Current plan is to use the earliest bid time.

2. **Performance Tracking**
   - How should we calculate player performance for automatic listing of bottom performers?
   - What metrics should be used to determine player performance (points, average, recent form)?
   - How frequently should performance data be updated?

3. **Squad Constraints**
   - How should we enforce squad composition rules (e.g., minimum number of batsmen, bowlers)?
   - Should these constraints be enforced at the database level or in application logic?
   - What should happen if a user's squad falls below the minimum required size?

4. **Auto-Assignment Logic**
   - What specific algorithm should be used for auto-assigning players to users who don't complete their squads?
   - How should we prioritize player assignments when multiple users need auto-assignment?
   - Should auto-assigned players have a different purchase price than market price?

5. **Fair Price Calculation**
   - What formula should be used to calculate the fair price of a player?
   - Should fair price be based on performance, original price, or a combination?
   - How often should fair prices be recalculated?

# GullyGuru

A fantasy cricket platform for IPL enthusiasts.

## Auction Implementation Plan

### Phase 1: Database & Models Setup (Week 1)
1. **Enhance Existing Models**
   - Update `AuctionRound` model with additional fields for timer settings
   - Extend `AuctionBid` model with validation rules and bid increment logic
   - Add relationships between models for efficient querying

2. **Create New Models**
   - Implement `AuctionTimer` model for tracking auction countdown
   - Create `AuctionLog` model for comprehensive audit trail
   - Develop `PlayerAuctionStatus` model to track player status in auction

3. **Database Migrations**
   - Create Alembic migration scripts for new models
   - Add indexes for performance optimization
   - Implement database constraints for data integrity

### Phase 2: API & Services Development (Week 1-2)
1. **Core Auction Services**
   - Develop `AuctionService` for managing auction rounds
   - Implement `BidService` for bid placement and validation
   - Create `AuctionTimerService` for timer management

2. **API Endpoints**
   - Create `/api/auctions/rounds` endpoints (GET, POST, PUT)
   - Implement `/api/auctions/bids` endpoints (GET, POST)
   - Add `/api/auctions/status`