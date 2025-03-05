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

## 2. Game Flow & Mechanics

### Initial Squad Submission (Round 0)
- **Private Submission:** Each manager submits **18 players** via the Telegram bot.
- **Budget Validation:** Total base price must **not exceed 100 Cr**.
- **Contested vs. Uncontested Players:**
  - **Uncontested players** are assigned at base price.
  - **Contested players** go into a **Round 1 Auction**.

### Round 1 Auction
- **Live Auction via Telegram Group**
- **Bid Increments:**  
  - **<1 Cr:** +0.10 Cr  
  - **<2 Cr:** +0.20 Cr  
  - **<5 Cr:** +0.50 Cr  
  - **≥5 Cr:** (Increment rule TBD)
- **Auction Timer:** If no new bid is received within **15 seconds**, the highest bidder wins.
- **Budget Deduction:** Winning bid is deducted from the manager’s budget.

### Weekly Transfer Windows
- **Duration:** Every weekend for **48 hours**.
- **Bidding System:** Managers **list players for sale** and **bid asynchronously**.
- **Bid Limits:** Each manager gets **4 free bids**; additional bids cost **10 Lakhs**.
- **Outcome:** Transfers are executed once bids are **accepted** or **expire**.

### Setting Playing XI & Scoring
- **Daily Lineup Selection:** Managers choose **11 players + Captain + Vice-Captain**.
- **Scoring System:**  
  - **Dream11 rules applied** (runs, wickets, strike rates, economy rate bonuses).
  - **Leaderboards updated daily.**

### Season Conclusion
- **Final Outcome:**  
  - Manager with **highest cumulative points** at season end wins.  
  - **Tie-breakers:** Total wickets, runs, or other factors.

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