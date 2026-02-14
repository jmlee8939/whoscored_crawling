"""매치 결과 조회 페이지."""
import streamlit as st
from db.queries import get_leagues, get_seasons, get_matches

st.set_page_config(page_title="Matches", page_icon="⚽", layout="wide")
st.title("📊 매치 결과")

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

    team_search = st.text_input("팀 검색")
    page_size = st.selectbox("페이지 크기", [20, 50, 100], index=0)

# ── 페이지네이션 ──
if "match_page" not in st.session_state:
    st.session_state.match_page = 0

matches, total = get_matches(
    season_id=season_id,
    team_name=team_search if team_search else None,
    limit=page_size,
    offset=st.session_state.match_page * page_size,
)

total_pages = max(1, (total + page_size - 1) // page_size)
st.caption(f"총 {total}건 (페이지 {st.session_state.match_page + 1}/{total_pages})")

# ── 페이지 이동 ──
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if st.button("◀ 이전", disabled=st.session_state.match_page <= 0):
        st.session_state.match_page -= 1
        st.rerun()
with col3:
    if st.button("다음 ▶", disabled=st.session_state.match_page >= total_pages - 1):
        st.session_state.match_page += 1
        st.rerun()

# ── 매치 테이블 ──
if not matches.empty:
    display_cols = [
        "league_code", "season_code", "home_team", "full_home_score",
        "full_away_score", "away_team", "date",
        "home_possession", "away_possession",
        "home_shot", "away_shot",
    ]
    available = [c for c in display_cols if c in matches.columns]
    st.dataframe(matches[available], use_container_width=True, hide_index=True)

    # ── 매치 상세 보기 ──
    with st.expander("매치 상세 보기"):
        idx = st.number_input("행 번호 선택", min_value=0, max_value=len(matches)-1, value=0, step=1)
        row = matches.iloc[idx]
        st.markdown(f"### {row.get('home_team', '')} {row.get('full_home_score', '')} - {row.get('full_away_score', '')} {row.get('away_team', '')}")
        st.markdown(f"**날짜:** {row.get('date', '')} | **킥오프:** {row.get('kick_off', '')}")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**홈팀 스탯**")
            for key in ["home_shot", "home_possession", "home_pass_success", "home_dribbles",
                        "home_aerials_won", "home_tackles", "home_corners", "home_total_passes"]:
                if key in row.index:
                    st.text(f"  {key.replace('home_', '')}: {row[key]}")
        with c2:
            st.markdown("**어웨이팀 스탯**")
            for key in ["away_shot", "away_possession", "away_pass_success", "away_dribbles",
                        "away_aerials_won", "away_tackles", "away_corners", "away_total_passes"]:
                if key in row.index:
                    st.text(f"  {key.replace('away_', '')}: {row[key]}")
else:
    st.info("데이터가 없습니다.")
