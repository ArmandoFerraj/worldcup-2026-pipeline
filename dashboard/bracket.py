import streamlit as st
import pandas as pd
from data import get_knockout

BRACKET_HEIGHT = 1400

STAGE_DISPLAY = [
    ("LAST_32", "Round of 32"),
    ("LAST_16", "Round of 16"),
    ("QUARTER_FINALS", "Quarter-finals"),
    ("SEMI_FINALS", "Semi-finals"),
    ("FINAL", "Final"),
]


def _winner_id(row):
    """The team id that advanced from a match row, or None if unresolved."""
    if row is None:
        return None
    if pd.notna(row["winner_id"]):
        return row["winner_id"]
    return None


def _find_match(pool, advancing_ids, used):
    """Find the (unused) match in pool whose home_id or away_id is one of
    the advancing team ids. Returns the row, or None if none match."""
    if not advancing_ids:
        return None
    for _, m in pool.iterrows():
        if m["match_id"] in used:
            continue
        if (pd.notna(m["home_id"]) and m["home_id"] in advancing_ids) or \
           (pd.notna(m["away_id"]) and m["away_id"] in advancing_ids):
            return m
    return None


def _order_rounds(df):
    """Return [(display_name, [match_rows_or_None in visual order]), ...].

    R32 is sorted by match_id (the fixed anchor). Each later round is
    ordered by tracing each slot's two feeders' winners into that round.
    """
    by_stage = {db: df[df["stage"] == db] for db, _ in STAGE_DISPLAY}

    # Anchor: R32 rows sorted by match_id, as a list of Series.
    r32 = [row for _, row in by_stage["LAST_32"].sort_values("match_id").iterrows()]

    ordered = [("Round of 32", r32)]
    prev = r32

    for db_stage, display in STAGE_DISPLAY[1:]:
        pool = by_stage[db_stage]
        n_slots = len(prev) // 2
        curr = []
        used = set()
        for n in range(n_slots):
            feeder_a = prev[2 * n]
            feeder_b = prev[2 * n + 1]
            advancing = {
                t for t in (_winner_id(feeder_a), _winner_id(feeder_b))
                if t is not None
            }
            match = _find_match(pool, advancing, used)
            if match is not None:
                used.add(match["match_id"])
            curr.append(match)  # row or None (blank slot)
        ordered.append((display, curr))
        prev = curr

    return ordered


def _match_box(home, away, home_score, away_score, winner, duration, home_pens, away_pens):
    """HTML for one match box, with an optional indicator next to the winner.

    winner: 'home', 'away', or None (unplayed).
    duration: 'REGULAR', 'EXTRA_TIME', 'PENALTY_SHOOTOUT', or None.
    home_pens/away_pens: shootout scores (only used for PENALTY_SHOOTOUT).
    """
    # A cell is greyed if its team lost (eliminated) or isn't determined
    # yet (TBD). The advancing team gets a subtle accent.
    home_cls = "team eliminated" if (winner == "away" or home is None) else "team"
    away_cls = "team eliminated" if (winner == "home" or away is None) else "team"
    if winner == "home":
        home_cls = "team winner"
    elif winner == "away":
        away_cls = "team winner"
    hs = "" if home_score is None else home_score
    as_ = "" if away_score is None else away_score
    home = home or "TBD"
    away = away or "TBD"

    # Note appended to the winning team's name: (OT) for extra time,
    # (pens H-A) for a shootout. Nothing for regulation/unplayed.
    note = ""
    if duration == "EXTRA_TIME":
        note = '<span class="match-note">(OT)</span>'
    elif duration == "PENALTY_SHOOTOUT" and home_pens is not None and away_pens is not None:
        note = f'<span class="match-note">(pens {home_pens}-{away_pens})</span>'

    home_label = f"{home}{note}" if winner == "home" else home
    away_label = f"{away}{note}" if winner == "away" else away

    return (
        '<div class="match">'
        f'<div class="{home_cls}"><span class="tla">{home_label}</span><span class="score">{hs}</span></div>'
        f'<div class="{away_cls}"><span class="tla">{away_label}</span><span class="score">{as_}</span></div>'
        '</div>'
    )


def _row_to_match(row):
    """Convert a get_knockout() dataframe row to a clean match tuple,
    normalizing pandas NaN -> None and float scores -> int. A None row
    (blank/unresolved slot) becomes an all-None tuple (renders as TBD)."""
    if row is None:
        return (None, None, None, None, None, None, None, None)
    home = row["home_tla"] if pd.notna(row["home_tla"]) else None
    away = row["away_tla"] if pd.notna(row["away_tla"]) else None
    home_score = int(row["home_score"]) if pd.notna(row["home_score"]) else None
    away_score = int(row["away_score"]) if pd.notna(row["away_score"]) else None
    winner = row["winner"] if pd.notna(row["winner"]) else None
    duration = row["duration"] if pd.notna(row["duration"]) else None
    home_pens = int(row["home_penalties"]) if pd.notna(row["home_penalties"]) else None
    away_pens = int(row["away_penalties"]) if pd.notna(row["away_penalties"]) else None
    return (home, away, home_score, away_score, winner, duration, home_pens, away_pens)


def render_bracket():
    df = get_knockout()
    ordered = _order_rounds(df)

    # Header row: all round titles, aligned and parallel.
    headers_html = ""
    for round_name, _ in ordered:
        headers_html += f'<div class="round-title">{round_name}</div>'

    # Bracket body: each round is an equal-height column of matches.
    columns_html = ""
    for _, matches in ordered:
        boxes = "".join(_match_box(*_row_to_match(m)) for m in matches)
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
        ".team.winner{border-left:3px solid #58a6ff;color:#f0f6fc;font-weight:600;}"
        ".tla{font-weight:600;letter-spacing:0.03em;}"
        ".match-note{font-size:0.7rem;font-weight:400;color:#8b949e;letter-spacing:0;margin-left:5px;}"
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