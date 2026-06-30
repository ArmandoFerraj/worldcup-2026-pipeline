{{ config(materialized='table') }}

SELECT
    player_iter.value ->> 'id'          AS player_id,
    player_iter.value ->> 'name'        AS player_name,
    player_iter.value ->> 'position'    AS position,
    player_iter.value ->> 'dateOfBirth' AS date_of_birth,
    team_iter.value ->> 'id'            AS team_id

FROM stg_teams,
    jsonb_array_elements(stg_teams.raw -> 'teams') AS team_iter,
    jsonb_array_elements(team_iter.value -> 'squad') AS player_iter

WHERE stg_teams.snap_shot_date = '2026-06-18_14-14'