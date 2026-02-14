"""크롤링 이력 및 DB 현황 페이지 — 실시간 크롤링 상태 포함."""
import json
from pathlib import Path

import streamlit as st
from db.queries import get_crawl_jobs, get_data_summary

st.set_page_config(page_title="Crawl Status", page_icon="📡", layout="wide")
st.title("📡 크롤링 현황 & DB 통계")

# ── 실시간 크롤링 상태 파일 ──
_STATUS_FILE = Path(__file__).resolve().parent.parent / "data" / "crawl_status.json"
_LOG_FILE = Path(__file__).resolve().parent.parent / "data" / "crawl_live.jsonl"


def _read_crawl_status() -> dict:
    try:
        return json.loads(_STATUS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"status": "idle"}


def _read_live_logs(tail: int = 100) -> list[dict]:
    try:
        lines = _LOG_FILE.read_text(encoding="utf-8").strip().splitlines()
        entries = []
        for line in lines[-tail:]:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                entries.append({"ts": "", "msg": line})
        return entries
    except FileNotFoundError:
        return []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 실시간 크롤링 모니터 (fragment, 3초 갱신)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@st.fragment(run_every=3)
def live_crawl_status():
    """현재 진행 중인 크롤링 상태를 실시간 표시."""
    status = _read_crawl_status()
    st_status = status.get("status", "idle")

    if st_status == "running":
        crawl_type = status.get("type", "")
        started = status.get("started_at", "")
        total = status.get("total", 0)
        completed = status.get("completed", 0)
        errors = status.get("errors", 0)

        st.warning(f"🔄 **크롤링 실행 중** — {crawl_type} (시작: {started})")

        if total > 0:
            progress = min((completed + errors) / total, 1.0)
            st.progress(progress, text=f"진행: {completed + errors}/{total} ({completed} 완료, {errors} 에러)")
        else:
            st.progress(0.0, text="URL 수집 중...")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("완료", completed)
        c2.metric("에러", errors)
        c3.metric("전체", total if total > 0 else "수집 중")
        elapsed = ""
        if started:
            from datetime import datetime
            try:
                dt = datetime.strptime(started, "%Y-%m-%d %H:%M:%S")
                delta = datetime.now() - dt
                mins = int(delta.total_seconds() // 60)
                secs = int(delta.total_seconds() % 60)
                elapsed = f"{mins}분 {secs}초"
            except ValueError:
                pass
        c4.metric("경과 시간", elapsed if elapsed else "—")

        db_msg = status.get("db_saved", "")
        if db_msg:
            st.caption(f"💾 {db_msg}")

        # 최근 로그 미리보기
        logs = _read_live_logs(tail=10)
        if logs:
            st.caption("📋 최근 로그")
            log_text = "\n".join(f"[{e['ts']}] {e['msg']}" for e in logs)
            st.code(log_text, language=None)

    elif st_status == "completed":
        crawl_type = status.get("type", "")
        completed_at = status.get("completed_at", "")
        total = status.get("total", 0)
        completed = status.get("completed", 0)
        errors = status.get("errors", 0)
        st.success(f"✅ **마지막 크롤링 완료** — {crawl_type} ({completed_at})")
        if total > 0:
            c1, c2, c3 = st.columns(3)
            c1.metric("완료", completed)
            c2.metric("에러", errors)
            c3.metric("전체", total)

    elif st_status == "error":
        crawl_type = status.get("type", "")
        error_msg = status.get("error_msg", "")
        st.error(f"❌ **마지막 크롤링 에러** — {crawl_type}")
        if error_msg:
            st.code(error_msg)


live_crawl_status()

st.divider()

# ── DB 요약 ──
st.subheader("📊 데이터베이스 현황")
summary = get_data_summary()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("리그", summary["total_leagues"])
col2.metric("시즌", summary["total_seasons"])
col3.metric("매치", f"{summary['total_matches']:,}")
col4.metric("선수 기록", f"{summary['total_players']:,}")
col5.metric("팀 기록", summary["total_teams"])

# ── 리그별 시즌 수 ──
st.subheader("🏆 리그별 현황")
league_df = summary.get("league_seasons")
if league_df is not None and not league_df.empty:
    st.dataframe(league_df, use_container_width=True, hide_index=True)

# ── 시즌별 데이터 커버리지 ──
st.subheader("📅 시즌별 데이터 커버리지")
season_df = summary.get("season_data")
if season_df is not None and not season_df.empty:
    st.dataframe(
        season_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "league_code": "리그",
            "season_label": "시즌",
            "match_count": st.column_config.NumberColumn("매치 수", format="%d"),
            "player_count": st.column_config.NumberColumn("선수 기록 수", format="%d"),
            "team_count": st.column_config.NumberColumn("팀 기록 수", format="%d"),
        },
    )

    # 시각화: 시즌별 매치 수 차트
    st.subheader("📈 시즌별 매치 수")
    chart_df = season_df[["league_code", "season_label", "match_count"]].copy()
    chart_df["label"] = chart_df["league_code"] + " " + chart_df["season_label"]
    chart_df = chart_df.set_index("label")
    st.bar_chart(chart_df["match_count"])

# ── 크롤링 작업 이력 ──
st.subheader("🔄 최근 크롤링 작업 이력")
jobs = get_crawl_jobs(limit=30)
if not jobs.empty:
    display_cols = [
        "job_type", "league_code", "season_code", "status",
        "total_items", "completed_items", "error_items",
        "completed_at", "created_at",
    ]
    available = [c for c in display_cols if c in jobs.columns]
    st.dataframe(
        jobs[available],
        use_container_width=True,
        hide_index=True,
        column_config={
            "job_type": "유형",
            "league_code": "리그",
            "season_code": "시즌",
            "status": "상태",
            "total_items": "전체",
            "completed_items": "완료",
            "error_items": "에러",
            "completed_at": "완료 시각",
            "created_at": "생성 시각",
        },
    )
else:
    st.info("크롤링 작업 이력이 없습니다.")
