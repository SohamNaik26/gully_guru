
## API Implementation

### 1. Fantasy Service
- **Status**: 
- **Details**:
  - Created `FantasyService` class in `src/api/services/fantasy.py`
  - Implemented methods:
    - `add_to_draft_squad`: Add a player to the draft squad
    - `remove_from_draft_squad`: Remove a player from the draft squad
    - `get_draft_squad`: Get the current draft squad
    - `submit_squad`: Submit the final squad
    - `get_submission_status`: Check submission status for a Gully
    - `start_auction`: Start the auction process

### 2. API Routes
- **Status**: ⏳ Pending
- **Details**:
  - Need to create routes in `src/api/routes/fantasy.py`:
    ```python
    @router.post("/draft-player", response_model=Dict[str, Any])
    async def add_to_draft_squad(...)
    
    @router.delete("/draft-player/{player_id}", response_model=Dict[str, Any])
    async def remove_from_draft_squad(...)
    
    @router.get("/draft-squad", response_model=Dict[str, Any])
    async def get_draft_squad(...)
    
    @router.post("/submit-squad", response_model=Dict[str, Any])
    async def submit_squad(...)
    
    @router.get("/submission-status/{gully_id}", response_model=Dict[str, Any])
    async def get_submission_status(...)
    
    @router.post("/start-auction/{gully_id}", response_model=Dict[str, Any])
    async def start_auction(...)
    ```

### 3. API Client Service
- **Status**: ⏳ Pending
- **Details**:
  - Need to update `src/api/services/fantasy/client.py` with methods to call the new API endpoints



## Bot Implementation

### 1. Squad Building Module
- **Status**: ⏳ Pending
- **Details**:
  - Create new file `src/bot/features/squad_building.py`
  - Implement callback functions:
    - `build_squad_callback`: Entry point for squad building
    - `filter_callback`: Filter players by type
    - `show_players_page`: Show paginated player list
    - `page_callback`: Handle pagination
    - `add_player_callback`: Add player to draft squad
    - `remove_player_callback`: Remove player from draft squad
    - `view_squad_callback`: View current draft squad
    - `submit_squad_callback`: Submit final squad
    - `confirm_submit_callback`: Confirm squad submission

### 2. Team Module Updates
- **Status**: ⏳ Pending
- **Details**:
  - Update `src/bot/features/team.py` to include squad building options
  - Add `edit_squad_callback` function to allow users to edit their squad

### 3. Admin Module Updates
- **Status**: ⏳ Pending
- **Details**:
  - Update `src/bot/features/admin.py` to include auction initiation
  - Add `admin_start_auction_callback` function to check if all users have submitted squads
  - Add `confirm_start_auction_callback` function to start the auction

### 4. Module Registration
- **Status**: ⏳ Pending
- **Details**:
  - Update `src/bot/features/__init__.py` to register the new handlers

## Implementation Details

### Using Auction Queue for Draft Squad
- Use `AuctionStatus.DRAFT` for players in the draft stage
- When a squad is submitted, update status to `AuctionStatus.PENDING`
- When auction starts, update contested players to `AuctionStatus.BIDDING` and uncontested to `AuctionStatus.COMPLETED`

### Inline Keyboard Approach
- Use inline keyboards instead of slash commands for user interactions
- Implement pagination for player selection
- Provide filtering options by player type
- Show squad summary with budget and player count

### User Flow
1. User selects "Build Squad" from main menu
2. User filters players by type or searches by name
3. User adds players to draft squad
4. User reviews squad and submits when ready
5. Admin checks submission status and starts auction when all users have submitted

## Testing Plan

### Database Testing
- Verify that `has_submitted_squad` and `submission_time` fields are added to `GullyParticipant` model
- Verify that `AuctionStatus.DRAFT` is available in the enum

### API Testing
- Test each API endpoint with valid and invalid inputs
- Verify proper error handling and validation

### Bot Testing
- Test the complete user flow from squad building to submission
- Test admin functionality for checking submission status and starting auction
- Verify proper handling of edge cases (budget limits, player count limits)

## Implementation Order
1. Database updates (✅ Completed)
2. API implementation (🔄 In Progress)
3. Bot functionality (⏳ Pending)

## Requirements from User Input
- Use existing auction queue for player selection
- Track whether participants have submitted their squads
- Use inline keyboards instead of slash commands
- Ensure admin oversight of the process
- Handle edge cases for player selection and budget limits
- Integrate with existing UI/UX flow

This implementation plan addresses all the requirements discussed and provides a clear roadmap for completing the squad building feature.