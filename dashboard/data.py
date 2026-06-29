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

    
