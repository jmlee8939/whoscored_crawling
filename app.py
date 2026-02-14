"""WhoScored Data Dashboard — 메인 페이지."""
import streamlit as st
from db.queries import get_data_summary

st.set_page_config(page_title="WhoScored Dashboard", page_icon="⚽", layout="wide")

st.title("⚽ WhoScored Data Dashboard")
st.markdown("WhoScored.com 크롤링 데이터 조회 대시보드")

summary = get_data_summary()

col1, col2, col3, col4 = st.columns(4)
col1.metric("총 매치", f"{summary['total_matches']:,}")
col2.metric("총 선수 기록", f"{summary['total_players']:,}")
col3.metric("총 팀 기록", f"{summary['total_teams']:,}")
col4.metric("총 시즌", f"{summary['total_seasons']:,}")

st.divider()

st.subheader("리그별 시즌 현황")
league_df = summary["league_seasons"]
if not league_df.empty:
    st.dataframe(league_df, use_container_width=True, hide_index=True)

st.subheader("시즌별 데이터 현황")
season_df = summary["season_data"]
if not season_df.empty:
    st.dataframe(season_df, use_container_width=True, hide_index=True)
