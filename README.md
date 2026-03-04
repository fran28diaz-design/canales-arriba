# 🎓 Plataforma Educativa de Inglés - English Academy

Una plataforma educativa completa construida con Flask para maestros de inglés y sus estudiantes.

## ✨ Características

### Para Maestros:
- ✅ Crear y gestionar tareas
- ✅ Subir materiales educativos (PDF, imágenes, documentos)
- ✅ Agregar videos (links de YouTube o Google Drive)
- ✅ Ver entregas de estudiantes
- ✅ Calificar tareas y dejar comentarios
- ✅ Dashboard con estadísticas

### Para Estudiantes:
- ✅ Ver tareas pendientes y completadas
- ✅ Descargar materiales de estudio
- ✅ Ver videos educativos
- ✅ Entregar tareas
- ✅ Ver calificaciones y comentarios
- ✅ Perfil editable

### General:
- ✅ Sistema de autenticación seguro
- ✅ Roles de usuario (maestro/estudiante)
- ✅ Base de datos SQLite
- ✅ Diseño responsive
- ✅ Interfaz intuitiva

## 🚀 Instalación Local

### Requisitos:
- Python 3.8+
- pip
- Git

### Pasos:

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/english-academy.git
cd english-academy
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
```

3. **Activar entorno virtual:**

En macOS/Linux:
```bash
source venv/bin/activate
```

En Windows:
```bash
venv\Scripts\activate
```

4. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

5. **Ejecutar la aplicación:**
```bash
python app.py
```

6. **Acceder a la aplicación:**
```
http://localhost:5000
```

## 📝 Primeros Pasos

1. **Registrarse:**
   - Abre `http://localhost:5000/register`
   - Selecciona "Maestro/a" para crear una cuenta de maestro
   - O selecciona "Estudiante" para crear una cuenta de estudiante

2. **Login:**
   - Inicia sesión con tu usuario y contraseña

3. **Como Maestro:**
   - Ve a "Subir Material" para compartir contenido
   - Ve a "Nueva Tarea" para crear tareas
   - En "Dashboard" verás todas tus tareas y entregas

4. **Como Estudiante:**
   - Verás todas las tareas disponibles en tu dashboard
   - Descarga los materiales de estudio
   - Haz clic en una tarea para entregarla

## 🌐 Desplegar en Render

### Paso 1: Preparar el repositorio en GitHub

1. **Crear un repositorio en GitHub:**
   - Ve a https://github.com/new
   - Nombre: `english-academy`
   - Descripción: "Plataforma educativa de inglés"
   - Haz el repositorio público

2. **Subir el código:**
```bash
cd /Users/a0330/Desktop/Ingles

# Inicializar git
git init

# Agregar los archivos
git add .

# Primer commit
git commit -m "Initial commit: English Academy platform"

# Agregar el repositorio remoto
git branch -M main
git remote add origin https://github.com/tu-usuario/english-academy.git

# Subir al repositorio
git push -u origin main
```

### Paso 2: Conectar con Render

1. **Crear cuenta en Render:**
   - Ve a https://render.com
   - Haz clic en "Sign up"
    - **Start Command:** `gunicorn app_simple:app`

2. **Crear nuevo servicio web:**
   - Click en "New +" → "Web Service"
   - Conecta tu repositorio de GitHub
   - Selecciona `english-academy`
   - Haz clic en "Connect"

3. **Configurar el servicio:**
   - **Name:** english-academy
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** Free (o paga si quieres mejor rendimiento)

4. **Variables de entorno:**
   - Haz clic en "Environment"
   - Agrega esta variable:
     - **Key:** `SECRET_KEY`
5. **Deploy:**
   - Haz clic en "Create Web Service"
   - Render comenzará el deploy automáticamente
   - Espera a que termine (5-10 minutos)

6. **Acceder a tu aplicación:**
   - Verás una URL como: `https://english-academy.onrender.com`
   - ¡Es tu aplicación en internet! 🎉

### Nota Importante:
- Render pone las aplicaciones en modo sleep si no hay actividad durante 15 minutos
- Para evitar esto, usa un plan pago

## 🔧 Estructura del Proyecto

```
english-academy/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias
├── Procfile              # Configuración para Render/Heroku
├── .env                  # Variables de entorno
├── .gitignore            # Archivos a ignorar en git
├── templates/            # Plantillas HTML
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── dashboard_teacher.html
│   ├── dashboard_student.html
│   ├── create_assignment.html
│   ├── assignment_detail.html
│   ├── upload_material.html
│   └── js/
│       └── script.js     # JavaScript
└── uploads/              # Carpeta para archivos subidos
```

## 🔐 Seguridad

- Contraseñas hasheadas con PBKDF2
- CSRF protection
- SQLAlchemy para prevenir SQL injection

La aplicación usa SQLite, que se crea automáticamente.

```
### Modelos:
- **User:** Usuarios (maestros y estudiantes)
- **Material:** Materiales educativos (PDF, imágenes, videos)

La plataforma funciona perfectamente en:
- Computadoras de escritorio
- Secundario: Verde (#2ecc71)
- Danger: Rojo (#e74c3c)
- Warning: Naranja (#f39c12)

- Notificaciones por email
- Foros de discusión
- Integración con Google Classroom
- Pagos con Stripe

### El sitio muestra error 404:

### Las imágenes no se cargan:
- Verifica que la carpeta `uploads/` exista
- Elimina `plataforma_inglesa.db`
- Reinicia la aplicación

### En Render: aplicación en "suspended":
- Render suspende apps gratis tras 15 min. sin actividad
- Usa un plan pago o mantén la app activa

## 📚 Documentación Flask

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)

## 👨‍💻 Contribuiciones

Las contribuiciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
4. Push a la rama
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT

## 📧 Contacto

¿Preguntas o sugerencias? ¡Abre un issue en GitHub!

---

**Hecho con ❤️ para educadores y estudiantes de inglés** 🎓📚
