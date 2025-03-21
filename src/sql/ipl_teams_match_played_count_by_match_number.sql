WITH base AS (
    SELECT match_number, home_team AS team FROM ipl_matches_schedule
    UNION ALL
    SELECT match_number, away_team AS team FROM ipl_matches_schedule
),

team_match_counts AS (
    SELECT
        team,
        match_number,
        COUNT(*) AS matches_played
    FROM base
    GROUP BY team, match_number
),

-- generate full matrix: all match_number + team pairs
teams AS (
    SELECT unnest(ARRAY[
        'Chennai Super Kings',
        'Mumbai Indians',
        'Royal Challengers Bengaluru',
        'Kolkata Knight Riders',
        'Delhi Capitals',
        'Sunrisers Hyderabad',
        'Punjab Kings',
        'Rajasthan Royals',
        'Gujarat Titans',
        'Lucknow Super Giants'
    ]) AS team
),
match_nums AS (
    SELECT DISTINCT match_number FROM ipl_matches_schedule
),
all_team_match_combos AS (
    SELECT t.team, m.match_number
    FROM teams t
    CROSS JOIN match_nums m
),

team_matches_with_zeros AS (
    SELECT
        atm.team,
        atm.match_number,
        COALESCE(tmc.matches_played, 0) AS matches_played
    FROM all_team_match_combos atm
    LEFT JOIN team_match_counts tmc
    ON atm.team = tmc.team AND atm.match_number = tmc.match_number
),

cumulative_matches AS (
    SELECT
        team,
        match_number,
        SUM(matches_played) OVER (
            PARTITION BY team ORDER BY match_number
        ) AS cumulative_matches_played
    FROM team_matches_with_zeros
)

SELECT *
FROM cumulative_matches
ORDER BY match_number, team;