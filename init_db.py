#!/usr/bin/env python3
"""schema.sql を適用して SQLite データベースを初期化する。

使い方:
    python3 init_db.py [db_path]

db_path 省略時は data/catalog.db。既存 DB にはスキーマを再適用するだけで、
データは消さない（CREATE TABLE IF NOT EXISTS のため冪等）。
"""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_DB = ROOT / "data" / "catalog.db"


def main() -> None:
    db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DB
    db_path.parent.mkdir(parents=True, exist_ok=True)

    schema = (ROOT / "schema.sql").read_text(encoding="utf-8")
    con = sqlite3.connect(db_path)
    try:
        con.executescript(schema)
        con.commit()
        tables = [
            r[0]
            for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
    finally:
        con.close()

    print(f"initialized: {db_path}")
    print(f"tables: {', '.join(tables)}")


if __name__ == "__main__":
    main()
