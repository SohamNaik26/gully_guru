

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


SELECT 
    *
FROM participant_players p
LEFT JOIN players pl ON pl.id = p.player_id
WHERE p.gully_participant_id = 16;