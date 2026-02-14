"""
DB 헬퍼 모듈 — CSV 저장 시 DB에도 동시 저장.
utils.py를 수정하지 않고, 이 모듈의 함수를 통해 DB 저장을 수행합니다.

사용 예시:
    # 방법 1: 직접 저장 함수 사용
    from db_helper import save_match_to_db
    df = pd.read_csv('PL2425_match.csv')
    save_match_to_db(df, 'PL', '2425')

    # 방법 2: 래퍼 함수 사용 (크롤링 + CSV + DB 동시 저장)
    from db_helper import crawl_and_save_team_stats
    df = crawl_and_save_team_stats(url, 'PL', '2425', 'team_data/PL2425_team.csv')
"""
import os
import json
import pandas as pd
from datetime import datetime

from db.database import get_connection, DB_PATH

# ── CSV→DB 컬럼 매핑 ──
MATCH_COL_MAP = {"home": "home_team", "away": "away_team"}

PLAYER_COL_MAP = {
    "Apps": "apps", "Mins": "mins", "Goals": "goals", "Assists": "assists",
    "Yel": "yel", "Red": "red", "SpG": "spg", "PS%": "ps_pct",
    "AerialsWon": "aerials_won", "MoM": "mom", "Rating": "rating",
    "KeyP": "key_p", "AvgP": "avg_p", "Crosses": "crosses",
    "LongB": "long_b", "ThrB": "thr_b", "Tackles": "tackles",
    "Inter": "inter", "Fouls": "fouls", "Offsides": "offsides",
    "Clear": "clear", "Drb": "drb", "Blocks": "blocks", "OwnG": "own_g",
    "Dribble": "dribble", "Fouled": "fouled", "Off": "off",
    "Disp": "disp", "UnsTch": "uns_tch",
    "player_name": "player_name", "team_number": "team_number",
    "team_name": "team_name", "age": "age", "position": "position", "sub": "sub",
}

TEAM_COL_MAP = {
    "team_name": "team_name", "P": "played", "W": "won", "D": "drawn", "L": "lost",
    "GF": "goals_for", "GA": "goals_against", "GD": "goal_diff", "Pts": "points",
    "Goals": "goals", "Shots pg": "shots_pg", "Yellow": "yellow", "Red": "red",
    "Poss%": "poss_pct", "Pass%": "pass_pct", "A_Won": "aerials_won", "Rating": "rating",
    "Shoted pg": "shoted_pg", "Tackles pg": "tackles_pg", "Intercept pg": "intercept_pg",
    "Fouls pg": "fouls_pg", "Offsides pg": "offsides_pg",
    "Shots OT pg": "shots_ot_pg", "Dribbles pg": "dribbles_pg", "Fouled pg": "fouled_pg",
}


def _season_label(code: str) -> str:
    y1 = int(code[:2])
    c1 = 2000 + y1 if y1 < 80 else 1900 + y1
    return f"{c1}-{code[2:]}"


def _ensure_season(conn, league_code, season_code):
    """시즌 ID를 가져오거나 생성."""
    league = conn.execute("SELECT id FROM leagues WHERE code = ?", (league_code,)).fetchone()
    if not league:
        raise ValueError(f"리그 코드 '{league_code}' 없음")
    league_id = league[0]
    row = conn.execute(
        "SELECT id FROM seasons WHERE league_id = ? AND season_code = ?",
        (league_id, season_code),
    ).fetchone()
    if row:
        return row[0]
    conn.execute(
        "INSERT INTO seasons (league_id, season_code, season_label) VALUES (?, ?, ?)",
        (league_id, season_code, _season_label(season_code)),
    )
    conn.commit()
    return conn.execute(
        "SELECT id FROM seasons WHERE league_id = ? AND season_code = ?",
        (league_id, season_code),
    ).fetchone()[0]


# ────────────────────────────────────────────
# 저장 함수
# ────────────────────────────────────────────

def save_match_to_db(df, league_code, season_code, source_file=None):
    """매치 결과 DataFrame을 DB에 저장."""
    conn = get_connection()
    try:
        season_id = _ensure_season(conn, league_code, season_code)
        df2 = df.copy()
        df2 = df2.loc[:, ~df2.columns.str.startswith("Unnamed")]
        count = 0
        for _, row in df2.iterrows():
            vals = {MATCH_COL_MAP.get(c, c): str(row[c]) if pd.notna(row[c]) else None for c in df2.columns}
            vals["season_id"] = season_id
            vals["source_file"] = source_file
            cols = list(vals.keys())
            conn.execute(
                f"INSERT OR REPLACE INTO matches ({', '.join(cols)}) VALUES ({', '.join(['?']*len(cols))})",
                [vals[c] for c in cols],
            )
            count += 1
        conn.commit()
        print(f"[DB] 매치 {count}건 저장 ({league_code} {season_code})")
        return count
    finally:
        conn.close()


def save_player_to_db(df, league_code, season_code, stat_type="full", source_file=None):
    """선수 통계 DataFrame을 DB에 저장."""
    conn = get_connection()
    try:
        season_id = _ensure_season(conn, league_code, season_code)
        df2 = df.copy()
        df2 = df2.loc[:, ~df2.columns.str.startswith("Unnamed")]
        count = 0
        for _, row in df2.iterrows():
            vals = {"season_id": season_id, "stat_type": stat_type, "source_file": source_file}
            for csv_col, db_col in PLAYER_COL_MAP.items():
                if csv_col in df2.columns:
                    v = row[csv_col]
                    vals[db_col] = str(v) if pd.notna(v) else None
            cols = list(vals.keys())
            conn.execute(
                f"INSERT OR REPLACE INTO player_stats ({', '.join(cols)}) VALUES ({', '.join(['?']*len(cols))})",
                [vals[c] for c in cols],
            )
            count += 1
        conn.commit()
        print(f"[DB] 선수 {count}건 저장 ({league_code} {season_code} {stat_type})")
        return count
    finally:
        conn.close()


def save_team_to_db(df, league_code, season_code, source_file=None):
    """팀 시즌 통계 DataFrame을 DB에 저장."""
    conn = get_connection()
    try:
        season_id = _ensure_season(conn, league_code, season_code)
        df2 = df.copy()
        df2 = df2.loc[:, ~df2.columns.str.startswith("Unnamed")]
        count = 0
        for _, row in df2.iterrows():
            vals = {"season_id": season_id, "source_file": source_file}
            for csv_col, db_col in TEAM_COL_MAP.items():
                if csv_col in df2.columns:
                    v = row[csv_col]
                    vals[db_col] = str(v) if pd.notna(v) else None
            cols = list(vals.keys())
            conn.execute(
                f"INSERT OR REPLACE INTO team_season_stats ({', '.join(cols)}) VALUES ({', '.join(['?']*len(cols))})",
                [vals[c] for c in cols],
            )
            count += 1
        conn.commit()
        print(f"[DB] 팀 {count}건 저장 ({league_code} {season_code})")
        return count
    finally:
        conn.close()


def save_match_urls_to_db(urls, league_code, season_code, source_file=None):
    """매치 URL 리스트를 DB에 저장."""
    conn = get_connection()
    try:
        season_id = _ensure_season(conn, league_code, season_code)
        if isinstance(urls, pd.DataFrame):
            for c in urls.columns:
                if urls[c].astype(str).str.startswith("http").any():
                    urls = urls[c].dropna().unique().tolist()
                    break
        count = 0
        for url in urls:
            conn.execute(
                "INSERT OR IGNORE INTO match_urls (season_id, url, source_file) VALUES (?, ?, ?)",
                (season_id, str(url), source_file),
            )
            count += 1
        conn.commit()
        print(f"[DB] 매치 URL {count}건 저장 ({league_code} {season_code})")
        return count
    finally:
        conn.close()


def log_crawl_job(job_type, league_code, season_code, status="completed",
                  total=0, completed=0, errors=0, error_list=None):
    """크롤링 작업 이력을 DB에 기록."""
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO crawl_jobs
               (job_type, league_code, season_code, status, total_items,
                completed_items, error_items, error_list, completed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (job_type, league_code, season_code, status, total, completed, errors,
             json.dumps(error_list) if error_list else None,
             datetime.now().isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


# ────────────────────────────────────────────
# 래퍼 함수 (utils.py 호출 + DB 자동 저장)
# ────────────────────────────────────────────

def crawl_and_save_all_matches(region, tournament, season_number, season_name,
                               league_code, season_code):
    """utils.crawling_all_matches() 호출 후 결과 CSV를 DB에도 저장."""
    from utils import crawling_all_matches
    error_list = crawling_all_matches(region, tournament, season_number, season_name)

    csv_path = f"{season_name}_match.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, index_col=0)
        save_match_to_db(df, league_code, season_code, source_file=csv_path)

    add_csv = f"{season_name}_add_match.csv"
    if os.path.exists(add_csv):
        add_df = pd.read_csv(add_csv, index_col=0)
        save_match_to_db(add_df, league_code, season_code, source_file=add_csv)

    total = len(pd.read_csv(csv_path, index_col=0)) if os.path.exists(csv_path) else 0
    log_crawl_job("match", league_code, season_code,
                  total=total, completed=total - len(error_list),
                  errors=len(error_list), error_list=error_list)
    return error_list


def crawl_and_save_player_stats(url, league_code, season_code, csv_path=None):
    """utils.crwaling_player_stats_at_once() 호출 후 DB에도 저장."""
    from utils import crwaling_player_stats_at_once
    df = crwaling_player_stats_at_once(url)
    if csv_path:
        df.to_csv(csv_path)
    save_player_to_db(df, league_code, season_code, stat_type="full", source_file=csv_path)
    log_crawl_job("player", league_code, season_code,
                  total=len(df), completed=len(df))
    return df


def crawl_and_save_team_stats(url, league_code, season_code, csv_path=None):
    """utils.league_table_added() 호출 후 DB에도 저장."""
    from utils import league_table_added
    df = league_table_added(url)
    if csv_path:
        df.to_csv(csv_path, index=False)
    save_team_to_db(df, league_code, season_code, source_file=csv_path)
    log_crawl_job("team", league_code, season_code,
                  total=len(df), completed=len(df))
    return df
