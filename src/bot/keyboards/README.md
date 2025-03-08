# GullyGuru Keyboard Modules

This directory contains keyboard modules for the GullyGuru Telegram bot. These modules provide functions for creating interactive keyboards for various bot features.

## Telegram Command Types and UI Approach

The GullyGuru bot uses a combination of slash commands and inline keyboards:

- **Slash Commands** are used for simple, direct actions (e.g., `/myteam`, `/bid`, `/game_guide`)
- **Inline Keyboards** (defined in this directory) are used for multi-step or complex interactions

For more details on the command structure and rationale, see the [User Management Documentation](../../docs/user_management.md).

## Streamlined Structure

The keyboard modules have been streamlined to focus on essential functionality for the core command set. Each module is organized by feature area:

### auction.py
- `get_auction_keyboard`: Creates a keyboard for auction actions
- `get_bid_keyboard`: Creates a keyboard with bid options
- `get_squad_selection_keyboard`: Creates a keyboard for squad selection during Round 0
- `get_time_slot_voting_keyboard`: Creates a keyboard for time slot voting

### common.py
- `get_back_button`: Creates a keyboard with just a back button
- `get_pagination_keyboard`: Creates a keyboard for pagination with previous and next buttons
- `get_confirmation_keyboard`: Creates a keyboard with confirm and cancel buttons

### games.py
- `get_match_list_keyboard`: Creates a keyboard for displaying a list of matches
- `get_match_details_keyboard`: Creates a keyboard for match details

### gullies.py
- `get_gully_list_keyboard`: Creates a keyboard for displaying a list of gullies
- `get_gully_context_keyboard`: Creates a keyboard showing the current gully context

### players.py
- `get_player_filters_keyboard`: Creates a keyboard for filtering players by team and type
- `get_player_details_keyboard`: Creates a keyboard for player details
- `get_my_team_keyboard`: Creates a keyboard for viewing and managing user's team

### transfers.py
- `get_transfer_menu_keyboard`: Creates a keyboard for the transfer menu based on window status
- `get_player_listing_keyboard`: Creates a keyboard for viewing a specific player listing
- `get_bid_confirmation_keyboard`: Creates a keyboard for confirming a bid
- `get_player_listing_keyboard_for_list`: Creates a keyboard with buttons for each player listing

## Callback Data Patterns

The keyboard modules use consistent callback data patterns:

- `back_to_*`: Navigation back to a specific section
- `*_page_*`: Pagination within a list
- `*_noop`: No-operation callbacks (used for display-only buttons)
- `select_*`: Selection actions
- `filter_*`: Filter actions
- `transfer_*`: Transfer-related actions
- `match_*`: Match-related actions
- `view_player_*`: Player detail actions
- `squad_*`: Squad selection actions

## Usage Guidelines

When using these keyboard modules:

1. Import the appropriate keyboard module for your feature
2. Call the relevant function with the required parameters
3. Use the returned `InlineKeyboardMarkup` in your message

Example:
```python
from src.bot.keyboards.players import get_my_team_keyboard

# Get the user's team data
team_players = await api_client.get_user_team(user_id)
captain_id = await api_client.get_team_captain(user_id)

# Create the keyboard
keyboard = get_my_team_keyboard(team_players, captain_id)

# Use the keyboard in a message
await update.message.reply_text(
    "Here is your team:",
    reply_markup=keyboard
) 