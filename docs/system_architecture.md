# GullyGuru System Architecture

## Overview

GullyGuru is a fantasy cricket platform built with a modern, service-oriented architecture. The system consists of three main components:

1. **Database Layer**: PostgreSQL database with SQLModel ORM
2. **API Layer**: FastAPI-based RESTful API
3. **Bot Layer**: Telegram bot for user interaction

This document provides a comprehensive overview of each component, their interactions, and the key functions available in each.

## System Components

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Telegram Bot   │◄────┤   FastAPI API   │◄────┤   PostgreSQL    │
│                 │     │                 │     │   Database      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
       ▲                       ▲                       ▲
       │                       │                       │
       └───────────────────────┴───────────────────────┘
                         Interactions
```

## 1. Database Layer

### Overview

The database layer uses PostgreSQL with SQLModel as the ORM. It provides the data persistence layer for the entire application.

### Key Models

#### User Models
- `User`: Represents a user in the system
- `GullyParticipant`: Represents a user's participation in a gully

#### Gully Models
- `Gully`: Represents a cricket community/league

#### Player Models
- `Player`: Represents a cricket player
- `PlayerStats`: Stores player statistics

#### Game Mechanics Models
- `AuctionRound`: Represents auction rounds for player bidding
- `AuctionBid`: Represents user bids for players
- `TransferWindow`: Represents transfer windows for player trading
- `TransferListing`: Represents player listings in transfer windows
- `TransferBid`: Represents bids on transfer listings

### Database Initialization

The database is initialized in `src/db/init.py` using the following process:
1. Create database engine
2. Create tables if they don't exist
3. Initialize default data if needed

```python
async def init_db():
    """Initialize the database."""
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

### Database Session Management

Database sessions are managed in `src/db/session.py` using dependency injection:

```python
async def get_session() -> AsyncSession:
    """Get a database session."""
    async with AsyncSessionLocal() as session:
        yield session
```

## 2. API Layer

### Overview

The API layer is built with FastAPI and provides RESTful endpoints for interacting with the system. It follows a service-oriented architecture with clear separation of concerns.

### API Structure

```
src/api/
├── client_factory.py       # Factory for creating API clients
├── api_client_instance.py  # Singleton API client instance
├── dependencies.py         # FastAPI dependencies
├── exceptions.py           # Custom API exceptions
├── routes/                 # API route definitions
│   ├── __init__.py
│   ├── users.py
│   ├── gullies.py
│   ├── players.py
│   └── ...
├── schemas/                # Pydantic models for API
│   ├── __init__.py
│   ├── user.py
│   ├── gully.py
│   └── ...
└── services/               # Service clients for API
    ├── __init__.py
    ├── base.py             # Base service class
    ├── users/              # User service
    ├── gullies/            # Gully service
    └── ...
```

### Key Services

#### BaseService

The `BaseService` class in `src/api/services/base.py` provides common functionality for all API services:

```python
class BaseService:
    """Base class for all API services."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(follow_redirects=True)
        
    async def _get(self, url: str, params: Dict = None) -> Dict:
        """Make a GET request to the API."""
        # Implementation...
        
    async def _post(self, url: str, data: Dict = None, json_data: Dict = None) -> Dict:
        """Make a POST request to the API."""
        # Implementation...
        
    # Other HTTP methods...
```

#### UserService

The `UserService` class provides methods for user management:

```python
class UserService(BaseService):
    """Service for user-related operations."""
    
    def __init__(self, base_url: str):
        super().__init__(base_url)
        self.endpoint = f"{self.base_url}/users/"
        
    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get a user by Telegram ID."""
        # Implementation...
        
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        # Implementation...
        
    # Other user-related methods...
```

#### GullyService

The `GullyService` class provides methods for gully management:

```python
class GullyService(BaseService):
    """Service for gully-related operations."""
    
    def __init__(self, base_url: str):
        super().__init__(base_url)
        self.endpoint = f"{self.base_url}/gullies/"
        
    async def get_gully(self, gully_id: int) -> Optional[Dict[str, Any]]:
        """Get a gully by ID."""
        # Implementation...
        
    async def create_gully(self, name: str, telegram_group_id: int) -> Dict[str, Any]:
        """Create a new gully."""
        # Implementation...
        
    # Other gully-related methods...
```

### API Client Factory

The `APIClientFactory` class in `src/api/client_factory.py` creates and manages service clients:

```python
class APIClientFactory:
    """Factory for creating API clients."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self._services = {}
        
    @property
    def users(self) -> UserService:
        """Get the user service."""
        if "users" not in self._services:
            self._services["users"] = UserService(self.base_url)
        return self._services["users"]
        
    @property
    def gullies(self) -> GullyService:
        """Get the gully service."""
        if "gullies" not in self._services:
            self._services["gullies"] = GullyService(self.base_url)
        return self._services["gullies"]
        
    # Other service properties...
```

### API Routes

The API routes are defined in the `src/api/routes/` directory and are organized by domain:

```python
# src/api/routes/users.py
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{telegram_id}", response_model=UserResponse)
async def get_user(telegram_id: int, session: AsyncSession = Depends(get_session)):
    """Get a user by Telegram ID."""
    # Implementation...
    
@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    """Create a new user."""
    # Implementation...
    
# Other user-related endpoints...
```

### API Client Instance

The API client instance is created in `src/api/api_client_instance.py`:

```python
# src/api/api_client_instance.py
from src.api.client_factory import APIClientFactory

# Create a singleton API client instance
api_client = APIClientFactory(base_url="http://localhost:8000/api")
```

## 3. Bot Layer

### Overview

The bot layer is built with the python-telegram-bot library and provides a user interface for interacting with the system through Telegram.

### Bot Structure

```
src/bot/
├── bot.py                 # Main bot file
├── command_scopes.py      # Command scope definitions
├── middleware.py          # Bot middleware
├── services/              # Bot services
│   ├── __init__.py
│   ├── user_service.py    # User service
│   ├── gully_service.py   # Gully service
│   └── admin_service.py   # Admin service
├── handlers/              # Command handlers
│   ├── __init__.py
│   ├── help.py
│   ├── join_gully.py
│   └── ...
├── callbacks/             # Callback query handlers
│   ├── __init__.py
│   ├── auction.py
│   └── ...
├── keyboards/             # Keyboard definitions
│   ├── __init__.py
│   ├── admin.py
│   └── ...
└── utils/                 # Utility functions
    ├── __init__.py
    └── ...
```

### Bot Services

#### Bot User Service

The `UserService` class in `src/bot/services/user_service.py` provides methods for user management:

```python
class UserService:
    """Service for user-related operations."""
    
    @staticmethod
    async def ensure_user_exists(user: User) -> Dict[str, Any]:
        """Ensure a user exists in the database."""
        # Implementation...
        
    @staticmethod
    async def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get a user by Telegram ID."""
        # Implementation...
        
    # Other user-related methods...
```

#### Bot Gully Service

The `GullyService` class in `src/bot/services/gully_service.py` provides methods for gully management:

```python
class GullyService:
    """Service for gully-related operations."""
    
    @staticmethod
    async def create_gully(name: str, telegram_group_id: int, creator_telegram_id: int = None) -> Optional[Dict[str, Any]]:
        """Create a new gully."""
        # Implementation...
        
    @staticmethod
    async def set_group_owner_as_admin(chat_id: int, gully_id: int, bot: Bot) -> Dict[str, Any]:
        """Set the group owner as admin."""
        # Implementation...
        
    # Other gully-related methods...
```

#### Bot Admin Service

The `AdminService` class in `src/bot/services/admin_service.py` provides methods for admin management:

```python
class AdminService:
    """Service for admin-related operations."""
    
    @staticmethod
    async def check_admin_status(user_id: int, gully_id: int) -> bool:
        """Check if a user is an admin in a gully."""
        # Implementation...
        
    @staticmethod
    async def assign_admin_role(user_id: int, gully_id: int) -> Dict[str, Any]:
        """Assign admin role to a user."""
        # Implementation...
        
    # Other admin-related methods...
```

### Command Handlers

Command handlers are defined in the `src/bot/handlers/` directory and are organized by functionality:

```python
# src/bot/handlers/join_gully.py
async def join_gully_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the /join_gully command."""
    # Implementation...
    
async def handle_gully_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the /join_gully command in a gully chat."""
    # Implementation...
    
# Other join gully-related handlers...
```

### Callback Query Handlers

Callback query handlers are defined in the `src/bot/callbacks/` directory:

```python
# src/bot/callbacks/auction.py
async def handle_auction_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle auction-related callback queries."""
    # Implementation...
```

### Command Scopes

Command scopes are defined in `src/bot/command_scopes.py`:

```python
async def setup_command_scopes(application: Application) -> None:
    """Set up command scopes for the bot."""
    # Implementation...
```

### Bot Middleware

Bot middleware is defined in `src/bot/middleware.py`:

```python
async def gully_context_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE, callback: Callable) -> Any:
    """Middleware for adding gully context to updates."""
    # Implementation...
    
async def new_chat_members_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle new chat members."""
    # Implementation...
```

### Bot Initialization

The bot is initialized in `src/bot/bot.py`:

```python
async def main_async():
    """Initialize and start the bot."""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("game_guide", game_guide_command))
    # More handlers...
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Set up command scopes
    await refresh_command_scopes(application)
    
    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
```

## Component Interactions

### Bot to API Interaction

The bot interacts with the API through the API client instance:

```python
# src/bot/services/gully_service.py
from src.api.api_client_instance import api_client

class GullyService:
    @staticmethod
    async def create_gully(name: str, telegram_group_id: int, creator_telegram_id: int = None) -> Optional[Dict[str, Any]]:
        try:
            gully_data = {
                "name": name,
                "telegram_group_id": telegram_group_id
            }
            return await api_client.gullies.create_gully(**gully_data)
        except Exception as e:
            logger.error(f"Error creating gully: {e}")
            return None
```

### API to Database Interaction

The API interacts with the database through SQLModel and the database session:

```python
# src/api/routes/users.py
@router.get("/{telegram_id}", response_model=UserResponse)
async def get_user(telegram_id: int, session: AsyncSession = Depends(get_session)):
    """Get a user by Telegram ID."""
    user = await session.exec(
        select(User).where(User.telegram_id == telegram_id)
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user
```

### Database to API Interaction

The database provides data to the API through SQLModel queries:

```python
# src/api/routes/gullies.py
@router.get("/{gully_id}/participants", response_model=List[GullyParticipantResponse])
async def get_gully_participants(gully_id: int, session: AsyncSession = Depends(get_session)):
    """Get all participants of a gully."""
    participants = await session.exec(
        select(GullyParticipant).where(GullyParticipant.gully_id == gully_id)
    ).all()
    
    return participants
```

## Function Reference

### API Functions

#### User API Functions

| Function | Description |
|----------|-------------|
| `get_user(telegram_id)` | Get a user by Telegram ID |
| `create_user(user_data)` | Create a new user |
| `update_user(telegram_id, user_data)` | Update an existing user |
| `get_user_by_id(user_id)` | Get a user by database ID |

#### Gully API Functions

| Function | Description |
|----------|-------------|
| `get_all_gullies()` | Get all gullies |
| `get_gully(gully_id)` | Get a gully by ID |
| `get_gully_by_group(group_id)` | Get a gully by Telegram group ID |
| `create_gully(name, telegram_group_id)` | Create a new gully |
| `get_gully_participants(gully_id)` | Get participants of a gully |
| `add_user_to_gully(user_id, gully_id, role)` | Add a user to a gully |

#### Admin API Functions

| Function | Description |
|----------|-------------|
| `get_gully_admins(gully_id)` | Get all admins of a gully |
| `assign_admin_role(user_id, gully_id)` | Assign admin role to a user |
| `remove_admin_role(user_id, gully_id)` | Remove admin role from a user |

### Bot Functions

#### User Bot Functions

| Function | Description |
|----------|-------------|
| `ensure_user_exists(user)` | Ensure a user exists in the database |
| `get_user(telegram_id)` | Get a user by Telegram ID |
| `get_user_by_id(user_id)` | Get a user by database ID |
| `update_user(telegram_id, user_data)` | Update a user's data |
| `get_active_gully(user_id)` | Get the user's active gully |
| `set_active_gully(user_id, gully_id)` | Set a gully as active for a user |

#### Gully Bot Functions

| Function | Description |
|----------|-------------|
| `create_gully(name, telegram_group_id, creator_telegram_id)` | Create a new gully |
| `set_group_owner_as_admin(chat_id, gully_id, bot)` | Set group owner as admin |
| `get_gully(gully_id)` | Get a gully by ID |
| `get_gully_by_group(group_id)` | Get a gully by group ID |
| `add_user_to_gully(user_id, gully_id, role)` | Add a user to a gully |
| `get_gully_participants(gully_id)` | Get all participants in a gully |
| `get_user_gully_participations(user_id)` | Get all gullies a user is in |
| `get_active_gullies()` | Get all active gullies |
| `scan_and_setup_groups(bot)` | Scan groups and set up gullies |

#### Admin Bot Functions

| Function | Description |
|----------|-------------|
| `check_admin_status(user_id, gully_id)` | Check if a user is an admin |
| `assign_admin_role(user_id, gully_id)` | Assign admin role to a user |
| `get_gully_admins(gully_id)` | Get all admins for a gully |
| `remove_admin_role(user_id, gully_id)` | Remove admin role from a user |

### Command Handlers

| Handler | Description |
|---------|-------------|
| `help_command(update, context)` | Handle the /help command |
| `game_guide_command(update, context)` | Handle the /game_guide command |
| `join_gully_command(update, context)` | Handle the /join_gully command |
| `my_team_command(update, context)` | Handle the /myteam command |
| `admin_panel_command(update, context)` | Handle the /admin_panel command |
| `add_member_command(update, context)` | Handle the /add_member command |
| `create_gully_command(update, context)` | Handle the /create_gully command |
| `manage_admins_command(update, context)` | Handle the /manage_admins command |

## Best Practices

1. **Service-Oriented Architecture**: Use services for business logic
2. **Dependency Injection**: Use dependency injection for database sessions
3. **Error Handling**: Use proper error handling and logging
4. **Type Hints**: Use type hints for better code quality
5. **Documentation**: Document all functions and classes
6. **Testing**: Write tests for all components
7. **Separation of Concerns**: Keep components separate and focused
8. **Consistent Naming**: Use consistent naming conventions
9. **Configuration Management**: Use environment variables for configuration
10. **Logging**: Use proper logging for debugging and monitoring

## Conclusion

The GullyGuru system is built with a modern, service-oriented architecture that separates concerns and provides a clean interface for each component. The database layer provides data persistence, the API layer provides a RESTful interface, and the bot layer provides a user interface through Telegram. The components interact through well-defined interfaces, making the system modular and maintainable. 