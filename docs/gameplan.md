# GullyGuru: Final Product Requirements Document (PDR)

## Table of Contents
1. [Overview & Objectives](#overview--objectives)  
2. [Game Flow & Mechanics](#game-flow--mechanics)  
   - [Initial Squad Submission (Round 0)](#initial-squad-submission-round-0)  
   - [Round 1 Auction](#round-1-auction)  
   - [Weekly Transfer Windows](#weekly-transfer-windows)  
   - [Setting Playing XI & Scoring](#setting-playing-xi--scoring)  
   - [Season Conclusion](#season-conclusion)  
3. [Technical Details](#technical-details)  
   - [Backend Architecture](#backend-architecture)  
   - [Data Pipelines & Operations](#data-pipelines--operations)  
   - [API Endpoints & Asynchronous Operations](#api-endpoints--asynchronous-operations)  
   - [Telegram Bot Interface](#telegram-bot-interface)
4. [Database Schema & Approach](#database-schema--approach)  
   - [Schema Overview](#schema-overview)  
   - [Schema Details](#schema-details)  
   - [Bulk Import & Data Validation](#bulk-import--data-validation)  
   - [Migrations & Optimizations](#migrations--optimizations)  
5. [GCP PostgreSQL System Requirements & Cost Estimate](#gcp-postgresql-system-requirements--cost-estimate)  
6. [Code Quality & CI/CD Practices](#code-quality--cicd-practices)  
7. [Remaining Questions](#remaining-questions)  
8. [Conclusion & Next Steps](#conclusion--next-steps)

---

## 1. Overview & Objectives

**GullyGuru** is a **fantasy cricket platform** targeting an Indian audience, where users (managers) form teams via a **Telegram bot interface**. Key objectives include:

- **User Engagement:** Managers draft players using an **auction-based system** and adjust their teams via **weekly transfers**.
- **Real-Time Scoring:** Fantasy points are updated **daily** based on **real IPL match data** (Dream11-style scoring).
- **Structured Data Storage:** PostgreSQL schema ensures **clean, validated data for players, auctions, and match stats**.
- **Scalable Architecture:** Using **FastAPI**, **SQLModel**, and **GCP Cloud Run** for high performance.

---

## 2. Game Flow & Mechanics -> User Journey after Onboarding as per onboarding.md doc.


⸻

🚀 Phase 1: Initial Team Selection (Week 0)

🔹 What Happens?
	1.	User joins a Gully (Telegram Group).
	2.	User selects between 15 to 18 players for their squad.
	3.	Users can modify their squad freely before the auction starts.
	4.	Once the auction begins, squads are locked.

✅ Impact on Tables:
	•	user_squad_submissions → Stores player selections.
	•	user_players → Initial squads are stored permanently.
	•	current_teams → Stores budget & squad for quick lookups.

⸻

🚀 Phase 2: Weekly Transfers & Auctions (Every Weekend)

🔹 When? Every Friday to Sunday (for 12 weeks).

⸻

1️⃣ Friday – Transfer Window Opens (Time-Aware Notification System)

🔹 When? 12 PM on Friday.

🔹 What Happens?
	1.	Users must list 4+ players for sale.
	2.	If a user does not list players, the bottom 4 players (by performance) are listed automatically.
	3.	Fair price for each player is calculated (separate system).
	4.	Users are notified in Telegram that the transfer window is open.

✅ Impact on Tables:
	•	auction_queue → Players enter the queue for bidding.

⸻

2️⃣ Saturday – Bidding Period Opens (Time-Aware Notification System)

🔹 When? 12 PM on Saturday.

🔹 What Happens?
	1.	Users can bid on players listed for transfer.
	2.	Bids remain private (users do not see other bids).
	3.	Tiebreaker: If two users bid the same highest amount, the earliest bid wins.
	4.	If a user does not have enough budget, they cannot bid.
	5.	Bidding remains open until 8 PM Sunday.

✅ Impact on Tables:
	•	auction_queue → Bid status updates from pending → bidding.

⸻

3️⃣ Sunday – Transfer Window Closes & Player Assignments

🔹 8 PM – Bidding Automatically Stops (Time-Aware Notification System)
	•	No more bids can be placed.
	•	The highest bid wins automatically.
	•	Users are notified that bidding has ended.

🔹 8 PM – 8:30 PM – Player Assignments & Budget Adjustments
	•	Players are transferred to their new teams.
	•	Budget is updated:
	•	If a player was sold at a higher price than the fair price, the difference is credited to the seller.
	•	If a player was sold at the fair price, the seller gets the exact fair price instantly.
	•	Unsold players move to the transfer market for purchase at fair price.
	•	Users are notified once all transfers are finalized.

✅ Impact on Tables:
	•	user_players → Players are assigned to new owners.
	•	current_teams → Budget updates.
	•	bank_transactions → Tracks bank purchases.
	•	transfer_market → Stores unsold players available for purchase.

⸻

4️⃣ 9 PM - 9:30 PM – Squad Finalization Auction

🔹 Why? This ensures every user has a squad of 15-18 players before the next week starts.

🔹 What Happens?
	1.	Users must finalize their squad of 15-18 players during this time.
	2.	If a user did not win any bids, they must buy players from the transfer market.
	3.	Transfer market is locked until 9 PM; users can only buy during this auction window.
	4.	Users have 30 minutes to purchase players at fair price.
	5.	If a user does not finalize their squad by 9:30 PM, players are auto-assigned.
	6.	Auto-assignment happens in the following way:
	•	Users with lower points get priority.
	•	The best available player within their budget is assigned.
	•	If no affordable player is available, the user plays with a smaller squad.
	7.	Once finalized, squads are locked for the next week.

✅ Impact on Tables:
	•	transfer_market → Players are purchased from here.
	•	user_players → Final squad updates happen here.
	•	current_teams → Updates with the final squads & remaining budget.

⸻

🚀 Phase 3: End of Season (Week 12)

🔹 When? After 12 weeks.
🔹 What Happens?
	1.	Final leaderboard is generated.
	2.	All data is archived for history.
	3.	Users can review their performance.

✅ Impact on Tables:
	•	user_players → Used for final team rankings.
	•	current_teams → Used for budget & performance summary.

⸻

🚀 Finalized Rules & Confirmations

Rule	Implementation
Tiebreaker for Bids	The earliest bid wins in case of a tie.
Bid Cancellation	Not allowed once a bid is placed.
Budget for Sold Players	Users get immediate credit when selling at fair price.
Restricted Market Access	Users cannot buy from transfer market before 9-9:30 PM Sunday.
Auto-Assignment for Missing Players	Users with lower points get priority, assigned based on fair price & budget.




---

## 3. Technical Details

### Backend Architecture
- **Framework:** FastAPI
- **Database:** PostgreSQL (GCP Cloud SQL)
- **Hosting:** GCP Cloud Run  
- **Communication:** Telegram Bot API  

### Data Pipelines & Operations
- **One-time CSV import for IPL players**
- **Daily API sync for match data** using a **cron job**.
- **Bulk Insert using SQLModel for structured data integrity.**

### API Endpoints & Asynchronous Operations
- **FastAPI Endpoints:** Squad submission, auctions, transfers, leaderboard.
- **Database Interaction:** `asyncpg` or `databases` library for non-blocking operations.

### Telegram Bot Interface
- **Command Structure:** Combination of slash commands and inline keyboards
  - **Slash Commands:** Used for simple, direct actions (e.g., `/myteam`, `/bid`)
  - **Inline Keyboards:** Used for multi-step or complex interactions
- **Command Scopes:** Different commands for private chats, group chats, and admin-only
- **Detailed Documentation:** See the [User Management Documentation](./user_management.md#telegram-ui) for complete details on command types and rationale

---

## 4. Database Schema & Approach

### Schema Overview
| Table Name                   | Purpose |
|------------------------------|---------|
| `users`                      | Stores manager details |
| `players`                    | IPL player data (from Cricksheet CSV) |
| `cricksheet_players`         | Unique player identifiers from external sources |
| `cricksheet_player_names`    | Alternative player name mappings |
| `user_squads`                | Mapping of users to drafted players |
| `auctions`                   | Stores final bid auction data |
| `transfers`                  | Transfer listings |
| `points`                     | Fantasy points per match |
| `matches`                    | Metadata for real IPL matches |

### Bulk Import & Data Validation
- **CSV Import:** Pandas reads CSV and converts to SQLModel.
- **Validation:** Pydantic ensures **type correctness** before insertion.
- **Bulk Insert:** `session.bulk_save_objects()` for **fast batch inserts**.

### Migrations & Optimizations
- **Alembic:** Version-controlled schema updates.
- **Indexes:**  
  - **user_id, player_id, match_date** for performance.
- **Partitioning:**  
  - `points` & `matches` partitioned by **match_date** for efficiency.

---

## 5. GCP PostgreSQL System Requirements & Cost Estimate

### Testing Phase
- **Instance Type:** `db-f1-micro` or `db-custom-1-4`
- **Storage:** **10GB SSD**
- **Deployment:** **Single-zone**
- **Estimated Cost:** **$10-$20/month**

### Production Scaling
- **Instance Type:** `db-custom-2-8` (2 vCPUs, 8GB RAM)
- **Estimated Monthly Cost:** **$130-$150/month**

---

## 6. Code Quality & CI/CD Practices
To enforce **clean code**, we add **SQLFluff, Black, and isort** as part of **CI/CD in GitHub**.

### Pre-Commit Hooks Configuration
Modify `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/sqlfluff/sqlfluff
    rev: "latest"
    hooks:
      - id: sqlfluff-lint
      - id: sqlfluff-fix

  - repo: https://github.com/psf/black
    rev: "stable"
    hooks:
      - id: black
        args: [--line-length=88]

  - repo: https://github.com/PyCQA/isort
    rev: "5.10.1"
    hooks:
      - id: isort

---