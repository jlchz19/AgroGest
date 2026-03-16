import sqlite3, os
DB = os.path.abspath('finca_ganadera.db')
print('DB path:', DB)
if not os.path.exists(DB):
    print('DB not found')
else:
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("PRAGMA table_info('empleado')")
    rows = cur.fetchall()
    print('empleado columns:')
    for r in rows:
        print(r)
    con.close()
