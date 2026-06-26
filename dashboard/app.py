import streamlit as st
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
import plotly.express as px

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
    return df

def get_standings():
    conn = get_connection()
    df = pd.read_sql(
        """
        SELECT
            fct_standings.snapshot_date,
            fct_standings.position,
            dim_teams.team_name,
            dim_teams.group_name
        FROM fct_standings
        JOIN dim_teams ON fct_standings.team_id = dim_teams.team_id
        ORDER BY fct_standings.snapshot_date
        """,
        conn,
    )
    conn.close()
    return df


st.title("World Cup 2026 Dashboard")

# ---------------- Golden Boot Race ----------------
st.header("Golden Boot Race")

scorers = get_scorers()

# find the top 6 scorers by their current max goals
top_players = (
    scorers.groupby("player_name")["goals"].max().sort_values(ascending=False).head(6).index
)
scorers_top = scorers[scorers["player_name"].isin(top_players)]

boot_fig = px.line(
    scorers_top,
    x="snapshot_date",
    y="goals",
    color="player_name",
    markers=True,
    labels={"snapshot_date": "Date", "goals": "Goals", "player_name": "Player"},
)
boot_fig.update_layout(legend_title_text="Player", height=500)
st.plotly_chart(boot_fig, use_container_width=True)


# ---------------- Position Race by Group (Bump Chart) ----------------
st.header("Position Race by Group")

standings = get_standings()

# group selector
groups = sorted(standings["group_name"].unique())
selected_group = st.selectbox("Select a group", groups)

# filter to the chosen group
group_df = standings[standings["group_name"] == selected_group]

bump_fig = px.line(
    group_df,
    x="snapshot_date",
    y="position",
    color="team_name",
    markers=True,
    labels={"snapshot_date": "Date", "position": "Position", "team_name": "Team"},
)
bump_fig.update_yaxes(autorange="reversed")  # 1st place on top
bump_fig.update_layout(legend_title_text="Team", height=500)
st.plotly_chart(bump_fig, use_container_width=True)