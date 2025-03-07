
-- Count of players by team in players table
SELECT 
    team, COUNT(*) as count
FROM 
    public.players
GROUP BY 
    team
ORDER BY 
    count DESC;
