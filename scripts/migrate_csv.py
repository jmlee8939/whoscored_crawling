#!/usr/bin/env python
"""기존 CSV 파일을 SQLite DB로 마이그레이션합니다."""
import os, sys, re, glob
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db.database import get_connection, init_db

ROOT = os.path.dirname(os.path.dirname(__file__))

# ── 리그 이름 매핑 ──
LEAGUE_MAP = {
    "PL": "PL", "LIGUE1": "LIGUE1", "Ligue1": "LIGUE1",
    "Bundesliga": "BL", "Laliga": "LIGA", "Serie": "SA",
}

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


def season_label(code: str) -> str:
    """1516 → 2015-16"""
    y1 = int(code[:2])
    y2 = int(code[2:])
    c1 = 2000 + y1 if y1 < 80 else 1900 + y1
    return f"{c1}-{code[2:]}"


def get_or_create_season(conn, league_code, season_code):
    """시즌 ID를 가져오거나 생성."""
    league = conn.execute("SELECT id FROM leagues WHERE code = ?", (league_code,)).fetchone()
    if not league:
        print(f"  ⚠ 리그 코드 '{league_code}' 없음, 건너뜀")
        return None
    league_id = league[0]
    row = conn.execute(
        "SELECT id FROM seasons WHERE league_id = ? AND season_code = ?",
        (league_id, season_code),
    ).fetchone()
    if row:
        return row[0]
    conn.execute(
        "INSERT INTO seasons (league_id, season_code, season_label) VALUES (?, ?, ?)",
        (league_id, season_code, season_label(season_code)),
    )
    conn.commit()
    return conn.execute(
        "SELECT id FROM seasons WHERE league_id = ? AND season_code = ?",
        (league_id, season_code),
    ).fetchone()[0]


def parse_filename(filepath):
    """파일명에서 리그, 시즌, 타입 파싱."""
    name = os.path.basename(filepath).replace(".csv", "")

    # match_url: PL2122_match_url
    if "_match_url" in name:
        m = re.match(r"([A-Za-z]+\d?)(\d{4})_match_url", name)
        if not m:
            m = re.match(r"([A-Za-z]+\d?)_(\d{4})_match_url", name)
        if m:
            return LEAGUE_MAP.get(m.group(1), m.group(1)), m.group(2), "match_url", None
        return None, None, None, None

    # add_match: PL2122_add_match
    if "_add_match" in name:
        m = re.match(r"([A-Za-z]+\d?)(\d{4})_add_match", name)
        if not m:
            m = re.match(r"([A-Za-z]+\d?)_(\d{4})_add_match", name)
        if m:
            return LEAGUE_MAP.get(m.group(1), m.group(1)), m.group(2), "add_match", None
        return None, None, None, None

    # match: PL2122_match, LIGUE1_1516_match
    if "_match" in name:
        m = re.match(r"([A-Za-z]+\d?)(\d{4})_match$", name)
        if not m:
            m = re.match(r"([A-Za-z]+\d?)_(\d{4})_match$", name)
        if m:
            return LEAGUE_MAP.get(m.group(1), m.group(1)), m.group(2), "match", None
        return None, None, None, None

    # league_table: PL1920_league_table
    if "_league_table" in name:
        m = re.match(r"([A-Za-z]+\d?)(\d{4})_league_table", name)
        if m:
            return LEAGUE_MAP.get(m.group(1), m.group(1)), m.group(2), "team", None
        return None, None, None, None

    # team: PL2425_team
    if "_team" in name:
        m = re.match(r"([A-Za-z]+\d?)(\d{4})_team", name)
        if m:
            return LEAGUE_MAP.get(m.group(1), m.group(1)), m.group(2), "team", None
        return None, None, None, None

    # player categorized: PL_player_offensive_1920
    m = re.match(r"([A-Za-z]+\d?)_player_(summary|defensive|offensive|passing)_(\d{4})", name)
    if m:
        return LEAGUE_MAP.get(m.group(1), m.group(1)), m.group(3), "player", m.group(2)

    # player full: PL_player_1516, Bundesliga_player_2223
    m = re.match(r"([A-Za-z]+\d?)_player_(\d{4})", name)
    if m:
        return LEAGUE_MAP.get(m.group(1), m.group(1)), m.group(2), "player", "full"

    return None, None, None, None


def migrate_match_urls(conn, filepath, season_id):
    """match_url CSV를 DB에 삽입."""
    df = pd.read_csv(filepath)
    # URL 컬럼 찾기 (보통 '0' 또는 unnamed)
    url_col = None
    for c in df.columns:
        if df[c].astype(str).str.startswith("http").any():
            url_col = c
            break
    if url_col is None:
        print(f"  ⚠ URL 컬럼을 찾을 수 없음: {filepath}")
        return 0
    urls = df[url_col].dropna().unique()
    count = 0
    for url in urls:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO match_urls (season_id, url, source_file) VALUES (?, ?, ?)",
                (season_id, str(url), os.path.basename(filepath)),
            )
            count += 1
        except Exception:
            pass
    conn.commit()
    return count


def migrate_matches(conn, filepath, season_id, is_add=False):
    """매치 결과 CSV를 DB에 삽입."""
    df = pd.read_csv(filepath)
    # unnamed index 컬럼 제거
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    count = 0
    for _, row in df.iterrows():
        try:
            vals = {MATCH_COL_MAP.get(c, c): str(row[c]) if pd.notna(row[c]) else None for c in df.columns}
            vals["season_id"] = season_id
            vals["source_file"] = os.path.basename(filepath)
            vals["is_add_match"] = 1 if is_add else 0
            cols = list(vals.keys())
            placeholders = ", ".join(["?"] * len(cols))
            conn.execute(
                f"INSERT OR IGNORE INTO matches ({', '.join(cols)}) VALUES ({placeholders})",
                [vals[c] for c in cols],
            )
            count += 1
        except Exception as e:
            pass
    conn.commit()
    return count


def migrate_players(conn, filepath, season_id, stat_type="full"):
    """선수 통계 CSV를 DB에 삽입."""
    df = pd.read_csv(filepath)
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    count = 0
    for _, row in df.iterrows():
        try:
            vals = {"season_id": season_id, "stat_type": stat_type,
                    "source_file": os.path.basename(filepath)}
            for csv_col, db_col in PLAYER_COL_MAP.items():
                if csv_col in df.columns:
                    v = row[csv_col]
                    vals[db_col] = str(v) if pd.notna(v) else None
            cols = list(vals.keys())
            placeholders = ", ".join(["?"] * len(cols))
            conn.execute(
                f"INSERT OR IGNORE INTO player_stats ({', '.join(cols)}) VALUES ({placeholders})",
                [vals[c] for c in cols],
            )
            count += 1
        except Exception:
            pass
    conn.commit()
    return count


def migrate_teams(conn, filepath, season_id):
    """팀 시즌 통계 CSV를 DB에 삽입."""
    df = pd.read_csv(filepath)
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    count = 0
    for _, row in df.iterrows():
        try:
            vals = {"season_id": season_id, "source_file": os.path.basename(filepath)}
            for csv_col, db_col in TEAM_COL_MAP.items():
                if csv_col in df.columns:
                    v = row[csv_col]
                    vals[db_col] = str(v) if pd.notna(v) else None
            cols = list(vals.keys())
            placeholders = ", ".join(["?"] * len(cols))
            conn.execute(
                f"INSERT OR IGNORE INTO team_season_stats ({', '.join(cols)}) VALUES ({placeholders})",
                [vals[c] for c in cols],
            )
            count += 1
        except Exception:
            pass
    conn.commit()
    return count


def main():
    init_db()
    conn = get_connection()

    # CSV 파일 수집
    csv_dirs = [
        os.path.join(ROOT, "league_match_data"),
        os.path.join(ROOT, "player_data"),
        os.path.join(ROOT, "team_data"),
        os.path.join(ROOT, "2223_player_statistics"),
        ROOT,
    ]
    csv_files = []
    for d in csv_dirs:
        if os.path.isdir(d):
            csv_files.extend(glob.glob(os.path.join(d, "*.csv")))

    # 중복 제거
    csv_files = list(set(csv_files))

    totals = {"match_url": 0, "match": 0, "player": 0, "team": 0}

    for fpath in sorted(csv_files):
        league, season, dtype, sub = parse_filename(fpath)
        if not league or not season or not dtype:
            continue

        season_id = get_or_create_season(conn, league, season)
        if not season_id:
            continue

        relpath = os.path.relpath(fpath, ROOT)
        if dtype == "match_url":
            n = migrate_match_urls(conn, fpath, season_id)
            totals["match_url"] += n
            print(f"  [match_url] {relpath}: {n}건")
        elif dtype == "match":
            n = migrate_matches(conn, fpath, season_id, is_add=False)
            totals["match"] += n
            print(f"  [match]     {relpath}: {n}건")
        elif dtype == "add_match":
            n = migrate_matches(conn, fpath, season_id, is_add=True)
            totals["match"] += n
            print(f"  [add_match] {relpath}: {n}건")
        elif dtype == "player":
            n = migrate_players(conn, fpath, season_id, stat_type=sub or "full")
            totals["player"] += n
            print(f"  [player/{sub}] {relpath}: {n}건")
        elif dtype == "team":
            n = migrate_teams(conn, fpath, season_id)
            totals["team"] += n
            print(f"  [team]      {relpath}: {n}건")

    conn.close()
    print("\n=== 마이그레이션 완료 ===")
    for k, v in totals.items():
        print(f"  {k}: {v}건")


if __name__ == "__main__":
    main()
