# GullyGuru Bot

This module contains the Telegram bot implementation for GullyGuru.

## Refactoring Summary

The bot code has been refactored to use the API services directly instead of having separate bot-level services. This simplifies the architecture and reduces code duplication.

### Changes Made:
1. Removed all bot-level services in `src/bot/services/`
2. Updated all feature modules to use the API client directly
3. Removed unused files (middleware.py and utils/ directory)
4. Added placeholder implementations for missing API services

### Missing API Services:
See the main README.md file for a list of API services that need to be implemented.

## Architecture

The bot is structured as follows:

- `bot.py`: Main entry point that initializes the bot and registers handlers
- `features/`: Contains feature modules that implement bot commands and callbacks
- `command_scopes.py`: Handles command scope management

## API Integration

The bot directly uses the API services from `src/api/services` through the `api_client` instance from `src/api/api_client_instance.py`. This eliminates the need for separate bot-level services.

### API Client Usage

To use the API client in a feature module:

```python
from src.api.api_client_instance import api_client

# Example: Get a user
user = await api_client.users.get_user(telegram_id)

# Example: Create a gully
gully = await api_client.gullies.create_gully(
    name="My Gully",
    telegram_group_id=chat_id
)
```

## Flows

This section documents the key user flows in the GullyGuru bot.

### Automatic User Onboarding Flow

The bot automatically handles user onboarding without requiring any commands:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Bot starts up                                                  │
│  [bot.py → main_async]                                          │
│                                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  System scans all groups the bot is a member of                 │
│  [sync_manager.py → sync_all_groups]                            │
│                                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  For each group, system creates a gully if it doesn't exist     │
│  [sync_manager.py → create_or_get_gully]                        │
│                                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  System identifies group admins and adds them as gully admins   │
│  [sync_manager.py → sync_group_members]                         │
│                                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  When new members join a group, they are automatically added    │
│  to the gully as members                                        │
│  [gully.py → new_chat_members_handler]                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Key Features of Automatic Onboarding:

1. **No Commands Required**: Users are automatically added to gullies when they join a group
2. **Admin Detection**: Group admins are automatically made gully admins
3. **Background Processing**: All synchronization happens in the background
4. **Separation of Roles**: Admins are not added as gully participants, only as admins

#### Implementation Notes:

- The system relies on Telegram's new member events to detect when users join a group
- Group admins are detected using the getChatAdministrators API
- The initial sync happens when the bot starts up
- New members are automatically added when they join a group

### Admin Panel Flow

The admin panel is accessible only in private chats and provides administrators with tools to manage their gullies.

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  User sends /admin_panel command in private chat                │
│  [Telegram → admin_panel_command]                               │
│                                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  System retrieves all gullies where user is an admin            │
│  [admin_panel_command → API client]                             │
│                                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  System displays list of gullies as inline keyboard buttons     │
│  [admin_panel_command → Telegram]                               │
│                                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  User selects a gully from the list                             │
│  [Telegram → handle_admin_callback]                             │
│                                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  System displays admin options for selected gully:              │
│  - Prompt Members                                               │
│  - Manage Auction                                               │
│  - Back to Gully List                                           │
│  [handle_admin_callback → Telegram]                             │
│                                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│                               │   │                               │
│  User selects "Prompt Members"│   │  User selects "Manage Auction"│
│  [Telegram → handle_admin_    │   │  [Telegram → handle_admin_    │
│   callback]                   │   │   callback]                   │
│                               │   │                               │
└───────────────┬───────────────┘   └───────────────┬───────────────┘
                │                                   │
                ▼                                   ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│                               │   │                               │
│  System asks for confirmation │   │  System displays auction      │
│  to send reminders            │   │  management options:          │
│  [handle_admin_callback →     │   │  - Start Auction              │
│   Telegram]                   │   │  - Back to Admin Panel        │
│                               │   │  [handle_admin_callback →     │
└───────────────┬───────────────┘   │   Telegram]                   │
                │                   │                               │
                │                   └───────────────┬───────────────┘
                ▼                                   │
┌───────────────────────────────┐                   │
│                               │                   │
│  User confirms sending        │                   │
│  reminders                    │                   │
│  [Telegram → handle_admin_    │                   │
│   callback]                   │                   │
│                               │                   │
└───────────────┬───────────────┘                   │
                │                                   │
                ▼                                   ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│                               │   │                               │
│  System retrieves members     │   │  User selects "Start Auction" │
│  without teams                │   │  [Telegram → handle_auction_  │
│  [handle_admin_callback →     │   │   callback]                   │
│   API client]                 │   │                               │
│                               │   └───────────────┬───────────────┘
└───────────────┬───────────────┘                   │
                │                                   │
                ▼                                   ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│                               │   │                               │
│  System sends reminders to    │   │  System starts the auction    │
│  members without teams        │   │  process for the selected     │
│  [handle_admin_callback →     │   │  gully                        │
│   Telegram]                   │   │  [handle_auction_callback →   │
│                               │   │   API client & Telegram]      │
└───────────────┬───────────────┘   │                               │
                │                   └───────────────────────────────┘
                ▼
┌───────────────────────────────┐
│                               │
│  System displays confirmation │
│  with count of reminders sent │
│  [handle_admin_callback →     │
│   Telegram]                   │
│                               │
└───────────────────────────────┘
```

#### Key Features of Admin Panel:

1. **Private Chat Only**: The admin panel is only accessible in private chats with the bot, not in group chats.
2. **Multi-Gully Management**: Admins can manage all gullies where they have admin privileges from a single interface.
3. **Prompt Members**: Admins can send reminders to members who haven't created their teams yet.
4. **Auction Management**: Admins can start auctions for their gullies.

#### Implementation Notes:

- The admin panel uses inline keyboard buttons for navigation
- Each action includes confirmation steps for important operations
- The flow maintains context about which gully is being managed
- All admin actions are validated against the user's admin privileges

# GullyGuru Bot Features

This directory contains the feature modules for the GullyGuru Telegram bot. Each feature module encapsulates a specific functionality of the bot, making the codebase more maintainable and easier to extend.

## Feature Modules

The bot is organized into the following feature modules:

### 1. Admin (`admin.py`)
Handles admin panel and member management:
- `/admin_panel` - Shows admin options for gully management in private chats
- Allows admins to prompt members to create teams
- Allows admins to manage auctions

### 2. Auction (`auction.py`)
Handles player auctions, bidding, and auction status:
- `/auction_status` - Shows the current auction status for the gully
- Callback handlers for bidding and auction management

### 3. Gully (`gully.py`)
Handles automatic user onboarding:
- Automatically creates gullies for groups
- Automatically adds new members to gullies
- Automatically sets group admins as gully admins

### 4. Team (`team.py`)
Handles team viewing and management:
- `/my_team` - Shows the user's current team composition
- Callback handlers for team management

## Handler Registration

All handlers are registered in the `__init__.py` file, which provides a single entry point for adding handlers to the application. This makes it easy to add new features without modifying the main bot file.

## Adding New Features

To add a new feature:

1. Create a new file in the `features` directory (e.g., `new_feature.py`)
2. Define your command and callback handlers in the file
3. Import your handlers in `__init__.py`
4. Add your handlers to the `register_handlers` function in `__init__.py`

## Command Scopes

Command scopes are managed in the `command_scopes.py` file in the parent directory. If you add new commands, make sure to update the command scopes accordingly. 