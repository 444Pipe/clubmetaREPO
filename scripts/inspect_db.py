import sqlite3
import sys

path = 'db.sqlite3'
try:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [r[0] for r in cur.fetchall()]
    print('TABLES:', tables)
    for t in tables:
        try:
            cur.execute(f'SELECT COUNT(*) FROM "{t}"')
            cnt = cur.fetchone()[0]
        except Exception as e:
            cnt = f'ERROR: {e}'
        print(f'{t}: {cnt}')
    conn.close()
except Exception as e:
    print('ERROR_OPENING_DB:', e)
    sys.exit(1)
