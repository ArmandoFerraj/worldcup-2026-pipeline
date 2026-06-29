{{ config(materialized='table') }}

SELECT
    (m.value ->> 'id')::int                            AS match_id,
    m.value ->> 'stage'                                AS stage,
    (m.value -> 'homeTeam' ->> 'id')::int              AS home_id,
    (m.value -> 'awayTeam' ->> 'id')::int              AS away_id,
    (m.value -> 'score' -> 'fullTime' ->> 'home')::int AS home_score,
    (m.value -> 'score' -> 'fullTime' ->> 'away')::int AS away_score,
    CASE
        WHEN m.value -> 'score' ->> 'winner' = 'HOME_TEAM' THEN (m.value -> 'homeTeam' ->> 'id')::int
        WHEN m.value -> 'score' ->> 'winner' = 'AWAY_TEAM' THEN (m.value -> 'awayTeam' ->> 'id')::int
        ELSE NULL
    END AS winner_id
FROM stg_matches s,
     jsonb_array_elements(s.raw -> 'matches') AS m
WHERE s.snap_shot_date = (SELECT MAX(snap_shot_date) FROM stg_matches)
  AND m.value ->> 'stage' != 'GROUP_STAGE'