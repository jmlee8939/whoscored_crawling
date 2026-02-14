"""선수 통계 조회 페이지."""
import streamlit as st
from db.queries import get_leagues, get_seasons, get_players

st.set_page_config(page_title="Players", page_icon="👤", layout="wide")
st.title("👤 선수 통계")

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
    player_search = st.text_input("선수 검색")
    position_options = ["전체", "FW", "MF", "DF", "GK", "AM", "DM", "M"]
    sel_position = st.selectbox("포지션", position_options)

    stat_type_options = ["full", "summary", "defensive", "offensive", "passing"]
    sel_stat_type = st.selectbox("통계 유형", stat_type_options)

    sort_options = {
        "레이팅": "rating", "골": "goals", "어시스트": "assists",
        "출전": "apps", "슈팅": "spg", "태클": "tackles",
        "키패스": "key_p", "드리블": "dribble", "패스 성공률": "ps_pct",
    }
    sel_sort = st.selectbox("정렬 기준", list(sort_options.keys()))
    sel_order = st.radio("정렬 순서", ["내림차순", "오름차순"], horizontal=True)

    page_size = st.selectbox("페이지 크기", [20, 50, 100], index=0)

# ── 페이지네이션 ──
if "player_page" not in st.session_state:
    st.session_state.player_page = 0

players, total = get_players(
    season_id=season_id,
    team_name=team_search if team_search else None,
    player_name=player_search if player_search else None,
    position=sel_position if sel_position != "전체" else None,
    stat_type=sel_stat_type,
    sort_by=sort_options[sel_sort],
    sort_order="DESC" if sel_order == "내림차순" else "ASC",
    limit=page_size,
    offset=st.session_state.player_page * page_size,
)

total_pages = max(1, (total + page_size - 1) // page_size)
st.caption(f"총 {total}건 (페이지 {st.session_state.player_page + 1}/{total_pages})")

# ── 페이지 이동 ──
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if st.button("◀ 이전", disabled=st.session_state.player_page <= 0, key="prev_player"):
        st.session_state.player_page -= 1
        st.rerun()
with col3:
    if st.button("다음 ▶", disabled=st.session_state.player_page >= total_pages - 1, key="next_player"):
        st.session_state.player_page += 1
        st.rerun()

# ── 선수 테이블 ──
if not players.empty:
    display_cols = [
        "league_code", "season_code", "player_name", "team_name",
        "position", "age", "apps", "mins",
        "goals", "assists", "rating",
        "spg", "ps_pct", "key_p", "tackles",
        "dribble", "aerials_won",
    ]
    available = [c for c in display_cols if c in players.columns]
    st.dataframe(players[available], use_container_width=True, hide_index=True)

    # ── 선수 상세 보기 ──
    with st.expander("선수 상세 보기"):
        idx = st.number_input("행 번호 선택", min_value=0, max_value=len(players)-1, value=0, step=1, key="player_idx")
        row = players.iloc[idx]
        st.markdown(f"### {row.get('player_name', '')} ({row.get('team_name', '')})")
        st.markdown(f"**포지션:** {row.get('position', '')} | **나이:** {row.get('age', '')} | **레이팅:** {row.get('rating', '')}")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**공격 스탯**")
            for key in ["goals", "assists", "spg", "key_p", "dribble", "crosses"]:
                if key in row.index and row[key] is not None:
                    st.text(f"  {key}: {row[key]}")
        with c2:
            st.markdown("**수비 스탯**")
            for key in ["tackles", "inter", "fouls", "clear", "blocks", "aerials_won"]:
                if key in row.index and row[key] is not None:
                    st.text(f"  {key}: {row[key]}")
        with c3:
            st.markdown("**패스 스탯**")
            for key in ["ps_pct", "avg_p", "long_b", "thr_b", "crosses"]:
                if key in row.index and row[key] is not None:
                    st.text(f"  {key}: {row[key]}")
else:
    st.info("데이터가 없습니다.")
