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

## Recent Updates

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

For detailed documentation on the gully system, see [Gully Management Documentation](docs/group_management.md).

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

### Medium Priority
1. **Notifications**
   - Add match start/end notifications
   - Create reminders for lineup submission deadlines
   - Implement transfer window opening/closing alerts

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

## Overview

GullyGuru is a comprehensive fantasy cricket platform that allows users to:
- Create and manage fantasy cricket teams
- Participate in auctions to acquire players
- Compete in leagues and tournaments
- Track player and team performance

## Tech Stack

- **Backend**: FastAPI, Python 3.9+
- **Database**: PostgreSQL, SQLModel, Alembic
- **Environment Management**: Pipenv
- **API Documentation**: Swagger UI, ReDoc

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL
- Pipenv

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/GullyGuru.git
   cd GullyGuru
   ```

2. Install dependencies:
   ```bash
   pipenv install
   
   # For development, include dev dependencies
   pipenv install --dev
   ```

3. Create a `.env` file with the following variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/gullyguru
   SECRET_KEY=your_secret_key
   ENVIRONMENT=development
   ```

4. Make the migration script executable:
   ```bash
   chmod +x scripts/migration.sh
   ```

5. Run database migrations:
   ```bash
   pipenv run ./scripts/migration.sh upgrade
   ```

## Development

### Running the Application

```bash
# Run the development server
pipenv run uvicorn src.main:app --reload
```

### Database Migrations

```bash
# Initialize Alembic (if not already initialized)
pipenv run ./scripts/migration.sh init

# Create a new migration
pipenv run ./scripts/migration.sh create "Description of changes"

# Apply migrations
pipenv run ./scripts/migration.sh upgrade

# Downgrade migrations
pipenv run ./scripts/migration.sh downgrade

# Show migration history
pipenv run ./scripts/migration.sh history
```

### Testing

```bash
# Run all tests
pipenv run pytest

# Run specific tests
pipenv run pytest tests/test_models.py

# Run tests with coverage
pipenv run pytest --cov=src

# Test database models
pipenv run python scripts/test_models.py
```

### Code Quality

```bash
# Format code
pipenv run black src/

# Sort imports
pipenv run isort src/

# Run linting
pipenv run flake8 src/
```

## Project Structure

```
GullyGuru/
├── alembic/                  # Database migration files
├── docs/                     # Documentation
│   ├── cursor_rules/         # Cursor rules for development
│   └── db_migration.md       # Database migration guide
├── scripts/                  # Utility scripts
│   ├── migration.sh          # Database migration script
│   └── test_models.py        # Model testing script
├── src/                      # Source code
│   ├── api/                  # API endpoints
│   │   └── schemas/          # API request/response models
│   │       ├── user.py       # User-related schemas
│   │       ├── player.py     # Player-related schemas
│   │       ├── match.py      # Match-related schemas
│   │       └── game.py       # Game mechanics schemas
│   ├── db/                   # Database models and utilities
│   │   ├── models/           # SQLModel definitions
│   │   └── init.py           # Database initialization
│   ├── services/             # Business logic
│   └── main.py               # Application entry point
├── tests/                    # Test suite
├── .env                      # Environment variables (not in version control)
├── .gitignore                # Git ignore file
├── Pipfile                   # Pipenv dependencies
├── Pipfile.lock              # Pipenv lock file
└── README.md                 # This file
```

## Troubleshooting

### Common Issues

1. **Migration Script Permissions**:
   If you get a "Permission denied" error when running the migration script, make sure it's executable:
   ```bash
   chmod +x scripts/migration.sh
   ```

2. **Database Connection Issues**:
   Ensure your PostgreSQL server is running and the DATABASE_URL is correct in your .env file.

3. **Alembic Not Initialized**:
   If you see errors about missing alembic.ini, run:
   ```bash
   pipenv run ./scripts/migration.sh init
   ```

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests to ensure everything works
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.



