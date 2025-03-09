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
- `/start` - Register with the bot
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
- `/start` - Register with the bot
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