# Database Migration Guide for GullyGuru

## Overview

GullyGuru uses:
- **PostgreSQL** as the primary database
- **SQLModel** for ORM functionality
- **Alembic** for database migrations
- **Pydantic** for data validation
- **Pipenv** for environment and dependency management

## Setup

### Prerequisites

- PostgreSQL installed and running
- Python environment with Pipenv installed
- Required packages (installed via Pipenv):
  - sqlmodel
  - alembic
  - psycopg2-binary
  - pydantic

### Installation

```bash
# Install all dependencies
pipenv install

# Install development dependencies
pipenv install --dev
```

### Configuration

Alembic is configured in the `alembic.ini` file at the project root. The database connection string is stored in environment variables for security.

## Model Organization

### Avoiding Circular Imports

To prevent circular imports when working with SQLModel and Alembic:

1. **Organize models in separate files** by domain or functionality
2. **Import models directly** in the `__init__.py` file:
   ```python
   # src/db/models/__init__.py
   from src.db.models.user import User
   from src.db.models.player import Player
   
   all_models = [User, Player]
   ```
3. **Import the all_models list** in `alembic/env.py`:
   ```python
   # alembic/env.py
   from src.db.models import all_models
   ```

### Using Base Models and Mixins

GullyGuru uses a modular approach to model definition:

1. **Base Model**: Provides common fields and functionality for all models
2. **Mixins**: Reusable components for common patterns (timestamps, UUIDs, metadata)
3. **Domain-specific Models**: Extend base models with domain-specific fields and relationships

Example:
```python
# Using the base model
class Player(Base, table=True):
    name: str
    team_id: Optional[int] = Field(default=None, foreign_key="teams.id")
    
# Using mixins for composition
class Match(ModularBase, TimestampMixin, UUIDMixin, table=True):
    home_team_id: int = Field(foreign_key="teams.id")
    away_team_id: int = Field(foreign_key="teams.id")
```

## Models Reference

GullyGuru uses a variety of models for different purposes. Here's a comprehensive list of all models and their primary uses:

### Base Models

| Model | File | Purpose | Description |
|-------|------|---------|-------------|
| `TimeStampedModel` | models.py | Base model | Base model with created_at and updated_at fields |

### Domain Models

#### User Models

| Model | File | Purpose | Database Table | Description |
|-------|------|---------|---------------|-------------|
| `User` | models.py | Database | users | User model for fantasy cricket managers |
| `UserPlayer` | models.py | Database | user_players | Link between users and their owned players |

#### Player Models

| Model | File | Purpose | Database Table | Description |
|-------|------|---------|---------------|-------------|
| `Player` | models.py | Database | players | Player model for IPL cricketers |
| `PlayerStats` | models.py | Database | player_stats | Cumulative player statistics |

#### Match Models

| Model | File | Purpose | Database Table | Description |
|-------|------|---------|---------------|-------------|
| `Match` | models.py | Database | matches | IPL match schedule and results |
| `MatchPerformance` | models.py | Database | match_performances | Individual player performance in a match |

#### Game Mechanics Models

| Model | File | Purpose | Database Table | Description |
|-------|------|---------|---------------|-------------|
| `AuctionRound` | models.py | Database | auction_rounds | Auction rounds for player bidding |
| `AuctionBid` | models.py | Database | auction_bids | User bids for players in auction rounds |
| `TransferWindow` | models.py | Database | transfer_windows | Transfer windows for player trading |
| `TransferListing` | models.py | Database | transfer_listings | Player listings in transfer windows |
| `TransferBid` | models.py | Database | transfer_bids | Bids on transfer listings |
| `MatchPoll` | models.py | Database | match_polls | Polls for predicting match outcomes |
| `PollVote` | models.py | Database | poll_votes | User votes on match polls |

#### Gully Models

| Model | File | Purpose | Database Table | Description |
|-------|------|---------|---------------|-------------|
| `Gully` | models.py | Database | gullies | Model for game instances (called 'Gullies') |
| `GullyParticipant` | models.py | Database | gully_participants | Model for game participants |

### Integration Models

#### API Integration Models

The External API Integration Models were previously used to store data from external cricket APIs but have been removed from the database to optimize the schema. The model definitions still exist in the codebase for future reference but are not currently used.

~~| Model | File | Purpose | Database Table | Description |~~
~~|-------|------|---------|---------------|-------------|~~
~~| `ApiTeam` | api.py | Database | api_teams | Cricket teams from external APIs |~~
~~| `ApiPlayer` | api.py | Database | api_players | Cricket players from external APIs |~~
~~| `ApiMatch` | api.py | Database | api_matches | Cricket matches from external APIs |~~
~~| `ApiPlayerStats` | api.py | Database | api_player_stats | Player statistics from external APIs |~~

#### Cricsheet Integration Models

| Model | File | Purpose | Database Table | Description |
|-------|------|---------|---------------|-------------|
| `CricsheetTeam` | cricsheet.py | Database | cricsheet_teams | Cricket teams from Cricsheet data |
| `CricsheetPlayer` | cricsheet.py | Database | cricsheet_players | Cricket players from Cricsheet data |
| `CricsheetMatch` | cricsheet.py | Database | cricsheet_matches | Cricket matches from Cricsheet data |
| `CricsheetInning` | cricsheet.py | Database | cricsheet_innings | Cricket innings from Cricsheet data |
| `CricsheetBall` | cricsheet.py | Database | cricsheet_balls | Cricket balls from Cricsheet data |

#### Kaggle Integration Models

| Model | File | Purpose | Database Table | Description |
|-------|------|---------|---------------|-------------|
| `KagglePlayer` | kaggle.py | Database | kaggle_players | Cricket players from Kaggle datasets |


### API Models (Pydantic Models)

These models are used for API requests and responses, not for database tables. They have been moved from `src/db/models/api.py` to a dedicated `src/api/schemas/` directory for better organization.

#### User API Models

| Model | File | Purpose | Description |
|-------|------|---------|-------------|
| `UserBase` | schemas/user.py | API | Base model for user data |
| `UserCreate` | schemas/user.py | API | Model for creating a new user |
| `UserResponse` | schemas/user.py | API | Response model for user data |
| `UserWithPlayers` | schemas/user.py | API | User model with owned players |

#### Player API Models

| Model | File | Purpose | Description |
|-------|------|---------|-------------|
| `PlayerBase` | schemas/player.py | API | Base model for player data |
| `PlayerCreate` | schemas/player.py | API | Model for creating a new player |
| `PlayerRead` | schemas/player.py | API | Model for reading player data |
| `PlayerResponse` | schemas/player.py | API | Response model for player data |

#### Match API Models

| Model | File | Purpose | Description |
|-------|------|---------|-------------|
| `MatchBase` | schemas/match.py | API | Base model for match data |
| `MatchCreate` | schemas/match.py | API | Model for creating a new match |
| `MatchResponse` | schemas/match.py | API | Response model for match data |

#### Stats API Models

| Model | File | Purpose | Description |
|-------|------|---------|-------------|
| `PlayerStatsResponse` | schemas/player.py | API | Response model for player statistics |
| `MatchPerformanceResponse` | schemas/match.py | API | Response model for player match performance |

#### Game Mechanics API Models

| Model | File | Purpose | Description |
|-------|------|---------|-------------|
| `UserSquadResponse` | schemas/game.py | API | Response model for user squad data |
| `AuctionBidCreate` | schemas/game.py | API | Model for creating a new auction bid |
| `AuctionBidResponse` | schemas/game.py | API | Response model for auction bid data |
| `LeaderboardEntry` | schemas/game.py | API | Entry in the leaderboard |
| `LeaderboardResponse` | schemas/game.py | API | Response model for leaderboard data |
| `UserPlayerBase` | schemas/game.py | API | Base model for user-player relationships |
| `UserPlayerCreate` | schemas/game.py | API | Model for creating user-player relationships |
| `UserPlayerRead` | schemas/game.py | API | Model for reading user-player relationships |
| `UserPlayerWithDetails` | schemas/game.py | API | User-player model with detailed player information |

#### Cricsheet API Models

| Model | File | Purpose | Description |
|-------|------|---------|-------------|
| `CricsheetMatchModel` | cricsheet.py | API | Pydantic model for match data from Cricsheet |
| `CricsheetInningsModel` | cricsheet.py | API | Pydantic model for innings data from Cricsheet |
| `CricsheetPlayerPerformanceModel` | cricsheet.py | API | Pydantic model for player performance in a match |

## Migration Workflow

### Creating a New Migration

When you need to make changes to the database schema:

1. Update the SQLModel models in the appropriate files
2. Generate a new migration version:
   ```bash
   pipenv run alembic revision --autogenerate -m "Description of changes"
   ```
3. Review the generated migration script in `migrations/versions/`
4. Apply the migration:
   ```bash
   pipenv run alembic upgrade head
   ```

### Rolling Back Migrations

To revert to a previous version:

```bash
# Downgrade by one version
pipenv run alembic downgrade -1

# Downgrade to a specific version
pipenv run alembic downgrade <revision_id>

# Downgrade to base (remove all migrations)
pipenv run alembic downgrade base
```

## Best Practices

1. **Always review auto-generated migrations** before applying them
2. **Commit migration scripts to version control**
3. **Test migrations** in development before applying to production
4. **Create meaningful migration messages** that describe the changes
5. **Keep migrations small and focused** on specific changes
6. **Never modify existing migration files** after they've been applied to any environment
7. **Ensure all models are imported** in the models `__init__.py` file to register with SQLModel.metadata
8. **Always use Pipenv** for running migration commands

## Common Issues and Solutions

### Migration Conflicts

If you encounter conflicts between migrations:

1. Ensure all developers are working from the same base migration
2. Coordinate schema changes among team members
3. Consider using branches for significant schema changes

### Circular Imports

If you encounter circular import errors:

1. Reorganize imports to be more direct (import from specific files, not the module itself)
2. Use the `all_models` list in `__init__.py` to register models
3. Consider using late binding with import statements inside functions if needed

### Data Migration

For migrations that require data transformation:

1. Use Alembic's `op.execute()` to run custom SQL
2. For complex data migrations, consider creating a separate Python script

## Production Deployment

When deploying migrations to production:

1. Always backup the database before migration
2. Run migrations during scheduled maintenance windows
3. Have a rollback plan ready
4. Test the migration process in a staging environment first

## Automation with Scripts

GullyGuru includes a migration script at `scripts/migration.sh` that automates common migration tasks:

```bash
# Run the migration script
pipenv run ./scripts/migration.sh
```

This script:
- Initializes Alembic if not already initialized
- Updates the database URL in alembic.ini
- Generates a new migration script
- Applies migrations to the database

## Integration with Application Startup

The application automatically runs migrations during startup through the `init_db()` function in `src/db/init.py`:

```python
async def init_db():
    """Initialize database and run migrations."""
    # Run Alembic migrations
    try:
        logger.info("Running database migrations...")
        result = subprocess.run(
            ["pipenv", "run", "alembic", "upgrade", "head"], 
            capture_output=True, text=True, check=False
        )
        # Log results...
    except Exception as e:
        logger.error(f"Failed to run migrations: {str(e)}")
        
    # As a fallback, ensure tables exist using SQLModel metadata
    # ...
```

## Model Registration

To ensure all models are included in migrations, register them in `src/db/models/__init__.py`:

```python
# Import all models
from src.db.models.user import User
from src.db.models.player import Player
# ... other models

# Create a list of all models for easy access
all_models = [
    User,
    Player,
    # ... other models
]
```

Then reference this in `alembic/env.py`:

```python
# Import all models to ensure they're registered with SQLModel.metadata
from src.db.models import all_models

# Set target metadata
target_metadata = SQLModel.metadata
```

## Testing Migrations

To test migrations before applying them:

```bash
# Create a test migration
pipenv run alembic revision --autogenerate -m "Test migration"

# Check what SQL would be executed without applying it
pipenv run alembic upgrade head --sql
```

## Advanced Migration Techniques

### Custom Migration Operations

For complex schema changes that Alembic can't auto-generate:

```python
# In a migration script
def upgrade():
    # Create a custom index
    op.create_index(
        'idx_player_performance',
        'player_stats',
        ['player_id', 'match_id', 'score'],
        unique=False
    )
    
    # Add a check constraint
    op.create_check_constraint(
        "valid_score_range",
        "player_stats",
        "score >= 0 AND score <= 100"
    )
```

### Handling Enum Types

When working with PostgreSQL enum types:

```python
# In your model
class PlayerRole(str, Enum):
    BATSMAN = "batsman"
    BOWLER = "bowler"
    ALL_ROUNDER = "all_rounder"
    WICKET_KEEPER = "wicket_keeper"

# In a migration script
def upgrade():
    op.create_type('player_role', 
                  [
                      'batsman',
                      'bowler',
                      'all_rounder',
                      'wicket_keeper'
                  ])
```

### Batch Processing for Large Tables

For migrations affecting large tables:

```python
def upgrade():
    # Process in batches to avoid locking the entire table
    op.execute("""
        DO $$
        DECLARE
            batch_size INT := 1000;
            max_id INT;
            current_id INT := 0;
        BEGIN
            SELECT MAX(id) INTO max_id FROM large_table;
            WHILE current_id <= max_id LOOP
                -- Process batch
                UPDATE large_table
                SET new_column = computed_value
                WHERE id > current_id AND id <= current_id + batch_size;
                
                current_id := current_id + batch_size;
                COMMIT;
            END LOOP;
        END $$;
    """)
```

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Pipenv Documentation](https://pipenv.pypa.io/)
