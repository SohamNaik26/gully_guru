import logging
from telegram import Update
from telegram.ext import ContextTypes

from src.db.session import get_session

logger = logging.getLogger(__name__)


async def leaderboard_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the /leaderboard command."""
    # Get top users by points
    async with get_session() as session:
        stmt = (
            "SELECT id, username, full_name, total_points "
            "FROM users "
            "ORDER BY total_points DESC "
            "LIMIT 10"
        )
        result = await session.execute(stmt)
        users = result.fetchall()

    if not users:
        await update.message.reply_text("No users found in the leaderboard yet.")
        return

    # Format leaderboard message
    leaderboard_text = "🏆 *Gully Cricket Leaderboard* 🏆\n\n"

    for i, user in enumerate(users, 1):
        leaderboard_text += (
            f"{i}. {user.full_name} (@{user.username}) - {user.total_points} points\n"
        )

    await update.message.reply_text(leaderboard_text, parse_mode="Markdown")
