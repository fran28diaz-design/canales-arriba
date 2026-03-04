#!/usr/bin/env python3
"""
🎓 ENGLISH ACADEMY - VERSIÓN ULTRA-SIMPLE
Sin dependencias externas - Solo librerías de Python integradas
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
import urllib.parse
from datetime import datetime

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"users": {}, "materials": {}, "assignments": {}}
    return {"users": {}, "materials": {}, "assignments": {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

# HTML TEMPLATE
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - English Academy</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        nav {{
            background: #2c3e50;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            color: white;
        }}
        nav a {{
            color: white;
            text-decoration: none;
            margin: 0 10px;
            padding: 8px 12px;
            border-radius: 5px;
            transition: 0.3s;
            display: inline-block;
        }}
        nav a:hover {{ background: #3498db; }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        .card {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        h1, h2 {{ color: #2c3e50; margin-bottom: 20px; }}
        input, textarea, select {{
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-family: Arial;
        }}
        button {{
            background: #3498db;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }}
        button:hover {{ background: #2980b9; }}
        .alert {{
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }}
        .alert-success {{ background: #d4edda; color: #155724; }}
        .alert-danger {{ background: #f8d7da; color: #721c24; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; }}
        .card-item {{ background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #3498db; }}
    </style>
</head>
<body>
    <nav>
        📚 English Academy | 
        <a href="/">Inicio</a>
        <a href="/login">Login</a>
        <a href="/register">Registro</a>
        {user_nav}
    </nav>
    <div class="container">
        {content}
    </div>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = HTML_TEMPLATE.format(
                title="Inicio",
                user_nav="",
                content="""
                <div class="card" style="text-align: center;">
                    <h1>🎓 Bienvenido a English Academy</h1>
                    <p style="font-size: 18px; color: #7f8c8d; margin: 20px 0;">
                        Plataforma Educativa para Maestros y Estudiantes
                    </p>
                    <div style="margin-top: 30px;">
                        <a href="/login" style="background: #3498db; color: white; padding: 15px 40px; border-radius: 8px; text-decoration: none; display: inline-block; margin: 10px; font-size: 16px;">Iniciar Sesión</a>
                        <a href="/register" style="background: #2ecc71; color: white; padding: 15px 40px; border-radius: 8px; text-decoration: none; display: inline-block; margin: 10px; font-size: 16px;">Crear Cuenta</a>
                    </div>
                    <div style="margin-top: 40px; background: #f8f9fa; padding: 20px; border-radius: 8px;">
                        <h3>Usuarios de Prueba:</h3>
                        <p><strong>Maestro:</strong> maestra / 123456</p>
                        <p><strong>Estudiante:</strong> estudiante / 123456</p>
                    </div>
                </div>
                """
            )
            self.wfile.write(html.encode())
        
        elif path == '/login':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = HTML_TEMPLATE.format(
                title="Login",
                user_nav="",
                content="""
                <div class="card" style="max-width: 400px; margin: 50px auto;">
                    <h1>Iniciar Sesión</h1>
                    <form method="POST" action="/login">
                        <label>Usuario:</label>
                        <input type="text" name="username" required>
                        <label>Contraseña:</label>
                        <input type="password" name="password" required>
                        <button type="submit">Entrar</button>
                    </form>
                    <p style="margin-top: 20px; text-align: center;">
                        ¿No tienes cuenta? <a href="/register">Registrate</a>
                    </p>
                </div>
                """
            )
            self.wfile.write(html.encode())
        
        elif path == '/register':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = HTML_TEMPLATE.format(
                title="Registro",
                user_nav="",
                content="""
                <div class="card" style="max-width: 400px; margin: 50px auto;">
                    <h1>Crear Cuenta</h1>
                    <form method="POST" action="/register">
                        <label>Nombre:</label>
                        <input type="text" name="nombre" required>
                        <label>Usuario:</label>
                        <input type="text" name="username" required>
                        <label>Email:</label>
                        <input type="email" name="email" required>
                        <label>Contraseña:</label>
                        <input type="password" name="password" required>
                        <label>Tipo:</label>
                        <select name="role">
                            <option value="student">Estudiante</option>
                            <option value="teacher">Maestro</option>
                        </select>
                        <button type="submit">Crear Cuenta</button>
                    </form>
                </div>
                """
            )
            self.wfile.write(html.encode())
        
        elif path.startswith('/dashboard/'):
            username = path.replace('/dashboard/', '')
            data = load_data()
            user = data['users'].get(username, {})
            
            if not user:
                self.send_response(404)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                html = HTML_TEMPLATE.format(
                    title="Error 404",
                    user_nav="",
                    content="<div class='card'><h1>❌ Usuario no encontrado</h1><p><a href='/'>Volver al inicio</a></p></div>"
                )
                self.wfile.write(html.encode())
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            role = user.get('role', 'student')
            if role == 'teacher':
                content = f"""
                <div style="padding: 20px;">
                    <h1>Dashboard - Maestro</h1>
                    <p style="font-size: 18px;">¡Bienvenido, {user.get('nombre', username)}!</p>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px;">
                        <div class="card">
                            <h2>📝 Crear Tarea</h2>
                            <p>Crea nuevas asignaciones para tu clase</p>
                            <button onclick="alert('Función no disponible en versión demo')" style="background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Crear</button>
                        </div>
                        <div class="card">
                            <h2>📚 Subir Materiales</h2>
                            <p>Carga videos y archivos para los estudiantes</p>
                            <button onclick="alert('Función no disponible en versión demo')" style="background: #2ecc71; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Subir</button>
                        </div>
                        <div class="card">
                            <h2>✅ Calificar</h2>
                            <p>Revisa y califica las entregas de estudiantes</p>
                            <button onclick="alert('Función no disponible en versión demo')" style="background: #f39c12; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Verificar</button>
                        </div>
                    </div>
                </div>
                """
            else:
                content = f"""
                <div style="padding: 20px;">
                    <h1>Dashboard - Estudiante</h1>
                    <p style="font-size: 18px;">¡Bienvenido, {user.get('nombre', username)}!</p>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px;">
                        <div class="card">
                            <h2>📋 Mis Tareas</h2>
                            <p>Ver las asignaciones pendientes</p>
                            <button onclick="alert('Función no disponible en versión demo')" style="background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Ver</button>
                        </div>
                        <div class="card">
                            <h2>📤 Mis Entregas</h2>
                            <p>Envía tus trabajos completados</p>
                            <button onclick="alert('Función no disponible en versión demo')" style="background: #2ecc71; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Enviar</button>
                        </div>
                        <div class="card">
                            <h2>📚 Materiales</h2>
                            <p>Accede a videos y recursos</p>
                            <button onclick="alert('Función no disponible en versión demo')" style="background: #9b59b6; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Descargar</button>
                        </div>
                        <div class="card">
                            <h2>⭐ Mis Calificaciones</h2>
                            <p>Ve tus notas y comentarios</p>
                            <button onclick="alert('Función no disponible en versión demo')" style="background: #e74c3c; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Ver</button>
                        </div>
                    </div>
                </div>
                """
            
            html = HTML_TEMPLATE.format(
                title=f"Dashboard - {username}",
                user_nav=f"<div style='float: right; color: white;'>{username} | <a href='/' style='color: white; text-decoration: none;'>Salir</a></div>",
                content=content
            )
            self.wfile.write(html.encode())
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = HTML_TEMPLATE.format(
                title="Error 404",
                user_nav="",
                content="<div class='card'><h1>❌ Página no encontrada (404)</h1><p><a href='/'>Volver al inicio</a></p></div>"
            )
            self.wfile.write(html.encode())
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode()
        parsed = parse_qs(post_data)
        
        path = urlparse(self.path).path
        data = load_data()
        
        if path == '/register':
            username = parsed.get('username', [''])[0]
            password = parsed.get('password', [''])[0]
            email = parsed.get('email', [''])[0]
            nombre = parsed.get('nombre', [''])[0]
            role = parsed.get('role', ['student'])[0]
            
            if username and password and email:
                data['users'][username] = {
                    'password': password,
                    'email': email,
                    'nombre': nombre,
                    'role': role
                }
                save_data(data)
                self.send_response(302)
                self.send_header('Location', '/login?msg=Cuenta creada!')
                self.end_headers()
            else:
                self.send_response(302)
                self.send_header('Location', '/register?error=Completa todos los campos')
                self.end_headers()
        
        elif path == '/login':
            username = parsed.get('username', [''])[0]
            password = parsed.get('password', [''])[0]
            
            if username in data['users'] and data['users'][username]['password'] == password:
                self.send_response(302)
                self.send_header('Location', f'/dashboard/{username}')
                self.send_header('Set-Cookie', f'user={username}; Path=/')
                self.end_headers()
            else:
                self.send_response(302)
                self.send_header('Location', '/login?error=Datos incorrectos')
                self.end_headers()

def run_server():
    print("=" * 60)
    import socket
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = '127.0.0.1'
    
    print("🎓 ENGLISH ACADEMY - Plataforma Educativa")
    print("=" * 60)
    print(f'\n✅ Servidor ejecutándose en http://{local_ip}:8000')
    print('   (Acceso local: http://localhost:8000)')
    print('\n👤 Usuarios de Prueba:')
    print('   Maestro: maestra / 123456')
    print('   Estudiante: estudiante / 123456')
    print('\n⌨️  Presiona Ctrl+C para detener\n')
    
    # Crear usuarios de prueba
    data = load_data()
    if 'maestra' not in data['users']:
        data['users']['maestra'] = {
            'password': '123456',
            'email': 'maestra@example.com',
            'nombre': 'Dra. Patricia',
            'role': 'teacher'
        }
        data['users']['estudiante'] = {
            'password': '123456',
            'email': 'estudiante@example.com',
            'nombre': 'Juan Pérez',
            'role': 'student'
        }
        save_data(data)
    
    server = HTTPServer(('0.0.0.0', 8000), Handler)
    server.serve_forever()

if __name__ == '__main__':
    run_server()
