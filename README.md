# Sistema de Gestión Ganadera

Una aplicación web completa desarrollada en Python con Flask para la gestión integral de fincas ganaderas.

## 🐄 Características Principales

### Gestión de Animales
- ✅ Registro completo de animales (vacas, cochinos, caballos, etc.)
- ✅ Seguimiento de peso, raza y estado
- ✅ Asignación a potreros específicos
- ✅ Historial de cada animal

### Gestión de Potreros
- ✅ Creación y administración de potreros
- ✅ Control de capacidad y área
- ✅ Definición de funciones específicas
- ✅ Seguimiento de animales por potrero

### Control de Vacunas
- ✅ Registro de vacunas aplicadas
- ✅ Alertas de próximas vacunas
- ✅ Historial médico por animal
- ✅ Control de fechas de vencimiento

### Gestión de Empleados
- ✅ Registro completo de personal
- ✅ Control de cargos y salarios
- ✅ Seguimiento de antigüedad
- ✅ Información de contacto

### Registro de Producción
- ✅ Seguimiento de producción de leche
- ✅ Control de producción de carne
- ✅ Registro de huevos y otros productos
- ✅ Análisis de calidad

### Inventario
- ✅ Control de alimentos y medicinas
- ✅ Gestión de equipos y herramientas
- ✅ Alertas de productos por vencer
- ✅ Valoración del inventario

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   # Si tienes git instalado
   git clone <url-del-repositorio>
   
   # O descargar el archivo ZIP y extraerlo
   ```

2. **Navegar al directorio del proyecto**
   ```bash
   cd sistema-gestion-ganadera
   ```

3. **Crear un entorno virtual (recomendado)**
   ```bash
   # En Windows
   python -m venv venv
   venv\Scripts\activate
   
   # En macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

5. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

6. **Abrir en el navegador**
   ```
   http://localhost:5000
   ```

## 👤 Acceso Inicial

### Credenciales por Defecto
- **Usuario:** admin
- **Contraseña:** admin123

⚠️ **Importante:** Cambia estas credenciales después del primer acceso por seguridad.

## 📊 Funcionalidades Detalladas

### Dashboard Principal
- Estadísticas en tiempo real
- Gráficos de distribución de animales
- Actividad reciente
- Acciones rápidas

### Gestión de Animales
- **Tipos soportados:** Vacas, cochinos, caballos, ovejas, cabras, pollos, pavos
- **Información registrada:** ID, raza, fecha nacimiento, peso, estado
- **Funcionalidades:** Crear, editar, ver detalles, asignar potreros

### Control de Potreros
- **Información:** Nombre, área, capacidad, función
- **Estados:** Disponible, ocupado, mantenimiento
- **Funciones comunes:** Cría, engorde, lechería, reproducción

### Sistema de Vacunas
- **Tipos comunes:** Triple viral, fiebre aftosa, brucelosis, carbunco
- **Alertas automáticas:** Productos próximos a vencer
- **Seguimiento:** Fechas de aplicación y próximas dosis

### Gestión de Personal
- **Cargos:** Veterinario, vaquero, porquero, administrador, etc.
- **Información:** Cédula, contacto, dirección, salario
- **Control:** Estado activo/inactivo, antigüedad

### Producción
- **Tipos:** Leche, carne, huevos, lana, miel
- **Control:** Cantidad, calidad, fechas
- **Análisis:** Resúmenes y estadísticas

### Inventario
- **Categorías:** Alimentos, medicinas, equipos, semillas
- **Control:** Cantidad, precio, vencimiento
- **Alertas:** Productos por vencer, stock bajo

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3.8+, Flask 2.3.3
- **Base de Datos:** SQLite (incluida)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Iconos:** Font Awesome 6
- **Gráficos:** Chart.js

## 📁 Estructura del Proyecto

```
sistema-gestion-ganadera/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias
├── README.md             # Este archivo
├── templates/            # Plantillas HTML
│   ├── base.html         # Plantilla base
│   ├── login.html        # Página de login
│   ├── index.html        # Dashboard
│   ├── animales.html     # Lista de animales
│   ├── nuevo_animal.html # Formulario nuevo animal
│   ├── potreros.html     # Lista de potreros
│   ├── nuevo_potrero.html # Formulario nuevo potrero
│   ├── vacunas.html      # Lista de vacunas
│   ├── nueva_vacuna.html # Formulario nueva vacuna
│   ├── empleados.html    # Lista de empleados
│   ├── nuevo_empleado.html # Formulario nuevo empleado
│   ├── produccion.html   # Lista de producción
│   ├── nueva_produccion.html # Formulario nueva producción
│   ├── inventario.html   # Lista de inventario
│   └── nuevo_inventario.html # Formulario nuevo inventario
└── finca_ganadera.db     # Base de datos (se crea automáticamente)
```

## 🔧 Configuración Avanzada

### Cambiar Base de Datos
Para usar MySQL o PostgreSQL en lugar de SQLite:

1. Instalar el driver correspondiente:
   ```bash
   # Para MySQL
   pip install mysqlclient
   
   # Para PostgreSQL
   pip install psycopg2-binary
   ```

2. Modificar la configuración en `app.py`:
   ```python
   # Para MySQL
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://usuario:contraseña@localhost/nombre_db'
   
   # Para PostgreSQL
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:contraseña@localhost/nombre_db'
   ```

### Configurar Variables de Entorno
Crear un archivo `.env` en la raíz del proyecto:
```env
SECRET_KEY=tu_clave_secreta_muy_segura
DATABASE_URL=sqlite:///finca_ganadera.db
FLASK_ENV=development
```

## 📈 Uso Recomendado

### Flujo de Trabajo Típico

1. **Configuración inicial:**
   - Crear potreros
   - Registrar empleados
   - Configurar inventario básico

2. **Registro de animales:**
   - Agregar animales existentes
   - Asignar a potreros
   - Registrar información básica

3. **Control sanitario:**
   - Programar vacunas
   - Registrar aplicaciones
   - Seguir calendario de vacunación

4. **Seguimiento diario:**
   - Registrar producción
   - Actualizar inventario
   - Monitorear estado de animales

5. **Análisis y reportes:**
   - Revisar dashboard
   - Analizar estadísticas
   - Tomar decisiones basadas en datos

## 🔒 Seguridad

### Recomendaciones
- Cambiar credenciales por defecto
- Usar HTTPS en producción
- Realizar respaldos regulares de la base de datos
- Mantener el sistema actualizado

### Respaldo de Datos
```bash
# Respaldo de SQLite
cp finca_ganadera.db finca_ganadera_backup_$(date +%Y%m%d).db
```

## 🐛 Solución de Problemas

### Error: "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Error: "Database is locked"
- Cerrar otras instancias de la aplicación
- Verificar permisos de escritura en el directorio

### Error: "Port already in use"
```bash
# Cambiar puerto en app.py
app.run(debug=True, port=5001)
```

## 📞 Soporte

Para reportar problemas o solicitar nuevas funcionalidades:
- Crear un issue en el repositorio
- Incluir información del sistema operativo
- Describir el problema detalladamente

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crear una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abrir un Pull Request

---

**Desarrollado con ❤️ para la gestión ganadera eficiente** 