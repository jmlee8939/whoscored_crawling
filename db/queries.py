"""데이터 조회 쿼리 함수 모음."""

from typing import Optional

import pandas as pd

from db.database import get_connection


def get_leagues() -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql_query("SELECT * FROM leagues ORDER BY code", conn)
    finally:
        conn.close()


def get_seasons(league_code: Optional[str] = None) -> pd.DataFrame:
    conn = get_connection()
    try:
        if league_code:
            return pd.read_sql_query(
                """SELECT s.*, l.code AS league_code, l.name AS league_name
                   FROM seasons s JOIN leagues l ON s.league_id = l.id
                   WHERE l.code = ? ORDER BY s.season_code DESC""",
                conn, params=(league_code,),
            )
        return pd.read_sql_query(
            """SELECT s.*, l.code AS league_code, l.name AS league_name
               FROM seasons s JOIN leagues l ON s.league_id = l.id
               ORDER BY l.code, s.season_code DESC""",
            conn,
        )
    finally:
        conn.close()


def get_matches(
    season_id: Optional[int] = None,
    team_name: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple:
    conn = get_connection()
    try:
        clauses, params = [], []
        if season_id:
            clauses.append("m.season_id = ?"); params.append(season_id)
        if team_name:
            clauses.append("(m.home_team LIKE ? OR m.away_team LIKE ?)")
            params.extend([f"%{team_name}%", f"%{team_name}%"])
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        total = conn.execute(f"SELECT COUNT(*) FROM matches m {where}", params).fetchone()[0]
        df = pd.read_sql_query(
            f"""SELECT m.*, s.season_code, s.season_label, l.code AS league_code
                FROM matches m JOIN seasons s ON m.season_id = s.id
                JOIN leagues l ON s.league_id = l.id {where}
                ORDER BY m.date DESC LIMIT ? OFFSET ?""",
            conn, params=params + [limit, offset],
        )
        return df, total
    finally:
        conn.close()


def get_players(
    season_id: Optional[int] = None,
    team_name: Optional[str] = None,
    position: Optional[str] = None,
    player_name: Optional[str] = None,
    stat_type: str = "full",
    sort_by: str = "rating",
    sort_order: str = "DESC",
    limit: int = 100,
    offset: int = 0,
) -> tuple:
    conn = get_connection()
    try:
        clauses, params = [], []
        if season_id:
            clauses.append("p.season_id = ?"); params.append(season_id)
        if team_name:
            clauses.append("p.team_name LIKE ?"); params.append(f"%{team_name}%")
        if position:
            clauses.append("p.position LIKE ?"); params.append(f"%{position}%")
        if player_name:
            clauses.append("p.player_name LIKE ?"); params.append(f"%{player_name}%")
        if stat_type:
            clauses.append("p.stat_type = ?"); params.append(stat_type)
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

        total = conn.execute(f"SELECT COUNT(*) FROM player_stats p {where}", params).fetchone()[0]

        allowed = {
            "rating", "goals", "assists", "apps", "mins", "player_name",
            "team_name", "age", "position", "spg", "tackles", "key_p",
            "dribble", "ps_pct",
        }
        if sort_by not in allowed:
            sort_by = "rating"
        if sort_order not in ("ASC", "DESC"):
            sort_order = "DESC"

        df = pd.read_sql_query(
            f"""SELECT p.*, s.season_code, s.season_label, l.code AS league_code
                FROM player_stats p JOIN seasons s ON p.season_id = s.id
                JOIN leagues l ON s.league_id = l.id {where}
                ORDER BY CAST(p.{sort_by} AS REAL) {sort_order}
                LIMIT ? OFFSET ?""",
            conn, params=params + [limit, offset],
        )
        return df, total
    finally:
        conn.close()


def get_teams(
    season_id: Optional[int] = None,
    sort_by: str = "points",
    sort_order: str = "DESC",
) -> pd.DataFrame:
    conn = get_connection()
    try:
        clauses, params = [], []
        if season_id:
            clauses.append("t.season_id = ?"); params.append(season_id)
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

        allowed = {
            "points", "won", "lost", "drawn", "goals_for", "goals_against",
            "goal_diff", "team_name", "rating", "shots_pg", "tackles_pg",
            "poss_pct", "pass_pct",
        }
        if sort_by not in allowed:
            sort_by = "points"
        if sort_order not in ("ASC", "DESC"):
            sort_order = "DESC"

        return pd.read_sql_query(
            f"""SELECT t.*, s.season_code, s.season_label, l.code AS league_code
                FROM team_season_stats t JOIN seasons s ON t.season_id = s.id
                JOIN leagues l ON s.league_id = l.id {where}
                ORDER BY CAST(t.{sort_by} AS REAL) {sort_order}""",
            conn, params=params,
        )
    finally:
        conn.close()


def get_crawl_jobs(limit: int = 20) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql_query(
            "SELECT * FROM crawl_jobs ORDER BY created_at DESC LIMIT ?",
            conn, params=(limit,),
        )
    finally:
        conn.close()


def get_data_summary() -> dict:
    conn = get_connection()
    try:
        s = {}
        s["total_matches"] = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
        s["total_players"] = conn.execute("SELECT COUNT(*) FROM player_stats").fetchone()[0]
        s["total_teams"] = conn.execute("SELECT COUNT(*) FROM team_season_stats").fetchone()[0]
        s["total_seasons"] = conn.execute("SELECT COUNT(*) FROM seasons").fetchone()[0]
        s["total_leagues"] = conn.execute("SELECT COUNT(*) FROM leagues").fetchone()[0]
        s["league_seasons"] = pd.read_sql_query(
            """SELECT l.code, l.name, COUNT(s.id) AS season_count
               FROM leagues l LEFT JOIN seasons s ON l.id = s.league_id
               GROUP BY l.id ORDER BY l.code""",
            conn,
        )
        s["season_data"] = pd.read_sql_query(
            """SELECT l.code AS league_code, s.season_label,
                      (SELECT COUNT(*) FROM matches m WHERE m.season_id = s.id) AS match_count,
                      (SELECT COUNT(*) FROM player_stats p WHERE p.season_id = s.id) AS player_count,
                      (SELECT COUNT(*) FROM team_season_stats t WHERE t.season_id = s.id) AS team_count
               FROM seasons s JOIN leagues l ON s.league_id = l.id
               ORDER BY l.code, s.season_code DESC""",
            conn,
        )
        return s
    finally:
        conn.close()
