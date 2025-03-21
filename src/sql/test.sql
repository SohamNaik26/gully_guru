SELECT 
    *,
    start_date_utc::timestamp + INTERVAL '5.5 hours' AS start_date_ist,
    end_date_utc::timestamp + INTERVAL '5.5 hours' AS end_date_ist
FROM ipl_balanced_rounds;

-- SELECT * FROM ipl_matches_schedule ORDER BY match_number;