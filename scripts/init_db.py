#!/usr/bin/env python
"""DB 초기화 스크립트."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db.database import init_db

if __name__ == "__main__":
    init_db()
