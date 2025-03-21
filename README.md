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


# How to play

# GullyGuru Fantasy Cricket - User Journey & Points Guide

## User Journey: From Joining to Season End

1. **First-Time Setup**: After joining a GullyGuru group in Telegram, start a private chat with the bot using `/start` to register and name your team.

2. **Initial Squad Selection**: Use `/squad` in private chat to select 15-18 players for your initial team within your 100 credit budget.

3. **Draft Phase**: Players wanted by multiple members enter the auction queue. Use the group chat to view contested players.

4. **Auction Participation**: When a contested player appears in auction (via `/next_player`), place your bids in the group chat to secure them.

5. **Team Completion**: After auctions conclude, check your final team with `/my_team`. Any missing slots are auto-filled to ensure a complete squad.

6. **Pre-Gameweek Planning**: Before matches begin, set your playing XI from your squad to maximize potential points.

7. **Live Scoring**: During matches, player performances are updated in real-time, with points accumulating based on their actions.

8. **Weekly Transfer Window**: At the end of each gameweek, use `/release_players` to release underperforming players and participate in the new mini-auction.

9. **Season Progress**: Track your position on the leaderboard as the season progresses, making strategic transfers to optimize your team.

10. **Season Conclusion**: At the end of the tournament, final rankings determine the gully champion.

## Points Calculation System

11. **Dream11-Style Scoring**: Points are awarded for batting, bowling, and fielding actions similar to Dream11:
    - Runs: 1 point per run
    - Boundaries: Bonus points (4 for fours, 6 for sixes)
    - Wickets: 25 points per wicket
    - Catches/Stumpings: 10 points each
    - Economy rate bonuses for bowlers
    - Strike rate bonuses for batsmen

12. **Unique Teams**: Unlike Dream11, each player can only be owned by one participant, making strategic selection crucial.

13. **Captain Bonus**: Your designated captain earns 2x points, while vice-captain earns 1.5x points.

14. **Performance Bonuses**: Additional points for milestones (centuries, five-wicket hauls, etc.).

15. **Transfer Strategy**: Weekly transfers allow adapting to player form and injuries, with limited transfers to encourage long-term planning.

16. **Transfer Market**: Players released enter a mini-auction where remaining budget and team needs determine bidding strategy.

17. **Budget Management**: Each player has a dynamic value that can increase/decrease based on performance, affecting your transfer capabilities.

18. **Team Balance**: Maintain a balanced squad across batting, bowling, and all-rounder categories to maximize point potential.

19. **Matchup Strategy**: Consider upcoming fixtures when selecting players for your XI each week.

20. **Long-term Planning**: Balance immediate points potential against future transfer flexibility for tournament knockout stages.

*Note: All team management is done in private chat with the bot, while auction and gully-wide activities happen in the group chat.*
