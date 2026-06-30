{{ config(materialized='table') }}

SELECT
    (m.value ->> 'id')::int               AS match_id,
    m.value ->> 'stage'                   AS stage,
    (m.value -> 'homeTeam' ->> 'id')::int AS home_id,
    (m.value -> 'awayTeam' ->> 'id')::int AS away_id,
    -- True on-field score: prefer regularTime + extraTime (knockout),
    -- fall back to fullTime (group stage has no regularTime field).
    COALESCE(
        (m.value -> 'score' -> 'regularTime' ->> 'home')::int
            + COALESCE((m.value -> 'score' -> 'extraTime' ->> 'home')::int, 0),
        (m.value -> 'score' -> 'fullTime' ->> 'home')::int
    )                                     AS home_score,
    COALESCE(
        (m.value -> 'score' -> 'regularTime' ->> 'away')::int
            + COALESCE((m.value -> 'score' -> 'extraTime' ->> 'away')::int, 0),
        (m.value -> 'score' -> 'fullTime' ->> 'away')::int
    )                                     AS away_score
FROM stg_matches s,
     jsonb_array_elements(s.raw -> 'matches') AS m
WHERE s.snap_shot_date = (SELECT MAX(snap_shot_date) FROM stg_matches)
  AND m.value ->> 'status' = 'FINISHED'