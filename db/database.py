"""SQLite 데이터베이스 스키마 정의 및 연결 관리."""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "whoscored.db")


def get_connection(db_path=None):
    """SQLite 연결을 반환합니다."""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path=None):
    """테이블 생성 + 리그 시드 데이터 삽입."""
    conn = get_connection(db_path)
    cur = conn.cursor()

    # ── leagues ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leagues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            region_number INTEGER NOT NULL,
            tournament_number INTEGER NOT NULL
        )
    """)

    # ── seasons ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS seasons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league_id INTEGER NOT NULL REFERENCES leagues(id),
            season_code TEXT NOT NULL,
            season_label TEXT NOT NULL,
            UNIQUE(league_id, season_code)
        )
    """)

    # ── matches ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season_id INTEGER NOT NULL REFERENCES seasons(id),
            match_url TEXT,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            date TEXT,
            kick_off TEXT,
            half_home_score TEXT,
            half_away_score TEXT,
            full_home_score TEXT,
            full_away_score TEXT,
            home_shot TEXT, away_shot TEXT,
            home_possession TEXT, away_possession TEXT,
            home_pass_success TEXT, away_pass_success TEXT,
            home_dribbles TEXT, away_dribbles TEXT,
            home_aerials_won TEXT, away_aerials_won TEXT,
            home_tackles TEXT, away_tackles TEXT,
            home_corners TEXT, away_corners TEXT,
            home_dispossessed TEXT, away_dispossessed TEXT,
            home_missing_player TEXT, away_missing_player TEXT,
            home_missing_player_rating TEXT, away_missing_player_rating TEXT,
            matchup_home_goals TEXT, matchup_away_goals TEXT,
            matchup_home_wins TEXT, matchup_draw TEXT, matchup_away_wins TEXT,
            home_total_att TEXT, away_total_att TEXT,
            home_open_att TEXT, away_open_att TEXT,
            home_set_att TEXT, away_set_att TEXT,
            home_counter_att TEXT, away_counter_att TEXT,
            home_pk_att TEXT, away_pk_att TEXT,
            home_own_att TEXT, away_own_att TEXT,
            home_total_passes TEXT, away_total_passes TEXT,
            home_crosses_passes TEXT, away_crosses_passes TEXT,
            home_long_balls TEXT, away_long_balls TEXT,
            home_short_passes TEXT, away_short_passes TEXT,
            source_file TEXT,
            is_add_match INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(season_id, home_team, away_team, date)
        )
    """)

    # ── player_stats ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season_id INTEGER NOT NULL REFERENCES seasons(id),
            player_name TEXT NOT NULL,
            team_number TEXT,
            team_name TEXT NOT NULL,
            age TEXT,
            position TEXT,
            apps TEXT, mins TEXT, goals TEXT, assists TEXT,
            yel TEXT, red TEXT, spg TEXT, ps_pct TEXT,
            aerials_won TEXT, mom TEXT, rating TEXT,
            key_p TEXT, avg_p TEXT, crosses TEXT, long_b TEXT, thr_b TEXT,
            tackles TEXT, inter TEXT, fouls TEXT, offsides TEXT,
            clear TEXT, drb TEXT, blocks TEXT, own_g TEXT,
            dribble TEXT, fouled TEXT, off TEXT, disp TEXT, uns_tch TEXT,
            sub TEXT,
            stat_type TEXT DEFAULT 'full',
            source_file TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(season_id, player_name, team_name, stat_type)
        )
    """)

    # ── team_season_stats ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS team_season_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season_id INTEGER NOT NULL REFERENCES seasons(id),
            team_name TEXT NOT NULL,
            played TEXT, won TEXT, drawn TEXT, lost TEXT,
            goals_for TEXT, goals_against TEXT, goal_diff TEXT, points TEXT,
            goals TEXT, shots_pg TEXT, yellow TEXT, red TEXT,
            poss_pct TEXT, pass_pct TEXT, aerials_won TEXT, rating TEXT,
            shoted_pg TEXT, tackles_pg TEXT, intercept_pg TEXT,
            fouls_pg TEXT, offsides_pg TEXT,
            shots_ot_pg TEXT, dribbles_pg TEXT, fouled_pg TEXT,
            source_file TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(season_id, team_name)
        )
    """)

    # ── match_urls ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS match_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season_id INTEGER NOT NULL REFERENCES seasons(id),
            url TEXT NOT NULL,
            crawled INTEGER DEFAULT 0,
            source_file TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(season_id, url)
        )
    """)

    # ── crawl_jobs ──
    cur.execute("""
        CREATE TABLE IF NOT EXISTS crawl_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_type TEXT NOT NULL,
            league_code TEXT NOT NULL,
            season_code TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            total_items INTEGER DEFAULT 0,
            completed_items INTEGER DEFAULT 0,
            error_items INTEGER DEFAULT 0,
            error_list TEXT,
            started_at TEXT,
            completed_at TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── 리그 시드 데이터 ──
    leagues = [
        ("PL", "Premier League", 252, 2),
        ("LIGA", "La Liga", 206, 4),
        ("SA", "Serie A", 108, 5),
        ("BL", "Bundesliga", 81, 3),
        ("LIGUE1", "Ligue 1", 74, 22),
    ]
    for code, name, region, tournament in leagues:
        cur.execute(
            "INSERT OR IGNORE INTO leagues (code, name, region_number, tournament_number) VALUES (?, ?, ?, ?)",
            (code, name, region, tournament),
        )

    conn.commit()
    conn.close()
    print(f"DB 초기화 완료: {db_path or DB_PATH}")
