from telegram import Update
from telegram.ext import ContextTypes
from typing import Callable, Any, Awaitable

from src.bot.bot import api_client

async def gully_context_middleware(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    callback: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[Any]]
) -> Any:
    """Middleware to handle gully context."""
    # Skip middleware for certain commands
    if update.message and update.message.text:
        skip_commands = ["/start", "/create_gully", "/join_gully", "/switch_gully", "/my_gullies"]
        if any(update.message.text.startswith(cmd) for cmd in skip_commands):
            return await callback(update, context)
    
    # Get user
    user = update.effective_user
    if not user:
        return await callback(update, context)
    
    # Get user from database
    db_user = await api_client.get_user(user.id)
    if not db_user:
        return await callback(update, context)
    
    # Handle group context
    if update.effective_chat and update.effective_chat.type in ["group", "supergroup"]:
        # Get gully for this group
        group_gully = await api_client.get_gully_by_group(update.effective_chat.id)
        
        if group_gully:
            # Store group gully in context
            context.chat_data["gully_id"] = group_gully.get("id")
            
            # If user has no active gully, set this as active
            if not db_user.get("active_gully_id"):
                await api_client.set_active_gully(db_user.get("id"), group_gully.get("id"))
    
    # Store active gully in context
    active_gully_id = db_user.get("active_gully_id")
    if active_gully_id:
        context.user_data["active_gully_id"] = active_gully_id
    
    return await callback(update, context) 