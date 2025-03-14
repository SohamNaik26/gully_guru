# team_building.md

## Overview
This document details the **team building process** for your fantasy cricket platform. It covers the entire workflow from initial squad selection (Round 0) through auction rounds, team management, and performance tracking. The process is designed to be intuitive, engaging, and fair for all participants in a Gully.

---

## Table of Contents
1. [Introduction & Goals](#introduction--goals)  
2. [Team Building Phases](#team-building-phases)  
3. [Round 0: Initial Squad Selection](#round-0-initial-squad-selection)  

## 2. Team Building Phases
The team building process consists of several distinct phases:

1. **Round 0**: Initial squad selection where users pick players within budget constraints.

---

## 3. Round 0: Initial Squad Selection

### 3.1 Entry Points & Initialization
- **Private Chat Menu**
  - After onboarding, users see an inline button: `[ Build My Squad (Round 0) ]`
  - The bot checks:
    - If the user has an active Gully
    - If Round 0 is open
    - If the user already submitted a squad
- **Conditional Flows**
  - If already submitted: "You've already submitted your squad."
  - If Round 0 is closed: "Round 0 has ended."
  - Otherwise → proceed with the selection flow.

### 3.2 Budget & Player Count Constraints
- Each user typically has 120 Cr (or similar) to spend on 18 players.
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