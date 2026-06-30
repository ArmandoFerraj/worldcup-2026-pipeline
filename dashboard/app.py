import streamlit as st
import plotly.express as px
from data import get_scorers, get_standings, get_assisters, get_penalty_merchant, get_worst_team, get_top_scoring_team
from bracket import render_bracket

st.set_page_config(
    page_title="World Cup 2026 Dashboard",
    layout="wide",
)
CHART_RATIO = [2, 1]

# Chart line colors, chosen to fit the dark theme and stay distinguishable.
CHART_COLORS = ["#58a6ff", "#a855f7", "#3fb950", "#f778ba", "#ff9e64"]

# ============ TOURNAMENT RACE RENDERERS ============

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
        color_discrete_sequence=CHART_COLORS,
        category_orders={"player_name": list(top_players)},
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
        color_discrete_sequence=CHART_COLORS,
        category_orders={"player_name": list(top_players)},
    )
    fig.update_xaxes(tickformat="%m-%d")
    fig.update_layout(legend_title_text="Player", height=500)

    col, _ = st.columns(CHART_RATIO)
    with col:
        st.plotly_chart(fig, use_container_width=True)


RACES = {
    "Golden Boot": render_golden_boot,
    "Assists": render_assists,
}


# ============ GROUP STAGE VIEW RENDERERS ============

def _group_cards(group_df, stat_col, stat_suffix):
    """Draw one card per team showing the current value of stat_col."""
    latest_date = group_df["snapshot_date"].max()
    latest_group = group_df[group_df["snapshot_date"] == latest_date].sort_values("position")

    cards = st.columns(len(latest_group))
    for card, (_, row) in zip(cards, latest_group.iterrows()):
        card.metric(
            row["team_name"],
            f"{int(row[stat_col])} {stat_suffix}",
            f"{int(row['position'])} place",
            delta_color="off",
        )


def render_position_race(group_df):
    _group_cards(group_df, "points", "pts")

    st.divider()
    st.header("Position Race")

    # Legend order: current standings (latest snapshot), best position first.
    latest = group_df[group_df["snapshot_date"] == group_df["snapshot_date"].max()]
    team_order = latest.sort_values("position")["team_name"].tolist()

    fig = px.line(
        group_df,
        x="snapshot_date",
        y="position",
        color="team_name",
        markers=True,
        labels={"snapshot_date": "Date", "position": "Position", "team_name": "Team"},
        color_discrete_sequence=CHART_COLORS,
        category_orders={"team_name": team_order},
    )
    fig.update_xaxes(tickformat="%m-%d")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(legend_title_text="Team", height=500)

    col, _ = st.columns(CHART_RATIO)
    with col:
        st.plotly_chart(fig, use_container_width=True)


def render_goals_for(group_df):
    _group_cards(group_df, "goals_for", "goals")

    st.divider()
    st.header("Goals For")

    # Legend order: current standings (latest snapshot), most goals first.
    latest = group_df[group_df["snapshot_date"] == group_df["snapshot_date"].max()]
    team_order = latest.sort_values("goals_for", ascending=False)["team_name"].tolist()

    fig = px.line(
        group_df,
        x="snapshot_date",
        y="goals_for",
        color="team_name",
        markers=True,
        labels={"snapshot_date": "Date", "goals_for": "Goals", "team_name": "Team"},
        color_discrete_sequence=CHART_COLORS,
        category_orders={"team_name": team_order},
    )
    fig.update_xaxes(tickformat="%m-%d")
    fig.update_layout(legend_title_text="Team", height=500)

    col, _ = st.columns(CHART_RATIO)
    with col:
        st.plotly_chart(fig, use_container_width=True)


def render_goal_difference(group_df):
    _group_cards(group_df, "goal_difference", "GD")

    st.divider()
    st.header("Goal Difference")

    # Legend order: current standings (latest snapshot), best GD first.
    latest = group_df[group_df["snapshot_date"] == group_df["snapshot_date"].max()]
    team_order = latest.sort_values("goal_difference", ascending=False)["team_name"].tolist()

    fig = px.line(
        group_df,
        x="snapshot_date",
        y="goal_difference",
        color="team_name",
        markers=True,
        labels={"snapshot_date": "Date", "goal_difference": "Goal Difference", "team_name": "Team"},
        color_discrete_sequence=CHART_COLORS,
        category_orders={"team_name": team_order},
    )
    fig.update_xaxes(tickformat="%m-%d")
    fig.update_layout(legend_title_text="Team", height=500)

    col, _ = st.columns(CHART_RATIO)
    with col:
        st.plotly_chart(fig, use_container_width=True)


GROUP_VIEWS = {
    "Position": render_position_race,
    "Goals For": render_goals_for,
    "Goal Difference": render_goal_difference,
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

    selected_race = st.radio(
        "Select a race",
        options=list(RACES.keys()),
        horizontal=True,
        label_visibility="collapsed",
    )

    RACES[selected_race]()

    st.divider()

    st.subheader("Fun Facts")
    st.write("")

    fact1, fact2, fact3 = st.columns(3)

    with fact1:
        pen = get_penalty_merchant()
        max_pens = int(pen["penalties"].iloc[0])
        if max_pens == 1:
            st.metric("Penalty Leaders", f"{len(pen)} players", "1 penalty each", delta_color="off")
        else:
            names = ", ".join(pen["player_name"].tolist())
            st.metric("Penalty Merchant", names, f"{max_pens} penalties", delta_color="off")

    with fact2:
        worst = get_worst_team()
        row = worst.iloc[0]
        st.metric(
            "Worst Team",
            row["team_name"],
            f"{int(row['points'])} pts, {int(row['goal_difference'])} GD",
            delta_color="off",
        )

    with fact3:
        top_scoring = get_top_scoring_team()
        names = ", ".join(top_scoring["team_name"].tolist())
        goals = int(top_scoring["goals_for"].iloc[0])
        st.metric("Most Goals", names, f"{goals} goals", delta_color="off")

# ---------------- GROUP STAGE TAB ----------------
with tab_group:
    standings = get_standings()
    groups = sorted(standings["group_name"].unique())

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

    GROUP_VIEWS[selected_view](group_df)


# ---------------- KNOCKOUTS TAB ----------------
with tab_knockout:
    st.header("Knockout Bracket")
    render_bracket()