"""크롤링 실행 페이지 — 실시간 로그/진행률 모니터링."""
import io
import json
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Crawl Run", page_icon="🚀", layout="wide")
st.title("🚀 크롤링 실행")

# ── 상수 ──
LEAGUE_META = {
    "PL":     {"name": "Premier League",  "region": 252, "tournament": 2},
    "LIGA":   {"name": "La Liga",         "region": 206, "tournament": 4},
    "SA":     {"name": "Serie A",         "region": 108, "tournament": 5},
    "BL":     {"name": "Bundesliga",      "region": 81,  "tournament": 3},
    "LIGUE1": {"name": "Ligue 1",         "region": 74,  "tournament": 22},
}

LOG_DIR = Path(__file__).resolve().parent.parent / "data"
LOG_FILE = LOG_DIR / "crawl_live.jsonl"
STATUS_FILE = LOG_DIR / "crawl_status.json"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 파일 기반 로그 유틸 (thread-safe)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_log_lock = threading.Lock()


def _write_status(data: dict):
    """현재 크롤링 상태를 JSON 파일에 기록."""
    with _log_lock:
        STATUS_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _read_status() -> dict:
    """현재 크롤링 상태를 JSON 파일에서 읽기."""
    try:
        return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"status": "idle"}


def _append_log(line: str):
    """로그 한 줄을 JSONL 파일에 추가."""
    entry = {"ts": datetime.now().strftime("%H:%M:%S"), "msg": line.rstrip()}
    with _log_lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _read_logs(tail: int = 200) -> list[dict]:
    """JSONL 로그 파일에서 마지막 N줄 읽기."""
    try:
        lines = LOG_FILE.read_text(encoding="utf-8").strip().splitlines()
        entries = []
        for line in lines[-tail:]:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                entries.append({"ts": "", "msg": line})
        return entries
    except FileNotFoundError:
        return []


def _clear_logs():
    """로그 파일 초기화."""
    with _log_lock:
        LOG_FILE.write_text("", encoding="utf-8")


class _FileLogCapture:
    """stdout을 가로채 파일에 기록 + 원래 stdout에도 출력."""
    def __init__(self, original_stdout):
        self._orig = original_stdout
        self._buf = ""

    def write(self, s):
        self._orig.write(s)
        self._buf += s
        # 줄 단위로 처리
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            stripped = line.strip()
            if stripped:
                _append_log(stripped)
                # 매치 크롤링 진행률 파싱
                self._update_progress(stripped)
        return len(s)

    def flush(self):
        self._orig.flush()

    def _update_progress(self, msg: str):
        """로그 메시지에서 진행률 추출하여 상태 파일 갱신."""
        status = _read_status()
        # "match_url 123 : crawling done" 패턴
        if "crawling done" in msg or "cawling done" in msg:
            status["completed"] = status.get("completed", 0) + 1
            _write_status(status)
        elif ": error" in msg:
            status["errors"] = status.get("errors", 0) + 1
            _write_status(status)
        elif "done," in msg and "matches" in msg:
            # "PL2425_match_url.csv: done, 380 matches" 패턴
            try:
                parts = msg.split("done,")[1].strip().split()
                status["total"] = int(parts[0])
                _write_status(status)
            except (IndexError, ValueError):
                pass
        elif msg.startswith("[DB]"):
            status["db_saved"] = msg
            _write_status(status)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 크롤링 실행 함수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _run_crawl(func, kwargs, crawl_type):
    """백그라운드 스레드에서 크롤링 실행."""
    _clear_logs()
    _write_status({
        "status": "running",
        "type": crawl_type,
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pid": os.getpid(),
        "total": 0,
        "completed": 0,
        "errors": 0,
    })
    _append_log(f"=== {crawl_type} 시작 ===")

    old_stdout = sys.stdout
    sys.stdout = _FileLogCapture(old_stdout)
    try:
        result = func(**kwargs)
        result_str = str(result) if result is not None else "완료"
        _append_log(f"=== 크롤링 완료: {result_str} ===")
        status = _read_status()
        status["status"] = "completed"
        status["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status["result"] = result_str
        _write_status(status)
    except Exception as e:
        # 정지(stopped)가 아닌 경우만 에러 처리
        status = _read_status()
        if status.get("status") != "stopped":
            _append_log(f"❌ 에러 발생: {e}")
            status["status"] = "error"
            status["error_msg"] = str(e)
            status["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _write_status(status)
    finally:
        sys.stdout = old_stdout


def _start_crawl(func, kwargs, crawl_type):
    """스레드를 생성하여 크롤링 시작."""
    t = threading.Thread(target=_run_crawl, args=(func, kwargs, crawl_type), daemon=True)
    t.start()


def _stop_crawl():
    """실행 중인 크롤링을 정지 — chromedriver/Chrome 프로세스 종료."""
    status = _read_status()
    if status.get("status") != "running":
        return

    _append_log("⏹️ 사용자가 크롤링을 정지했습니다.")
    status["status"] = "stopped"
    status["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _write_status(status)

    # Selenium chromedriver + 자동화용 Chrome 프로세스 종료 (좀비 UE 제외)
    try:
        # chromedriver (정상 S 상태만)
        result = subprocess.run(
            ["pgrep", "-f", "chromedriver.*--port"],
            capture_output=True, text=True,
        )
        for pid_str in result.stdout.strip().splitlines():
            pid = int(pid_str)
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

        # Selenium이 띄운 Chrome (--test-type=webdriver 플래그가 있는 것만)
        result = subprocess.run(
            ["pgrep", "-f", "test-type=webdriver"],
            capture_output=True, text=True,
        )
        for pid_str in result.stdout.strip().splitlines():
            pid = int(pid_str)
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    except Exception:
        pass

    _append_log("⏹️ 크롤링 프로세스가 정지되었습니다.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 실시간 모니터링 fragment (3초마다 자동 갱신)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@st.fragment(run_every=3)
def live_monitor():
    """크롤링 상태를 실시간으로 표시하는 fragment."""
    status = _read_status()
    st_status = status.get("status", "idle")

    # ── 상태 배너 ──
    if st_status == "running":
        crawl_type = status.get("type", "")
        started = status.get("started_at", "")
        col_status, col_stop = st.columns([4, 1])
        with col_status:
            st.warning(f"🔄 **크롤링 실행 중** — {crawl_type} (시작: {started})")
        with col_stop:
            if st.button("⏹️ 정지", key="btn_stop", type="primary"):
                _stop_crawl()
                st.rerun()

        # ── 진행률 ──
        total = status.get("total", 0)
        completed = status.get("completed", 0)
        errors = status.get("errors", 0)

        if total > 0:
            progress = min((completed + errors) / total, 1.0)
            st.progress(progress, text=f"진행: {completed + errors}/{total} ({completed} 완료, {errors} 에러)")
        else:
            st.progress(0.0, text="URL 수집 중...")

        c1, c2, c3 = st.columns(3)
        c1.metric("완료", completed)
        c2.metric("에러", errors)
        c3.metric("전체", total if total > 0 else "수집 중")

        # ── DB 저장 현황 ──
        db_msg = status.get("db_saved", "")
        if db_msg:
            st.caption(f"💾 {db_msg}")

    elif st_status == "completed":
        crawl_type = status.get("type", "")
        completed_at = status.get("completed_at", "")
        result = status.get("result", "")
        st.success(f"✅ **크롤링 완료** — {crawl_type} ({completed_at})")

        total = status.get("total", 0)
        completed = status.get("completed", 0)
        errors = status.get("errors", 0)
        if total > 0:
            c1, c2, c3 = st.columns(3)
            c1.metric("완료", completed)
            c2.metric("에러", errors)
            c3.metric("전체", total)
        if result:
            st.info(f"결과: {result}")

    elif st_status == "stopped":
        crawl_type = status.get("type", "")
        completed_at = status.get("completed_at", "")
        st.info(f"⏹️ **크롤링 정지됨** — {crawl_type} ({completed_at})")
        total = status.get("total", 0)
        completed = status.get("completed", 0)
        errors = status.get("errors", 0)
        if total > 0:
            c1, c2, c3 = st.columns(3)
            c1.metric("완료", completed)
            c2.metric("에러", errors)
            c3.metric("전체", total)

    elif st_status == "error":
        crawl_type = status.get("type", "")
        error_msg = status.get("error_msg", "")
        st.error(f"❌ **크롤링 에러** — {crawl_type}")
        if error_msg:
            st.code(error_msg)

    # ── 실시간 로그 ──
    logs = _read_logs(tail=150)
    if logs:
        with st.expander("📋 실시간 로그" if st_status == "running" else "📋 마지막 크롤링 로그",
                          expanded=(st_status == "running")):
            log_text = "\n".join(f"[{e['ts']}] {e['msg']}" for e in logs)
            st.code(log_text, language=None)


# ── fragment 렌더링 ──
live_monitor()

st.divider()

# ── 현재 상태 확인 (버튼 비활성화 판단용) ──
_cur_status = _read_status()
is_running = _cur_status.get("status") == "running"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 탭 구성 — 크롤링 시작 폼
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tab1, tab2, tab3 = st.tabs(["⚽ 매치 크롤링", "👤 선수 통계 크롤링", "🏟️ 팀 통계 크롤링"])

# ── 탭 1: 매치 크롤링 ──
with tab1:
    st.subheader("⚽ 매치 크롤링")
    st.caption("시즌 전체 매치 결과를 크롤링합니다. (소요시간: 수십 분 ~ 수 시간)")

    col1, col2 = st.columns(2)
    with col1:
        league_opts = {f"{c} — {m['name']}": c for c, m in LEAGUE_META.items()}
        sel = st.selectbox("리그 선택", list(league_opts.keys()), key="match_league")
        lc = league_opts[sel]
        meta = LEAGUE_META[lc]
        st.caption(f"Region: {meta['region']} | Tournament: {meta['tournament']}")
    with col2:
        sc = st.text_input("시즌 코드", value="2425", key="match_season_code",
                           help="예: 2425 (24-25 시즌), 2324 (23-24 시즌)")
        sn = st.number_input("WhoScored 시즌 번호", min_value=1, value=10274,
                             key="match_season_number",
                             help="WhoScored URL에서 확인 가능한 시즌 번호")

    sname = f"{lc}{sc}"
    st.caption(f"파일명: `{sname}_match.csv`, `{sname}_match_url.csv`")

    if st.button("🚀 매치 크롤링 시작", disabled=is_running, key="btn_match", type="primary"):
        from db_helper import crawl_and_save_all_matches
        _start_crawl(
            crawl_and_save_all_matches,
            {"region": meta["region"], "tournament": meta["tournament"],
             "season_number": sn, "season_name": sname,
             "league_code": lc, "season_code": sc},
            f"매치 크롤링 ({lc} {sc})",
        )
        time.sleep(0.5)
        st.rerun()

# ── 탭 2: 선수 통계 크롤링 ──
with tab2:
    st.subheader("👤 선수 통계 크롤링")
    st.caption("WhoScored 선수 통계 페이지에서 전체 선수 데이터를 크롤링합니다. (소요시간: 5~20분)")

    player_url = st.text_input(
        "WhoScored 선수 통계 URL",
        placeholder="https://www.whoscored.com/Regions/.../PlayerStatistics",
        key="player_url",
    )
    col1, col2 = st.columns(2)
    with col1:
        lo_p = {f"{c} — {m['name']}": c for c, m in LEAGUE_META.items()}
        sel_p = st.selectbox("리그 선택", list(lo_p.keys()), key="player_league")
        lc_p = lo_p[sel_p]
    with col2:
        sc_p = st.text_input("시즌 코드", value="2425", key="player_season_code")
    csv_p = st.text_input("CSV 저장 경로 (선택사항)",
                          placeholder=f"player_data/{lc_p}{sc_p}_player.csv", key="player_csv")

    if st.button("🚀 선수 통계 크롤링 시작", disabled=is_running or not player_url,
                 key="btn_player", type="primary"):
        from db_helper import crawl_and_save_player_stats
        _start_crawl(
            crawl_and_save_player_stats,
            {"url": player_url, "league_code": lc_p, "season_code": sc_p,
             "csv_path": csv_p if csv_p else None},
            f"선수 통계 크롤링 ({lc_p} {sc_p})",
        )
        time.sleep(0.5)
        st.rerun()

# ── 탭 3: 팀 통계 크롤링 ──
with tab3:
    st.subheader("🏟️ 팀 통계 크롤링")
    st.caption("WhoScored 리그 테이블 페이지에서 팀 통계를 크롤링합니다. (소요시간: 1~5분)")

    team_url = st.text_input(
        "WhoScored 리그 테이블 URL",
        placeholder="https://www.whoscored.com/Regions/.../Standings",
        key="team_url",
    )
    col1, col2 = st.columns(2)
    with col1:
        lo_t = {f"{c} — {m['name']}": c for c, m in LEAGUE_META.items()}
        sel_t = st.selectbox("리그 선택", list(lo_t.keys()), key="team_league")
        lc_t = lo_t[sel_t]
    with col2:
        sc_t = st.text_input("시즌 코드", value="2425", key="team_season_code")
    csv_t = st.text_input("CSV 저장 경로 (선택사항)",
                          placeholder=f"team_data/{lc_t}{sc_t}_team.csv", key="team_csv")

    if st.button("🚀 팀 통계 크롤링 시작", disabled=is_running or not team_url,
                 key="btn_team", type="primary"):
        from db_helper import crawl_and_save_team_stats
        _start_crawl(
            crawl_and_save_team_stats,
            {"url": team_url, "league_code": lc_t, "season_code": sc_t,
             "csv_path": csv_t if csv_t else None},
            f"팀 통계 크롤링 ({lc_t} {sc_t})",
        )
        time.sleep(0.5)
        st.rerun()

# ── 하단 안내 ──
st.divider()
st.markdown("""
### 📌 사용 안내
1. **매치 크롤링**: 시즌 전체 매치 결과를 크롤링합니다. WhoScored 시즌 번호는 URL에서 확인하세요.
2. **선수/팀 통계**: WhoScored 해당 페이지 URL을 직접 입력합니다.
3. 크롤링 실행 중에는 다른 크롤링을 시작할 수 없습니다.
4. 크롤링 결과는 CSV 파일 + SQLite DB에 자동 저장됩니다.
5. 크롤링 이력은 [📡 크롤링 현황](/Crawl_Status) 페이지에서 확인할 수 있습니다.
6. **실시간 모니터링**: 크롤링 진행 중 상단에서 진행률과 로그를 실시간으로 확인할 수 있습니다.
""")
