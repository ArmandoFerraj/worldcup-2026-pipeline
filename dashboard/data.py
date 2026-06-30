import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

def get_scorers():
    conn = get_connection()
    df = pd.read_sql(
        "SELECT snapshot_date, player_name, goals FROM fct_scorers ORDER BY snapshot_date",
        conn,
    )
    conn.close()
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], format="%Y-%m-%d_%H-%M")
    return df

def get_assisters():
    conn = get_connection()
    df = pd.read_sql(
        "SELECT snapshot_date, player_name, assists FROM fct_scorers ORDER BY snapshot_date",
        conn,
    )
    conn.close()
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], format="%Y-%m-%d_%H-%M")
    return df

def get_standings():
    conn = get_connection()
    df = pd.read_sql(
        """
        SELECT
            fct_standings.snapshot_date,
            fct_standings.position,
            fct_standings.points,
            fct_standings.goals_for,
            fct_standings.goal_difference,
            dim_teams.team_name,
            dim_teams.group_name
        FROM fct_standings
        JOIN dim_teams ON fct_standings.team_id = dim_teams.team_id
        ORDER BY fct_standings.snapshot_date
        """,
        conn,
    )
    conn.close()
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"], format="%Y-%m-%d_%H-%M")
    return df


def get_penalty_merchant():
    conn = get_connection()
    df = pd.read_sql(
        """
        WITH latest AS (
            SELECT player_name, penalties
            FROM fct_scorers
            WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM fct_scorers)
        )
        SELECT player_name, penalties
        FROM latest
        WHERE penalties = (SELECT MAX(penalties) FROM latest)
        ORDER BY player_name
        """,
        conn,
    )
    conn.close()
    return df


def get_worst_team():
    conn = get_connection()
    df = pd.read_sql(
        """
        SELECT dim_teams.team_name, fct_standings.points, fct_standings.goal_difference
        FROM fct_standings
        JOIN dim_teams ON fct_standings.team_id = dim_teams.team_id
        WHERE fct_standings.snapshot_date = (SELECT MAX(snapshot_date) FROM fct_standings)
        ORDER BY fct_standings.points ASC, fct_standings.goal_difference ASC
        LIMIT 1
        """,
        conn,
    )
    conn.close()
    return df


def get_top_scoring_team():
    conn = get_connection()
    df = pd.read_sql(
        """
        WITH latest AS (
            SELECT fct_standings.team_id, fct_standings.goals_for, dim_teams.team_name
            FROM fct_standings
            JOIN dim_teams ON fct_standings.team_id = dim_teams.team_id
            WHERE fct_standings.snapshot_date = (SELECT MAX(snapshot_date) FROM fct_standings)
        )
        SELECT team_name, goals_for
        FROM latest
        WHERE goals_for = (SELECT MAX(goals_for) FROM latest)
        ORDER BY team_name
        """,
        conn,
    )
    conn.close()
    return df


def get_oldest_scorer():
    conn = get_connection()
    df = pd.read_sql(
        """
        WITH scorers_latest AS (
            SELECT DISTINCT player_id
            FROM fct_scorers
            WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM fct_scorers)
              AND goals > 0
        )
        SELECT
            dim_players.player_name,
            dim_players.date_of_birth,
            date_part('year', age(dim_players.date_of_birth::date))::int AS age
        FROM scorers_latest
        JOIN dim_players ON scorers_latest.player_id = dim_players.player_id
        ORDER BY dim_players.date_of_birth ASC
        LIMIT 1
        """,
        conn,
    )
    conn.close()
    return df


def get_squad_age_extremes():
    conn = get_connection()
    df = pd.read_sql(
        """
        WITH team_ages AS (
            SELECT
                dim_teams.team_name,
                AVG(date_part('year', age(dim_players.date_of_birth::date))) AS avg_age
            FROM dim_players
            JOIN dim_teams ON dim_players.team_id = dim_teams.team_id
            GROUP BY dim_teams.team_name
        )
        (SELECT team_name, avg_age, 'oldest' AS kind FROM team_ages ORDER BY avg_age DESC LIMIT 1)
        UNION ALL
        (SELECT team_name, avg_age, 'youngest' AS kind FROM team_ages ORDER BY avg_age ASC LIMIT 1)
        """,
        conn,
    )
    conn.close()
    return df


def get_highest_scoring_match():
    conn = get_connection()
    df = pd.read_sql(
        """
        SELECT
            home_team.team_name AS home_name,
            away_team.team_name AS away_name,
            fct_matches.home_score,
            fct_matches.away_score,
            fct_matches.home_score + fct_matches.away_score AS total_goals
        FROM fct_matches
        JOIN dim_teams AS home_team ON fct_matches.home_id::text = home_team.team_id
        JOIN dim_teams AS away_team ON fct_matches.away_id::text = away_team.team_id
        ORDER BY total_goals DESC
        LIMIT 1
        """,
        conn,
    )
    conn.close()
    return df


def get_biggest_margin():
    conn = get_connection()
    df = pd.read_sql(
        """
        SELECT
            home_team.team_name AS home_name,
            away_team.team_name AS away_name,
            fct_matches.home_score,
            fct_matches.away_score,
            ABS(fct_matches.home_score - fct_matches.away_score) AS margin
        FROM fct_matches
        JOIN dim_teams AS home_team ON fct_matches.home_id::text = home_team.team_id
        JOIN dim_teams AS away_team ON fct_matches.away_id::text = away_team.team_id
        ORDER BY margin DESC
        LIMIT 1
        """,
        conn,
    )
    conn.close()
    return df


def get_most_clean_sheets():
    conn = get_connection()
    df = pd.read_sql(
        """
        WITH conceded AS (
            SELECT home_id AS team_id, away_score AS goals_conceded FROM fct_matches
            UNION ALL
            SELECT away_id AS team_id, home_score AS goals_conceded FROM fct_matches
        ),
        sheets AS (
            SELECT team_id, COUNT(*) AS clean_sheets
            FROM conceded
            WHERE goals_conceded = 0
            GROUP BY team_id
        )
        SELECT dim_teams.team_name, sheets.clean_sheets
        FROM sheets
        JOIN dim_teams ON sheets.team_id::text = dim_teams.team_id
        WHERE sheets.clean_sheets = (SELECT MAX(clean_sheets) FROM sheets)
        ORDER BY dim_teams.team_name
        """,
        conn,
    )
    conn.close()
    return df


def get_knockout():
    conn = get_connection()
    df = pd.read_sql(
        """
        SELECT
            fct_knockout.match_id,
            fct_knockout.stage,
            fct_knockout.duration,
            fct_knockout.home_id,
            fct_knockout.away_id,
            fct_knockout.winner_id,
            home_team.team_tla AS home_tla,
            away_team.team_tla AS away_tla,
            fct_knockout.home_score,
            fct_knockout.away_score,
            fct_knockout.home_penalties,
            fct_knockout.away_penalties,
            CASE
                WHEN fct_knockout.winner_id = fct_knockout.home_id THEN 'home'
                WHEN fct_knockout.winner_id = fct_knockout.away_id THEN 'away'
                ELSE NULL
            END AS winner
        FROM fct_knockout
        LEFT JOIN dim_teams AS home_team ON fct_knockout.home_id::text = home_team.team_id
        LEFT JOIN dim_teams AS away_team ON fct_knockout.away_id::text = away_team.team_id
        ORDER BY fct_knockout.match_id
        """,
        conn,
    )
    conn.close()
    return df