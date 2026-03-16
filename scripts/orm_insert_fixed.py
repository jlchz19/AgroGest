# Inserts an Empleado using the app's ORM with valid model fields
import sys
sys.path.insert(0, r"C:\Users\jlchz\OneDrive\Desktop\fincas")
from app_simple import app, db, Empleado

with app.app_context():
    try:
        e = Empleado(
            cedula='TEST123',
            nombre='ORMTest2',
            apellido='User',
            telefono='123',
            direccion='Calle Falsa 123',
            cargo='Tester',
            fecha_contratacion='2020-01-01',
            salario=1000.0,
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
