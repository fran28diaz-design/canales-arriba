#!/bin/bash

echo "🚀 Iniciando instalación de English Academy..."
echo ""

# Colores para terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar si Python está disponible
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python no está disponible. Instalando Xcode Command Line Tools...${NC}"
    xcode-select --install
    echo "Por favor, espera a que termine la instalación y ejecuta este script nuevamente."
    exit 1
fi

echo -e "${GREEN}✓ Python encontrado$(python3 --version)${NC}"
echo ""

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv
echo -e "${GREEN}✓ Entorno virtual creado${NC}"
echo ""

# Activar entorno virtual
echo "🔌 Activando entorno virtual..."
source venv/bin/activate
echo -e "${GREEN}✓ Entorno virtual activado${NC}"
echo ""

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencias instaladas${NC}"
echo ""

# Crear base de datos
echo "💾 Inicializando base de datos..."
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('✓ Base de datos creada')"
echo ""

# Ejemplo de usuario
echo "👤 Creando usuario de ejemplo..."
python3 -c "
from app import app, db, User
from werkzeug.security import generate_password_hash

app.app_context().push()

# Eliminar usuarios de ejemplo si existen
User.query.delete()
db.session.commit()

# Crear usuario de ejemplo maestro
teacher = User(
    username='maestra',
    email='maestra@example.com',
    password=generate_password_hash('123456'),
    role='teacher',
    nombre='Dra. Patricia García'
)
db.session.add(teacher)

# Crear usuario de ejemplo estudiante
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
echo ""

echo -e "${GREEN}✅ ¡Instalación completada!${NC}"
echo ""
echo "📝 Usuarios de ejemplo:"
echo "  👨‍🏫 Maestro:"
echo "     Usuario: maestra"
echo "     Contraseña: 123456"
echo ""
echo "  👨‍🎓 Estudiante:"
echo "     Usuario: estudiante"
echo "     Contraseña: 123456"
echo ""
echo "🚀 Para ejecutar la aplicación:"
echo "   source venv/bin/activate"
echo "   python3 app.py"
echo ""
echo "🌐 Accede a: http://localhost:5000"
echo ""
