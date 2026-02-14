"""팀 시즌 통계 조회 페이지."""
import streamlit as st
from db.queries import get_leagues, get_seasons, get_teams

st.set_page_config(page_title="Teams", page_icon="🏟️", layout="wide")
st.title("🏟️ 팀 시즌 통계")

# ── 사이드바 필터 ──
with st.sidebar:
    st.header("필터")
    leagues = get_leagues()
    league_options = ["전체"] + leagues["code"].tolist()
    sel_league = st.selectbox("리그", league_options)

    season_id = None
    if sel_league != "전체":
        seasons = get_seasons(sel_league)
        if not seasons.empty:
            season_options = dict(zip(seasons["season_label"], seasons["id"]))
            sel_season = st.selectbox("시즌", ["전체"] + list(season_options.keys()))
            if sel_season != "전체":
                season_id = season_options[sel_season]

    sort_options = {
        "승점": "points", "승": "won", "패": "lost", "무": "drawn",
        "득점": "goals_for", "실점": "goals_against", "득실차": "goal_diff",
        "레이팅": "rating", "슈팅": "shots_pg", "태클": "tackles_pg",
        "점유율": "poss_pct", "패스 성공률": "pass_pct",
    }
    sel_sort = st.selectbox("정렬 기준", list(sort_options.keys()))
    sel_order = st.radio("정렬 순서", ["내림차순", "오름차순"], horizontal=True)

# ── 데이터 조회 ──
teams = get_teams(
    season_id=season_id,
    sort_by=sort_options[sel_sort],
    sort_order="DESC" if sel_order == "내림차순" else "ASC",
)

st.caption(f"총 {len(teams)}건")

if not teams.empty:
    # ── 순위표 ──
    st.subheader("📋 순위표")
    rank_cols = [
        "league_code", "season_code", "team_name",
        "played", "won", "drawn", "lost",
        "goals_for", "goals_against", "goal_diff", "points", "rating",
    ]
    available_rank = [c for c in rank_cols if c in teams.columns]
    st.dataframe(teams[available_rank], use_container_width=True, hide_index=True)

    # ── 공격 통계 ──
    st.subheader("⚔️ 공격 통계")
    attack_cols = [
        "team_name", "goals", "shots_pg", "shots_ot_pg",
        "dribbles_pg", "fouled_pg", "poss_pct",
    ]
    available_attack = [c for c in attack_cols if c in teams.columns]
    if available_attack:
        st.dataframe(teams[available_attack], use_container_width=True, hide_index=True)

    # ── 수비 통계 ──
    st.subheader("🛡️ 수비 통계")
    defense_cols = [
        "team_name", "shoted_pg", "tackles_pg", "intercept_pg",
        "fouls_pg", "offsides_pg", "aerials_won",
    ]
    available_defense = [c for c in defense_cols if c in teams.columns]
    if available_defense:
        st.dataframe(teams[available_defense], use_container_width=True, hide_index=True)

    # ── 패스 & 기타 ──
    st.subheader("📊 패스 & 기타")
    pass_cols = [
        "team_name", "pass_pct", "poss_pct",
        "yellow", "red", "rating",
    ]
    available_pass = [c for c in pass_cols if c in teams.columns]
    if available_pass:
        st.dataframe(teams[available_pass], use_container_width=True, hide_index=True)

    # ── 팀 상세 보기 ──
    with st.expander("팀 상세 보기"):
        team_names = teams["team_name"].tolist()
        sel_team = st.selectbox("팀 선택", team_names)
        row = teams[teams["team_name"] == sel_team].iloc[0]

        st.markdown(f"### {row.get('team_name', '')} ({row.get('league_code', '')} {row.get('season_code', '')})")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**기본 정보**")
            for key, label in [("played", "경기수"), ("won", "승"), ("drawn", "무"),
                               ("lost", "패"), ("points", "승점")]:
                if key in row.index:
                    st.text(f"  {label}: {row[key]}")
        with c2:
            st.markdown("**공격**")
            for key, label in [("goals_for", "득점"), ("shots_pg", "슈팅/경기"),
                               ("shots_ot_pg", "유효슈팅/경기"), ("dribbles_pg", "드리블/경기"),
                               ("fouled_pg", "파울유도/경기")]:
                if key in row.index:
                    st.text(f"  {label}: {row[key]}")
        with c3:
            st.markdown("**수비**")
            for key, label in [("goals_against", "실점"), ("tackles_pg", "태클/경기"),
                               ("intercept_pg", "인터셉트/경기"), ("fouls_pg", "파울/경기"),
                               ("aerials_won", "공중볼 성공")]:
                if key in row.index:
                    st.text(f"  {label}: {row[key]}")
else:
    st.info("데이터가 없습니다.")
