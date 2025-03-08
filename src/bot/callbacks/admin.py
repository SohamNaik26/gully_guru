from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Dict, Any, List

from src.bot.api_client_instance import api_client
from src.bot.handlers.admin import admin_panel_command


async def handle_admin_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle admin panel callbacks."""
    query = update.callback_query
    user_id = update.effective_user.id

    # Check if user is admin
    is_admin = await api_client.is_admin(user_id)
    if not is_admin:
        await query.answer("You don't have admin permissions.")
        return

    # Get callback data
    callback_data = query.data
    parts = callback_data.split("_")

    if len(parts) < 2:
        return

    action = parts[1]

    # Handle different actions
    if action == "panel":
        # Show admin panel
        await admin_panel_command(update, context)

    elif action == "gully":
        # Handle gully selection
        await handle_gully_selection(update, context, parts)

    elif action == "start":
        # Handle start auction round
        if len(parts) >= 4:
            gully_id = int(parts[3])
            round_type = parts[2]  # round_zero or round_one

            if round_type == "round":
                # Start Round 0
                await query.edit_message_text(
                    f"Starting Round 0 for gully {gully_id}...\n\n"
                    "This will initiate the squad submission phase. "
                    "Users will be able to submit their preferred squads.",
                    parse_mode="Markdown",
                )
                # Call API to start Round 0
                result = await api_client.start_auction_round_zero(gully_id)
                if result:
                    await query.edit_message_text(
                        f"✅ Round 0 has been started successfully!\n\n"
                        "Users can now submit their squads using the /submit_squad command.",
                        parse_mode="Markdown",
                    )
                else:
                    await query.edit_message_text(
                        "❌ Failed to start Round 0. Please try again later.",
                        parse_mode="Markdown",
                    )

            elif round_type == "round":
                # Start Round 1
                await query.edit_message_text(
                    f"Starting Round 1 for gully {gully_id}...\n\n"
                    "This will initiate the live auction for contested players.",
                    parse_mode="Markdown",
                )
                # Call API to start Round 1
                result = await api_client.start_auction_round_one(gully_id)
                if result:
                    await query.edit_message_text(
                        "✅ Round 1 has been started successfully!\n\n"
                        "The live auction for contested players has begun.",
                        parse_mode="Markdown",
                    )
                else:
                    await query.edit_message_text(
                        "❌ Failed to start Round 1. Please try again later.",
                        parse_mode="Markdown",
                    )

    elif action == "next":
        # Handle next player in auction
        if len(parts) >= 4:
            gully_id = int(parts[3])

            await query.edit_message_text(
                f"Moving to next player in auction for gully {gully_id}...",
                parse_mode="Markdown",
            )

            # Call API to move to next player
            result = await api_client.next_auction_player(gully_id)
            if result:
                player = result.get("player", {})
                await query.edit_message_text(
                    f"✅ Moved to next player: {player.get('name')}\n\n"
                    f"Base price: ₹{player.get('base_price')} cr\n"
                    f"Team: {player.get('team')}\n"
                    f"Type: {player.get('player_type')}\n\n"
                    "The auction for this player has begun.",
                    parse_mode="Markdown",
                )
            else:
                await query.edit_message_text(
                    "❌ Failed to move to next player. Please try again later.",
                    parse_mode="Markdown",
                )

    elif action == "end":
        # Handle end auction round
        if len(parts) >= 4:
            gully_id = int(parts[3])

            await query.edit_message_text(
                f"Ending current auction round for gully {gully_id}...",
                parse_mode="Markdown",
            )

            # Call API to end auction round
            result = await api_client.end_auction_round(gully_id)
            if result:
                await query.edit_message_text(
                    "✅ Auction round has been ended successfully!\n\n"
                    "All current player auctions have been finalized.",
                    parse_mode="Markdown",
                )
            else:
                await query.edit_message_text(
                    "❌ Failed to end auction round. Please try again later.",
                    parse_mode="Markdown",
                )

    elif action == "complete":
        # Handle complete auction
        if len(parts) >= 4:
            gully_id = int(parts[3])

            await query.edit_message_text(
                f"Completing the entire auction process for gully {gully_id}...\n\n"
                "This will finalize all player allocations and update user budgets.",
                parse_mode="Markdown",
            )

            # Call API to complete auction
            result = await api_client.complete_auction(gully_id)
            if result:
                await query.edit_message_text(
                    "✅ Auction has been completed successfully!\n\n"
                    "All players have been allocated to users and budgets have been updated.",
                    parse_mode="Markdown",
                )
            else:
                await query.edit_message_text(
                    "❌ Failed to complete auction. Please try again later.",
                    parse_mode="Markdown",
                )

    elif action == "view":
        # Handle view users
        if len(parts) >= 4:
            gully_id = int(parts[3])
            # Implement view users functionality
            await query.edit_message_text(
                f"Viewing users for gully {gully_id}...", parse_mode="Markdown"
            )

    elif action == "add":
        # Handle add admin
        if len(parts) >= 4:
            gully_id = int(parts[3])
            # Implement add admin functionality
            await query.edit_message_text(
                f"Adding admin for gully {gully_id}...", parse_mode="Markdown"
            )

    elif action == "remove":
        # Handle remove admin
        if len(parts) >= 4:
            gully_id = int(parts[3])
            # Implement remove admin functionality
            await query.edit_message_text(
                f"Removing admin for gully {gully_id}...", parse_mode="Markdown"
            )

    elif action == "create":
        # Handle create match
        if len(parts) >= 4:
            gully_id = int(parts[3])
            # Implement create match functionality
            await query.edit_message_text(
                f"Creating match for gully {gully_id}...", parse_mode="Markdown"
            )

    elif action == "edit":
        # Handle edit name/dates
        if len(parts) >= 4:
            gully_id = int(parts[3])
            # Implement edit functionality
            await query.edit_message_text(
                f"Editing settings for gully {gully_id}...", parse_mode="Markdown"
            )

    elif action == "generate":
        # Handle generate invite
        if len(parts) >= 4:
            gully_id = int(parts[3])
            # Implement generate invite functionality
            await query.edit_message_text(
                f"Generating invite for gully {gully_id}...", parse_mode="Markdown"
            )

    else:
        # Unknown action
        await query.answer("Unknown action.")


async def handle_gully_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE, parts: List[str]
) -> None:
    """Handle gully selection for admin panel."""
    query = update.callback_query

    # Get gully ID from callback data
    if len(parts) < 3:
        return

    gully_id = int(parts[2])

    # Set active gully for the user
    user_id = update.effective_user.id
    await api_client.set_active_game(user_id, gully_id)

    # Get gully info
    gully = await api_client.get_gully(gully_id)

    # Create admin panel keyboard with auction-related options
    keyboard = [
        # Auction Management
        [
            InlineKeyboardButton(
                "🔨 Start Round 0", callback_data=f"admin_start_round_zero_{gully_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "🏁 Start Round 1", callback_data=f"admin_start_round_one_{gully_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "⏭️ Next Player", callback_data=f"admin_next_player_{gully_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "🛑 End Auction Round", callback_data=f"admin_end_round_{gully_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "🏆 Complete Auction",
                callback_data=f"admin_complete_auction_{gully_id}",
            )
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"🛠️ *Admin Panel - {gully.get('name')}* 🛠️\n\n"
        f"Welcome to the admin panel. Here you can manage auction-related functionality for your gully.\n\n"
        f"• Start Round 0: Begin the initial squad submission phase\n"
        f"• Start Round 1: Begin the live auction for contested players\n"
        f"• Next Player: Move to the next player in the auction\n"
        f"• End Auction Round: End the current auction round\n"
        f"• Complete Auction: Finalize the entire auction process\n",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


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


async def handle_section_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE, parts: List[str]
) -> None:
    """Handle section selection in admin panel."""
    query = update.callback_query
    user_id = update.effective_user.id

    # Check if user is admin
    is_admin = await api_client.is_admin(user_id)
    if not is_admin:
        await query.answer("You don't have admin permissions.")
        return

    # Get section and gully ID from callback data
    if len(parts) < 4:
        return

    section = parts[2]
    gully_id = int(parts[3])

    # Get gully info
    gully = await api_client.get_gully(gully_id)

    # Handle different sections
    if section == "users":
        # User Management Section
        keyboard = [
            [
                InlineKeyboardButton(
                    "👁️ View Users", callback_data=f"admin_view_users_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "➕ Add Admin", callback_data=f"admin_add_admin_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "➖ Remove Admin", callback_data=f"admin_remove_admin_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "📊 Bulk Add Users",
                    callback_data=f"admin_bulk_add_users_{gully_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Back to Admin Panel", callback_data=f"admin_gully_{gully_id}"
                )
            ],
        ]

        message = (
            f"👥 *User Management - {gully.get('name')}* 👥\n\n"
            f"Manage users and their roles in your gully:\n\n"
            f"• View all users in your gully\n"
            f"• Add admin privileges to users\n"
            f"• Remove admin privileges from users\n"
            f"• Bulk add users to your gully\n"
        )

    elif section == "auction":
        # Auction Management Section
        keyboard = [
            [
                InlineKeyboardButton(
                    "🏁 Start Auction", callback_data=f"admin_start_auction_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "⚙️ Auction Settings",
                    callback_data=f"admin_auction_settings_{gully_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "📋 Player List", callback_data=f"admin_player_list_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Back to Admin Panel", callback_data=f"admin_gully_{gully_id}"
                )
            ],
        ]

        message = (
            f"🔨 *Auction Management - {gully.get('name')}* 🔨\n\n"
            f"Configure and run player auctions:\n\n"
            f"• Start a new auction session\n"
            f"• Configure auction settings\n"
            f"• Manage player list for auction\n"
        )

    elif section == "matches":
        # Match Management Section
        keyboard = [
            [
                InlineKeyboardButton(
                    "➕ Create Match", callback_data=f"admin_create_match_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "📝 Update Scores", callback_data=f"admin_update_scores_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "📅 Schedule Matches",
                    callback_data=f"admin_schedule_matches_{gully_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Back to Admin Panel", callback_data=f"admin_gully_{gully_id}"
                )
            ],
        ]

        message = (
            f"🏆 *Match Management - {gully.get('name')}* 🏆\n\n"
            f"Set up and manage matches:\n\n"
            f"• Create new matches\n"
            f"• Update match scores\n"
            f"• Schedule upcoming matches\n"
        )

    elif section == "settings":
        # Gully Settings Section
        keyboard = [
            [
                InlineKeyboardButton(
                    "✏️ Edit Name", callback_data=f"admin_edit_name_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "📅 Edit Dates", callback_data=f"admin_edit_dates_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "💰 Edit Points", callback_data=f"admin_edit_points_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Back to Admin Panel", callback_data=f"admin_gully_{gully_id}"
                )
            ],
        ]

        message = (
            f"⚙️ *Gully Settings - {gully.get('name')}* ⚙️\n\n"
            f"Configure general settings for your gully:\n\n"
            f"• Edit gully name and description\n"
            f"• Modify start and end dates\n"
            f"• Configure point system\n"
        )

    elif section == "roles":
        # Admin Roles Section
        keyboard = [
            [
                InlineKeyboardButton(
                    "👁️ View Admins", callback_data=f"admin_view_admins_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "➕ Add Admin", callback_data=f"admin_add_admin_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "➖ Remove Admin", callback_data=f"admin_remove_admin_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Back to Admin Panel", callback_data=f"admin_gully_{gully_id}"
                )
            ],
        ]

        message = (
            f"🔐 *Admin Roles - {gully.get('name')}* 🔐\n\n"
            f"Manage admin permissions:\n\n"
            f"• View current admins\n"
            f"• Add new admins\n"
            f"• Remove admin privileges\n"
        )

    elif section == "invite":
        # Invite Management Section
        keyboard = [
            [
                InlineKeyboardButton(
                    "🔗 Generate Invite Link",
                    callback_data=f"admin_generate_invite_{gully_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    "⏱️ 24-Hour Link", callback_data=f"admin_24h_invite_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🗑️ Revoke Links", callback_data=f"admin_revoke_invites_{gully_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Back to Admin Panel", callback_data=f"admin_gully_{gully_id}"
                )
            ],
        ]

        message = (
            f"🔗 *Invite Management - {gully.get('name')}* 🔗\n\n"
            f"Create and manage invite links:\n\n"
            f"• Generate permanent invite links\n"
            f"• Create temporary 24-hour links\n"
            f"• Revoke existing invite links\n"
        )

    else:
        # Invalid section, return to admin panel
        await handle_gully_selection(update, context, ["admin", "gully", str(gully_id)])
        return

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )
