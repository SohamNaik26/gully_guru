# team_building.md

## Overview
This document details the **team building process** for your fantasy cricket platform. It covers the entire workflow from initial squad selection (Round 0) through auction rounds, team management, and performance tracking. The process is designed to be intuitive, engaging, and fair for all participants in a Gully.

---

## Table of Contents
1. [Introduction & Goals](#introduction--goals)  
2. [Team Building Phases](#team-building-phases)  
3. [Round 0: Initial Squad Selection](#round-0-initial-squad-selection)  
4. [Auction Rounds](#auction-rounds)  
5. [Team Management](#team-management)  
6. [Performance Tracking](#performance-tracking)  
7. [Squad Constraints & Validation](#squad-constraints--validation)  
8. [Edge Cases & Handling](#edge-cases--handling)  
9. [Example Conversations](#example-conversations)  
10. [Flow Diagrams](#flow-diagrams)
11. [Implementation Status](#implementation-status)


## 2. Team Building Phases
The team building process consists of several distinct phases:

1. **Round 0**: Initial squad selection where users pick players within budget constraints.
2. **Auction Rounds**: Contested players from Round 0 are auctioned to the highest bidder.
3. **Team Management**: Users can view, analyze, and make changes to their teams.
4. **Performance Tracking**: The system tracks player performance and updates team points.
5. **Substitutions**: Users can make strategic substitutions based on performance.

---

## 3. Round 0: Initial Squad Selection

### 3.1 Entry Points & Initialization
- **Private Chat Menu**
  - After onboarding, users see an inline button: `[ Build My Squad (Round 0) ]` or can use the `/submit_squad` command.
  - The bot checks:
    - If the user has an active Gully
    - If Round 0 is open
    - If the user already submitted a squad
- **Conditional Flows**
  - If already submitted: "You've already submitted your squad."
  - If Round 0 is closed: "Round 0 has ended."
  - Otherwise → proceed with the selection flow.

### 3.2 Budget & Player Count Constraints
- Each user typically has 100 Cr (or similar) to spend on 18 players.
- The bot tracks:
  - Number of players selected so far
  - Total base price spent
  - Role constraints (e.g., minimum wicketkeepers, bowlers, etc.)

### 3.3 Step-by-Step Inline Flow
1. **Initial Prompt**
   ```
   "You have 18 spots to fill with a max budget of 100 Cr.
    Let's start picking players.
    Choose from filters below or search by name."
   ```

2. **Inline Keyboards for Filtering & Pagination**
   ```
   [ Filter by Batsmen ] [ Filter by Bowlers ] [ All-Rounders ] [ Wicketkeepers ]
   [ Search by Team ] ...

   [ << Prev ] [ Player A (Add) ] [ Player B (Add) ] [ Next >> ]
   ```

3. **Selecting a Player**
   - When the user taps `[ Add ]` for a player:
     - The bot checks current budget usage + role constraints.
     - If valid:
       - Add the player to the user's "temp" Round 0 squad in the DB.
       - Reply with: "Player X (BAT) added. Squad Count: 1/18. Budget Used: 10.0 / 100 Cr"
       - Show updated inline keyboard: `[ Undo Add ] [ Continue Selecting ] [ View Squad ]`
     - If invalid (over budget or role cap), the bot rejects and prompts the user to remove some player or pick a different one.

4. **Viewing/Editing Current Selections**
   - At any time, user can tap `[ View Squad ]` to see a summary:
     ```
     "Your Squad So Far:
       1) Player A (BAT) - 10.0 Cr
       2) Player B (BOWL) - 8.5 Cr
       ...
       Budget Used: 18.5 / 100 Cr
       Spots Left: 16"
     ```
   - Inline buttons for: `[ Remove Player X ] [ Continue Picking ] [ Submit Squad ]`

### 3.4 Submitting the Final Squad
1. **Validation**
   - Once the user has the required number of players, the bot automatically checks if the total base price is ≤ user budget, role distribution is correct, etc.
2. **Confirmation Prompt**
   ```
   "You have selected 18 players for a total base price of 95.5 Cr.
    Confirm submission?"
   ```
   - Inline: `[ Confirm ] [ Cancel ]`
3. **Post-Submission**
   - If user taps `[ Confirm ]`, the bot:
     - Finalizes the user's Round 0 squad in the DB (marked "submitted").
     - Possibly notifies the group: "@Username has submitted their Round 0 squad."
   - If `[ Cancel ]`, user can continue to edit.

### 3.5 Handling Edits & Re-Submissions
- By default, once the user confirms, the squad is locked.
- If edits are allowed until the Round 0 deadline:
  - The user can re-open `[ Build My Squad (Round 0) ]`.
  - The bot shows "You have a submitted squad. Do you want to revise it?"
  - If yes, the user can remove/add players again, subject to the same constraints, and re-confirm.

### 3.6 Backend Logic & Auction Preparation
1. **Saving Round 0 Picks**
   - For each selected player, store an entry in a UserPlayer table:
     - user_id, player_id, purchase_price = base_price, gully_id.
     - Mark them as "pending Round 0" until user hits `[ Confirm ]`.
2. **Contested vs. Uncontested**
   - Once Round 0 ends:
     - For each player with >1 interested user → place them in the contested pool for Round 1 Auction.
     - For those with a single interested user → that user retains them at base price.
3. **Announcement**
   - The system can post group updates:
     - "Round 0 has ended. X players are contested. Auction Round 1 starts soon."

---

## 4. Auction Rounds

### 4.1 Auction Initialization
- **Auction Start**
  - After Round 0 ends, the system identifies contested players.
  - The admin (or system) initiates the auction with `/start_auction` or an inline button.
  - The bot announces in the group: "Auction Round 1 is starting! X players are contested."

### 4.2 Auction Flow
1. **Player Selection**
   - The system selects the first contested player.
   - The bot announces in the group:
     ```
     "AUCTION: Player X (BAT)
      Base Price: 10.0 Cr
      Interested Users: @User1, @User2, @User3
      Starting Bid: 10.0 Cr
      Time Remaining: 2:00"
     ```

2. **Bidding Process**
   - Users can bid using inline buttons: `[ Bid 10.5 Cr ] [ Bid 11.0 Cr ] [ Pass ]`
   - Each bid extends the timer by a set amount (e.g., 30 seconds).
   - The bot updates the message with each new bid:
     ```
     "AUCTION: Player X (BAT)
      Current Bid: 11.0 Cr by @User2
      Previous Bid: 10.5 Cr by @User1
      Time Remaining: 1:45"
     ```

3. **Auction Conclusion**
   - When the timer expires, the highest bidder wins:
     ```
     "AUCTION ENDED: Player X (BAT)
      SOLD to @User2 for 11.0 Cr!"
     ```
   - The system updates the UserPlayer record with the final purchase price.
   - The bot moves to the next contested player.

### 4.3 Auction Rounds
- **Multiple Rounds**
  - Auction can be split into multiple rounds (e.g., by player type or value).
  - Each round follows the same basic flow but with different player pools.

### 4.4 Post-Auction
- **Summary**
  - After all contested players are auctioned, the bot provides a summary:
    ```
    "Auction Complete!
     Total Players Auctioned: 25
     Highest Bid: Player Y for 15.0 Cr by @User3
     Most Acquisitions: @User2 (8 players)"
    ```
- **Team Updates**
  - Each user's team is updated with their auction acquisitions.
  - Users can view their updated teams with `/my_team`.

---

## 5. Team Management

### 5.1 Viewing Team
- **Command**: `/my_team`
- **Response**:
  ```
  "🏏 Your Team in <GullyName> 🏏

   Total Points: 350

   Players:
   • Virat Kohli (BAT, RCB) - 45 pts
   • Jasprit Bumrah (BOWL, MI) - 60 pts
   ...

   [ Manage Team ] [ View Stats ]"
  ```

### 5.2 Team Analysis
- **Inline Button**: `[ View Stats ]`
- **Response**:
  ```
  "Team Analysis:
   
   Role Distribution:
   • Batsmen: 6
   • Bowlers: 6
   • All-Rounders: 4
   • Wicketkeepers: 2
   
   Team Composition:
   • RCB: 4 players
   • MI: 3 players
   • CSK: 3 players
   ...
   
   [ Back to Team ] [ Performance Breakdown ]"
  ```

### 5.3 Player Performance
- **Inline Button**: `[ Performance Breakdown ]`
- **Response**:
  ```
  "Player Performance:
   
   Top Performers:
   1. Jasprit Bumrah - 60 pts
   2. Virat Kohli - 45 pts
   3. MS Dhoni - 40 pts
   
   Bottom Performers:
   1. Player X - 5 pts
   2. Player Y - 10 pts
   3. Player Z - 12 pts
   
   [ Back to Stats ] [ Substitution Options ]"
  ```

---

## 6. Performance Tracking

### 6.1 Match Updates
- **Automatic Updates**
  - After each real-world match, the system updates player performances.
  - The bot can send notifications to users:
    ```
    "Match Update: MI vs RCB
     
     Your Players:
     • Virat Kohli: 75 runs, 2 catches - 15 pts
     • Jasprit Bumrah: 3 wickets - 12 pts
     
     Team Points: +27
     
     [ View Full Team ] [ Match Details ]"
    ```

### 6.2 Leaderboard
- **Command**: `/leaderboard`
- **Response**:
  ```
  "Gully Leaderboard:
   
   1. @User1 - 450 pts
   2. @User2 - 425 pts
   3. @User3 - 380 pts
   ...
   
   Your Position: 5th (350 pts)
   
   [ View Top Teams ] [ My Team ]"
  ```

### 6.3 Player Rankings
- **Command**: `/player_rankings`
- **Response**:
  ```
  "Top Players in Gully:
   
   1. Jasprit Bumrah (BOWL) - 85 pts
   2. Virat Kohli (BAT) - 80 pts
   3. MS Dhoni (WK) - 75 pts
   ...
   
   [ Filter by Role ] [ Players in My Team ]"
  ```

---

## 7. Squad Constraints & Validation

### 7.1 Role Constraints
- **Minimum Requirements**
  - Batsmen: 4-8
  - Bowlers: 4-8
  - All-Rounders: 2-6
  - Wicketkeepers: 1-4
  - Total: 18 players

### 7.2 Budget Constraints
- **Initial Budget**: 120 Cr
- **Maximum Spend**: Cannot exceed budget
- **Minimum Spend**: No specific minimum, but all 18 spots must be filled

### 7.3 Team Composition Constraints
- **Maximum Players from Same Team**: 4 (to ensure diversity)

### 7.4 Validation Process
- **Automatic Validation**
  - When user attempts to submit squad
  - Before finalizing auction results
  - When making substitutions
- **Validation Messages**
  - If invalid: "Your squad doesn't meet requirements. You need at least 4 batsmen."
  - If valid: "Squad validated successfully!"

---

## 8. Edge Cases & Handling

### 8.1 Incomplete Squads
- **Auto-Completion**
  - If a user doesn't complete their squad by the deadline, the system can auto-assign players.
  - The bot notifies: "Your squad was incomplete. The system has auto-assigned players to complete your squad."

### 8.2 Budget Overruns
- **Auction Limits**
  - During auctions, users cannot bid beyond their remaining budget.
  - The bot prevents invalid bids: "You don't have enough budget for this bid."

### 8.3 Player Unavailability
- **Injury/Absence Handling**
  - If a real-world player becomes unavailable, the system can:
    - Allow free substitution
    - Auto-substitute with a similar player
    - Award partial points based on replacement player

### 8.4 Tie-Breaking
- **Equal Bids**
  - In case of simultaneous equal bids, the first bidder gets priority.
  - The bot announces: "Equal bids received. @User1's bid was first and is accepted."

### 8.5 Disconnections
- **Session Recovery**
  - If a user disconnects during squad selection or auction, they can resume where they left off.
  - The bot provides a recovery option: "You have an incomplete session. Would you like to continue?"

---

## 9. Example Conversations

### 9.1 Round 0 Squad Selection

**User**: /submit_squad

**Bot**:
```
"Welcome to Round 0 squad selection.
 You have 18 spots and 100 Cr.
 How do you want to start?"

[ Filter by Batsmen ]   [ Filter by Bowlers ]
[ Filter by All-Rounders ]  [ Filter by Wicketkeepers ]
[ Search by Team ]   [ View Squad ]
```

**User**: *taps [ Filter by Batsmen ]*

**Bot**:
```
"Showing Batsmen (page 1):
 1) Rohit Sharma (Base 10 Cr) -> [Add]
 2) Virat Kohli (Base 10 Cr) -> [Add]
 ...

[ << Prev ]   [ Next >> ]
[ Switch Filter ]   [ View Squad ]   [ Cancel ]
```

**User**: *taps [Add] for Virat Kohli*

**Bot**:
```
"Virat Kohli added.
 Squad: 1/18, Budget Used: 10/100 Cr"

[ Undo Add ] [ Continue Selecting ] [ View Squad ] [ Submit Squad ]
```

**User**: *taps [ View Squad ]*

**Bot**:
```
"Your Squad:
 1) Virat Kohli (BAT) - 10.0 Cr
 Spots used: 1/18, Budget used: 10.0/100 Cr

[ Remove Player Kohli ] [ Continue Selecting ] [ Submit Squad ]
```

### 9.2 Auction Bidding

**Bot** (in group):
```
"AUCTION: Rohit Sharma (BAT)
 Base Price: 10.0 Cr
 Interested Users: @User1, @User2
 Starting Bid: 10.0 Cr
 Time Remaining: 2:00"

[ Bid 10.5 Cr ] [ Bid 11.0 Cr ] [ Pass ]
```

**User1**: *taps [ Bid 10.5 Cr ]*

**Bot** (updates message):
```
"AUCTION: Rohit Sharma (BAT)
 Current Bid: 10.5 Cr by @User1
 Time Remaining: 1:45"

[ Bid 11.0 Cr ] [ Bid 11.5 Cr ] [ Pass ]
```

**User2**: *taps [ Bid 11.0 Cr ]*

**Bot** (updates message):
```
"AUCTION: Rohit Sharma (BAT)
 Current Bid: 11.0 Cr by @User2
 Previous Bid: 10.5 Cr by @User1
 Time Remaining: 1:30"

[ Bid 11.5 Cr ] [ Bid 12.0 Cr ] [ Pass ]
```

**User1**: *doesn't bid again, timer expires*

**Bot**:
```
"AUCTION ENDED: Rohit Sharma (BAT)
 SOLD to @User2 for 11.0 Cr!"
```

### 9.3 Team Management

**User**: /my_team

**Bot**:
```
"🏏 Your Team in IPL Fantasy 🏏

 Total Points: 350

 Players:
 • Virat Kohli (BAT, RCB) - 45 pts
 • Jasprit Bumrah (BOWL, MI) - 60 pts
 ...

 [ Manage Team ] [ View Stats ]"
```

**User**: *taps [ View Stats ]*

**Bot**:
```
"Team Analysis:
 
 Role Distribution:
 • Batsmen: 6
 • Bowlers: 6
 • All-Rounders: 4
 • Wicketkeepers: 2
 
 Team Composition:
 • RCB: 4 players
 • MI: 3 players
 • CSK: 3 players
 ...
 
 [ Back to Team ] [ Performance Breakdown ]"
```

---

## 10. Flow Diagrams

### 10.1 Round 0 Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PRIVATE CHAT: Round 0 Initialization                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│1) User taps [Build My Squad] or types /submit_squad                    │
│   - Bot checks if user has active Gully                                │
│   - Bot checks if Round 0 is open                                      │
│   - Bot checks if user already submitted a squad                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│2) Bot presents filtering options:                                      │
│   [Filter by Batsmen] [Filter by Bowlers] [All-Rounders] [Wicketkeepers]│
│   [Search by Team] [View Squad]                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│3) User selects filter, bot shows players with [Add] buttons            │
│   - User taps [Add] for a player                                       │
│   - Bot checks budget and role constraints                             │
│   - If valid, adds player to temp squad                                │
│   - If invalid, shows error message                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│4) User continues adding players until squad is complete                │
│   - Can view squad at any time                                         │
│   - Can remove players if needed                                       │
│   - Bot tracks budget usage and role distribution                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│5) User taps [Submit Squad]                                             │
│   - Bot validates final squad                                          │
│   - If valid, asks for confirmation                                    │
│   - If invalid, shows error message                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│6) User confirms submission                                             │
│   - Bot finalizes squad in database                                    │
│   - Bot notifies group of submission                                   │
│   - Round 0 complete for this user                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Auction Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GROUP CHAT: Auction Initialization                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│1) Admin or system initiates auction                                    │
│   - Bot announces auction start                                        │
│   - Bot identifies contested players                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│2) Bot selects first contested player                                   │
│   - Announces player details                                           │
│   - Shows starting bid and timer                                       │
│   - Provides bid buttons                                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│3) Users place bids                                                     │
│   - Each bid extends timer                                             │
│   - Bot updates message with current bid                               │
│   - Bot prevents invalid bids (over budget)                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│4) Timer expires                                                        │
│   - Highest bidder wins player                                         │
│   - Bot announces winner                                               │
│   - System updates database                                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│5) Process repeats for all contested players                            │
│   - Bot moves to next player                                           │
│   - Auction continues until all players are sold                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│6) Auction concludes                                                    │
│   - Bot provides summary                                               │
│   - Users can view updated teams                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

## 11. Implementation Status

The team building workflow is currently in development with the following components:

### Round 0: Initial Squad Selection
- ✅ Basic squad selection UI
- ✅ Player filtering and pagination
- ✅ Budget and role constraint tracking
- ⚠️ Squad validation (partial implementation)
- ⚠️ Re-submission handling (not implemented)

### Auction Rounds
- ✅ Contested player identification
- ⚠️ Auction UI (partial implementation)
- ⚠️ Bidding logic (partial implementation)
- ❌ Timer functionality (not implemented)
- ❌ Multi-round support (not implemented)

### Team Management
- ✅ Basic team viewing
- ⚠️ Team analysis (partial implementation)
- ❌ Performance breakdown (not implemented)
- ❌ Substitutions (not implemented)

### Performance Tracking
- ⚠️ Match updates (partial implementation)
- ❌ Leaderboard (not implemented)
- ❌ Player rankings (not implemented)

### Squad Constraints & Validation
- ✅ Basic role constraints
- ✅ Budget constraints
- ⚠️ Team composition constraints (partial implementation)
- ⚠️ Validation messaging (partial implementation)

### Edge Cases & Handling
- ❌ Auto-completion (not implemented)
- ⚠️ Budget overrun prevention (partial implementation)
- ❌ Player unavailability handling (not implemented)
- ❌ Tie-breaking (not implemented)
- ❌ Session recovery (not implemented) 