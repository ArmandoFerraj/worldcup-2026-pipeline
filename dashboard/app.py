import streamlit as st
import plotly.express as px
from data import get_scorers, get_standings, get_assisters

st.set_page_config(
    page_title="World Cup 2026 Dashboard",
    layout="wide",
)
CHART_RATIO = [2, 1]

# ============ TOURNAMENT RACE RENDERERS ============
# Each race is a self-contained function: it fetches its own data and
# draws its own metric cards + chart. To add a new race (total goals,
# etc.), write a new render_* function and register it in RACES below.

def render_golden_boot():
    scorers = get_scorers()
    latest_date = scorers["snapshot_date"].max()
    latest = scorers[scorers["snapshot_date"] == latest_date]

    top_row = latest.sort_values("goals", ascending=False).iloc[0]

    m1, m2, m3 = st.columns(3)
    m1.metric("Top Scorer", top_row["player_name"], f"{int(top_row['goals'])} goals")
    m2.metric("Total Goals", int(latest["goals"].sum()))
    m3.metric("Players Who've Scored", latest["player_name"].nunique())

    st.divider()
    st.header("Golden Boot Race")

    top_players = (
        scorers.groupby("player_name")["goals"].max().sort_values(ascending=False).head(5).index
    )
    scorers_top = scorers[scorers["player_name"].isin(top_players)]

    fig = px.line(
        scorers_top,
        x="snapshot_date",
        y="goals",
        color="player_name",
        markers=True,
        labels={"snapshot_date": "Date", "goals": "Goals", "player_name": "Player"},
    )
    fig.update_xaxes(tickformat="%m-%d")
    fig.update_layout(legend_title_text="Player", height=500)

    col, _ = st.columns(CHART_RATIO)
    with col:
        st.plotly_chart(fig, use_container_width=True)


def render_assists():
    assisters = get_assisters()
    latest_date = assisters["snapshot_date"].max()
    latest = assisters[assisters["snapshot_date"] == latest_date]

    top_row = latest.sort_values("assists", ascending=False).iloc[0]

    m1, m2, m3 = st.columns(3)
    m1.metric("Top Assister", top_row["player_name"], f"{int(top_row['assists'])} assists")
    m2.metric("Total Assists", int(latest["assists"].sum()))
    m3.metric("Players With Assists", int((latest["assists"] > 0).sum()))

    st.divider()
    st.header("Assist Leaders")

    top_players = (
        assisters.groupby("player_name")["assists"].max().sort_values(ascending=False).head(5).index
    )
    assisters_top = assisters[assisters["player_name"].isin(top_players)]

    fig = px.line(
        assisters_top,
        x="snapshot_date",
        y="assists",
        color="player_name",
        markers=True,
        labels={"snapshot_date": "Date", "assists": "Assists", "player_name": "Player"},
    )
    fig.update_xaxes(tickformat="%m-%d")
    fig.update_layout(legend_title_text="Player", height=500)

    col, _ = st.columns(CHART_RATIO)
    with col:
        st.plotly_chart(fig, use_container_width=True)


# Register tournament races here. Key = label shown in the selector,
# value = the render function. Add new races by adding a line.
RACES = {
    "Golden Boot": render_golden_boot,
    "Assists": render_assists,
}


# ============ GROUP STAGE VIEW RENDERERS ============
# Each view draws one chart for a single group's dataframe (group_df).
# To add a new view (points, goal difference, etc.), write a new
# render_group_* function and register it in GROUP_VIEWS below.

def render_position_race(group_df):
    st.header("Position Race")
    fig = px.line(
        group_df,
        x="snapshot_date",
        y="position",
        color="team_name",
        markers=True,
        labels={"snapshot_date": "Date", "position": "Position", "team_name": "Team"},
    )
    fig.update_xaxes(tickformat="%m-%d")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(legend_title_text="Team", height=500)

    col, _ = st.columns(CHART_RATIO)
    with col:
        st.plotly_chart(fig, use_container_width=True)

# Register group-stage views here.
GROUP_VIEWS = {
    "Position": render_position_race,
}

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚽ World Cup 2026")

    st.markdown(
        "An automated ELT pipeline tracking the 2026 World Cup. "
        "It captures daily snapshots from a "
        "[live football API](https://www.football-data.org/) and "
        "visualizes how the tournament unfolds over time."
    )

    st.divider()

    st.subheader("Tech Stack")
    st.markdown(
        """
        - **Python** — extraction & loading
        - **AWS S3** — data lake
        - **AWS RDS (PostgreSQL)** — data warehouse
        - **dbt** — transformations
        - **AWS EC2 + cron** — automation
        - **Streamlit + Plotly** — dashboard
        """
    )

    st.divider()

    st.caption("Data updates daily at 5 AM ET")
    st.markdown("[View the code on GitHub](https://github.com/ArmandoFerraj)")


st.title("World Cup 2026 Dashboard")

tab_tournament, tab_group, tab_knockout = st.tabs(
    ["Tournament", "Group Stage", "Knockouts"]
)

# ---------------- TOURNAMENT TAB ----------------
with tab_tournament:
    # Selector: pick which race to view
    selected_race = st.radio(
        "Select a race",
        options=list(RACES.keys()),
        horizontal=True,
        label_visibility="collapsed",
    )

    # Render the selected race (it fetches its own data + draws cards + chart)
    RACES[selected_race]()

    st.divider()

    # Fun-facts / superlatives section (placeholder for now)
    st.subheader("Fun Facts")
    st.info("Tournament superlatives coming soon.")

# ---------------- GROUP STAGE TAB ----------------
with tab_group:
    standings = get_standings()
    groups = sorted(standings["group_name"].unique())

    # Two selectors side by side: which group, and which view
    sel_col1, sel_col2 = st.columns(2)
    with sel_col1:
        selected_group = st.selectbox("Group", groups)
    with sel_col2:
        selected_view = st.radio(
            "View",
            options=list(GROUP_VIEWS.keys()),
            horizontal=True,
        )

    group_df = standings[standings["group_name"] == selected_group]

    # Cards: current points for each team in the selected group
    latest_date = group_df["snapshot_date"].max()
    latest_group = group_df[group_df["snapshot_date"] == latest_date].sort_values("position")

    cards = st.columns(len(latest_group))
    for card, (_, row) in zip(cards, latest_group.iterrows()):
        card.metric(
            row["team_name"],
            f"{int(row['points'])} pts",
            f"{int(row['position'])} place",
            delta_color="off",
        )

    st.divider()

    # Render the selected view (its chart)
    GROUP_VIEWS[selected_view](group_df)


# ---------------- KNOCKOUTS TAB ----------------
with tab_knockout:
    st.header("Knockout Bracket")
    st.info("The bracket will appear here as the knockout rounds progress.")