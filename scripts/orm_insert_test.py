# Inserts an Empleado using the app's ORM to verify model and DB schema are aligned
import sys
sys.path.insert(0, r"C:\Users\jlchz\OneDrive\Desktop\fincas")
from app_simple import app, db, Empleado

with app.app_context():
    try:
        e = Empleado(
            nombre='ORMTest',
            apellido='User',
            cargo='Tester',
            telefono='123',
            email='orm@test',
            fecha_contratacion='2020-01-01',
            finca_id=1,
            nacionalidad='TestLand',
            condiciones_enfermedades='None',
            referencia_personal='Ref',
            foto_empleado='emp.png',
            foto_cedula='ced.png',
            fecha_ingreso='2020-01-02'
        )
        db.session.add(e)
        db.session.commit()
        print('ORM INSERT OK id=', e.id)
    except Exception as exc:
        import traceback
        print('ORM INSERT ERROR:', type(exc).__name__, exc)
        print(traceback.format_exc())
        db.session.rollback()
