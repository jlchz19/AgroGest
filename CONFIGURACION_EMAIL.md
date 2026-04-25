# Configuración de Email para AgroGest

## Problema Actual
El sistema de recuperación de contraseña muestra el error: "No se pudo enviar el correo de recuperación. Por favor, contacta al administrador."

## Solución Implementada (Temporal)
Cuando el email falla, el sistema ahora muestra el código de recuperación directamente en la pantalla y también lo imprime en la consola del servidor.

## Configuración Permanente (Recomendada)

### Paso 1: Habilitar Verificación en 2 Pasos en Google
1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Sección "Seguridad"
3. Activa "Verificación en dos pasos"

### Paso 2: Generar Contraseña de Aplicación
1. En la misma sección de seguridad, busca "Contraseñas de aplicaciones"
2. Haz clic en "Generar"
3. Selecciona "Otra (nombre personalizado)"
4. Escribe "AgroGest" como nombre
5. Google generará una contraseña de 16 caracteres (ej: abcd efgh ijkl mnop)
6. Copia esta contraseña (sin espacios)

### Paso 3: Actualizar Archivo .env
Edita el archivo `.env` y reemplaza `EMAIL_PASSWORD` con la contraseña de aplicación generada:

```env
FLASK_APP=app_simple.py

# Configuración de Email para notificaciones
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=abcd_efgh_ijkl_mnop  # Contraseña de aplicación de 16 caracteres
EMAIL_USE_TLS=True
```

### Paso 4: Reiniciar la Aplicación
Reinicia el servidor Flask para que cargue la nueva configuración.

## Verificación
Una vez configurado, puedes probar el sistema:
1. Ve a la página de login
2. Haz clic en "¿Olvidaste tu contraseña?"
3. Ingresa tu email
4. Deberías recibir un email con el código de 6 dígitos

## Notas Importantes
- **Nunca uses tu contraseña normal de Gmail** en el archivo .env
- **Usa siempre contraseñas de aplicación** para mayor seguridad
- Las contraseñas de aplicación pueden ser revocadas en cualquier momento desde tu cuenta de Google
- Mantén el archivo .env seguro y nunca lo subas a repositorios públicos

## Solución de Problemas Comunes

### Error: "Username and Password not accepted"
- Verifica que estás usando una contraseña de aplicación, no tu contraseña normal
- Asegúrate de que la verificación en 2 pasos está activada

### Error: "SMTP Authentication failed"
- Revisa que el email y contraseña sean correctos
- Verifica que no haya espacios extraños en la contraseña

### Error: "Connection timeout"
- Verifica tu conexión a internet
- Asegúrate de que el puerto 587 no esté bloqueado por tu firewall

## Contacto de Soporte
Si continúas teniendo problemas, contacta al administrador del sistema proporcionando:
- El error exacto que aparece
- Los logs de la consola del servidor
- Capturas de pantalla si es posible
