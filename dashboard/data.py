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