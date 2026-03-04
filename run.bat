@echo off
chcp 65001 > nul
cls

echo.
echo ================================================
echo   🎓 English Academy - Server Started
echo ================================================
echo.

REM Verificar si el entorno virtual existe
if not exist "venv" (
    echo ⚠️  El entorno virtual no existe. Ejecuta 'setup.bat' primero.
    pause
    exit /b 1
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

echo.
echo 🚀 Iniciando Flask...
echo.
echo 📝 URL local: http://localhost:5000
echo.
echo 👤 Usuarios de prueba:
echo    Maestro: maestra / 123456
echo    Estudiante: estudiante / 123456
echo.
echo ⌨️  Presiona Ctrl+C para detener el servidor
echo.
echo.

python app.py
pause
