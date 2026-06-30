{{ config(materialized='table') }}

SELECT
    (m.value ->> 'id')::int                                  AS match_id,
    m.value ->> 'stage'                                      AS stage,
    m.value -> 'score' ->> 'duration'                        AS duration,
    (m.value -> 'homeTeam' ->> 'id')::int                    AS home_id,
    (m.value -> 'awayTeam' ->> 'id')::int                    AS away_id,
    (m.value -> 'score' -> 'regularTime' ->> 'home')::int
        + COALESCE((m.value -> 'score' -> 'extraTime' ->> 'home')::int, 0) AS home_score,
    (m.value -> 'score' -> 'regularTime' ->> 'away')::int
        + COALESCE((m.value -> 'score' -> 'extraTime' ->> 'away')::int, 0) AS away_score,
    (m.value -> 'score' -> 'penalties' ->> 'home')::int      AS home_penalties,
    (m.value -> 'score' -> 'penalties' ->> 'away')::int      AS away_penalties,
    CASE
        WHEN m.value -> 'score' ->> 'winner' = 'HOME_TEAM' THEN (m.value -> 'homeTeam' ->> 'id')::int
        WHEN m.value -> 'score' ->> 'winner' = 'AWAY_TEAM' THEN (m.value -> 'awayTeam' ->> 'id')::int
        ELSE NULL
    END                                                      AS winner_id
FROM stg_matches s,
     jsonb_array_elements(s.raw -> 'matches') AS m
WHERE s.snap_shot_date = (SELECT MAX(snap_shot_date) FROM stg_matches)
  AND m.value ->> 'stage' != 'GROUP_STAGE'