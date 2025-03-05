# Fantasy Cricket Auction System

## Overview

The GullyGuru Fantasy Cricket platform features a sophisticated auction system that allows managers to bid on players in a competitive environment. The auction process is designed to be engaging, fair, and strategic, with both public and private components.

## Auction Workflow

### 1. Initial Squad Submission (Round 0)

Before the auction begins, each manager privately submits their preferred 18-player squad to the bot. This process includes:

- **Private Selection**: Managers select players through a conversation with the bot
- **Budget Validation**: Total squad value must not exceed 100 cr
- **Squad Size**: Exactly 18 players must be selected
- **Submission Tracking**: System tracks which managers have submitted their squads

### 2. Contested vs. Uncontested Players

Once all managers have submitted their squads:

- **Uncontested Players**: Players selected by only one manager are automatically assigned to that manager at base price
- **Contested Players**: Players selected by multiple managers go to auction
- **Budget Deduction**: Base price of uncontested players is deducted from the manager's budget

### 3. Live Auction Process

The auction for contested players follows these steps:

1. **Auction Initialization**:
   - Admin initiates the auction in the group chat
   - System randomly selects the order of players to be auctioned

2. **Player Announcement**:
   - Current player details are announced in the group chat
   - All managers receive private messages with bidding options

3. **Bidding Rules**:
   - **Starting Bid**: Equal to player's base price
   - **Bid Increments**:
     - <1 Cr: +0.10 Cr
     - <2 Cr: +0.20 Cr
     - <5 Cr: +0.50 Cr
     - ≥5 Cr: +1.00 Cr
   - **Bid Placement**: Managers place bids in private chats with the bot
   - **Public Announcements**: Each bid is announced in the group chat

4. **Auction Timer**:
   - Each player auction lasts for 60 seconds
   - If no new bid is received within 15 seconds, the highest bidder wins
   - Timer extensions may occur if bids are placed near the end

5. **Auction Completion**:
   - Highest bidder wins the player
   - Winning bid amount is deducted from the manager's budget
   - Player is added to the winner's team
   - Results are announced in the group chat

6. **Next Player**:
   - System moves to the next contested player
   - Process repeats until all contested players are auctioned

## Privacy and Transparency

The auction system balances privacy and transparency:

- **Public Information** (visible in group chat):
  - Current player up for auction
  - Current highest bid and bidder
  - Auction timer status
  - Final auction results

- **Private Information** (visible only to individual managers):
  - Manager's remaining budget
  - Personalized bidding options based on budget
  - Confirmation of bid placement
  - Updated budget after winning an auction

## Technical Implementation

### Database Models

The auction system uses several database models:

```python
class Auction(TimeStampedModel, table=True):
    """Model for auction rounds."""
    __tablename__ = "auctions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(default="pending")  # pending, active, completed
    current_player_id: Optional[int] = Field(default=None, foreign_key="players.id")
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    
    # Relationships
    current_player: Optional["Player"] = Relationship()
    bids: List["AuctionBid"] = Relationship(back_populates="auction")


class AuctionBid(TimeStampedModel, table=True):
    """Model for auction bids."""
    __tablename__ = "auction_bids"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    auction_id: int = Field(foreign_key="auctions.id")
    user_id: int = Field(foreign_key="users.id")
    player_id: int = Field(foreign_key="players.id")
    bid_amount: Decimal = Field()
    status: str = Field(default="pending")  # pending, accepted, rejected
    
    # Relationships
    auction: Optional[Auction] = Relationship(back_populates="bids")
    user: Optional["User"] = Relationship(back_populates="bids")
    player: Optional["Player"] = Relationship()
```

### API Endpoints

The auction system exposes several API endpoints:

- `GET /api/fantasy/auction/current`: Get current auction status
- `POST /api/fantasy/auction/start-round`: Start an auction round for a player
- `POST /api/fantasy/auction/bid`: Place a bid in the auction
- `POST /api/fantasy/auction/end-round`: End an auction round and process results
- `GET /api/fantasy/auction/history`: Get auction history

### Bot Commands

The auction system provides several bot commands:

- `/auction`: View current auction status
- `/bid [amount]`: Place a bid in the auction
- `/auctionhistory`: View recent auction results
- `/start_auction` (admin only): Start the auction process

## Edge Cases and Handling

The auction system handles several edge cases:

1. **Insufficient Budget**: Managers cannot place bids exceeding their remaining budget
2. **Minimum Bid Requirement**: Bids must meet minimum increment requirements
3. **Auction Timeout**: If no bids are placed, player remains unassigned
4. **Connection Issues**: Bid confirmations ensure bids are properly recorded
5. **Concurrent Bids**: System handles near-simultaneous bids with proper ordering

## Post-Auction

After the auction completes:

1. **Team Finalization**: Managers can view their complete teams
2. **Budget Status**: Managers can see their remaining budget
3. **Auction Summary**: System provides a summary of all auction results
4. **Transfer Preparation**: System prepares for the weekly transfer window phase 