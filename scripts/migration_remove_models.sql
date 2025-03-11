-- Migration script to remove models and modify GullyParticipant

-- 1. Remove fields from GullyParticipant
ALTER TABLE gully_participants DROP COLUMN IF EXISTS is_active;
ALTER TABLE gully_participants DROP COLUMN IF EXISTS last_active_at;
ALTER TABLE gully_participants DROP COLUMN IF EXISTS registration_complete;

-- 2. Remove status column from Gully
ALTER TABLE gullies DROP COLUMN IF EXISTS status;

-- 3. Drop models from line 195-341
-- Drop Match and MatchPerformance tables
DROP TABLE IF EXISTS match_performances;
DROP TABLE IF EXISTS matches;

-- Drop AuctionRound and AuctionBid tables
DROP TABLE IF EXISTS auction_bids;
DROP TABLE IF EXISTS auction_rounds;

-- Drop TransferWindow, TransferListing, and TransferBid tables
DROP TABLE IF EXISTS transfer_bids;
DROP TABLE IF EXISTS transfer_listings;
DROP TABLE IF EXISTS transfer_windows;

-- 4. Drop AdminPermission table
DROP TABLE IF EXISTS admin_permissions; 