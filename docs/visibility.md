# Fantasy Cricket Bot: Visibility and Information Structure

## Overview

This document outlines the visibility and information structure of the GullyGuru Fantasy Cricket bot, detailing what information is public versus private, how data flows between components, and how user interactions are managed across different contexts.

## Information Visibility Framework

### Public Information (Group Chat)

Information visible to all users in group chats:

1. **Auction Announcements**
   - Current player being auctioned
   - Current highest bid and bidder
   - Auction timer status (e.g., "15 seconds remaining")
   - Timer extensions when bids are placed
   - Final auction results for each player

2. **Transfer Window Updates**
   - Transfer window opening/closing announcements
   - Available players for transfer (without bid details)
   - Transfer completion announcements

3. **Match and Scoring Updates**
   - Match schedules
   - Live match status
   - Daily leaderboard summaries
   - Weekly result announcements

4. **Administrative Announcements**
   - Season start/end
   - Rule changes
   - Special events

### Private Information (Direct Messages)

Information visible only to individual users:

1. **Personal Team Management**
   - Complete squad details
   - Budget information
   - Team composition validation results
   - Maximum possible bid calculations

2. **Auction Interactions**
   - Personalized bidding options based on budget
   - Bid confirmation messages
   - Budget warnings when approaching limits
   - Detailed auction history for owned players

3. **Transfer System**
   - Personal transfer listings
   - Bid status on other players
   - Free bid count remaining
   - Transfer results specific to the user

4. **Playing XI Selection**
   - Team selection interface
   - Captain/Vice-Captain selection
   - Lineup submission confirmations
   - Deadline reminders

5. **Performance Metrics**
   - Detailed point breakdowns for owned players
   - Historical performance data
   - Personal ranking information

## Component Interaction Structure

### Bot-to-Database Flow

1. **User Registration and Authentication**
   - Telegram user data → User database entry
   - Authentication tokens for API access

2. **Team Management**
   - Player selections → UserPlayerLink entries
   - Budget updates → User record modifications

3. **Auction System**
   - Bid placements → AuctionBid entries
   - Auction results → UserPlayerLink and User budget updates

4. **Transfer System**
   - Transfer listings → TransferListing entries
   - Bids → TransferBid entries
   - Completed transfers → UserPlayerLink modifications

5. **Match Scoring**
   - Player performances → PlayerMatch entries
   - User points → UserMatch entries

### API-to-Bot Flow

1. **Data Retrieval**
   - User information for decision-making
   - Player data for display
   - Match information for updates

2. **Action Processing**
   - Bid validation and processing
   - Transfer completion
   - Team composition validation

3. **Notification Triggers**
   - Timer-based events (auction endings, deadlines)
   - Status changes (transfer window opening/closing)
   - Score updates

## User Interaction Patterns

### Conversation Handlers

The bot implements several conversation handlers to manage multi-step interactions:

1. **Registration Flow**
   - Username selection
   - Team name selection
   - Confirmation

2. **Auction Bidding**
   - Bid amount selection/entry
   - Confirmation
   - Result notification

3. **Transfer Listing**
   - Player selection
   - Price setting
   - Confirmation

4. **Bid Placement**
   - Amount selection
   - Free/paid bid choice
   - Confirmation

5. **Playing XI Selection** (Planned)
   - Player selection
   - Captain/Vice-Captain designation
   - Formation confirmation

### Keyboard Navigation

The bot uses a hierarchical keyboard navigation system:

1. **Main Menu**
   - Team management
   - Auction access
   - Transfer market
   - Match center
   - Settings

2. **Contextual Submenus**
   - Dynamic options based on current state
   - Back navigation to parent menus
   - Quick actions for common tasks

3. **Action Confirmations**
   - Explicit confirmation for irreversible actions
   - Cancel options to prevent accidental actions

## Privacy Considerations

### Data Protection

1. **User Information**
   - Budget information is only visible to the user
   - Bid capacity is calculated privately
   - Team composition details are protected

2. **Strategic Information**
   - Bidding intentions are not revealed until confirmed
   - Transfer targets are private until bids are placed
   - Playing XI selections are hidden until matches begin

### Transparency Balance

1. **Public Accountability**
   - All completed transactions are publicly announced
   - Current highest bids are visible to maintain fairness
   - Final team compositions are public after deadlines

2. **Private Decision-Making**
   - Users can evaluate options privately before committing
   - Budget management tools are provided confidentially
   - Strategic planning interfaces are private

## Implementation Notes

1. **Spam Management**
   - Not a priority for the MVP
   - Will be addressed in future iterations

2. **Do Not Disturb Mode**
   - Not included in the current implementation
   - May be added based on user feedback

3. **Salary Cap System**
   - Not implemented; using auction budget only
   - Simplifies initial implementation

4. **Live Match Calculations**
   - Points will be updated after matches end
   - Using Dream11 scoring system
   - No real-time point updates during matches

5. **Analytics**
   - Basic statistics only in MVP
   - Advanced analytics planned for future versions 