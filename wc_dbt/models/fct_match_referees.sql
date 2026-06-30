{{ config(materialized='table') }}

SELECT
    (m.value ->> 'id')::int                 AS match_id,
    (ref.value ->> 'id')::int               AS referee_id,
    ref.value ->> 'name'                     AS referee_name
FROM stg_matches s,
     jsonb_array_elements(s.raw -> 'matches') AS m,
     jsonb_array_elements(m.value -> 'referees') AS ref
WHERE s.snap_shot_date = (SELECT MAX(snap_shot_date) FROM stg_matches)
  AND m.value ->> 'status' = 'FINISHED'