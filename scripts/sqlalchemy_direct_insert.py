import sqlalchemy as sa
from sqlalchemy import text
from datetime import date

DB_URI = 'sqlite:///finca_ganadera.db'
print('SQLAlchemy version:', sa.__version__)
engine = sa.create_engine(DB_URI)
print('Engine URL:', engine.url)

# List PRAGMA table_info
with engine.connect() as conn:
    try:
        rows = conn.execute(text("PRAGMA table_info('empleado')")).fetchall()
        print('PRAGMA table_info rows:', len(rows))
        for r in rows:
            print(r)
    except Exception as e:
        print('PRAGMA error:', e)

# Try insert using core
ins_sql = text('''
INSERT INTO empleado
  (nombre, apellido, cargo, telefono, email, fecha_contratacion, finca_id,
   nacionalidad, condiciones_enfermedades, referencia_personal,
   foto_empleado, foto_cedula, fecha_ingreso)
VALUES (:nombre, :apellido, :cargo, :telefono, :email, :fecha_contratacion, :finca_id,
        :nacionalidad, :condiciones_enfermedades, :referencia_personal,
        :foto_empleado, :foto_cedula, :fecha_ingreso)
''')
params = {
    'nombre': 'SA_Test',
    'apellido': 'SA_Last',
    'cargo': 'Dev',
    'telefono': '111',
    'email': 'sa@test',
    'fecha_contratacion': date.today().isoformat(),
    'finca_id': 1,
    'nacionalidad': 'SA',
    'condiciones_enfermedades': 'None',
    'referencia_personal': 'Ref',
    'foto_empleado': 'emp.png',
    'foto_cedula': 'ced.png',
    'fecha_ingreso': date.today().isoformat(),
}

with engine.begin() as conn:
    try:
        res = conn.execute(ins_sql, params)
        print('Insert OK, rowcount=', getattr(res, 'rowcount', None))
    except Exception as e:
        print('Insert ERROR:', type(e).__name__, e)
        # print last executed if available
        try:
            print('LastExecuted:', getattr(e, 'statement', 'N/A'))
        except Exception:
            pass
