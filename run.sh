#!/bin/bash

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}"
echo "╔════════════════════════════════════════╗"
echo "║  🎓 English Academy - Server Started   ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  El entorno virtual no existe. Ejecuta './setup.sh' primero.${NC}"
    exit 1
fi

# Activar entorno virtual
source venv/bin/activate

# Ejecutar la aplicación
echo ""
echo -e "${GREEN}🚀 Iniciando Flask...${NC}"
echo ""
echo "📝 URL local: http://localhost:5000"
echo ""
echo "👤 Usuarios de prueba:"
echo "   Maestro: maestra / 123456"
echo "   Estudiante: estudiante / 123456"
echo ""
echo "⌨️  Presiona Ctrl+C para detener el servidor"
echo ""

python3 app.py
