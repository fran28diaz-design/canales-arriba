# 🌐 Guía Completa de Despliegue en Render

## 📋 Tabla de Contenidos
1. [Requisitos Previos](#requisitos-previos)
2. [Paso 1: Preparar GitHub](#paso-1-preparar-github)
3. [Paso 2: Conectar con Render](#paso-2-conectar-con-render)
4. [Paso 3: Configuración Final](#paso-3-configuración-final)
5. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
6. [Solución de Problemas](#solución-de-problemas)

---

## ✅ Requisitos Previos

1. **Cuenta de GitHub** (gratis en https://github.com)
2. **Cuenta de Render** (gratis en https://render.com)
3. **Git instalado** en tu computadora
4. **El código completado** en `/Users/a0330/Desktop/Ingles`

---

## Paso 1: Preparar GitHub

### 1.1 Crear un Repositorio en GitHub

1. Ve a https://github.com/new
2. Rellena los campos:
   - **Repository name:** `english-academy`
   - **Description:** `Plataforma Educativa de Inglés`
   - **Visibility:** Público (`Public`)
3. Deja lo demás por defecto
4. Haz clic en "Create repository"

### 1.2 Subir tu código

Abre una terminal y ejecuta los siguientes comandos:

```bash
# Entrar a la carpeta del proyecto
cd /Users/a0330/Desktop/Ingles

# Inicializar Git
git init

# Agregar todos los archivos
git add .

# Crear el primer commit
git commit -m "Initial commit: English Academy platform"

# Renombrar la rama a 'main' (si es necesario)
git branch -M main

# Agregar el repositorio remoto
git remote add origin https://github.com/TU-USUARIO/english-academy.git

# Subir el código
git push -u origin main
```

**⚠️ Reemplaza `TU-USUARIO` con tu nombre de usuario de GitHub**

### 1.3 Verificar que fue exitoso

- Ve a tu repositorio en GitHub: `https://github.com/TU-USUARIO/english-academy`
- Deberías ver todos tus archivos allí

---

## Paso 2: Conectar con Render

### 2.1 Crear una Cuenta en Render

1. Ve a https://render.com
2. Haz clic en "Sign up" en la esquina superior derecha
3. Opción A: Usa tu cuenta de GitHub (recomendado)
   - Haz clic en "Sign up with GitHub"
   - Autoriza la aplicación
4. Opción B: Usa email y contraseña

### 2.2 Crear un Nuevo Servicio Web

1. Una vez en Render, haz clic en el botón `New +` en la esquina superior izquierda
2. Selecciona `Web Service`

### 2.3 Conectar tu repositorio de GitHub

1. En "Connect a repository", selecciona tu repositorio `english-academy`
   - Si no aparece, haz clic en "Connect Account" para autorizar GitHub
   - Busca `english-academy`
2. Haz clic en "Connect"

---

## Paso 3: Configuración Final

### 3.1 Configurar los detalles del servicio

Una vez conectado el repositorio, rellena lo siguiente:

| Campo | Valor |
|-------|-------|
| **Name** | `english-academy` |
| **Environment** | `Python 3` |
| **Region** | Elige la más cercana a ti (o deja los Aarón por defecto) |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app_simple:app` |

### 3.2 Agregar Variables de Entorno

1. Baja hasta la sección **Environment Variables**
2. Haz clic en "Add Environment Variable"
3. Agrega esto:

```
KEY: SECRET_KEY
VALUE: tu-clave-secreta-super-segura-2026-cambiar-ahora
```

**👉 Cámbia el valor de SECRET_KEY por algo único y seguro**, por ejemplo:
```
production-secret-key-xyz123abc456def789ghi
```

### 3.3 Seleccionar el Plan

En "Instance Type":
- **Free** - $0/mes (con limitaciones)
- **Starter** - $7/mes (recomendado para producción)

Para probar, elige **Free**.

### 3.4 Desplegar

1. Desplázate hasta el final de la página
2. Haz clic en **"Create Web Service"**

Render comenzará a desplegar tu aplicación de inmediato.

**⏳ Espera 5-10 minutos** a que termine el deploy

---

## 🎉 ¡Succeso!

Una vez que el deploy termine:

1. Verás una URL como: `https://english-academy.onrender.com`
2. **¡Esa es tu URL pública!** Puedes compartirla con cualquiera
3. Haz clic en la URL para abrir tu aplicación

### Primeras pruebas:

- Accede a `https://english-academy.onrender.com/login`
- Crea una cuenta de maestro
- Prueba subir materiales y crear tareas
- Crea una cuenta de estudiante en otra ventana incognito
- Verifica que el estudiante ve los materiales

---

## 🔄 Actualizar la Aplicación

Cuando hagas cambios en tu código local:

1. Comitea los cambios en Git:
```bash
git add .
git commit -m "Descripción de los cambios"
git push origin main
```

2. Render detectará los cambios automáticamente y hará un nuevo deploy

---

## ⏸️ Monitoreo y Mantenimiento

### Ver los logs de la aplicación

1. En Render, ve a tu servicio `english-academy`
2. Haz clic en la pestaña **"Logs"**
3. Aquí verás cualquier error o mensaje

### Reiniciar la aplicación

Si algo falla:
1. Ve a la configuración del servicio
2. Desplázate hasta "Dangerously Manually Deploy"
3. Haz clic en "Latest Deploy"

### Base de datos en Render

⚠️ **Importante:** El archivo `plataforma_inglesa.db` se perderá si la aplicación reinicia.

Para producción real, deberías usar una base de datos en la nube como:
- PostgreSQL (recomendado)
- MongoDB
- MySQL

Por ahora, la aplicación funcionará con SQLite en Render.

---

## 🐛 Solución de Problemas

### Error: "Application failed to start"

**Solución:**
1. Verifica que el archivo `Procfile` exista y tenga:
   ```
   web: gunicorn app:app
   ```
2. Verifica que `gunicorn` esté en `requirements.txt`
3. Revisa los logs para más detalles

### La aplicación se queda en "Building"

**Solución:**
1. Espera más tiempo (hasta 15 minutos)
2. Si persiste, ve a "Dangerously Manually Deploy" > "Clear Build Cache" > "Deploy Latest"

### Error de base de datos

**Solución:**
- No hay solución porque SQLite no persiste en Render
- Para producción, usa PostgreSQL (ver sección de Base de Datos)

### "Application failed to boot"

**Solución:**
1. Verifica que `SECRET_KEY` esté configurada en Environment Variables
2. Comprueba que los módulos en `requirements.txt` sean correctos
3. Revisa los logs para ver el error específico

### La aplicación es lenta o se detiene

**Solución:**
- Render coloca en "sleep" las aplicaciones gratuitas tras 15 minutos sin actividad
- La primera solicitud después del sleep tarda más
- Para evitar esto, usa un plan pago ($7/mes)

---

## 📞 Soporte

Si tienes problemas:

1. **Documentación de Render:** https://render.com/docs
2. **Stack Overflow:** Busca tu error con la etiqueta `render-com`
3. **GitHub Issues:** Crea un issue en tu repositorio

---

## 🚀 Próximos Pasos (Opcional)

### Agregar un Dominio Personalizado

En Render, ve a "Settings" y busca "Custom Domain":
1. Agrega tu dominio (p. ej., `english-academy.com`)
2. Sigue las instrucciones para configurar el DNS
3. Render te dará un certificado SSL automáticamente

### Migrar a PostgreSQL para Producción

Cuando estés listo para llevar esto a producción:

1. Crea una base de datos PostgreSQL en Render
2. Actualiza `app.py`:
   ```python
   import os
   DB_URL = os.getenv('DATABASE_URL')
   app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
   ```
3. Agrega `psycopg2-binary` a `requirements.txt`

---

## ✅ Checklist Final

Antes de considerar tu aplicación "en vivo":

- [ ] El repositorio de GitHub está público y tiene todo el código
- [ ] Render muestra "Running" (no "Building" o "Failed")
- [ ] Puedes acceder a la URL pública sin errores
- [ ] Puedes registrarte y crear una cuenta
- [ ] Puedes iniciar sesión
- [ ] El maestro puede crear tareas
- [ ] El estudiante puede ver tareas y entregarlas
- [ ] Los archivos se descargan correctamente

---

## 📚 Links Útiles

- [GitHub](https://github.com)
- [Render](https://render.com)
- [Flask Documentation](https://flask.palletsprojects.com)
- [SQLAlchemy](https://www.sqlalchemy.org)
- [Gunicorn](https://gunicorn.org)

---

**¡Felicidades! Tu aplicación está en línea y disponible para que cualquiera la use.** 🎉

Para mantenerla segura:
1. Cambia la `SECRET_KEY` regularmente
2. Usa contraseñas fuertes
3. Mantén las dependencias actualizadas
4. Monitorea los logs regularmente

**Hecho con ❤️ para educadores** 🎓
