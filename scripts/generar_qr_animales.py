import os
import sys
import qrcode
from qrcode.constants import ERROR_CORRECT_L
import socket

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar configuración
from config import config

def generar_qr_para_animales():
    """Genera códigos QR para todos los animales activos en la finca actual."""
    try:
        # Importar después de agregar al path
        from app_simple import app, db, Animal, Finca
        
        # Crear directorio para los códigos QR si no existe
        os.makedirs('static/qr_codes', exist_ok=True)
        
        # Obtener la URL del servidor desde la configuración
        server_url = config['default'].SERVER_URL.rstrip('/')
        print(f"Usando la URL del servidor: {server_url}")
        
        # Obtener la finca actual
        finca = Finca.query.filter_by(nombre='Hacienda San José').first()
        
        if not finca:
            print("No se encontró la finca 'Hacienda San José'")
            return
        
        # Obtener todos los animales activos de la finca
        animales = Animal.query.filter_by(finca_id=finca.id, estado='activo').all()
        
        if not animales:
            print("No se encontraron animales activos en la finca")
            return
        
        print(f"Generando códigos QR para {len(animales)} animales...")
        
        for animal in animales:
            try:
                # Generar la URL del código QR
                url = f"{server_url}/animal/qr/{animal.id}"
                print(f"URL generada para {animal.identificacion}: {url}")
                
                # Crear el código QR
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(url)
                qr.make(fit=True)
                
                # Crear la imagen del código QR
                img = qr.make_image(fill_color="#007bff", back_color="white")
                
                # Guardar la imagen
                filename = f"qr_{animal.identificacion}.png".replace(" ", "_")
                filepath = os.path.join('static', 'qr_codes', filename)
                img.save(filepath)
                
                print(f"Código QR generado para {animal.identificacion}: {filepath}")
                
            except Exception as e:
                print(f"Error al generar código QR para {animal.identificacion}: {str(e)}")
        
        print("\n¡Proceso completado!")
        print(f"\nPara acceder a los códigos QR desde tu teléfono:")
        print(f"1. Asegúrate de que tu teléfono tenga acceso a la URL: {server_url}")
        print(f"2. Escanea el código QR con la cámara de tu teléfono")
        print(f"3. Si usas una IP local, asegúrate de que tu teléfono esté en la misma red")
        print(f"4. Si usas un dominio, asegúrate de que esté configurado correctamente")
        
    except Exception as e:
        print(f"Error general: {str(e)}")
        print("Asegúrate de que la aplicación Flask esté en ejecución")

if __name__ == "__main__":
    generar_qr_para_animales()
