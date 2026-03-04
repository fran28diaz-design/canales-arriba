@echo off
chcp 65001 > nul
cls

echo.
echo 🚀 Iniciando instalación de English Academy...
echo.

REM Verificar si Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Python no está instalado o no está en el PATH
    echo Por favor, descarga Python desde https://www.python.org/downloads/
    echo Asegúrate de marcar "Add Python to PATH" durante la instalación
    pause
    exit /b 1
)

echo ✓ Python encontrado
for /f "tokens=*" %%i in ('python --version') do echo %%i
echo.

REM Crear entorno virtual
echo 📦 Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo ❌ Error al crear el entorno virtual
    pause
    exit /b 1
)
echo ✓ Entorno virtual creado
echo.

REM Activar entorno virtual
echo 🔌 Activando entorno virtual...
call venv\Scripts\activate.bat
echo ✓ Entorno virtual activado
echo.

REM Instalar dependencias
echo 📥 Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error al instalar dependencias
    pause
    exit /b 1
)
echo ✓ Dependencias instaladas
echo.

REM Crear base de datos
echo 💾 Inicializando base de datos...
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✓ Base de datos creada')"
echo.

REM Crear usuarios de ejemplo
echo 👤 Creando usuarios de ejemplo...
python -c "
from app import app, db, User
from werkzeug.security import generate_password_hash

app.app_context().push()

User.query.delete()
db.session.commit()

teacher = User(
    username='maestra',
    email='maestra@example.com',
    password=generate_password_hash('123456'),
    role='teacher',
    nombre='Dra. Patricia García'
)
db.session.add(teacher)

student = User(
    username='estudiante',
    email='estudiante@example.com',
    password=generate_password_hash('123456'),
    role='student',
    nombre='Juan Pérez'
)
db.session.add(student)

db.session.commit()
print('✓ Usuarios de ejemplo creados')
"
echo.

echo.
echo ✅ ¡Instalación completada!
echo.
echo 📝 Usuarios de ejemplo:
echo   👨‍🏫 Maestro:
echo      Usuario: maestra
echo      Contraseña: 123456
echo.
echo   👨‍🎓 Estudiante:
echo      Usuario: estudiante
echo      Contraseña: 123456
echo.
echo 🚀 Para ejecutar la aplicación:
echo    python app.py
echo.
echo 🌐 Accede a: http://localhost:5000
echo.
pause
