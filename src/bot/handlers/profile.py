import logging
from telegram import Update
from telegram.ext import ContextTypes

from src.db.session import get_session
from src.api.api_client_instance import api_client

logger = logging.getLogger(__name__)


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /profile command."""
    user = update.effective_user

    # Get user from database
    db_user = await api_client.get_user(user.id)

    if not db_user:
        await update.message.reply_text(
            "You don't have an account yet. Use /join_gully to create one."
        )
        return

    # Get user's team
    async with get_session() as session:
        # Use direct database access for complex queries
        user_id = db_user["id"]

        # Get user's players
        stmt = (
            "SELECT p.name, p.team, p.player_type, upl.price "
            "FROM user_player_links upl "
            "JOIN players p ON upl.player_id = p.id "
            "WHERE upl.user_id = :user_id"
        )

        result = await session.execute(stmt, {"user_id": user_id})
        players = result.fetchall()

    # Format profile message
    message = f"*Profile: {db_user['username']}*\n\n"
    message += f"*Budget:* ₹{db_user.get('budget', 0)} cr\n"
    message += f"*Total Points:* {db_user.get('total_points', 0)}\n"
    message += f"*Rank:* {db_user.get('rank', 'N/A')}\n\n"

    # Add team summary
    if players:
        message += f"*Team:* {len(players)} players\n"
        # You could add more team summary info here
    else:
        message += "*Team:* No players yet\n"

    await update.message.reply_text(message, parse_mode="Markdown")
