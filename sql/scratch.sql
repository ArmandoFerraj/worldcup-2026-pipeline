SELECT s.snapshot_date, s.points, s.played, s.position
FROM fct_standings s
JOIN dim_teams t ON s.team_id = t.team_id
WHERE t.team_name LIKE '%Bosnia%'
ORDER BY s.snapshot_date;