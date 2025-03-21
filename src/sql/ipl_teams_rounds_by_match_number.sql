WITH match_nums AS (
    SELECT DISTINCT match_number FROM ipl_matches_schedule
),
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
all_team_match_combos AS (
    SELECT t.team, m.match_number
    FROM teams t
    CROSS JOIN match_nums m
),
base AS (
    SELECT match_number, home_team AS team FROM ipl_matches_schedule
    UNION ALL
    SELECT match_number, away_team AS team FROM ipl_matches_schedule
),
team_match_counts AS (
    SELECT team, match_number, COUNT(*) AS matches_played
    FROM base
    GROUP BY team, match_number
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
        ) AS cumulative_played
    FROM team_matches_with_zeros
),
pivoted AS (
    SELECT
        team,
        MAX(CASE WHEN match_number = 1 THEN cumulative_played ELSE 0 END) AS match_1,
        MAX(CASE WHEN match_number = 2 THEN cumulative_played ELSE 0 END) AS match_2,
        MAX(CASE WHEN match_number = 3 THEN cumulative_played ELSE 0 END) AS match_3,
        MAX(CASE WHEN match_number = 4 THEN cumulative_played ELSE 0 END) AS match_4,
        MAX(CASE WHEN match_number = 5 THEN cumulative_played ELSE 0 END) AS match_5,
        MAX(CASE WHEN match_number = 6 THEN cumulative_played ELSE 0 END) AS match_6,
        MAX(CASE WHEN match_number = 7 THEN cumulative_played ELSE 0 END) AS match_7,
        MAX(CASE WHEN match_number = 8 THEN cumulative_played ELSE 0 END) AS match_8,
        MAX(CASE WHEN match_number = 9 THEN cumulative_played ELSE 0 END) AS match_9,
        MAX(CASE WHEN match_number = 10 THEN cumulative_played ELSE 0 END) AS match_10,
        MAX(CASE WHEN match_number = 11 THEN cumulative_played ELSE 0 END) AS match_11,
        MAX(CASE WHEN match_number = 12 THEN cumulative_played ELSE 0 END) AS match_12,
        MAX(CASE WHEN match_number = 13 THEN cumulative_played ELSE 0 END) AS match_13,
        MAX(CASE WHEN match_number = 14 THEN cumulative_played ELSE 0 END) AS match_14,
        MAX(CASE WHEN match_number = 15 THEN cumulative_played ELSE 0 END) AS match_15,
        MAX(CASE WHEN match_number = 16 THEN cumulative_played ELSE 0 END) AS match_16,
        MAX(CASE WHEN match_number = 17 THEN cumulative_played ELSE 0 END) AS match_17,
        MAX(CASE WHEN match_number = 18 THEN cumulative_played ELSE 0 END) AS match_18,
        MAX(CASE WHEN match_number = 19 THEN cumulative_played ELSE 0 END) AS match_19,
        MAX(CASE WHEN match_number = 20 THEN cumulative_played ELSE 0 END) AS match_20,
        MAX(CASE WHEN match_number = 21 THEN cumulative_played ELSE 0 END) AS match_21,
        MAX(CASE WHEN match_number = 22 THEN cumulative_played ELSE 0 END) AS match_22,
        MAX(CASE WHEN match_number = 23 THEN cumulative_played ELSE 0 END) AS match_23,
        MAX(CASE WHEN match_number = 24 THEN cumulative_played ELSE 0 END) AS match_24,
        MAX(CASE WHEN match_number = 25 THEN cumulative_played ELSE 0 END) AS match_25,
        MAX(CASE WHEN match_number = 26 THEN cumulative_played ELSE 0 END) AS match_26,
        MAX(CASE WHEN match_number = 27 THEN cumulative_played ELSE 0 END) AS match_27,
        MAX(CASE WHEN match_number = 28 THEN cumulative_played ELSE 0 END) AS match_28,
        MAX(CASE WHEN match_number = 29 THEN cumulative_played ELSE 0 END) AS match_29,
        MAX(CASE WHEN match_number = 30 THEN cumulative_played ELSE 0 END) AS match_30,
        MAX(CASE WHEN match_number = 31 THEN cumulative_played ELSE 0 END) AS match_31,
        MAX(CASE WHEN match_number = 32 THEN cumulative_played ELSE 0 END) AS match_32,
        MAX(CASE WHEN match_number = 33 THEN cumulative_played ELSE 0 END) AS match_33,
        MAX(CASE WHEN match_number = 34 THEN cumulative_played ELSE 0 END) AS match_34,
        MAX(CASE WHEN match_number = 35 THEN cumulative_played ELSE 0 END) AS match_35,
        MAX(CASE WHEN match_number = 36 THEN cumulative_played ELSE 0 END) AS match_36,
        MAX(CASE WHEN match_number = 37 THEN cumulative_played ELSE 0 END) AS match_37,
        MAX(CASE WHEN match_number = 38 THEN cumulative_played ELSE 0 END) AS match_38,
        MAX(CASE WHEN match_number = 39 THEN cumulative_played ELSE 0 END) AS match_39,
        MAX(CASE WHEN match_number = 40 THEN cumulative_played ELSE 0 END) AS match_40,
        MAX(CASE WHEN match_number = 41 THEN cumulative_played ELSE 0 END) AS match_41,
        MAX(CASE WHEN match_number = 42 THEN cumulative_played ELSE 0 END) AS match_42,
        MAX(CASE WHEN match_number = 43 THEN cumulative_played ELSE 0 END) AS match_43,
        MAX(CASE WHEN match_number = 44 THEN cumulative_played ELSE 0 END) AS match_44,
        MAX(CASE WHEN match_number = 45 THEN cumulative_played ELSE 0 END) AS match_45,
        MAX(CASE WHEN match_number = 46 THEN cumulative_played ELSE 0 END) AS match_46,
        MAX(CASE WHEN match_number = 47 THEN cumulative_played ELSE 0 END) AS match_47,
        MAX(CASE WHEN match_number = 48 THEN cumulative_played ELSE 0 END) AS match_48,
        MAX(CASE WHEN match_number = 49 THEN cumulative_played ELSE 0 END) AS match_49,
        MAX(CASE WHEN match_number = 50 THEN cumulative_played ELSE 0 END) AS match_50,
        MAX(CASE WHEN match_number = 51 THEN cumulative_played ELSE 0 END) AS match_51,
        MAX(CASE WHEN match_number = 52 THEN cumulative_played ELSE 0 END) AS match_52,
        MAX(CASE WHEN match_number = 53 THEN cumulative_played ELSE 0 END) AS match_53,
        MAX(CASE WHEN match_number = 54 THEN cumulative_played ELSE 0 END) AS match_54,
        MAX(CASE WHEN match_number = 55 THEN cumulative_played ELSE 0 END) AS match_55,
        MAX(CASE WHEN match_number = 56 THEN cumulative_played ELSE 0 END) AS match_56,
        MAX(CASE WHEN match_number = 57 THEN cumulative_played ELSE 0 END) AS match_57,
        MAX(CASE WHEN match_number = 58 THEN cumulative_played ELSE 0 END) AS match_58,
        MAX(CASE WHEN match_number = 59 THEN cumulative_played ELSE 0 END) AS match_59,
        MAX(CASE WHEN match_number = 60 THEN cumulative_played ELSE 0 END) AS match_60,
        MAX(CASE WHEN match_number = 61 THEN cumulative_played ELSE 0 END) AS match_61,
        MAX(CASE WHEN match_number = 62 THEN cumulative_played ELSE 0 END) AS match_62,
        MAX(CASE WHEN match_number = 63 THEN cumulative_played ELSE 0 END) AS match_63,
        MAX(CASE WHEN match_number = 64 THEN cumulative_played ELSE 0 END) AS match_64,
        MAX(CASE WHEN match_number = 65 THEN cumulative_played ELSE 0 END) AS match_65,
        MAX(CASE WHEN match_number = 66 THEN cumulative_played ELSE 0 END) AS match_66,
        MAX(CASE WHEN match_number = 67 THEN cumulative_played ELSE 0 END) AS match_67,
        MAX(CASE WHEN match_number = 68 THEN cumulative_played ELSE 0 END) AS match_68,
        MAX(CASE WHEN match_number = 69 THEN cumulative_played ELSE 0 END) AS match_69,
        MAX(CASE WHEN match_number = 70 THEN cumulative_played ELSE 0 END) AS match_70,
        MAX(CASE WHEN match_number = 71 THEN cumulative_played ELSE 0 END) AS match_71,
        MAX(CASE WHEN match_number = 72 THEN cumulative_played ELSE 0 END) AS match_72,
        MAX(CASE WHEN match_number = 73 THEN cumulative_played ELSE 0 END) AS match_73,
        MAX(CASE WHEN match_number = 74 THEN cumulative_played ELSE 0 END) AS match_74,
        MAX(CASE WHEN match_number = 75 THEN cumulative_played ELSE 0 END) AS match_75,
        MAX(CASE WHEN match_number = 76 THEN cumulative_played ELSE 0 END) AS match_76
    FROM cumulative_matches
    GROUP BY team
)

SELECT *
FROM pivoted
ORDER BY team;