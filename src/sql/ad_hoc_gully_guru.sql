
SELECT * FROM users;

SELECT * FROM gullies;

-- UPDATE gullies SET status = 'draft' WHERE id = 6;


SELECT * FROM gully_participants 
-- WHERE id = 14;


SELECT * FROM draft_selections;

SELECT * FROM participant_players 
-- LEFT JOIN players ON participant_players.player_id = players.id
WHERE gully_participant_id = 15;

-- # update state to owned
-- UPDATE participant_players SET status = 'owned' WHERE gully_participant_id = 15;

-- SELECT * FROM auction_queue;
-- SELECT * FROM draft_selections
-- WHERE gully_participant_id = 14