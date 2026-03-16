import sys, os
sys.path.insert(0, os.path.abspath('.'))
from app_simple import app
import sqlite3

uri = app.config.get('SQLALCHEMY_DATABASE_URI')
print('SQLALCHEMY_DATABASE_URI:', uri)
if uri and uri.startswith('sqlite:///'):
    path = uri.replace('sqlite:///', '')
    if path.startswith('/') and os.name == 'nt' and path[1].isalpha() and path[2:3]==':':
        path = path[1:]
    db_path = os.path.abspath(path)
else:
    db_path = os.path.abspath('finca_ganadera.db')
print('Resolved DB path:', db_path)
if os.path.exists(db_path):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("PRAGMA table_info('empleado')")
    rows = cur.fetchall()
    print('empleado columns (count):', len(rows))
    for r in rows:
        print(r)
    con.close()
else:
    print('DB file not found at', db_path)
