import sys
from datetime import date
sys.path.insert(0, r"C:\Users\jlchz\OneDrive\Desktop\fincas")
from app_simple import app, db, Empleado

with app.app_context():
    try:
        e = Empleado(
            cedula='TESTREF123',
            nombre='RefTest',
            apellido='Apellido',
            telefono='0000',
            direccion='Calle Test',
            cargo='Especialista XYZ',
            fecha_contratacion=date(2020,1,1),
            salario=500.0,
            finca_id=1,
            nacionalidad='Venezolano',
            condiciones_enfermedades='Ninguna',
            referencia_personal='Juan Perez - 0414-xxx',
            referencia_file='static/uploads/referencias/sample_ref.pdf',
            alergico_medicamento=True,
            alergias_medicamento='Penicilina',
            fecha_ingreso=date(2020,1,2)
        )
        db.session.add(e)
        db.session.commit()
        print('ORM Insert OK id=', e.id)
    except Exception as exc:
        import traceback
        print('ORM Insert ERROR:', type(exc).__name__, exc)
        print(traceback.format_exc())
        db.session.rollback()
