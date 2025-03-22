SELECT 
    *,
    start_date_utc::timestamp + INTERVAL '5.5 hours' AS start_date_ist,
    end_date_utc::timestamp + INTERVAL '5.5 hours' AS end_date_ist
FROM ipl_balanced_rounds;

-- SELECT * FROM ipl_matches_schedule ORDER BY match_number;

SELECT * FROM gullies;
SELECT * FROM gully_participants
WHERE gully_id = 7;



SELECT 
    g.team_name,
    120 - SUM(p.purchase_price) AS remaining_budget,
    MIN(g.budget) AS min_budget
    
FROM participant_players p
LEFT JOIN gully_participants g
ON p.gully_participant_id = g.id



WHERE g.gully_id = 7 AND p.status = 'owned'

GROUP BY 1