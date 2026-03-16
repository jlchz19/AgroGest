import sqlite3
from datetime import date

DB_PATH = r"C:\Users\jlchz\OneDrive\Desktop\fincas\finca_ganadera.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
try:
    cur.execute("""
    INSERT INTO empleado
      (nombre, apellido, cargo, telefono, email, fecha_contratacion, finca_id,
       nacionalidad, condiciones_enfermedades, referencia_personal,
       foto_empleado, foto_cedula, fecha_ingreso)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        'TestNombre', 'TestApellido', 'PruebaCargo', '000', 'test@example.com',
        date.today().isoformat(), 1,
        'TestNacionalidad', 'Ninguna', 'Referencia', 'foto_emp.png', 'foto_cedula.png', date.today().isoformat()
    ))
    conn.commit()
    print('INSERT OK, lastrowid=', cur.lastrowid)
except Exception as e:
    print('INSERT ERROR:', type(e).__name__, e)
    # Also print PRAGMA table_info for debugging
    try:
        for row in cur.execute("PRAGMA table_info('empleado')"):
            print(row)
    except Exception as e2:
        print('PRAGMA ERROR:', e2)
finally:
    conn.close()
