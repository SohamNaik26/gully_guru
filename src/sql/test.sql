SELECT 
    *,
    start_date_utc::timestamp + INTERVAL '5.5 hours' AS start_date_ist,
    end_date_utc::timestamp + INTERVAL '5.5 hours' AS end_date_ist
FROM ipl_balanced_rounds;

-- SELECT * FROM ipl_matches_schedule ORDER BY match_number;

SELECT * FROM gullies;
SELECT * FROM gully_participants;


SELECT * FROM draft_selections
LEFT JOIN players ON draft_selections.player_id = players.id
WHERE gully_participant_id = 16;


SELECT * FROM participant_players
WHERE gully_participant_id = 18;



-- WHERE gully_participant_id = 16;


SELECT * FROM ipl_balanced_rounds;