# Fantasy Cricket Bot: Gully Management System

## Overview

The GullyGuru Fantasy Cricket bot supports multiple concurrent gullies across different Telegram groups. This document outlines how the bot manages group associations, gully instances, and user participation across multiple leagues.

## Core Concepts

### Gully Instance

A "Gully Instance" represents a complete fantasy cricket competition with:
- A unique season with defined start and end dates
- A dedicated auction for player acquisition
- Specific transfer windows for team adjustments
- A distinct leaderboard for participant rankings
- A defined set of participants from a Telegram group

### Group Association

Each Gully Instance is associated with a specific Telegram group:
- **One Gully Per Group**: Only one gully can be created per Telegram group
- The group serves as the public forum for the gully
- All public announcements are made in this group
- Only members of the group can participate in the associated gully

### User Participation

Users can participate in multiple Gully Instances simultaneously:
- Each participation is tracked separately
- Users have different teams, budgets, and standings in each gully
- Private interactions with the bot are contextualized to the relevant gully

## User Flow

### Gully Creation and Joining

1. **Gully Creation**
   - Admin creates a new gully with `/create_gully [name]`
   - Bot verifies it has necessary permissions in the group
   - Bot stores the group ID in the gully record
   - Bot announces the gully creation in the group

2. **Participant Registration**
   - Users join the gully with `/join_gully` in the group
   - Bot creates GullyParticipant records
   - Bot sends welcome messages to participants

### Navigation and Commands

1. **Group Commands**
   - `/create_gully [name]`: Create gully in the current group
   - `/join_gully`: Join the gully associated with the current group
   - `/gully_info`: Show information about the current group's gully
   - `/leaderboard`: Show the leaderboard for the current group's gully

2. **Private Commands**
   - `/my_gullies`: List all gullies the user is participating in
   - `/switch_gully [gully_id]`: Switch active context to specified gully
   - `/gully_info`: Show information about the active gully

## Database Structure

### Gully Table

```python
class Gully(TimeStampedModel, table=True):
    """Model for gully instances."""
    __tablename__ = "gullies"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field()
    telegram_group_id: int = Field(unique=True)  # Enforces one gully per group
    status: str = Field(default="pending")  # pending, active, completed
    start_date: datetime = Field()
    end_date: datetime = Field()
    
    # Relationships
    auctions: List["Auction"] = Relationship(back_populates="gully")
    transfer_windows: List["TransferWindow"] = Relationship(back_populates="gully")
    participants: List["GullyParticipant"] = Relationship(back_populates="gully")
```

### Gully Participant Table

```python
class GullyParticipant(TimeStampedModel, table=True):
    """Model for gully participants."""
    __tablename__ = "gully_participants"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    gully_id: int = Field(foreign_key="gullies.id")
    user_id: int = Field(foreign_key="users.id")
    team_name: str = Field()
    budget: Decimal = Field(default=100.0)
    points: int = Field(default=0)
    
    # Relationships
    gully: Optional["Gully"] = Relationship(back_populates="participants")
    user: Optional["User"] = Relationship(back_populates="gully_participations")
    players: List["Player"] = Relationship(link_model="UserPlayerLink")
```

### User Model

```python
class User(TimeStampedModel, table=True):
    """Model for users."""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True)
    first_name: str = Field()
    last_name: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    active_gully_id: Optional[int] = Field(default=None, foreign_key="gullies.id")
    
    # Relationships
    players: List["Player"] = Relationship(link_model="UserPlayerLink", back_populates="user")
    bids: List["AuctionBid"] = Relationship(back_populates="user")
    gully_participations: List["GullyParticipant"] = Relationship(back_populates="user")
    active_gully: Optional["Gully"] = Relationship()
```

## One Gully Per Group Rule

The system enforces a strict "one gully per group" rule through multiple layers:

1. **Database Constraint**: The `telegram_group_id` field has a unique constraint
2. **API Validation**: The API checks for existing gullies before creation
3. **Bot Command Validation**: The bot verifies no existing gully before proceeding

### Implementation Example

```python
# Bot-level validation
existing_gully = await api_client.get_gully_by_group(update.effective_chat.id)
if existing_gully:
    await update.message.reply_text(
        f"This group already has a gully: *{existing_gully.get('name')}*\n"
        f"Status: {existing_gully.get('status')}\n\n"
        f"You cannot create another gully in this group.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# API-level validation
existing_gully = session.exec(
    select(Gully).where(Gully.telegram_group_id == gully_data.telegram_group_id)
).first()
if existing_gully:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="This group already has an active gully"
    )
```

## Context Management

The bot intelligently manages context to ensure users interact with the correct gully:

### Group Context

When in a group, the bot automatically uses that group's gully context:

```python
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
```

### Private Chat Context

In private chats, the bot maintains the user's active gully context:

```python
# Store active gully in context
active_gully_id = db_user.get("active_gully_id")
if active_gully_id:
    context.user_data["active_gully_id"] = active_gully_id
```

## Data Isolation

Each gully maintains complete isolation of its data:

1. **Team Isolation**: Users have separate teams in each gully
2. **Budget Isolation**: Budget is tracked per gully
3. **Auction Isolation**: Each gully has its own auction instance
   - Bids are specific to a gully's auction
4. **Transfer Isolation**: Transfer windows are gully-specific
   - Listings and bids are isolated to their respective gullies

## Security Considerations

1. **Group Verification**
   - Verify bot has necessary permissions in groups
   - Ensure only group admins can create/manage gullies

2. **User Authentication**
   - Verify users are members of the associated group
   - Prevent unauthorized access to gully data

3. **Command Authorization**
   - Restrict sensitive commands to gully admins
   - Validate user permissions for each action

4. **Data Isolation**
   - Ensure strict isolation between different gullies' data
   - Prevent data leakage between gully instances

## Gully Lifecycle

### Creation Phase

1. **Initialization**: Admin creates the gully with basic parameters
2. **Participant Recruitment**: Users join the gully
3. **Setup**: Admin configures auction settings, player pools, etc.

### Active Phase

1. **Auction**: Players are auctioned to participants
2. **Match Preparation**: Users select their playing XI before matches
3. **Scoring**: Points are calculated based on real-world performances
4. **Transfers**: Users can adjust their teams during transfer windows

### Completion Phase

1. **Final Rankings**: Final leaderboard is generated
2. **Awards**: Winners are announced
3. **Statistics**: Season statistics are compiled
4. **Archiving**: Gully is marked as completed

## Context Indicators

To help users understand which gully they're currently interacting with, the bot provides clear context indicators:

1. **Message Headers**: Messages in private chats include the active gully name
   ```
   🏏 Active Gully: IPL Fantasy 2023
   
   Your team currently has 15 players...
   ```

2. **Command Responses**: Responses to commands include gully context
   ```
   🏏 IPL Fantasy 2023
   
   Current Leaderboard:
   1. Team Alpha - 450 pts
   2. Team Beta - 425 pts
   ...
   ```

3. **Inline Keyboards**: Navigation keyboards include context switching options
   ```
   [View Team] [Switch Gully] [Settings]
   ```

## API Integration

The gully context is integrated throughout the API:

1. **Context Parameters**: API endpoints accept gully_id parameters
   ```
   GET /api/v1/users/{user_id}/team?gully_id=123
   ```

2. **Response Filtering**: Responses are filtered by gully context
   ```json
   {
     "team": {
       "gully_id": 123,
       "name": "Team Alpha",
       "players": [...]
     }
   }
   ```

3. **Validation**: API validates that users have access to the requested gully
   ```python
   # Check if user is participant in gully
   participant = session.exec(
       select(GullyParticipant)
       .where(GullyParticipant.user_id == current_user.id)
       .where(GullyParticipant.gully_id == gully_id)
   ).first()
   
   if not participant:
       raise HTTPException(
           status_code=status.HTTP_403_FORBIDDEN,
           detail="You are not a participant in this gully"
       )
   ```

## Middleware Implementation

The gully context middleware ensures all bot interactions have the correct context:

```python
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
```

## Best Practices

1. **Clear Context Indicators**: Always make it clear which gully a user is interacting with
2. **Consistent Terminology**: Use consistent terminology for gully-related concepts
3. **Intuitive Navigation**: Make it easy for users to switch between gullies
4. **Data Isolation**: Ensure strict isolation between different gullies' data
5. **Permission Validation**: Always validate that users have appropriate permissions