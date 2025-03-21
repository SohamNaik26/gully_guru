WITH base AS (
    SELECT match_number, round_number, home_team AS team FROM ipl_matches_schedule
    UNION ALL
    SELECT match_number, round_number, away_team AS team FROM ipl_matches_schedule
),

team_match_counts AS (
    SELECT
        team,
        round_number,
        match_number,
        COUNT(*) AS matches_played
    FROM base
    GROUP BY team, round_number, match_number
),

team_rounds_all AS (
    -- generate all team-round pairs to ensure full matrix
    SELECT
        round_number,
        unnest(ARRAY[
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
    FROM (SELECT DISTINCT round_number FROM ipl_matches_schedule) r
),

joined_counts AS (
    SELECT
        tra.round_number,
        tra.team,
        COALESCE(tmc.matches_played, 0) AS matches_played
    FROM team_rounds_all tra
    LEFT JOIN team_match_counts tmc
      ON tra.round_number = tmc.round_number AND tra.team = tmc.team
),

cumulative_matches AS (
    SELECT
        team,
        round_number,
        SUM(matches_played) OVER (
            PARTITION BY team
            ORDER BY round_number
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_matches
    FROM joined_counts
),

pivoted AS (
    SELECT
        team,
        MAX(CASE WHEN round_number = 1 THEN cumulative_matches ELSE 0 END) AS round_1,
        MAX(CASE WHEN round_number = 2 THEN cumulative_matches ELSE 0 END) AS round_2,
        MAX(CASE WHEN round_number = 3 THEN cumulative_matches ELSE 0 END) AS round_3,
        MAX(CASE WHEN round_number = 4 THEN cumulative_matches ELSE 0 END) AS round_4,
        MAX(CASE WHEN round_number = 5 THEN cumulative_matches ELSE 0 END) AS round_5,
        MAX(CASE WHEN round_number = 6 THEN cumulative_matches ELSE 0 END) AS round_6,
        MAX(CASE WHEN round_number = 7 THEN cumulative_matches ELSE 0 END) AS round_7,
        MAX(CASE WHEN round_number = 8 THEN cumulative_matches ELSE 0 END) AS round_8,
        MAX(CASE WHEN round_number = 9 THEN cumulative_matches ELSE 0 END) AS round_9,
        MAX(CASE WHEN round_number = 10 THEN cumulative_matches ELSE 0 END) AS round_10,
        MAX(CASE WHEN round_number = 11 THEN cumulative_matches ELSE 0 END) AS round_11
    FROM cumulative_matches
    GROUP BY team
)

SELECT *
FROM pivoted
ORDER BY team;