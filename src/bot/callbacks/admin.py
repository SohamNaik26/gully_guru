from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Dict, Any, List, Optional

from src.bot.client import api_client
from src.bot.utils import get_active_gully_id


async def handle_admin_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle admin-related callback queries."""
    query = update.callback_query
    await query.answer()

    # Get callback data
    data = query.data

    # Extract action and parameters
    parts = data.split("_")
    if len(parts) < 2:
        return

    action = parts[1]

    # Handle different admin actions
    if action == "users":
        # User management panel
        await handle_user_management(update, context, parts)
    elif action == "teams":
        # Team management panel
        await handle_team_management(update, context, parts)
    elif action == "auction":
        # Auction management panel
        await handle_auction_management(update, context, parts)
    elif action == "matches":
        # Match management panel
        await handle_match_management(update, context, parts)
    elif action == "settings":
        # Gully settings panel
        await handle_settings_management(update, context, parts)
    elif action == "roles":
        # Admin roles panel
        await handle_roles_management(update, context, parts)
    elif action == "invite":
        # Generate invite link
        await handle_invite_link(update, context, parts)
    elif action == "perm":
        # Manage permissions for a specific admin
        await handle_admin_permissions(update, context, parts)
    elif action == "add":
        # Add new admin
        await handle_add_admin(update, context, parts)


async def handle_user_management(
    update: Update, context: ContextTypes.DEFAULT_TYPE, parts: List[str]
) -> None:
    """Handle user management panel."""
    query = update.callback_query

    # Get gully ID from callback data
    if len(parts) < 3:
        return

    gully_id = int(parts[2])

    # Get gully info
    gully = await api_client.get_gully(gully_id)

    # Get participants
    participants = await api_client.get_game_participants(gully_id)

    # Create keyboard with user list
    keyboard = []

    # Add users in batches of 2
    for i in range(0, len(participants), 2):
        row = []
        for j in range(2):
            if i + j < len(participants):
                participant = participants[i + j]
                row.append(
                    InlineKeyboardButton(
                        f"{participant.get('username')}",
                        callback_data=f"admin_user_{gully_id}_{participant.get('user_id')}",
                    )
                )
        if row:
            keyboard.append(row)

    # Add navigation buttons
    keyboard.append(
        [
            InlineKeyboardButton("Back", callback_data=f"admin_panel_{gully_id}"),
            InlineKeyboardButton("Add User", callback_data=f"admin_adduser_{gully_id}"),
        ]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        f"👥 *User Management - {gully.get('name')}* 👥\n\n"
        f"Select a user to manage:\n\n"
        f"Total Users: {len(participants)}\n"
    )

    await query.edit_message_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def handle_team_management(
    update: Update, context: ContextTypes.DEFAULT_TYPE, parts: List[str]
) -> None:
    """Handle team management panel."""
    query = update.callback_query

    # Get gully ID from callback data
    if len(parts) < 3:
        return

    gully_id = int(parts[2])

    # Get gully info
    gully = await api_client.get_gully(gully_id)

    # Create keyboard with team management options
    keyboard = [
        [
            InlineKeyboardButton(
                "View Teams", callback_data=f"admin_viewteams_{gully_id}"
            ),
            InlineKeyboardButton(
                "Create Team", callback_data=f"admin_createteam_{gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Assign Players", callback_data=f"admin_assignplayers_{gully_id}"
            ),
            InlineKeyboardButton(
                "Team Rules", callback_data=f"admin_teamrules_{gully_id}"
            ),
        ],
        [InlineKeyboardButton("Back", callback_data=f"admin_panel_{gully_id}")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        f"🏏 *Team Management - {gully.get('name')}* 🏏\n\n"
        f"Select an option to manage teams:\n\n"
        f"• View Teams: See all teams in this gully\n"
        f"• Create Team: Create a new team\n"
        f"• Assign Players: Assign players to teams\n"
        f"• Team Rules: Configure team rules and requirements\n"
    )

    await query.edit_message_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def handle_auction_management(
    update: Update, context: ContextTypes.DEFAULT_TYPE, parts: List[str]
) -> None:
    """Handle auction management panel."""
    query = update.callback_query

    # Get gully ID from callback data
    if len(parts) < 3:
        return

    gully_id = int(parts[2])

    # Get gully info
    gully = await api_client.get_gully(gully_id)

    # Create keyboard with auction management options
    keyboard = [
        [
            InlineKeyboardButton(
                "Start Round 0", callback_data=f"admin_startround0_{gully_id}"
            ),
            InlineKeyboardButton(
                "Start Auction", callback_data=f"admin_startauction_{gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Next Player", callback_data=f"admin_nextplayer_{gully_id}"
            ),
            InlineKeyboardButton(
                "Complete Auction", callback_data=f"admin_completeauction_{gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Auction Settings", callback_data=f"admin_auctionsettings_{gully_id}"
            ),
            InlineKeyboardButton(
                "View Status", callback_data=f"admin_auctionstatus_{gully_id}"
            ),
        ],
        [InlineKeyboardButton("Back", callback_data=f"admin_panel_{gully_id}")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        f"🔨 *Auction Management - {gully.get('name')}* 🔨\n\n"
        f"Select an option to manage auctions:\n\n"
        f"• Start Round 0: Begin squad submissions\n"
        f"• Start Auction: Begin live auction\n"
        f"• Next Player: Move to next player in auction\n"
        f"• Complete Auction: End the auction process\n"
        f"• Auction Settings: Configure auction rules\n"
        f"• View Status: Check current auction status\n"
    )

    await query.edit_message_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def handle_match_management(
    update: Update, context: ContextTypes.DEFAULT_TYPE, parts: List[str]
) -> None:
    """Handle match management panel."""
    query = update.callback_query

    # Get gully ID from callback data
    if len(parts) < 3:
        return

    gully_id = int(parts[2])

    # Get gully info
    gully = await api_client.get_gully(gully_id)

    # Create keyboard with match management options
    keyboard = [
        [
            InlineKeyboardButton(
                "Create Match", callback_data=f"admin_creatematch_{gully_id}"
            ),
            InlineKeyboardButton(
                "Edit Match", callback_data=f"admin_editmatch_{gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Update Scores", callback_data=f"admin_updatescores_{gully_id}"
            ),
            InlineKeyboardButton(
                "Match Results", callback_data=f"admin_matchresults_{gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Create Poll", callback_data=f"admin_createpoll_{gully_id}"
            ),
            InlineKeyboardButton(
                "Close Poll", callback_data=f"admin_closepoll_{gully_id}"
            ),
        ],
        [InlineKeyboardButton("Back", callback_data=f"admin_panel_{gully_id}")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        f"🏆 *Match Management - {gully.get('name')}* 🏆\n\n"
        f"Select an option to manage matches:\n\n"
        f"• Create Match: Add a new match\n"
        f"• Edit Match: Modify match details\n"
        f"• Update Scores: Update match scores\n"
        f"• Match Results: View and publish results\n"
        f"• Create Poll: Create a prediction poll\n"
        f"• Close Poll: Close and score a poll\n"
    )

    await query.edit_message_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def handle_settings_management(
    update: Update, context: ContextTypes.DEFAULT_TYPE, parts: List[str]
) -> None:
    """Handle gully settings panel."""
    query = update.callback_query

    # Get gully ID from callback data
    if len(parts) < 3:
        return

    gully_id = int(parts[2])

    # Get gully info
    gully = await api_client.get_gully(gully_id)

    # Create keyboard with settings options
    keyboard = [
        [
            InlineKeyboardButton(
                "Edit Name", callback_data=f"settings_name_{gully_id}"
            ),
            InlineKeyboardButton(
                "Edit Dates", callback_data=f"settings_dates_{gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Auction Settings", callback_data=f"settings_auction_{gully_id}"
            ),
            InlineKeyboardButton(
                "Transfer Settings", callback_data=f"settings_transfer_{gully_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "Match Settings", callback_data=f"settings_match_{gully_id}"
            ),
            InlineKeyboardButton(
                "Notification Settings", callback_data=f"settings_notify_{gully_id}"
            ),
        ],
        [InlineKeyboardButton("Back", callback_data=f"admin_panel_{gully_id}")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        f"⚙️ *Gully Settings - {gully.get('name')}* ⚙️\n\n"
        f"Configure settings for your gully:\n\n"
        f"*Current Settings:*\n"
        f"• Name: {gully.get('name')}\n"
        f"• Start Date: {gully.get('start_date')}\n"
        f"• End Date: {gully.get('end_date')}\n"
        f"• Status: {gully.get('status')}\n\n"
        f"Select an option below to modify settings:"
    )

    await query.edit_message_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def handle_roles_management(
    update: Update, context: ContextTypes.DEFAULT_TYPE, parts: List[str]
) -> None:
    """Handle admin roles panel."""
    query = update.callback_query

    # Get gully ID from callback data
    if len(parts) < 3:
        return

    gully_id = int(parts[2])

    # Get gully info
    gully = await api_client.get_gully(gully_id)

    # Get all admins for this gully
    try:
        admins = await api_client.get_gully_admins(gully_id)

        # Create keyboard with admin usernames
        keyboard = []
        for admin in admins:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{admin.get('username')} ({admin.get('role')})",
                        callback_data=f"admin_perm_{gully_id}_{admin.get('user_id')}",
                    )
                ]
            )

        # Add button to add new admin
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Add New Admin", callback_data=f"admin_add_{gully_id}"
                )
            ]
        )

        # Add back button
        keyboard.append(
            [InlineKeyboardButton("Back", callback_data=f"admin_panel_{gully_id}")]
        )

        reply_markup = InlineKeyboardMarkup(keyboard)

        message = (
            f"👥 *Admin Roles - {gully.get('name')}* 👥\n\n"
            f"Select an admin to view or modify their permissions:\n\n"
        )

        await query.edit_message_text(
            message, reply_markup=reply_markup, parse_mode="Markdown"
        )
    except Exception as e:
        # Handle error
        await query.edit_message_text(
            f"Error fetching admin roles: {str(e)}\n\nPlease try again.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Back", callback_data=f"admin_panel_{gully_id}"
                        )
                    ]
                ]
            ),
            parse_mode="Markdown",
        )


async def handle_invite_link(
    update: Update, context: ContextTypes.DEFAULT_TYPE, parts: List[str]
) -> None:
    """Handle invite link generation."""
    query = update.callback_query

    # Get gully ID from callback data
    if len(parts) < 3:
        return

    gully_id = int(parts[2])

    # Get user ID
    user_id = update.effective_user.id

    # Generate invite link
    try:
        result = await api_client.generate_invite_link(
            gully_id=gully_id, expiration_hours=24  # Default to 24 hours
        )

        if result.get("invite_link"):
            # Create keyboard with options
            keyboard = [
                [
                    InlineKeyboardButton(
                        "1 Hour", callback_data=f"invite_1_{gully_id}"
                    ),
                    InlineKeyboardButton(
                        "24 Hours", callback_data=f"invite_24_{gully_id}"
                    ),
                    InlineKeyboardButton(
                        "7 Days", callback_data=f"invite_168_{gully_id}"
                    ),
                ],
                [InlineKeyboardButton("Back", callback_data=f"admin_panel_{gully_id}")],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            message = (
                f"🔗 *Invite Link Generated* 🔗\n\n"
                f"Gully: *{result.get('gully_name')}*\n"
                f"Expires in: *{result.get('expires_in')}*\n\n"
                f"Link: {result.get('invite_link')}\n\n"
                f"Share this link with users you want to invite to your gully.\n\n"
                f"Select a different expiration time if needed:"
            )

            await query.edit_message_text(
                message, reply_markup=reply_markup, parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                f"Failed to generate invite link: {result.get('detail', 'Unknown error')}\n\nPlease try again.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Back", callback_data=f"admin_panel_{gully_id}"
                            )
                        ]
                    ]
                ),
                parse_mode="Markdown",
            )
    except Exception as e:
        # Handle error
        await query.edit_message_text(
            f"Error generating invite link: {str(e)}\n\nPlease try again.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Back", callback_data=f"admin_panel_{gully_id}"
                        )
                    ]
                ]
            ),
            parse_mode="Markdown",
        )


async def handle_admin_permissions(
    update: Update, context: ContextTypes.DEFAULT_TYPE, parts: List[str]
) -> None:
    """Handle admin permissions management."""
    query = update.callback_query

    # Get gully ID and user ID from callback data
    if len(parts) < 4:
        return

    gully_id = int(parts[2])
    admin_id = int(parts[3])

    # Get admin permissions
    try:
        permissions = await api_client.get_user_permissions(admin_id, gully_id)

        # Get admin info
        admin_info = await api_client.get_user_by_id(admin_id)

        # Create keyboard with permission toggles
        keyboard = []

        # Define all possible permissions
        all_permissions = [
            ("user_management", "User Management"),
            ("team_management", "Team Management"),
            ("auction_management", "Auction Management"),
            ("match_management", "Match Management"),
            ("settings_management", "Settings Management"),
            ("all", "All Permissions"),
        ]

        # Check which permissions are active
        active_permissions = [p.get("permission_type") for p in permissions]

        # Create toggle buttons for each permission
        for perm_type, perm_name in all_permissions:
            is_active = perm_type in active_permissions
            status = "✅" if is_active else "❌"
            action = "remove" if is_active else "add"

            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{perm_name}: {status}",
                        callback_data=f"perm_{action}_{gully_id}_{admin_id}_{perm_type}",
                    )
                ]
            )

        # Add remove admin button
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Remove Admin Role",
                    callback_data=f"admin_remove_{gully_id}_{admin_id}",
                )
            ]
        )

        # Add back button
        keyboard.append(
            [InlineKeyboardButton("Back", callback_data=f"admin_roles_{gully_id}")]
        )

        reply_markup = InlineKeyboardMarkup(keyboard)

        message = (
            f"🔐 *Admin Permissions - {admin_info.get('username')}* 🔐\n\n"
            f"Manage permissions for this admin in the gully.\n"
            f"Click on a permission to toggle it:\n\n"
        )

        await query.edit_message_text(
            message, reply_markup=reply_markup, parse_mode="Markdown"
        )
    except Exception as e:
        # Handle error
        await query.edit_message_text(
            f"Error fetching admin permissions: {str(e)}\n\nPlease try again.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Back", callback_data=f"admin_roles_{gully_id}"
                        )
                    ]
                ]
            ),
            parse_mode="Markdown",
        )


async def handle_add_admin(
    update: Update, context: ContextTypes.DEFAULT_TYPE, parts: List[str]
) -> None:
    """Handle adding a new admin."""
    query = update.callback_query

    # Get gully ID from callback data
    if len(parts) < 3:
        return

    gully_id = int(parts[2])

    # Get gully info
    gully = await api_client.get_gully(gully_id)

    # Get participants who are not admins
    participants = await api_client.get_game_participants(gully_id)

    # Filter out existing admins
    admins = await api_client.get_gully_admins(gully_id)
    admin_ids = [admin.get("user_id") for admin in admins]

    non_admin_participants = [
        p for p in participants if p.get("user_id") not in admin_ids
    ]

    # Create keyboard with user list
    keyboard = []

    # Add users in batches of 2
    for i in range(0, len(non_admin_participants), 2):
        row = []
        for j in range(2):
            if i + j < len(non_admin_participants):
                participant = non_admin_participants[i + j]
                row.append(
                    InlineKeyboardButton(
                        f"{participant.get('username')}",
                        callback_data=f"admin_nominate_{gully_id}_{participant.get('user_id')}",
                    )
                )
        if row:
            keyboard.append(row)

    # Add back button
    keyboard.append(
        [InlineKeyboardButton("Back", callback_data=f"admin_roles_{gully_id}")]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        f"👑 *Add New Admin - {gully.get('name')}* 👑\n\n"
        f"Select a user to nominate as admin:\n\n"
    )

    await query.edit_message_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )
