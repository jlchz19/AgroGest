#!/usr/bin/env python3
"""
Script para eliminar todos los usuarios excepto los administradores
"""

from app_simple import app, db, Usuario

def eliminar_usuarios_no_admin():
    with app.app_context():
        # Ver usuarios actuales
        usuarios = Usuario.query.all()
        print('=== USUARIOS ACTUALES ===')
        for u in usuarios:
            print(f'ID: {u.id}, Username: {u.username}, Rol: {u.rol}, Email: {u.email}')
        
        # Contar usuarios no admin
        usuarios_no_admin = Usuario.query.filter(Usuario.rol != 'admin').all()
        print(f'\n=== USUARIOS A ELIMINAR (NO ADMIN) ===')
        print(f'Total: {len(usuarios_no_admin)} usuarios')
        
        if not usuarios_no_admin:
            print('No hay usuarios no-admin para eliminar.')
            return
        
        for u in usuarios_no_admin:
            print(f'  - ID: {u.id}, Username: {u.username}, Email: {u.email}')
        
        # Confirmación
        confirmacion = input('\n¿Estás seguro de eliminar estos usuarios? (s/N): ')
        if confirmacion.lower() != 's':
            print('Operación cancelada.')
            return
        
        # Eliminar usuarios no admin
        try:
            eliminados = 0
            for u in usuarios_no_admin:
                print(f'Eliminando usuario: {u.username}...')
                
                # Primero eliminar registros asociados al usuario
                from app_simple import AlertaPersonalizada, PasswordResetToken
                
                # Eliminar alertas personalizadas
                alertas = AlertaPersonalizada.query.filter_by(usuario_id=u.id).all()
                for alerta in alertas:
                    db.session.delete(alerta)
                    print(f'  - Eliminando alerta asociada')
                
                # Eliminar tokens de reseteo de contraseña
                tokens = PasswordResetToken.query.filter_by(usuario_id=u.id).all()
                for token in tokens:
                    db.session.delete(token)
                    print(f'  - Eliminando token de reseteo')
                
                # Eliminar el usuario
                db.session.delete(u)
                eliminados += 1
            
            db.session.commit()
            print(f'\n✅ Se eliminaron {eliminados} usuarios correctamente.')
            
            # Ver usuarios restantes
            usuarios_restantes = Usuario.query.all()
            print('\n=== USUARIOS RESTANTES ===')
            for u in usuarios_restantes:
                print(f'ID: {u.id}, Username: {u.username}, Rol: {u.rol}, Email: {u.email}')
                
        except Exception as e:
            db.session.rollback()
            print(f'\n❌ Error al eliminar usuarios: {e}')

if __name__ == '__main__':
    eliminar_usuarios_no_admin()
