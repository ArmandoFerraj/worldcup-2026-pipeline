{{ config(materialized='table') }}

WITH unpacked AS (
    SELECT
        snap_shot_date AS snapshot_date,
        split_part(snap_shot_date, '_', 1) AS snapshot_day,
        team_row.value -> 'team' ->> 'id'              AS team_id,
        (team_row.value ->> 'position')::int           AS position,
        (team_row.value ->> 'points')::int             AS points,
        (team_row.value ->> 'goalsFor')::int           AS goals_for,
        (team_row.value ->> 'goalsAgainst')::int       AS goals_against,
        (team_row.value ->> 'goalDifference')::int     AS goal_difference,
        (team_row.value ->> 'playedGames')::int        AS played
    FROM stg_standings,
        jsonb_array_elements(raw -> 'standings') AS group_iter,
        jsonb_array_elements(group_iter.value -> 'table') AS team_row
),

-- Keep only the latest snapshot for each day (drops same-day duplicates
-- from manual runs, so each day shows one point on the charts).
latest_per_day AS (
    SELECT snapshot_day, MAX(snapshot_date) AS snapshot_date
    FROM unpacked
    GROUP BY snapshot_day
)

SELECT unpacked.snapshot_date,
       unpacked.team_id,
       unpacked.position,
       unpacked.points,
       unpacked.goals_for,
       unpacked.goals_against,
       unpacked.goal_difference,
       unpacked.played
FROM unpacked
JOIN latest_per_day
  ON unpacked.snapshot_date = latest_per_day.snapshot_date