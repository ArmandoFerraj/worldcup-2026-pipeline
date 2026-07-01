{{ config(materialized='table') }}

WITH unpacked AS (
    SELECT
        snap_shot_date AS snapshot_date,
        split_part(snap_shot_date, '_', 1) AS snapshot_day,
        scorer_iter.value -> 'player' ->> 'id'   AS player_id,
        scorer_iter.value -> 'player' ->> 'name' AS player_name,
        scorer_iter.value -> 'team' ->> 'id'     AS team_id,
        (scorer_iter.value ->> 'goals')::int                  AS goals,
        COALESCE((scorer_iter.value ->> 'assists')::int, 0)   AS assists,
        COALESCE((scorer_iter.value ->> 'penalties')::int, 0) AS penalties
    FROM stg_scorers,
        jsonb_array_elements(raw -> 'scorers') AS scorer_iter
),

-- Keep only the latest snapshot for each day (drops same-day duplicates
-- from manual runs, so each day shows one point on the charts).
latest_per_day AS (
    SELECT snapshot_day, MAX(snapshot_date) AS snapshot_date
    FROM unpacked
    GROUP BY snapshot_day
)

SELECT unpacked.snapshot_date,
       unpacked.player_id,
       unpacked.player_name,
       unpacked.team_id,
       unpacked.goals,
       unpacked.assists,
       unpacked.penalties
FROM unpacked
JOIN latest_per_day
  ON unpacked.snapshot_date = latest_per_day.snapshot_date