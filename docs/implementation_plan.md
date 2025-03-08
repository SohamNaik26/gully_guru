# Implementation Plan: Streamlined User Journey

This document outlines the implementation tasks required to support the streamlined user journey for onboarding and initial squad submission.

## 1. Bot Code Implementation

### Command Handlers

| Command | File | Implementation Tasks |
|---------|------|----------------------|
| `/start` | `src/bot/handlers/start.py` | - Update to detect new users<br>- Add name collection flow<br>- Add deep linking support<br>- Prompt for squad submission if not submitted |
| `/submit_squad` | `src/bot/handlers/auction.py` | - Enhance player selection UI<br>- Add budget tracking<br>- Improve validation logic<br>- Add group notification on completion |
| `/auction_status` | `src/bot/handlers/auction.py` | - Update to show status of all rounds<br>- Include Round 0 submission status<br>- Add countdown to deadline<br>- Show Round 1 and 2 status |

### Event Handlers

| Event | File | Implementation Tasks |
|-------|------|----------------------|
| New Member | `src/bot/middleware.py` | - Detect when users are added to group<br>- Send welcome message with deep link<br>- Auto-register user in database |
| Callback Queries | `src/bot/callbacks/auction.py` | - Handle player selection callbacks<br>- Implement filter callbacks<br>- Add pagination for player lists |

### UI Components

| Component | File | Implementation Tasks |
|-----------|------|----------------------|
| Player Selection Keyboard | `src/bot/keyboards/auction.py` | - Enhance `get_squad_selection_keyboard`<br>- Add filter buttons<br>- Improve pagination |
| Squad Confirmation | `src/bot/keyboards/auction.py` | - Create `get_squad_confirmation_keyboard`<br>- Add Yes/No buttons |
| Player Filters | `src/bot/keyboards/players.py` | - Enhance filter options<br>- Add price range filters |

## 2. API Implementation

### Endpoints

| Endpoint | File | Implementation Tasks |
|----------|------|----------------------|
| `/users/register` | `src/api/routes/users.py` | - Update to handle auto-registration<br>- Add support for minimal registration |
| `/squads/submit` | `src/api/routes/squads.py` | - Enhance validation logic<br>- Add budget checking<br>- Implement squad balance validation |
| `/squads/status` | `src/api/routes/squads.py` | - Add endpoint to get submission status<br>- Include deadline information |
| `/players/list` | `src/api/routes/players.py` | - Add filtering by type, team, price<br>- Improve pagination |

### API Client Methods

| Method | File | Implementation Tasks |
|--------|------|----------------------|
| `register_user` | `src/bot/client.py` | - Update to handle minimal registration<br>- Add support for auto-registration |
| `submit_squad` | `src/bot/client.py` | - Enhance validation logic<br>- Add budget checking |
| `get_squad_status` | `src/bot/client.py` | - Add method to get submission status<br>- Include deadline information |
| `get_players` | `src/bot/client.py` | - Add filtering by type, team, price<br>- Improve pagination |

## 3. Database Models

### Updates to Existing Models

| Model | File | Implementation Tasks |
|-------|------|----------------------|
| `User` | `src/db/models/user.py` | - Add fields for registration status<br>- Add fields for onboarding completion |
| `Squad` | `src/db/models/squad.py` | - Add fields for submission status<br>- Add fields for validation status |
| `Player` | `src/db/models/player.py` | - Ensure fields for filtering are indexed<br>- Add fields for display in selection UI |

### New Models (if needed)

| Model | File | Implementation Tasks |
|-------|------|----------------------|
| `SquadSubmission` | `src/db/models/squad_submission.py` | - Track submission attempts<br>- Store validation results<br>- Link to final squad |
| `OnboardingStatus` | `src/db/models/onboarding.py` | - Track onboarding steps<br>- Store completion status |

## 4. Pydantic Schemas

### Request Schemas

| Schema | File | Implementation Tasks |
|--------|------|----------------------|
| `UserRegistrationRequest` | `src/api/schemas/users.py` | - Update to support minimal registration<br>- Add validation for required fields |
| `SquadSubmissionRequest` | `src/api/schemas/squads.py` | - Add validation for player list<br>- Add budget validation<br>- Add squad balance validation |
| `PlayerFilterRequest` | `src/api/schemas/players.py` | - Add filters for type, team, price<br>- Add pagination parameters |

### Response Schemas

| Schema | File | Implementation Tasks |
|--------|------|----------------------|
| `UserResponse` | `src/api/schemas/users.py` | - Add fields for registration status<br>- Add fields for onboarding completion |
| `SquadSubmissionResponse` | `src/api/schemas/squads.py` | - Add fields for submission status<br>- Add fields for validation results |
| `SquadStatusResponse` | `src/api/schemas/squads.py` | - Add fields for submission status<br>- Include deadline information |
| `PlayerListResponse` | `src/api/schemas/players.py` | - Enhance player information<br>- Add pagination metadata |

## 5. Implementation Sequence

1. **Database Model Updates**
   - Update existing models
   - Create new models if needed
   - Run migrations

2. **API Implementation**
   - Update Pydantic schemas
   - Implement/update API endpoints
   - Add validation logic

3. **Bot Client Updates**
   - Update API client methods
   - Add new methods as needed

4. **UI Components**
   - Update keyboard modules
   - Enhance inline keyboards
   - Improve pagination

5. **Command Handlers**
   - Update `/start` command
   - Enhance `/submit_squad` command
   - Update `/auction_status` command to include all rounds

6. **Event Handlers**
   - Implement new member detection
   - Add welcome message with deep link
   - Handle callback queries

7. **Testing**
   - Test user registration flow
   - Test squad submission flow
   - Test group notifications

## 6. Priority Tasks

These tasks should be prioritized for immediate implementation:

1. **New Member Detection and Welcome Message**
   - Critical for onboarding new users
   - Provides clear entry point to private chat

2. **Enhanced Squad Selection UI**
   - Improves user experience during squad selection
   - Makes it easier to browse and select players

3. **Budget Tracking and Validation**
   - Ensures squads meet requirements
   - Provides real-time feedback to users

4. **Group Notifications**
   - Enhances social proof
   - Helps admins track progress 