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
# Each view is self-contained: given a single group's dataframe
# (group_df), it draws its own metric cards + chart. To add a new view,
# write a new render_group_* function and register it in GROUP_VIEWS below.

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


def render_goals_for(group_df):
    _group_cards(group_df, "goals_for", "goals")

    st.divider()
    st.header("Goals For")

    fig = px.line(
        group_df,
        x="snapshot_date",
        y="goals_for",
        color="team_name",
        markers=True,
        labels={"snapshot_date": "Date", "goals_for": "Goals", "team_name": "Team"},
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

    fig = px.line(
        group_df,
        x="snapshot_date",
        y="goal_difference",
        color="team_name",
        markers=True,
        labels={"snapshot_date": "Date", "goal_difference": "Goal Difference", "team_name": "Team"},
    )
    fig.update_xaxes(tickformat="%m-%d")
    fig.update_layout(legend_title_text="Team", height=500)

    col, _ = st.columns(CHART_RATIO)
    with col:
        st.plotly_chart(fig, use_container_width=True)


# Register group-stage views here.
GROUP_VIEWS = {
    "Position": render_position_race,
    "Goals For": render_goals_for,
    "Goal Difference": render_goal_difference,
}


# ============ KNOCKOUT BRACKET ============
# Static skeleton: left-to-right rounds, hardcoded placeholder matches,
# greying for eliminated teams, no connecting lines yet.
#
# Layout approach:
#  - Round titles live in their own aligned header row (parallel).
#  - Every round column shares the SAME fixed height + justify-content:
#    space-around, so each round's matches auto-center against their
#    feeder pair -> symmetric bracket. (16 -> 8 -> 4 -> 2 -> 1)
#  - Third-place match is dropped (it breaks the clean funnel symmetry).
#
# NOTE: HTML is built with NO leading whitespace per line, otherwise
# Streamlit's markdown parser treats indented lines as code blocks.

# Height tuned to fit 16 R32 matches comfortably; other rounds stretch
# to match, which produces the feeder-midpoint alignment.
BRACKET_HEIGHT = 1400


def _match_box(home, away, home_score, away_score, winner):
    """HTML for one match box. winner: 'home', 'away', or None (unplayed)."""
    home_cls = "team eliminated" if winner == "away" else "team"
    away_cls = "team eliminated" if winner == "home" else "team"
    hs = "" if home_score is None else home_score
    as_ = "" if away_score is None else away_score
    home = home or "TBD"
    away = away or "TBD"
    return (
        '<div class="match">'
        f'<div class="{home_cls}"><span class="tla">{home}</span><span class="score">{hs}</span></div>'
        f'<div class="{away_cls}"><span class="tla">{away}</span><span class="score">{as_}</span></div>'
        '</div>'
    )


def render_bracket():
    # tuple = (home, away, home_score, away_score, winner)
    # Clean funnel: 16 R32 -> 8 R16 -> 4 QF -> 2 SF -> 1 Final.
    rounds = {
        "Round of 32": [
            ("RSA", "CAN", 0, 1, "away"),
            ("BRA", "KOR", 2, 0, "home"),
            ("ARG", "AUS", 3, 1, "home"),
            ("FRA", "POL", 1, 0, "home"),
            ("ENG", "SEN", 2, 1, "home"),
            ("ESP", "MAR", 0, 1, "away"),
            ("GER", "JPN", 1, 2, "away"),
            ("POR", "SUI", 4, 1, "home"),
            ("NED", "USA", 3, 1, "home"),
            ("CRO", "MEX", 1, 0, "home"),
            ("BEL", "URU", 2, 2, "away"),
            ("ITA", "NGA", 1, 0, "home"),
            ("COL", "EGY", 2, 1, "home"),
            ("DEN", "GHA", 0, 2, "away"),
            ("SRB", "ECU", 1, 3, "away"),
            ("WAL", "QAT", 2, 0, "home"),
        ],
        "Round of 16": [
            ("CAN", "BRA", None, None, None),
            ("ARG", "FRA", None, None, None),
            ("ENG", "MAR", None, None, None),
            ("JPN", "POR", None, None, None),
            ("NED", "CRO", None, None, None),
            ("URU", "ITA", None, None, None),
            ("COL", "GHA", None, None, None),
            ("ECU", "WAL", None, None, None),
        ],
        "Quarter-finals": [
            (None, None, None, None, None),
            (None, None, None, None, None),
            (None, None, None, None, None),
            (None, None, None, None, None),
        ],
        "Semi-finals": [
            (None, None, None, None, None),
            (None, None, None, None, None),
        ],
        "Final": [
            (None, None, None, None, None),
        ],
    }

    # Header row: all round titles, aligned and parallel.
    headers_html = ""
    for round_name in rounds:
        headers_html += f'<div class="round-title">{round_name}</div>'

    # Bracket body: each round is an equal-height column of matches.
    columns_html = ""
    for matches in rounds.values():
        boxes = "".join(_match_box(*m) for m in matches)
        columns_html += f'<div class="round">{boxes}</div>'

    css = (
        "<style>"
        ".bracket-wrap{overflow-x:auto;padding:4px 4px 24px 4px;}"
        ".bracket-headers{display:flex;gap:72px;}"
        ".bracket-headers .round-title{min-width:170px;text-align:center;font-weight:600;font-size:0.8rem;color:#8b949e;text-transform:uppercase;letter-spacing:0.04em;padding-bottom:10px;}"
        f".bracket-body{{display:flex;gap:72px;height:{BRACKET_HEIGHT}px;}}"
        ".round{display:flex;flex-direction:column;justify-content:space-around;min-width:170px;}"
        ".match{background:#161b22;border:1px solid #30363d;border-radius:6px;overflow:hidden;}"
        ".team{display:flex;justify-content:space-between;align-items:center;padding:8px 10px;font-size:0.9rem;color:#f0f6fc;}"
        ".match .team:first-child{border-bottom:1px solid #30363d;}"
        ".team.eliminated{color:#6e7681;opacity:0.6;}"
        ".tla{font-weight:600;letter-spacing:0.03em;}"
        ".score{color:#8b949e;}"
        "</style>"
    )

    html = (
        f'{css}'
        '<div class="bracket-wrap">'
        f'<div class="bracket-headers">{headers_html}</div>'
        f'<div class="bracket-body">{columns_html}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


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

    # Render the selected view (it draws its own cards + chart)
    GROUP_VIEWS[selected_view](group_df)


# ---------------- KNOCKOUTS TAB ----------------
with tab_knockout:
    st.header("Knockout Bracket")
    render_bracket()