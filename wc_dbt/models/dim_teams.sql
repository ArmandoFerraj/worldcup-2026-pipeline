{{ config(materialized='table') }}

SELECT
    team_iter.value ->> 'id'    AS team_id,
    team_iter.value ->> 'name'  AS team_name,
    team_iter.value ->> 'tla'   AS team_tla,
    team_iter.value ->> 'crest' AS team_crest,
    team_iter.value -> 'coach' ->> 'name'        AS coach_name,
    team_iter.value -> 'coach' ->> 'nationality' AS coach_nationality,
    group_iter.value ->> 'group' AS group_name

FROM stg_teams,
    jsonb_array_elements(stg_teams.raw -> 'teams') AS team_iter,
    stg_standings,
    jsonb_array_elements(stg_standings.raw -> 'standings') AS group_iter,
    jsonb_array_elements(group_iter.value -> 'table') AS standings_team_iter

WHERE team_iter.value ->> 'id' = standings_team_iter.value -> 'team' ->> 'id'
  AND stg_teams.snap_shot_date = '2026-06-18_14-14'
  AND stg_standings.snap_shot_date = '2026-06-18_14-14'