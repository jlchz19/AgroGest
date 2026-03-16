import sqlite3
import os

DB = os.path.join(os.path.dirname(__file__), '..', 'finca_ganadera.db')
DB = os.path.abspath(DB)
print(f"Using DB: {DB}")
if not os.path.exists(DB):
    print("Database file not found.")
    raise SystemExit(1)

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("PRAGMA table_info('empleado')")
cols = cur.fetchall()
existing = [c[1] for c in cols]
print("Existing columns:")
for c in existing:
    print(" -", c)

needed = {
    'nacionalidad': 'TEXT',
    'condiciones_enfermedades': 'TEXT',
    'referencia_personal': 'TEXT',
    'foto_empleado': 'TEXT',
    'foto_cedula': 'TEXT',
    'fecha_ingreso': 'DATE'
}

for col, typ in needed.items():
    if col in existing:
        print(f"Column '{col}' already exists, skipping.")
        continue
    try:
        sql = f"ALTER TABLE empleado ADD COLUMN {col} {typ};"
        print("Executing:", sql)
        cur.execute(sql)
        conn.commit()
        print(f"Added column: {col}")
    except Exception as e:
        print(f"Failed to add column {col}: {e}")

cur.execute("PRAGMA table_info('empleado')")
cols2 = cur.fetchall()
print("Columns after change:")
for c in cols2:
    print(" -", c[1])

conn.close()
print("Done.")
