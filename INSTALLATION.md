# 🚀 Guía de Instalación y Ejecución Local

## 📋 Índice
1. [Requisitos](#requisitos)
2. [Instalación en macOS](#instalación-en-macos)
3. [Instalación en Windows](#instalación-en-windows)
4. [Instalación en Linux](#instalación-en-linux)
5. [Primeros Pasos](#primeros-pasos)
6. [Crear Cuentas de Prueba](#crear-cuentas-de-prueba)

---

## ✅ Requisitos

- **Python 3.8+** - [Descargar](https://www.python.org/downloads/)
- **Git** (opcional) - [Descargar](https://git-scm.com)
- Al menos 500MB de espacio libre
- Navegador web moderno

Verifica que tengas Python:
```bash
python3 --version
```

---

## 🍎 Instalación en macOS

### Opción A: Automática (Recomendado)

1. Abre Terminal
2. Ve a la carpeta del proyecto:
```bash
cd /Users/a0330/Desktop/Ingles
```

3. Ejecuta el script de instalación:
```bash
chmod +x setup.sh
./setup.sh
```

4. Espera a que termine (2-3 minutos)

5. Para ejecutar la app después:
```bash
chmod +x run.sh
./run.sh
```

### Opción B: Manual

1. Abre Terminal y ve a la carpeta:
```bash
cd /Users/a0330/Desktop/Ingles
```

2. Crea el entorno virtual:
```bash
python3 -m venv venv
```

3. Actívalo:
```bash
source venv/bin/activate
```

4. Instala las dependencias:
```bash
pip install -r requirements.txt
```

5. Crea la base de datos:
```bash
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('✓ DB creada')"
```

6. Ejecuta la aplicación:
```bash
python3 app.py
```

7. Abre en tu navegador:
```
http://localhost:5000
```

---

## 💻 Instalación en Windows

### Opción A: Automática (Recomendado)

1. Abre PowerShell o CMD en la carpeta del proyecto:
   - Haz clic derecho en la carpeta
   - Selecciona "Open in Terminal" o "Open PowerShell here"

2. Ejecuta:
```bash
setup.bat
```

3. Espera a que termine

4. Para ejecutar la app después:
```bash
run.bat
```

### Opción B: Manual

1. Abre PowerShell o CMD en la carpeta del proyecto

2. Crea el entorno virtual:
```bash
python -m venv venv
```

3. Actívalo:
```bash
venv\Scripts\activate.bat
```

4. Instala las dependencias:
```bash
pip install -r requirements.txt
```

5. Crea la base de datos:
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✓ DB creada')"
```

6. Ejecuta la aplicación:
```bash
python app.py
```

7. Abre en tu navegador:
```
http://localhost:5000
```

---

## 🐧 Instalación en Linux

### Ubuntu/Debian

1. Abre Terminal

2. Instala Python y pip (si no están instalados):
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

3. Ve a la carpeta del proyecto:
```bash
cd /Users/a0330/Desktop/Ingles
```

4. Crea el entorno virtual:
```bash
python3 -m venv venv
```

5. Actívalo:
```bash
source venv/bin/activate
```

6. Instala las dependencias:
```bash
pip install -r requirements.txt
```

7. Crea la base de datos:
```bash
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('✓ DB creada')"
```

8. Ejecuta la aplicación:
```bash
python3 app.py
```

9. Abre en tu navegador:
```
http://localhost:5000
```

---

## 🎯 Primeros Pasos

### 1. La aplicación está ejecutándose

Deberías ver en la terminal:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

### 2. Abre el navegador

Accede a: `http://localhost:5000`

### 3. Crea una cuenta

- Haz clic en "Registrarse"
- Rellena los campos:
  - **Nombre:** Tu nombre
  - **Usuario:** Nombre de usuario único
  - **Email:** Tu email
  - **Contraseña:** Al menos 6 caracteres
  - **Tipo:** Selecciona "Maestro/a" o "Estudiante"

### 4. Inicia sesión

- Usa el usuario y contraseña que creaste

### 5. Como Maestro:

- Entre a "Subir Material" para compartir contenido
- Entre a "Nueva Tarea" para crear tareas
- En el Dashboard verás todas tus tareas y entregas

### 6. Como Estudiante:

- En el Dashboard verás todas las tareas disponibles
- Haz clic en una tarea para entregarla
- Descarga los materiales de estudio

---

## 👥 Crear Cuentas de Prueba

### Opción A: Usar los usuarios de ejemplo

Después de ejecutar `setup.sh` o `setup.bat`, ya tendrás dos usuarios:

**Maestro:**
- Usuario: `maestra`
- Contraseña: `123456`

**Estudiante:**
- Usuario: `estudiante`
- Contraseña: `123456`

### Opción B: Crear usuarios manualmente

1. Con la app ejecutándose, haz clic en "Registrarse"
2. Crea dos cuentas:
   - Una como Maestro
   - Una como Estudiante

### Opción C: Script personalizado

Crea un archivo `create_users.py`:

```python
from app import app, db, User
from werkzeug.security import generate_password_hash

app.app_context().push()

# Limpiar usuarios anteriores (opcional)
User.query.delete()

# Crear maestro
teacher = User(
    username='tu_usuario_maestro',
    email='maestro@example.com',
    password=generate_password_hash('tu_contraseña'),
    role='teacher',
    nombre='Tu Nombre'
)
db.session.add(teacher)

# Crear estudiante
student = User(
    username='tu_usuario_estudiante',
    email='estudiante@example.com',
    password=generate_password_hash('tu_contraseña'),
    role='student',
    nombre='Nombre del Estudiante'
)
db.session.add(student)

db.session.commit()
print('✓ Usuarios creados')
```

Luego ejecuta:
```bash
python3 create_users.py
```

---

## 🔍 Verificar que todo funciona

### 1. Base de datos creada

Deberías ver un archivo `plataforma_inglesa.db` en la carpeta del proyecto

### 2. Carpeta uploads creada

La carpeta `uploads/` debe existir para guardar archivos

### 3. Acceder a diferentes páginas

- Home: `http://localhost:5000/`
- Login: `http://localhost:5000/login`
- Register: `http://localhost:5000/register`
- Dashboard Maestro: `http://localhost:5000/dashboard/teacher`
- Dashboard Estudiante: `http://localhost:5000/dashboard/student`

### 4. Crear contenido

- Como maestro, crea una tarea
- Como estudiante, entrégala
- Verifica que el maestro pueda calificarla

---

## 🛑 Detener la aplicación

Presiona `Ctrl + C` en la terminal

---

## 🔄 Reactivar después de cerrar

Si cierras la terminal y quieres ejecutar la app de nuevo:

**macOS/Linux:**
```bash
cd /Users/a0330/Desktop/Ingles
source venv/bin/activate
python3 app.py
```

**Windows:**
```bash
cd /Users/a0330/Desktop/Ingles
venv\Scripts\activate.bat
python app.py
```

---

## 🐛 Problemas Comunes

### Error: "No module named 'flask'"

**Causa:** El entorno virtual no está activado o las dependencias no se instalaron

**Solución:**
```bash
# Asegúrate de que el entorno virtual esté activado
source venv/bin/activate  # macOS/Linux

# O

venv\Scripts\activate.bat  # Windows

# Luego instala las dependencias
pip install -r requirements.txt
```

### Error: "Address already in use"

**Causa:** El puerto 5000 está ocupado

**Solución:**
```bash
# Cambia el puerto en app.py (última línea):
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Base de datos corrupta

**Causa:** La BD se corrompió

**Solución:**
```bash
# Elimina la base de datos
rm plataforma_inglesa.db  # macOS/Linux
del plataforma_inglesa.db  # Windows

# Reinicia la app
python3 app.py
```

### No puedo acceder desde otro dispositivo

**Causa:** El servidor solo escucha en localhost

**Solución:**
1. Busca tu IP local:
   ```bash
   ipconfig getifaddr en0  # macOS
   ipconfig  # Windows (busca "IPv4 Address")
   ```

2. Accede desde otro dispositivo usando:
   ```
   http://TU_IP:5000
   ```

---

## 📊 Monitoreo

Mientras la aplicación está ejecutándose, verás los logs en la terminal:

```
HTTP GET /dashboard/teacher
HTTP POST /material/upload
...
```

Esto es útil para ver qué está pasando

---

## ✅ Checklist

- [ ] Python 3.8+ instalado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Base de datos creada
- [ ] Aplicación ejecutándose sin errores
- [ ] Puedo acceder a `http://localhost:5000`
- [ ] Puedo crear una cuenta
- [ ] Puedo iniciar sesión
- [ ] Puedo crear tareas (como maestro)
- [ ] Puedo entregar tareas (como estudiante)

---

## 🎉 ¡Listo!

¡Tu plataforma educativa está funcionando localmente! 

Ahora puedes:
1. Probar todas las características
2. Hacer cambios al código
3. Personalizar el diseño
4. Prepararte para desplegar en Render

---

Para desplegar en internet, sigue la guía: `DEPLOYMENT_RENDER.md`
