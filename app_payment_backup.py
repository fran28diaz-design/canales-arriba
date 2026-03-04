#!/usr/bin/env python3
"""
🎓 ENGLISH ACADEMY - CON SISTEMA DE MÉTODOS DE PAGO
Plataforma educativa con gestión de pagos
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
import socket
from datetime import datetime

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"users": {}, "materials": {}, "assignments": {}, "payment_methods": {}, "student_payments": {}}
    return {"users": {}, "materials": {}, "assignments": {}, "payment_methods": {}, "student_payments": {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

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
            max-width: 1000px;
            margin: 0 auto;
        }}
        .card {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-bottom: 20px;
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
            font-size: 14px;
        }}
        button:hover {{ background: #2980b9; }}
        .btn-success {{ background: #27ae60; }}
        .btn-success:hover {{ background: #229954; }}
        .btn-danger {{ background: #e74c3c; }}
        .btn-danger:hover {{ background: #c0392b; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }}
        .card-item {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db; }}
        .payment-method {{ background: #f0f9ff; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #27ae60; }}
        label {{ display: block; margin-top: 10px; font-weight: bold; color: #2c3e50; }}
        .form-group {{ margin-bottom: 15px; }}
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
        data = load_data()
        
        if path == '/':
            self.render_home()
        elif path == '/login':
            self.render_login()
        elif path == '/register':
            self.render_register()
        elif path.startswith('/dashboard/'):
            username = path.replace('/dashboard/', '')
            self.render_dashboard(username, data)
        elif path == '/payment-methods':
            self.render_payment_methods(data)
        else:
            self.render_404()
    
    def render_home(self):
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
                    Plataforma Educativa con Sistema de Pago
                </p>
                <div style="margin-top: 30px;">
                    <a href="/login" style="background: #3498db; color: white; padding: 15px 40px; border-radius: 8px; text-decoration: none; display: inline-block; margin: 10px; font-size: 16px;">Iniciar Sesión</a>
                    <a href="/register" style="background: #2ecc71; color: white; padding: 15px 40px; border-radius: 8px; text-decoration: none; display: inline-block; margin: 10px; font-size: 16px;">Crear Cuenta</a>
                </div>
                <div style="margin-top: 40px; background: #f8f9fa; padding: 20px; border-radius: 8px;">
                    <h3>🔑 Usuarios de Prueba:</h3>
                    <p><strong>👨‍🏫 Maestro/Admin:</strong> maestra / 123456</p>
                    <p><strong>👨‍🎓 Estudiante:</strong> estudiante / 123456</p>
                </div>
            </div>
            """
        )
        self.wfile.write(html.encode())
    
    def render_login(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = HTML_TEMPLATE.format(
            title="Iniciar Sesión",
            user_nav="",
            content="""
            <div class="card" style="max-width: 400px; margin: 50px auto;">
                <h1>🔐 Iniciar Sesión</h1>
                <form method="POST" action="/login">
                    <div class="form-group">
                        <label>Usuario:</label>
                        <input type="text" name="username" required>
                    </div>
                    <div class="form-group">
                        <label>Contraseña:</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit" class="btn-success" style="width: 100%;">Entrar</button>
                </form>
                <p style="margin-top: 20px; text-align: center;">
                    ¿No tienes cuenta? <a href="/register" style="color: #3498db;">Regístrate aquí</a>
                </p>
            </div>
            """
        )
        self.wfile.write(html.encode())
    
    def render_register(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = HTML_TEMPLATE.format(
            title="Crear Cuenta",
            user_nav="",
            content="""
            <div class="card" style="max-width: 400px; margin: 50px auto;">
                <h1>📝 Crear Cuenta</h1>
                <form method="POST" action="/register">
                    <div class="form-group">
                        <label>Nombre Completo:</label>
                        <input type="text" name="nombre" required>
                    </div>
                    <div class="form-group">
                        <label>Usuario:</label>
                        <input type="text" name="username" required>
                    </div>
                    <div class="form-group">
                        <label>Email:</label>
                        <input type="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label>Contraseña:</label>
                        <input type="password" name="password" required>
                    </div>
                    <div class="form-group">
                        <label>Tipo de Usuario:</label>
                        <select name="role">
                            <option value="student">Estudiante</option>
                            <option value="teacher">Maestro/Administrador</option>
                        </select>
                    </div>
                    <button type="submit" class="btn-success" style="width: 100%;">Crear Cuenta</button>
                </form>
            </div>
            """
        )
        self.wfile.write(html.encode())
    
    def render_dashboard(self, username, data):
        user = data['users'].get(username, {})
        
        if not user:
            self.render_404()
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        role = user.get('role', 'student')
        
        if role == 'teacher':
            content = self.teacher_dashboard(username, user, data)
        else:
            content = self.student_dashboard(username, user, data)
        
        html = HTML_TEMPLATE.format(
            title=f"Dashboard - {username}",
            user_nav=f"<div style='float: right; color: white;'>{username} ({role}) | <a href='/' style='color: white; text-decoration: none;'>Salir</a></div>",
            content=content
        )
        self.wfile.write(html.encode())
    
    def teacher_dashboard(self, username, user, data):
        payment_methods = data.get('payment_methods', {})
        
        methods_html = ""
        if payment_methods:
            for method_id, method in payment_methods.items():
                methods_html += f"""
                <div class="payment-method">
                    <strong>💳 {method['name']}</strong>
                    <br><small>{method['description']}</small>
                </div>
                """
        else:
            methods_html = '<p style="color: #999;">No hay métodos de pago configurados aún</p>'
        
        return f"""
        <div>
            <h1>👨‍🏫 Dashboard - Maestro/Administrador</h1>
            <p style="font-size: 16px; color: #555; margin-bottom: 30px;">¡Bienvenido, <strong>{user.get('nombre', username)}</strong>!</p>
            
            <div class="grid">
                <div class="card-item">
                    <h3>📝 Crear Tarea</h3>
                    <p>Crea nuevas asignaciones para tu clase</p>
                    <button onclick="alert('Función en desarrollo')">Crear</button>
                </div>
                <div class="card-item">
                    <h3>📚 Subir Materiales</h3>
                    <p>Carga videos y archivos educativos</p>
                    <button onclick="alert('Función en desarrollo')">Subir</button>
                </div>
                <div class="card-item">
                    <h3>✅ Calificar</h3>
                    <p>Revisa y califica entregas estudiantiles</p>
                    <button onclick="alert('Función en desarrollo')">Verificar</button>
                </div>
                <div class="card-item">
                    <h3>💳 Métodos de Pago</h3>
                    <p>Administra opciones de pago</p>
                    <button onclick="window.location.href='/payment-methods'" class="btn-danger">Administrar</button>
                </div>
            </div>
            
            <div class="card" style="margin-top: 30px;">
                <h2>💰 Métodos de Pago Vigentes</h2>
                {methods_html}
            </div>
        </div>
        """
    
    def student_dashboard(self, username, user, data):
        payment_methods = data.get('payment_methods', {})
        student_payment = data.get('student_payments', {}).get(username, {})
        current_payment = student_payment.get('selected_method', '')
        
        methods_options = '<option value="">-- Selecciona un método --</option>'
        for method_id, method in payment_methods.items():
            selected = 'selected' if current_payment == method_id else ''
            methods_options += f'<option value="{method_id}" {selected}>💳 {method["name"]} - {method["description"]}</option>'
        
        current_payment_display = "No seleccionado"
        if current_payment and current_payment in payment_methods:
            pm = payment_methods[current_payment]
            current_payment_display = f"{pm['name']} ({pm['description']})"
        
        return f"""
        <div>
            <h1>👨‍🎓 Dashboard - Estudiante</h1>
            <p style="font-size: 16px; color: #555; margin-bottom: 30px;">¡Bienvenido, <strong>{user.get('nombre', username)}</strong>!</p>
            
            <div class="grid">
                <div class="card-item">
                    <h3>📋 Mis Tareas</h3>
                    <p>Ver asignaciones pendientes</p>
                    <button onclick="alert('Función en desarrollo')">Ver</button>
                </div>
                <div class="card-item">
                    <h3>📤 Mis Entregas</h3>
                    <p>Envía trabajos completados</p>
                    <button onclick="alert('Función en desarrollo')">Enviar</button>
                </div>
                <div class="card-item">
                    <h3>📚 Materiales</h3>
                    <p>Accede a recursos educativos</p>
                    <button onclick="alert('Función en desarrollo')">Descargar</button>
                </div>
                <div class="card-item">
                    <h3>⭐ Calificaciones</h3>
                    <p>Ve tus notas y retroalimentación</p>
                    <button onclick="alert('Función en desarrollo')">Ver</button>
                </div>
            </div>
            
            <div class="card" style="margin-top: 30px; max-width: 600px;">
                <h2>💳 Método de Pago</h2>
                <p style="font-size: 14px; color: #666; margin-bottom: 15px;">
                    Selecciona tu opción de pago preferida para acceder a los cursos premium.
                </p>
                
                <form method="POST" action="/select-payment">
                    <input type="hidden" name="username" value="{username}">
                    
                    <div class="form-group">
                        <label>Elige tu método de pago:</label>
                        <select name="payment_method">
                            {methods_options}
                        </select>
                    </div>
                    
                    <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <p><strong>Método Seleccionado:</strong></p>
                        <p style="font-size: 16px; color: #27ae60;"><strong>{current_payment_display}</strong></p>
                    </div>
                    
                    <button type="submit" class="btn-success" style="width: 100%;">💾 Guardar Método de Pago</button>
                </form>
            </div>
        </div>
        """
    
    def render_payment_methods(self, data):
        payment_methods = data.get('payment_methods', {})
        
        methods_list = ""
        if payment_methods:
            for method_id, method in payment_methods.items():
                methods_list += f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #27ae60;">
                    <strong style="font-size: 16px;">💳 {method['name']}</strong>
                    <br><small style="color: #666;">{method['description']}</small>
                    <br><small style="color: #999;">ID: {method_id}</small>
                </div>
                """
        else:
            methods_list = '<p style="color: #999; text-align: center;">No hay métodos de pago configurados</p>'
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = HTML_TEMPLATE.format(
            title="Métodos de Pago",
            user_nav="<div style='float: right; color: white;'><a href='/dashboard/maestra' style='color: white; text-decoration: none;'>← Volver</a></div>",
            content=f"""
            <div>
                <h1>💳 Administrador de Métodos de Pago</h1>
                
                <div class="card" style="max-width: 500px;">
                    <h2>➕ Agregar Nuevo Método</h2>
                    <form method="POST" action="/add-payment-method">
                        <div class="form-group">
                            <label>Nombre del Método:</label>
                            <input type="text" name="name" placeholder="ej: Tarjeta de Crédito" required>
                        </div>
                        
                        <div class="form-group">
                            <label>Descripción:</label>
                            <input type="text" name="description" placeholder="ej: Visa, Mastercard, PayPal, etc." required>
                        </div>
                        
                        <button type="submit" class="btn-success" style="width: 100%;">✅ Agregar Método</button>
                    </form>
                </div>
                
                <div class="card" style="margin-top: 30px;">
                    <h2>📋 Métodos Vigentes</h2>
                    {methods_list}
                </div>
            </div>
            """
        )
        self.wfile.write(html.encode())
    
    def render_404(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = HTML_TEMPLATE.format(
            title="Página no encontrada",
            user_nav="",
            content="""
            <div class="card" style="text-align: center;">
                <h1>❌ Página no encontrada (404)</h1>
                <p>La página que buscas no existe</p>
                <a href="/" style="display: inline-block; background: #3498db; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin-top: 10px;">Volver al inicio</a>
            </div>
            """
        )
        self.wfile.write(html.encode())
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode()
        parsed = parse_qs(post_data)
        
        path = urlparse(self.path).path
        data = load_data()
        
        if path == '/register':
            self.handle_register(parsed, data)
        elif path == '/login':
            self.handle_login(parsed, data)
        elif path == '/add-payment-method':
            self.handle_add_payment(parsed, data)
        elif path == '/select-payment':
            self.handle_select_payment(parsed, data)
    
    def handle_register(self, parsed, data):
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
            self.send_header('Location', '/login?msg=¡Cuenta creada exitosamente!')
            self.end_headers()
        else:
            self.send_response(302)
            self.send_header('Location', '/register?error=Completa todos los campos')
            self.end_headers()
    
    def handle_login(self, parsed, data):
        username = parsed.get('username', [''])[0]
        password = parsed.get('password', [''])[0]
        
        if username in data['users'] and data['users'][username]['password'] == password:
            self.send_response(302)
            self.send_header('Location', f'/dashboard/{username}')
            self.send_header('Set-Cookie', f'user={username}; Path=/')
            self.end_headers()
        else:
            self.send_response(302)
            self.send_header('Location', '/login?error=Usuario o contraseña incorrectos')
            self.end_headers()
    
    def handle_add_payment(self, parsed, data):
        name = parsed.get('name', [''])[0]
        description = parsed.get('description', [''])[0]
        
        if name and description:
            method_id = str(len(data.get('payment_methods', {})) + 1)
            if 'payment_methods' not in data:
                data['payment_methods'] = {}
            data['payment_methods'][method_id] = {
                'name': name,
                'description': description,
                'date_created': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            save_data(data)
        
        self.send_response(302)
        self.send_header('Location', '/payment-methods')
        self.end_headers()
    
    def handle_select_payment(self, parsed, data):
        username = parsed.get('username', [''])[0] or 'estudiante'
        payment_method = parsed.get('payment_method', [''])[0]
        
        if 'student_payments' not in data:
            data['student_payments'] = {}
        
        if username not in data['student_payments']:
            data['student_payments'][username] = {}
        
        data['student_payments'][username]['selected_method'] = payment_method
        data['student_payments'][username]['date_selected'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_data(data)
        
        self.send_response(302)
        self.send_header('Location', f'/dashboard/{username}')
        self.end_headers()
    
    def log_message(self, format, *args):
        return

def run_server():
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = '127.0.0.1'
    
    print("\n" + "=" * 70)
    print("🎓 ENGLISH ACADEMY - PLATAFORMA EDUCATIVA CON SISTEMA DE PAGO")
    print("=" * 70)
    print(f'✅ Servidor ejecutándose en: http://{local_ip}:8000')
    print(f'   Acceso local: http://localhost:8000')
    print("\n👤 USUARIOS DE PRUEBA:")
    print('   👨‍🏫 Maestro/Admin: maestra / 123456')
    print('   👨‍🎓 Estudiante: estudiante / 123456')
    print("\n📋 FUNCIONALIDADES:")
    print('   • Autenticación de usuarios')
    print('   • Dashboard diferenciado por rol')
    print('   • Maestro puede crear métodos de pago')
    print('   • Estudiante puede seleccionar método de pago')
    print("\n⌨️  Presiona Ctrl+C para detener\n")
    print("=" * 70 + "\n")
    
    data = load_data()
    if 'maestra' not in data.get('users', {}):
        data['users'] = {
            'maestra': {
                'password': '123456',
                'email': 'maestra@example.com',
                'nombre': 'Dra. Patricia García',
                'role': 'teacher'
            },
            'estudiante': {
                'password': '123456',
                'email': 'estudiante@example.com',
                'nombre': 'Juan Pérez López',
                'role': 'student'
            }
        }
        
        if 'payment_methods' not in data:
            data['payment_methods'] = {
                '1': {'name': 'Tarjeta de Crédito', 'description': 'Visa, Mastercard, AmEx'},
                '2': {'name': 'PayPal', 'description': 'Pago Digital Seguro'},
                '3': {'name': 'Transferencia Bancaria', 'description': 'Acceso Institucional'}
            }
        
        save_data(data)
    
    try:
        server = HTTPServer(('0.0.0.0', 8000), Handler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Servidor detenido correctamente")

if __name__ == '__main__':
    run_server()
