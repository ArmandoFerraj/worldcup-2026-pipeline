{{ config(materialized='table') }}

SELECT
    snap_shot_date AS snapshot_date,
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