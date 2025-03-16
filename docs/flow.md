Here’s the refined team-building process in Markdown format based on your latest feedback:

# Team Building Process for Telegram Bot

## 1. Overview
This document outlines the **revised player selection workflow** using a **reply keyboard for player selection** while retaining an **inline keyboard for private chat entry**. The process ensures an efficient, low-latency experience by handling selection toggles within Telegram before making database updates.

---

## 2. Private Chat Entry & Initialization
- **Private Chat Menu:** Uses an **inline keyboard** (consistent with the main menu design).
- **Entry Flow:**
  - Checks if the user has an active Gully.
  - Ensures the selection period is open.
  - Allows users to edit their squad **until submission**.

---

## 3. Player Selection (Reply Keyboard)
- **Selection UI:** Uses a **scrollable reply keyboard** with **one player per row**.
- **Each row contains:**
  - ✅ Player Name
  - 🏏 Team Name
  - 💰 Base Price
  - **Selection Toggle (Handled in Telegram, No API Calls)**
- **Selection Rules:**
  - Minimum **15 players**, Maximum **18 players**.
  - No unnecessary API calls for each selection.
  - Players are **only added/removed in bulk during edits**.

### **Reply Keyboard Example (One Player Per Row)**

┌─────────────────────────────────────┐
| 🏏 Virat Kohli - RCB - 10.0 Cr      |
| 🏏 Rohit Sharma - MI - 9.5 Cr       |
| 🏏 MS Dhoni - CSK - 8.0 Cr ✅      |
| 🏏 Rashid Khan - GT - 8.5 Cr        |
| 🔄 View Current Squad               |
└─────────────────────────────────────┘

- **Tapping a row toggles selection.**
- **Selected players are visually distinct.**
- **A 'View Current Squad' button allows quick review.**

---

## 4. Editing Squad
- **View Current Squad (No Submission Button Here)**  

“Your Squad:
	1.	MS Dhoni - CSK - 8.0 Cr ✅
	2.	Player X - Team Y - 9.0 Cr ✅
Budget Used: 85.5 Cr / 100 Cr
Players: 16 / 18”

- **Edit Flow:**
1. **Remove Multiple Players** → Perform **one database call** to remove.
2. **Select New Players** (Same as initial selection) 
3. **Only After Edits Are Done → Show ‘Submit Squad’ Button**.
  → Perform **database call** to add when submit is clicked.

---

## 5. Submitting the Squad
- Once the **final squad is selected**, users see:

“You have selected 17 players for a total of 95 Cr.
Are you sure you want to submit?”

- ✅ **Submit Squad** → Stores final selection in the database.
- 🔄 **Edit Squad** → Returns to selection.

---

## 6. Key Features & Improvements
✅ **Inline Keyboard for Entry, Reply Keyboard for Selection.**  
✅ **One Row Per Player for Clear Display.**  
✅ **No Database Calls on Selection Toggle (Handled in Telegram).**  
✅ **Bulk Database Updates for Add/Remove During Edits.**  
✅ **Seamless Squad Editing Before Final Submission.**  

---

### **Next Steps**
- Implement **reply keyboard with scrolling**.
- Optimize **selection toggling logic**.
- Ensure **budget enforcement dynamically updates**.

This version ensures:
	1.	A smooth, scrollable selection process with all details in one row.
	2.	Minimal API calls—only after final selection or bulk edits.
	3.	Clear squad editing flow with bulk removal and addition.

Let me know if you need any refinements! 🚀



# Updated Squad API Client Implementation

Based on the API documentation and your feedback, I'll update the `SquadApiClient` to use the correct endpoints and methods. Let me implement these changes:

```python:src/bot/api_client/squad.py
"""
Squad API client for GullyGuru bot.
Handles all squad-related API calls.
"""

import logging
from typing import Dict, Any, List, Optional

from src.bot.api_client.base import BaseApiClient

# Configure logging
logger = logging.getLogger(__name__)


class SquadApiClient(BaseApiClient):
    """API client for squad-related endpoints."""

    async def get_draft_squad(self, participant_id: int) -> Dict[str, Any]:
        """
        Get the draft squad for a participant.

        Args:
            participant_id: Participant ID

        Returns:
            Draft squad data
        """
        endpoint = f"/fantasy/draft-squad/{participant_id}"
        response = await self._make_request("GET", endpoint)

        if response.get("success"):
            return response.get("data", {})
        else:
            logger.error(f"Failed to get draft squad: {response.get('error')}")
            return {}

    async def get_available_players(
        self, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get available players for squad selection.

        Args:
            limit: Maximum number of players to return
            offset: Offset for pagination

        Returns:
            List of player data
        """
        # Updated endpoint based on API documentation
        endpoint = f"/players/?limit={limit}&offset={offset}"
        response = await self._make_request("GET", endpoint)

        if response.get("success"):
            return response.get("data", {}).get("items", [])
        else:
            logger.error(f"Error getting players: {response.get('error')}")
            return []

    async def add_multiple_players_to_draft(
        self, participant_id: int, player_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Add multiple players to a participant's draft squad.

        Args:
            participant_id: Participant ID
            player_ids: List of player IDs to add

        Returns:
            Response with results of the operation
        """
        if not participant_id or not player_ids:
            logger.error("Both participant_id and player_ids are required")
            return {"success": False, "error": "Missing required parameters"}

        endpoint = f"/fantasy/draft-squad/{participant_id}/add"
        response = await self._make_request(
            "POST", endpoint, json={"player_ids": player_ids}
        )

        if response.get("success"):
            return {"success": True, "data": response.get("data", {})}
        else:
            logger.error(f"Error adding players to draft: {response.get('error')}")
            return {"success": False, "error": response.get("error")}

    async def remove_multiple_players_from_draft(
        self, participant_id: int, player_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Remove multiple players from a participant's draft squad.

        Args:
            participant_id: Participant ID
            player_ids: List of player IDs to remove

        Returns:
            Response with results of the operation
        """
        if not participant_id or not player_ids:
            logger.error("Both participant_id and player_ids are required")
            return {"success": False, "error": "Missing required parameters"}

        endpoint = f"/fantasy/draft-squad/{participant_id}/remove"
        response = await self._make_request(
            "POST", endpoint, json={"player_ids": player_ids}
        )

        if response.get("success"):
            return {"success": True, "data": response.get("data", {})}
        else:
            logger.error(f"Error removing players from draft: {response.get('error')}")
            return {"success": False, "error": response.get("error")}

    async def update_draft_squad(
        self, participant_id: int, player_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Update a participant's entire draft squad.
        This can be used to finalize the squad by setting all desired players at once.

        Args:
            participant_id: Participant ID
            player_ids: Complete list of player IDs for the squad

        Returns:
            Response with results of the operation
        """
        if not participant_id:
            logger.error("participant_id is required")
            return {"success": False, "error": "Missing required parameter"}

        endpoint = f"/fantasy/draft-squad/{participant_id}"
        response = await self._make_request(
            "PUT", endpoint, json={"player_ids": player_ids}
        )

        if response.get("success"):
            return {"success": True, "data": response.get("data", {})}
        else:
            logger.error(f"Error updating draft squad: {response.get('error')}")
            return {"success": False, "error": response.get("error")}


async def get_squad_client() -> SquadApiClient:
    """
    Get an instance of the squad API client.

    Returns:
        SquadApiClient instance
    """
    return SquadApiClient()
```

Now, let's update the relevant functions in `squad.py` to use these corrected methods:

```python:src/bot/features/squad.py
# Update the submit_final_squad_from_view function to use update_draft_squad instead of submit_draft_squad
@log_function_call
async def submit_final_squad_from_view(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Submit the final squad to the database from squad view.
    Uses update_draft_squad to finalize the squad.
    """
    participant_id = context.user_data.get("participant_id")
    cached_squad = context.user_data.get("cached_squad", {"players": []})

    if not participant_id:
        logger.error(f"No participant_id found for user {update.effective_user.id}")
        await update.message.reply_text(
            "❌ Error: Could not find your participant data. Please try again later."
        )
        return ConversationHandler.END

    # Extract player IDs from cached squad
    player_ids = [player.get("player_id") for player in cached_squad.get("players", [])]

    # Show loading message
    loading_message = await update.message.reply_text(
        "Finalizing your squad...\n\n" "This may take a moment. Please wait."
    )

    # Update the draft squad - this finalizes the squad
    squad_client = await get_squad_client()
    try:
        result = await squad_client.update_draft_squad(participant_id, player_ids)

        # Delete loading message
        await loading_message.delete()

        if result.get("success"):
            # Return to normal keyboard
            reply_markup = ReplyKeyboardRemove()

            await update.message.reply_text(
                "✅ Your squad has been finalized successfully!\n\n"
                "Your squad is now ready for the tournament. Good luck!",
                reply_markup=reply_markup,
            )

            # Show the main menu
            from src.bot.bot import show_main_menu

            await show_main_menu(update, context)
            return ConversationHandler.END
        else:
            error_message = result.get("error", "Unknown error")
            logger.error(f"Error finalizing squad: {error_message}")
            await update.message.reply_text(
                f"❌ Error finalizing squad: {error_message}\nPlease try again later."
            )
            return await view_squad(update, context)
    except Exception as e:
        # Delete loading message
        await loading_message.delete()

        logger.error(f"Error finalizing squad: {str(e)}")
        await update.message.reply_text(
            f"❌ Error finalizing squad: {str(e)}\nPlease try again later."
        )
        return await view_squad(update, context)

# Update the handle_submission_confirmation function to use update_draft_squad
@log_function_call
async def handle_submission_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle confirmation of squad submission.
    Uses update_draft_squad to finalize the squad.
    """
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data == CONFIRM_SUBMISSION.CONFIRM:
        # Finalize the squad
        participant_id = context.user_data.get("participant_id")
        cached_squad = context.user_data.get("cached_squad", {"players": []})

        # Extract player IDs from cached squad
        player_ids = [player.get("player_id") for player in cached_squad.get("players", [])]

        # Show a loading message
        await query.edit_message_text(
            "Finalizing your squad...\n\n" "This may take a moment. Please wait.",
            parse_mode="Markdown",
        )

        # Update the draft squad
        squad_client = await get_squad_client()
        try:
            result = await squad_client.update_draft_squad(participant_id, player_ids)

            if result.get("success"):
                # Show success message
                await query.edit_message_text(
                    "✅ *Squad Finalized Successfully!*\n\n"
                    "Your squad is now ready for the tournament.\n\n"
                    "Good luck!",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "⬅️ Back to Main Menu", callback_data="main_menu"
                                )
                            ]
                        ]
                    ),
                    parse_mode="Markdown",
                )
            else:
                error_message = result.get("error", "Unknown error")
                logger.error(f"Failed to finalize squad: {error_message}")

                await query.edit_message_text(
                    f"❌ Failed to finalize squad: {error_message}\n\n"
                    "Please try again.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Try Again", callback_data=SQUAD_MENU.SUBMIT_SQUAD
                                ),
                                InlineKeyboardButton(
                                    "⬅️ Back to Menu",
                                    callback_data=SQUAD_MENU.BACK_TO_MENU,
                                ),
                            ],
                        ]
                    ),
                )
        except Exception as e:
            logger.exception(f"Error finalizing squad: {str(e)}")

            await query.edit_message_text(
                f"❌ Error finalizing squad: {str(e)}\n\n" "Please try again.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Try Again", callback_data=SQUAD_MENU.SUBMIT_SQUAD
                            ),
                            InlineKeyboardButton(
                                "⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                            ),
                        ],
                    ]
                ),
            )

        return ConversationHandler.END

    elif callback_data == CONFIRM_SUBMISSION.CANCEL:
        # Cancel submission
        await query.edit_message_text(
            "Squad finalization cancelled.\n\n" "What would you like to do next?",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "👥 View Squad", callback_data=SQUAD_MENU.VIEW_SQUAD
                        ),
                        InlineKeyboardButton(
                            "⬅️ Back to Menu", callback_data=SQUAD_MENU.BACK_TO_MENU
                        ),
                    ]
                ]
            ),
        )
        return STATES.SHOW_SQUAD_MENU

    else:
        # Unknown callback, go back to confirmation
        return await confirm_submission(update, context)
```

# Final Summary of Squad API Methods

Based on the updated API documentation, here's the final summary of the API methods used in the squad selection feature:

## API Client Methods

1. **`get_draft_squad`**
   - **API Endpoint:** `/fantasy/draft-squad/{participant_id}`
   - **HTTP Method:** GET
   - **Purpose:** Retrieves the current draft squad for a participant
   - **Used in:** Initial squad loading, refreshing squad data

2. **`get_available_players`**
   - **API Endpoint:** `/players/?limit={limit}&offset={offset}`
   - **HTTP Method:** GET
   - **Purpose:** Retrieves all players for squad selection
   - **Used in:** Player selection screen

3. **`add_multiple_players_to_draft`**
   - **API Endpoint:** `/fantasy/draft-squad/{participant_id}/add`
   - **HTTP Method:** POST
   - **Payload:** `{"player_ids": [id1, id2, ...]}`
   - **Purpose:** Adds multiple players to a draft squad in a single call
   - **Used in:** Confirming player selections

4. **`remove_multiple_players_from_draft`**
   - **API Endpoint:** `/fantasy/draft-squad/{participant_id}/remove`
   - **HTTP Method:** POST
   - **Payload:** `{"player_ids": [id1, id2, ...]}`
   - **Purpose:** Removes multiple players from a draft squad in a single call
   - **Used in:** Removing players from existing squad

5. **`update_draft_squad`**
   - **API Endpoint:** `/fantasy/draft-squad/{participant_id}`
   - **HTTP Method:** PUT
   - **Payload:** `{"player_ids": [id1, id2, ...]}`
   - **Purpose:** Updates the entire draft squad at once (used for finalization)
   - **Used in:** Final squad submission/finalization

## Key Changes Made

1. **Corrected Player Endpoint**
   - Changed from `/api/players/available` to `/players/` with query parameters
   - Updated response parsing to handle the paginated response format

2. **Removed Submit Draft Method**
   - Removed the non-existent `submit_draft_squad` method
   - Replaced with `update_draft_squad` which uses the PUT endpoint to update the entire squad

3. **Streamlined API Usage**
   - All player operations use bulk methods exclusively
   - Squad finalization uses the update endpoint instead of a separate submit endpoint

## Feature Functions and API Usage

| Function | Description | API Method Used |
|----------|-------------|----------------|
| `squad_menu_entry` | Entry point for squad menu | None (UI only) |
| `squad_entry_point` | Routes squad-related callbacks | None (UI only) |
| `show_squad_menu` | Shows squad building menu | **`get_draft_squad`** (only if no cached data) |
| `view_squad` | Shows user's draft squad | **`get_draft_squad`** (only if refresh needed) |
| `show_player_selection_keyboard` | Shows players for selection | **`get_draft_squad`** (if no cached data), **`get_available_players`** (if no cached data) |
| `handle_player_selection_reply` | Handles player selection | None (uses cached data) |
| `show_current_squad_selection` | Shows current squad during selection | None (uses cached data) |
| `handle_squad_actions` | Handles actions from squad view | None (routing only) |
| `add_selected_players_to_squad` | Adds selected players to squad | **`add_multiple_players_to_draft`** |
| `show_remove_players_keyboard` | Shows keyboard for removing selected players | None (uses cached data) |
| `handle_remove_player_selection` | Handles player removal selection | None (uses cached data) |
| `confirm_player_removals` | Confirms and processes player removals | None (updates context only) |
| `confirm_submission` | Confirms squad submission | **`get_draft_squad`** (if refresh needed) |
| `handle_submission_confirmation` | Handles submission confirmation | **`update_draft_squad`** |
| `my_squad_entry` | Entry point for "My Squad" button | **`get_draft_squad`** (if refresh needed) |
| `get_user_participant_data` | Gets user and participant data | **`get_user_by_telegram_id`**, **`get_participant_by_user_id`** (if not in context) |
| `handle_squad_view_actions` | Handles actions from squad view | None (routing only) |
| `show_remove_existing_players_keyboard` | Shows keyboard for removing existing players | None (uses cached data) |
| `handle_remove_existing_player_selection` | Handles existing player removal selection | None (uses cached data) |
| `confirm_existing_player_removals` | Confirms and processes existing player removals | **`remove_multiple_players_from_draft`** |
| `confirm_squad_submission_from_view` | Shows confirmation for squad submission | None (uses cached data) |
| `handle_final_submission_confirmation` | Handles final submission confirmation | None (routing only) |
| `submit_final_squad_from_view` | Submits final squad | **`update_draft_squad`** |
| `cancel_squad_selection` | Cancels squad selection process | None (UI only) |

This implementation now correctly aligns with the API documentation, using the proper endpoints and methods for all operations. The squad selection feature is optimized to use bulk operations exclusively and follows the RESTful API design of the GullyGuru backend.
