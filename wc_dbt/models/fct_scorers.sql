{{ config(materialized='table') }}

SELECT
    snap_shot_date AS snapshot_date,
    scorer_iter.value -> 'player' ->> 'id'   AS player_id,
    scorer_iter.value -> 'player' ->> 'name' AS player_name,
    scorer_iter.value -> 'team' ->> 'id'     AS team_id,
    (scorer_iter.value ->> 'goals')::int                  AS goals,
    COALESCE((scorer_iter.value ->> 'assists')::int, 0)   AS assists,
    COALESCE((scorer_iter.value ->> 'penalties')::int, 0) AS penalties
FROM stg_scorers,
    jsonb_array_elements(raw -> 'scorers') AS scorer_iter