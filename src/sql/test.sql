
SELECT * FROM users


SELECT * FROM gullies;



SELECT * FROM gully_participants
WHERE gully_id = 8;





SELECT * FROM participant_players
WHERE gully_participant_id = 31
-- LEFT JOIN players ON players.id = participant_players.player_id
-- WHERE gully_participant_id IN (SELECT id FROM gully_participants WHERE gully_id = 7);







