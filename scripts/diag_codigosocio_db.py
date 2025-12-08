from pathlib import Path
import sqlite3
import sys
from pathlib import Path as P

# Ensure project root on path
PROJECT_ROOT = P(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from clubelmeta import settings

print('Using DB file:', settings.DATABASES['default']['NAME'])

db = settings.DATABASES['default']['NAME']
conn = sqlite3.connect(str(db))
cur = conn.cursor()
try:
    cur.execute("PRAGMA table_info(reservas_codigosocio);")
    rows = cur.fetchall()
    if not rows:
        print('Table reservas_codigosocio not found or empty.')
    else:
        print('Columns in reservas_codigosocio:')
        for r in rows:
            print(r)
except Exception as e:
    print('Error querying table:', e)
finally:
    conn.close()
