import streamlit as st
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
import plotly.express as px

load_dotenv()

st.set_page_config(
    page_title="World Cup 2026 Dashboard",
    layout="wide",
)


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


# Adjust this ratio to resize the charts.
# [3, 1] = chart is 75% width. Higher first number = wider chart.
CHART_RATIO = [2, 1]


st.title("World Cup 2026 Dashboard")

tab_tournament, tab_group, tab_knockout = st.tabs(
    ["Tournament", "Group Stage", "Knockouts"]
)

# ---------------- TOURNAMENT TAB ----------------
with tab_tournament:
    st.header("Golden Boot Race")

    scorers = get_scorers()

    top_players = (
        scorers.groupby("player_name")["goals"].max().sort_values(ascending=False).head(5).index
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

    col, _ = st.columns(CHART_RATIO)
    with col:
        st.plotly_chart(boot_fig, use_container_width=True)


# ---------------- GROUP STAGE TAB ----------------
with tab_group:
    st.header("Position Race by Group")

    standings = get_standings()

    groups = sorted(standings["group_name"].unique())
    selected_group = st.selectbox("Select a group", groups)

    group_df = standings[standings["group_name"] == selected_group]

    bump_fig = px.line(
        group_df,
        x="snapshot_date",
        y="position",
        color="team_name",
        markers=True,
        labels={"snapshot_date": "Date", "position": "Position", "team_name": "Team"},
    )
    bump_fig.update_yaxes(autorange="reversed")
    bump_fig.update_layout(legend_title_text="Team", height=500)

    col, _ = st.columns(CHART_RATIO)
    with col:
        st.plotly_chart(bump_fig, use_container_width=True)


# ---------------- KNOCKOUTS TAB ----------------
with tab_knockout:
    st.header("Knockout Bracket")
    st.info("The bracket will appear here as the knockout rounds progress.")