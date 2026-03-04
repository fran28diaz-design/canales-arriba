#!/bin/bash

echo "🔧 Resolviendo instalación de Xcode..."

# Intenta aceptar el diálogo de Xcode
sudo /usr/bin/xcode-select --install <<< "" 2>/dev/null || true

# Espera un poco
sleep 2

# Intenta resetear
sudo /usr/bin/xcode-select --reset 2>/dev/null || true

# Espera más
sleep 2

# Ahora crea el venv
echo "📦 Creando entorno virtual..."
/usr/bin/python3 -m venv /Users/a0330/Desktop/Ingles/venv

echo "✅ Entorno virtual creado"

# Instala dependencias
echo "📥 Instalando dependencias..."
cd /Users/a0330/Desktop/Ingles
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo "✅ Dependencias instaladas"

# Crea la base de datos
echo "💾 Inicializando base de datos..."
python3 << 'EOF'
from app import app, db, User
from werkzeug.security import generate_password_hash

app.app_context().push()
db.create_all()
print("✓ Base de datos creada")
EOF

# Crea usuarios de prueba
python3 << 'EOF'
from app import app, db, User
from werkzeug.security import generate_password_hash

app.app_context().push()

# Limpiar usuarios anteriores
User.query.delete()
db.session.commit()

# Crear usuarios
teacher = User(
    username='maestra',
    email='maestra@example.com',
    password=generate_password_hash('123456'),
    role='teacher',
    nombre='Dra. Patricia García'
)
student = User(
    username='estudiante',
    email='estudiante@example.com',
    password=generate_password_hash('123456'),
    role='student',
    nombre='Juan Pérez'
)
db.session.add(teacher)
db.session.add(student)
db.session.commit()
print("✓ Usuarios de prueba creados")
EOF

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "👤 Usuarios de prueba:"
echo "   👨‍🏫 Maestro: maestra / 123456"
echo "   👨‍🎓 Estudiante: estudiante / 123456"
echo ""
echo "🚀 Ejecutando la aplicación..."
echo ""

cd /Users/a0330/Desktop/Ingles
source venv/bin/activate
python3 app.py
