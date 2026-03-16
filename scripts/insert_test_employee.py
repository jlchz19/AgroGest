from app_simple import app, db, Empleado
from datetime import datetime

with app.app_context():
    emp = Empleado(
        cedula='TEST123456',
        nombre='Prueba',
        apellido='Automática',
        telefono='3000000000',
        direccion='Calle Test 123',
        cargo='Auxiliar',
        fecha_contratacion=datetime.utcnow().date(),
        salario=0.0,
        finca_id=1,
        nacionalidad='Colombiana',
        condiciones_enfermedades='Ninguna',
        referencia_personal='N/A',
        fecha_ingreso=datetime.utcnow().date()
    )
    db.session.add(emp)
    db.session.commit()
    print('Inserted empleado id=', emp.id)
