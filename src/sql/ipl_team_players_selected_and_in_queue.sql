SELECT
    p.name AS player_name,
    p.team AS player_ipl_team,
    p.player_type AS player_role,
    p.base_price AS price,
    p.sold_price AS current_ipl_price
FROM auction_queue aq
LEFT JOIN players p ON p.id = aq.player_id
WHERE aq.gully_id = 7
ORDER BY p.sold_price DESC;