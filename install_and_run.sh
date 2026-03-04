#!/bin/bash

echo "⏳ Esperando instalación de Xcode Command Line Tools..."
echo ""

# Esperar a que se complete la instalación
while ! command -v git &> /dev/null; do
    echo "⏳ Aún instalando... (intento cada 5 segundos)"
    sleep 5
done

echo "✅ Xcode Command Line Tools instaladas"
echo ""

cd /Users/a0330/Desktop/Ingles

echo "🚀 Instalando English Academy..."
echo ""

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv

# Activar y instalar
echo "📥 Instalando dependencias..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "✅ ¡Instalación completada!"
echo ""

# Crear base de datos
echo "💾 Creando base de datos..."
python3 -c "from app import app, db, User; from werkzeug.security import generate_password_hash; app.app_context().push(); db.create_all(); 

# Limpiar usuarios anteriores
User.query.delete()

# Crear usuarios de ejemplo
teacher = User(username='maestra', email='maestra@example.com', password=generate_password_hash('123456'), role='teacher', nombre='Dra. Patricia')
student = User(username='estudiante', email='estudiante@example.com', password=generate_password_hash('123456'), role='student', nombre='Juan Pérez')
db.session.add(teacher)
db.session.add(student)
db.session.commit()
print('✓ Base de datos lista')
"

echo ""
echo "🎉 ¡Listo!"
echo ""
echo "👤 Usuarios de prueba:"
echo "   Maestro: maestra / 123456"
echo "   Estudiante: estudiante / 123456"
echo ""
echo "Ejecutando la aplicación..."
echo ""
python3 app.py
