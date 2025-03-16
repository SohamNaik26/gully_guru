
SELECT * FROM users;

SELECT * FROM gullies;

-- UPDATE gullies SET status = 'draft' WHERE id = 6;


SELECT * FROM gully_participants;
SELECT * FROM draft_selections;
SELECT * FROM participant_players;
SELECT * FROM auction_queue;
SELECT * FROM draft_selections
WHERE gully_participant_id = 14