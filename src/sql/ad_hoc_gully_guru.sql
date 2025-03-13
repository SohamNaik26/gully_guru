-- Count of players by team in players table
-- SELECT 
--     DISTINCT player_type
-- FROM 
--     public.players


-- Basic queries to view data
SELECT 
    *
FROM 
    public.users

SELECT 
    *
FROM 
    public.gullies

SELECT 
    *
FROM 
    public.gully_participants

-- Verify the new columns in gully_participants
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM 
    information_schema.columns
WHERE 
    table_name = 'gully_participants'
ORDER BY 
    ordinal_position;

-- Check if the ParticipantRole enum type exists
SELECT 
    t.typname AS enum_name,
    e.enumlabel AS enum_value
FROM 
    pg_type t
JOIN 
    pg_enum e ON t.oid = e.enumtypid
WHERE 
    t.typname = 'participantrole'
ORDER BY 
    e.enumsortorder;

-- Check gully_participants with the new fields
SELECT 
    id,
    gully_id,
    user_id,
    team_name,
    budget,
    points,
    role,
    has_submitted_squad,
    submission_time
FROM 
    public.gully_participants
ORDER BY 
    id;

-- Count of participants by role
SELECT 
    role, 
    COUNT(*) as count
FROM 
    public.gully_participants
GROUP BY 
    role;

-- Count of participants by submission status
SELECT 
    has_submitted_squad, 
    COUNT(*) as count
FROM 
    public.gully_participants
GROUP BY 
    has_submitted_squad;
