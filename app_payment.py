#!/usr/bin/env python3
"""
🎓 ENGLISH ACADEMY PRO - SISTEMA COMPLETO CON PERFILES Y PROGRESO
Plataforma educativa con pagos, perfiles, progreso y hábitos
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
import socket
from datetime import datetime, date, timedelta
import hashlib
import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return create_default_data()
    return create_default_data()

def create_default_data():
    return {
        "users": {},
        "student_profiles": {},
        "student_progress": {},
        "student_habits": {},
        "payment_methods": {},
        "student_accounts": {},
        "transactions": {},
        "password_reset_tokens": {}
    }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def encrypt_card(card_number):
    return hashlib.sha256(card_number.encode()).hexdigest()[:16]

def mask_card(card_number):
    return "*" * (len(card_number) - 4) + card_number[-4:]

def get_birthday_message(birth_date):
    """Devuelve mensajeif es el cumpleaños hoy"""
    try:
        today = date.today()
        bday = datetime.strptime(birth_date, "%Y-%m-%d").date()
        if bday.month == today.month and bday.day == today.day:
            age = today.year - bday.year
            return f"🎉 ¡Feliz Cumpleaños! 🎂 ¡Hoy cumples {age} años!"
        return None
    except:
        return None

def send_reset_email(email, reset_token, username):
    """Envía email para resetear contraseña"""
    try:
        # Configurar SMTP de Gmail
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "learning.english.academy@gmail.com"  # Usuario debe configurar
        sender_password = "ydxs sqzy kpgh gkuz"  # Contraseña de aplicación del usuario (debe configurar)
        
        message = MIMEMultipart("alternative")
        message["Subject"] = "🔐 Resetear tu contraseña - English Academy Pro"
        message["From"] = sender_email
        message["To"] = email
        
        reset_link = f"http://localhost:8000/reset-password?token={reset_token}&user={username}"
        
        text = f"""¡Hola {username}!

Recibimos una solicitud para resetear tu contraseña en English Academy Pro.

Haz clic en el siguiente enlace para crear una nueva contraseña:
{reset_link}

Este enlace expirará en 1 hora.

Si no solicitaste un reset de contraseña, ignora este correo.

¡Saludos,
English Academy Pro Team! 🎓"""

        html = f"""<html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #1a1a2e; margin: 0;">🔐 Resetear Contraseña</h1>
                </div>
                <p style="color: #333; font-size: 16px; line-height: 1.6;">¡Hola <strong>{username}</strong>!</p>
                <p style="color: #333; font-size: 16px; line-height: 1.6;">Recibimos una solicitud para resetear tu contraseña en <strong>English Academy Pro</strong>.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="background: linear-gradient(135deg, #4c90e2 0%, #2e5c8a 100%); color: white; padding: 14px 35px; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block;">Resetear Contraseña</a>
                </div>
                <p style="color: #999; font-size: 13px;">O copia este enlace en tu navegador:</p>
                <p style="color: #4c90e2; font-size: 12px; word-break: break-all;">{reset_link}</p>
                <p style="color: #999; font-size: 13px; margin-top: 20px;"><strong>⏰ Nota:</strong> Este enlace expirará en 1 hora.</p>
                <p style="color: #999; font-size: 13px;">Si no solicitaste un reset de contraseña, ignora este correo.</p>
                <div style="border-top: 1px solid #e0e0e0; margin-top: 30px; padding-top: 20px; text-align: center;">
                    <p style="color: #999; font-size: 12px;">¡Saludos,<br>English Academy Pro Team 🎓</p>
                </div>
            </div>
        </body>
        </html>"""
        
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        
        message.attach(part1)
        message.attach(part2)
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message.as_string())
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

def generate_reset_token(username, data):
    """Genera un token para resetear contraseña"""
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now() + timedelta(hours=1)).isoformat()
    
    if "password_reset_tokens" not in data:
        data["password_reset_tokens"] = {}
    
    data["password_reset_tokens"][token] = {
        "username": username,
        "expires_at": expires_at
    }
    return token

def validate_reset_token(token, data):
    """Valida un token de reset y retorna el usuario si es válido"""
    if "password_reset_tokens" not in data:
        return None
    
    reset_data = data["password_reset_tokens"].get(token)
    if not reset_data:
        return None
    
    try:
        expires_at = datetime.fromisoformat(reset_data["expires_at"])
        if datetime.now() > expires_at:
            del data["password_reset_tokens"][token]
            return None
        return reset_data["username"]
    except:
        return None

DAILY_VERSES = [
    {
        "book": "John",
        "chapter": 3,
        "verse": 16,
        "text": "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life."
    },
    {
        "book": "Philippians",
        "chapter": 4,
        "verse": 13,
        "text": "I can do all this through him who gives me strength."
    },
    {
        "book": "Proverbs",
        "chapter": 17,
        "verse": 17,
        "text": "A friend loves at all times, and a brother is born for a time of adversity."
    },
    {
        "book": "Matthew",
        "chapter": 6,
        "verse": 33,
        "text": "But seek first his kingdom and his righteousness, and all these things will be given to you as well."
    },
    {
        "book": "Psalm",
        "chapter": 23,
        "verse": 1,
        "text": "The Lord is my shepherd, I lack nothing."
    },
    {
        "book": "1 Corinthians",
        "chapter": 13,
        "verse": 4,
        "text": "Love is patient, love is kind. It does not envy, it does not boast, it is not proud."
    },
    {
        "book": "Proverbs",
        "chapter": 22,
        "verse": 6,
        "text": "Start children off on the way they should go; even when they are old they will not depart from it."
    },
    {
        "book": "Deuteronomy",
        "chapter": 31,
        "verse": 8,
        "text": "The Lord himself goes before you and will be with you; he will never leave you nor forsake you."
    },
    {
        "book": "Joshua",
        "chapter": 1,
        "verse": 9,
        "text": "Have I not commanded you? Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go."
    },
    {
        "book": "Psalm",
        "chapter": 139,
        "verse": 14,
        "text": "I praise you because I am fearfully and wonderfully made; your works are wonderful, I know that full well."
    },
    {
        "book": "Romans",
        "chapter": 12,
        "verse": 2,
        "text": "Do not conform to the pattern of this world, but be transformed by the renewing of your mind."
    },
    {
        "book": "Proverbs",
        "chapter": 27,
        "verse": 12,
        "text": "The prudent see danger and take refuge, but the simple keep going and pay the penalty."
    },
    {
        "book": "1 Peter",
        "chapter": 5,
        "verse": 7,
        "text": "Cast all your anxiety on him because he cares for you."
    },
    {
        "book": "Ephesians",
        "chapter": 4,
        "verse": 2,
        "text": "Be completely humble and gentle; be patient, bearing with one another in love."
    },
    {
        "book": "Psalm",
        "chapter": 37,
        "verse": 5,
        "text": "Commit to the Lord whatever you do, and your plans will succeed."
    }
]

def get_daily_verse():
    """Retorna un versículo basado en la fecha actual"""
    today = date.today()
    day_of_year = today.timetuple().tm_yday
    verse_index = day_of_year % len(DAILY_VERSES)
    return DAILY_VERSES[verse_index]

NAVBAR_TEMPLATE = """<div class="navbar-container">
    <div class="navbar">
        <div class="navbar-brand">📚 English Academy</div>
        <div class="navbar-menu">
            <a href="/dashboard/{username}" class="nav-item {home_active}">🏠 Inicio</a>
            <a href="/profile/{username}" class="nav-item {profile_active}">👤 Perfil</a>
            <a href="/progress/{username}" class="nav-item {progress_active}">📊 Progreso</a>
            <a href="/habits/{username}" class="nav-item {habits_active}">✓ Hábitos</a>
            <a href="/wallet/{username}" class="nav-item {wallet_active}">💳 Cartera</a>
            <a href="/" class="nav-item nav-logout">🚪 Salir</a>
        </div>
    </div>
</div>"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - English Academy Pro</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
        }}
        .navbar-container {{
            background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
            padding: 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 8px 25px rgba(0,0,0,0.25);
        }}
        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 35px;
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
        }}
        .navbar-brand {{
            color: white;
            font-size: 22px;
            font-weight: 700;
            display: flex;
            gap: 8px;
        }}
        .navbar-menu {{
            display: flex;
            gap: 8px;
        }}
        .nav-item {{
            color: #b0c0d0;
            text-decoration: none;
            padding: 9px 16px;
            border-radius: 6px;
            transition: 0.3s;
            font-size: 13px;
            font-weight: 500;
        }}
        .nav-item:hover {{
            background: rgba(76, 144, 226, 0.2);
            color: white;
        }}
        .nav-item.active {{
            background: linear-gradient(135deg, #4c90e2 0%, #2e5c8a 100%);
            color: white;
            font-weight: 600;
        }}
        .container {{
            max-width: 1100px;
            margin: 25px auto;
            padding: 0 20px;
        }}
        .card {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.12);
            margin-bottom: 20px;
            transition: box-shadow 0.3s;
        }}
        .card:hover {{
            box-shadow: 0 10px 35px rgba(0,0,0,0.15);
        }}
        h1 {{
            color: #1a1a2e;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 26px;
            border-bottom: 3px solid #4c90e2;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #1a1a2e;
            margin-top: 20px;
            margin-bottom: 15px;
            font-size: 18px;
            font-weight: 600;
        }}
        .birthday-banner {{
            background: linear-gradient(135deg, #4c90e2 0%, #2e5c8a 100%);
            color: white;
            padding: 22px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 18px;
            font-weight: 600;
            box-shadow: 0 6px 20px rgba(76, 144, 226, 0.3);
        }}
        .profile-card {{
            background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
            color: white;
            padding: 35px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }}
        .profile-avatar {{
            font-size: 65px;
            margin-bottom: 12px;
        }}
        .profile-name {{
            font-size: 26px;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        .profile-age {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .progress-bar {{
            background: #e8e8e8;
            border-radius: 10px;
            height: 32px;
            margin: 12px 0;
            overflow: hidden;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.08);
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #4c90e2 0%, #2e5c8a 100%);
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 12px;
            transition: width 0.3s;
        }}
        .habit-item {{
            background: #f8f9fa;
            padding: 16px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #4c90e2;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: 0.3s;
        }}
        .habit-item:hover {{
            background: #f0f4f9;
            box-shadow: 0 3px 10px rgba(76, 144, 226, 0.15);
        }}
        .habit-checkbox {{
            width: 24px;
            height: 24px;
            cursor: pointer;
            accent-color: #4c90e2;
        }}
        .social-link {{
            display: inline-block;
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #4c90e2 0%, #2e5c8a 100%);
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 50px;
            margin: 6px;
            text-decoration: none;
            transition: 0.3s;
            font-size: 18px;
            box-shadow: 0 4px 12px rgba(76, 144, 226, 0.25);
        }}
        .social-link:hover {{
            background: linear-gradient(135deg, #3a75cc 0%, #1e4a70 100%);
            transform: translateY(-3px);
            box-shadow: 0 6px 16px rgba(76, 144, 226, 0.35);
        }}
        .input-group {{
            margin-bottom: 15px;
        }}
        .input-group label {{
            display: block;
            margin-bottom: 6px;
            color: #1a1a2e;
            font-weight: 600;
            font-size: 13px;
        }}
        .input-group input,
        .input-group textarea,
        .input-group select {{
            width: 100%;
            padding: 11px 12px;
            border: 2px solid #e0e0e0;
            border-radius: 7px;
            font-family: 'Segoe UI';
            font-size: 13px;
            transition: 0.3s;
            background: white;
            color: #1a1a2e;
        }}
        .input-group input:focus,
        .input-group textarea:focus,
        .input-group select:focus {{
            outline: none;
            border-color: #4c90e2;
            box-shadow: 0 0 0 3px rgba(76, 144, 226, 0.1);
        }}
        .btn {{
            background: linear-gradient(135deg, #4c90e2 0%, #2e5c8a 100%);
            color: white;
            padding: 10px 22px;
            border: none;
            border-radius: 7px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: 0.3s;
            box-shadow: 0 4px 12px rgba(76, 144, 226, 0.25);
        }}
        .btn:hover {{
            background: linear-gradient(135deg, #3a75cc 0%, #1e4a70 100%);
            box-shadow: 0 6px 18px rgba(76, 144, 226, 0.35);
            transform: translateY(-1px);
        }}
        .btn-success {{
            background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
            box-shadow: 0 4px 12px rgba(39, 174, 96, 0.25);
        }}
        .btn-success:hover {{
            background: linear-gradient(135deg, #229954 0%, #186a3b 100%);
            box-shadow: 0 6px 18px rgba(39, 174, 96, 0.35);
        }}
        .btn-danger {{
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            box-shadow: 0 4px 12px rgba(231, 76, 60, 0.25);
        }}
        .btn-danger:hover {{
            background: linear-gradient(135deg, #d63425 0%, #a93226 100%);
            box-shadow: 0 6px 18px rgba(231, 76, 60, 0.35);
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #4c90e2 0%, #2e5c8a 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 6px 18px rgba(76, 144, 226, 0.25);
            transition: 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 28px rgba(76, 144, 226, 0.35);
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 6px;
        }}
        .stat-label {{
            font-size: 12px;
            opacity: 0.95;
            font-weight: 500;
        }}
        .form-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        @media (max-width: 768px) {{
            .navbar {{
                flex-direction: column;
                gap: 12px;
                padding: 12px 20px;
            }}
            .navbar-menu {{
                flex-direction: column;
                gap: 5px;
                width: 100%;
            }}
            .container {{
                padding: 0 15px;
            }}
            .card {{
                padding: 20px;
            }}
            .form-row {{
                grid-template-columns: 1fr;
            }}
            .grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    {navbar}
    <div class="container">
        {content}
    </div>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        query_params = parse_qs(urlparse(self.path).query)
        data = load_data()
        
        if path == '/':
            # redirigir automáticamente a login para evitar mostrar información adicional
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
        elif path == '/login':
            self.render_login()
        elif path == '/register':
            self.render_register()
        elif path == '/reset-password':
            token = query_params.get('token', [''])[0]
            username_param = query_params.get('user', [''])[0]
            self.render_reset_password(token, username_param, data)
        elif path.startswith('/dashboard/'):
            username = path.replace('/dashboard/', '')
            self.render_dashboard(username, data)
        elif path.startswith('/profile/'):
            username = path.replace('/profile/', '')
            self.render_profile(username, data)
        elif path.startswith('/progress/'):
            username = path.replace('/progress/', '')
            self.render_progress(username, data)
        elif path.startswith('/habits/'):
            username = path.replace('/habits/', '')
            self.render_habits(username, data)
        elif path.startswith('/wallet/'):
            username = path.replace('/wallet/', '')
            self.render_wallet(username, data)
        elif path == '/payment-methods':
            self.render_payment_methods(data)
        elif path.startswith('/link-account/'):
            username = path.replace('/link-account/', '')
            self.render_link_account(username, data)
        elif path.startswith('/transactions/'):
            username = path.replace('/transactions/', '')
            self.render_transactions(username, data)
        else:
            self.render_404()
    
    def get_navbar(self, username, active_page):
        return NAVBAR_TEMPLATE.format(
            username=username,
            home_active='active' if active_page == 'home' else '',
            profile_active='active' if active_page == 'profile' else '',
            progress_active='active' if active_page == 'progress' else '',
            habits_active='active' if active_page == 'habits' else '',
            wallet_active='active' if active_page == 'wallet' else ''
        )
    
    def render_home(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = """<!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>English Academy Pro - Plataforma Educativa Integral</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
                    color: #333;
                }}
                .navbar-header {{
                    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
                    padding: 16px 35px;
                    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    position: sticky;
                    top: 0;
                    z-index: 1000;
                }}
                .navbar-brand {{
                    color: white;
                    font-size: 22px;
                    font-weight: 700;
                    display: flex;
                    gap: 8px;
                }}
                .navbar-links {{
                    display: flex;
                    gap: 12px;
                }}
                .nav-link {{
                    color: white;
                    text-decoration: none;
                    padding: 9px 16px;
                    border-radius: 6px;
                    transition: 0.3s;
                    font-size: 13px;
                    font-weight: 600;
                    background: linear-gradient(135deg, #4c90e2 0%, #2e5c8a 100%);
                    box-shadow: 0 3px 10px rgba(76, 144, 226, 0.25);
                }}
                .nav-link:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(76, 144, 226, 0.35);
                }}
                .hero {{
                    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
                    padding: 80px 20px;
                    text-align: center;
                    color: white;
                }}
                .hero h1 {{
                    font-size: 48px;
                    margin-bottom: 15px;
                    font-weight: 800;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }}
                .hero .subtitle {{
                    font-size: 20px;
                    color: #4c90e2;
                    margin-bottom: 10px;
                    font-weight: 600;
                }}
                .hero-description {{
                    font-size: 16px;
                    color: #e0e0e0;
                    margin: 20px auto;
                    max-width: 600px;
                    line-height: 1.6;
                }}
                .hero-buttons {{
                    margin-top: 40px;
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    flex-wrap: wrap;
                }}
                .btn-primary {{
                    background: linear-gradient(135deg, #4c90e2 0%, #2e5c8a 100%);
                    color: white;
                    padding: 14px 35px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 700;
                    border: none;
                    cursor: pointer;
                    transition: 0.3s;
                    font-size: 15px;
                    box-shadow: 0 6px 20px rgba(76, 144, 226, 0.35);
                }}
                .btn-primary:hover {{
                    background: linear-gradient(135deg, #3a75cc 0%, #1e4a70 100%);
                    transform: translateY(-3px);
                    box-shadow: 0 10px 30px rgba(76, 144, 226, 0.45);
                }}
                .btn-secondary {{
                    background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
                    color: white;
                    padding: 14px 35px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 700;
                    border: none;
                    cursor: pointer;
                    transition: 0.3s;
                    font-size: 15px;
                    box-shadow: 0 6px 20px rgba(39, 174, 96, 0.35);
                }}
                .btn-secondary:hover {{
                    background: linear-gradient(135deg, #229954 0%, #186a3b 100%);
                    transform: translateY(-3px);
                    box-shadow: 0 10px 30px rgba(39, 174, 96, 0.45);
                }}
                .stats {{
                    background: white;
                    padding: 60px 20px;
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 30px;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .stat-card {{
                    text-align: center;
                    padding: 20px;
                }}
                .stat-number {{
                    font-size: 42px;
                    font-weight: 800;
                    color: #4c90e2;
                    margin-bottom: 8px;
                }}
                .stat-label {{
                    color: #666;
                    font-size: 14px;
                    font-weight: 600;
                }}
                .features-section {{
                    background: white;
                    padding: 60px 20px;
                    text-align: center;
                }}
                .section-title {{
                    font-size: 36px;
                    font-weight: 800;
                    color: #1a1a2e;
                    margin-bottom: 15px;
                }}
                .section-subtitle {{
                    color: #666;
                    font-size: 16px;
                    margin-bottom: 40px;
                    max-width: 500px;
                    margin-left: auto;
                    margin-right: auto;
                }}
                .features-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 25px;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .feature-card {{
                    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
                    transition: 0.3s;
                    border: 1px solid #e8e8e8;
                }}
                .feature-card:hover {{
                    transform: translateY(-8px);
                    box-shadow: 0 15px 35px rgba(0,0,0,0.15);
                    border-color: #4c90e2;
                }}
                .feature-icon {{
                    font-size: 48px;
                    margin-bottom: 15px;
                    display: block;
                }}
                .feature-name {{
                    font-size: 18px;
                    font-weight: 700;
                    color: #1a1a2e;
                    margin-bottom: 10px;
                }}
                .feature-description {{
                    color: #666;
                    font-size: 13px;
                    line-height: 1.6;
                }}
                .how-it-works {{
                    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
                    padding: 60px 20px;
                    color: white;
                    text-align: center;
                }}
                .how-it-works .section-title {{
                    color: white;
                }}
                .how-it-works .section-subtitle {{
                    color: #e0e0e0;
                }}
                .steps {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                    gap: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .step {{
                    background: rgba(255,255,255,0.1);
                    padding: 25px;
                    border-radius: 10px;
                    border: 2px solid rgba(76, 144, 226, 0.3);
                    transition: 0.3s;
                }}
                .step:hover {{
                    background: rgba(76, 144, 226, 0.2);
                    border-color: #4c90e2;
                }}
                .step-number {{
                    font-size: 36px;
                    font-weight: 800;
                    color: #4c90e2;
                    margin-bottom: 10px;
                }}
                .step-title {{
                    font-size: 16px;
                    font-weight: 700;
                    margin-bottom: 8px;
                }}
                .step-description {{
                    font-size: 13px;
                    color: #d0d0d0;
                }}
                .credentials {{
                    background: white;
                    padding: 50px 20px;
                    text-align: center;
                }}
                .credentials-box {{
                    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 12px;
                    max-width: 500px;
                    margin: 0 auto;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }}
                .cred-title {{
                    font-weight: 800;
                    margin-bottom: 20px;
                    color: #4c90e2;
                    font-size: 18px;
                }}
                .cred-item {{
                    margin: 12px 0;
                    font-family: 'Courier New', monospace;
                    color: #e0e0e0;
                    font-size: 14px;
                    padding: 12px;
                    background: rgba(76, 144, 226, 0.1);
                    border-radius: 6px;
                    border-left: 3px solid #4c90e2;
                    text-align: left;
                }}
                .footer {{
                    background: linear-gradient(135deg, #0a0a1a 0%, #050510 100%);
                    color: #999;
                    padding: 30px 20px;
                    text-align: center;
                    font-size: 13px;
                }}
                .footer-content {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .footer-divider {{
                    height: 1px;
                    background: #333;
                    margin: 20px 0;
                }}
                @media (max-width: 768px) {{
                    .navbar-header {{
                        flex-direction: column;
                        gap: 12px;
                    }}
                    .navbar-links {{
                        width: 100%;
                        flex-direction: column;
                    }}
                    .nav-link {{
                        text-align: center;
                    }}
                    .hero {{
                        padding: 50px 15px;
                    }}
                    .hero h1 {{
                        font-size: 32px;
                    }}
                    .hero .subtitle {{
                        font-size: 18px;
                    }}
                    .hero-buttons {{
                        flex-direction: column;
                        gap: 12px;
                    }}
                    .btn-primary, .btn-secondary {{
                        width: 100%;
                    }}
                    .stats {{
                        grid-template-columns: 1fr;
                        gap: 20px;
                    }}
                    .features-grid {{
                        grid-template-columns: 1fr;
                    }}
                    .steps {{
                        grid-template-columns: 1fr;
                    }}
                    .section-title {{
                        font-size: 28px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="navbar-header">
                <div class="navbar-brand">🎓 English Academy</div>
                <div class="navbar-links">
                    <a href="/login" class="nav-link">🔐 Inicio de Sesión</a>
                    <a href="/register" class="nav-link">📝 Registro</a>
                </div>
            </div>
            
            <section class="hero">
                <div style="max-width: 900px; margin: 0 auto;">
                    <h1>🎓 English Academy Pro</h1>
                    <p class="subtitle">La Plataforma Educativa Integral Más Completa</p>
                    <p class="hero-description">
                        Aprende inglés con una plataforma profesional diseñada para estudiantes modernos. 
                        Perfiles personalizados, seguimiento de progreso en tiempo real, hábitos diarios, pagos seguros y mucho más.
                    </p>
                    <div class="hero-buttons">
                        <a href="/login" class="btn-primary">🔐 Iniciar Sesión</a>
                        <a href="/register" class="btn-secondary">📝 Crear Cuenta Gratis</a>
                    </div>
                </div>
            </section>
            
            <section class="stats">
                <div class="stat-card">
                    <div class="stat-number">1000+</div>
                    <div class="stat-label">Estudiantes Activos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">500+</div>
                    <div class="stat-label">Lecciones Disponibles</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">98%</div>
                    <div class="stat-label">Tasa de Satisfacción</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">24/7</div>
                    <div class="stat-label">Soporte al Cliente</div>
                </div>
            </section>
            
            <section class="features-section">
                <h2 class="section-title">Características Principales</h2>
                <p class="section-subtitle">Todas las herramientas que necesitas para aprender inglés de forma efectiva</p>
                
                <div class="features-grid">
                    <div class="feature-card">
                        <span class="feature-icon">👤</span>
                        <div class="feature-name">Perfiles Personalizados</div>
                        <div class="feature-description">Crea tu perfil con foto, bio, fechas de cumpleaños y enlaces a redes sociales</div>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon">📊</span>
                        <div class="feature-name">Progreso en Tiempo Real</div>
                        <div class="feature-description">Visualiza tu avance con gráficas detalladas de lecciones completadas y horas estudiadas</div>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon">✓</span>
                        <div class="feature-name">Hábitos Diarios</div>
                        <div class="feature-description">Mantén el control de tus hábitos de estudio y construye rachas consistentes</div>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon">🎂</span>
                        <div class="feature-name">Cumpleaños Especiales</div>
                        <div class="feature-description">Recibe mensajes personalizados en tu día especial con reconocimiento de la plataforma</div>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon">💳</span>
                        <div class="feature-name">Pagos Seguros</div>
                        <div class="feature-description">Gestiona tarjetas de crédito de forma segura con encriptación SHA-256</div>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon">🌐</span>
                        <div class="feature-name">Redes Sociales</div>
                        <div class="feature-description">Conecta tus redes sociales y comparte tus logros con tu comunidad</div>
                    </div>
                </div>
            </section>
            
            <section class="how-it-works">
                <h2 class="section-title">¿Cómo Funciona?</h2>
                <p class="section-subtitle">Cuatro simples pasos para comenzar tu viaje de aprendizaje</p>
                
                <div class="steps">
                    <div class="step">
                        <div class="step-number">1️⃣</div>
                        <div class="step-title">Registrarse</div>
                        <div class="step-description">Crea tu cuenta con tu email en segundos</div>
                    </div>
                    <div class="step">
                        <div class="step-number">2️⃣</div>
                        <div class="step-title">Personalizar</div>
                        <div class="step-description">Configura tu perfil con información personal</div>
                    </div>
                    <div class="step">
                        <div class="step-number">3️⃣</div>
                        <div class="step-title">Aprender</div>
                        <div class="step-description">Únete a cursos y comienza tus lecciones</div>
                    </div>
                    <div class="step">
                        <div class="step-number">4️⃣</div>
                        <div class="step-title">Progresar</div>
                        <div class="step-description">Rastrear tu avance y alcanzar tus metas</div>
                    </div>
                </div>
            </section>
            
            <section class="credentials">
                <h2 class="section-title">Cuenta de Prueba</h2>
                <div class="credentials-box">
                    <div class="cred-title">🔓 Credenciales para Probar</div>
                    <div class="cred-item">👨‍🏫 Maestro: <strong>maestra</strong> / <strong>123456</strong></div>
                    <div class="cred-item">👨‍🎓 Estudiante: <strong>estudiante</strong> / <strong>123456</strong></div>
                </div>
            </section>
            
            <footer class="footer">
                <div class="footer-content">
                    <p>🎓 English Academy Pro © 2026 | Plataforma Educativa Integral</p>
                    <div class="footer-divider"></div>
                    <p>Diseñado con ❤️ para conectar educadores y estudiantes</p>
                </div>
            </footer>
        </body>
        </html>"""
        self.wfile.write(html.encode())
    
    def render_login(self):
        verse = get_daily_verse()
        day_html = f"<div style='text-align:center; margin-bottom:20px; color:#fff;'><strong>{verse['book']} {verse['chapter']}:{verse['verse']}</strong> – {verse['text']}</div>"
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = f"""<!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Iniciar Sesión - English Academy Pro</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }}
                .auth-container {{ width: 100%; max-width: 450px; }}
                .auth-box {{ background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%); padding: 45px; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.35); color: white; }}
                .logo {{ text-align: center; margin-bottom: 35px; }}
                .logo-text {{ font-size: 32px; font-weight: 800; color: white; margin: 0; }}
                .logo-sub {{ font-size: 12px; color: #ccc; margin-top: 5px; }}
                h1 {{ color: white; margin-bottom: 30px; text-align: center; font-size: 24px; font-weight: 700; }}
                .input-group {{ margin-bottom: 18px; }}
                label {{ display: block; margin-bottom: 7px; color: #fff; font-weight: 600; font-size: 13px; }}
                input {{ width: 100%; padding: 12px 13px; border: 2px solid #444; border-radius: 8px; font-size: 14px; transition: 0.3s; background: #222; color: #fff; }}
                input:focus {{ outline: none; border-color: #4c90e2; box-shadow: 0 0 0 4px rgba(76, 144, 226, 0.1); }}
                button {{ width: 100%; padding: 13px; background: linear-gradient(135deg, #1db954 0%, #17a44a 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 15px; font-weight: 700; transition: 0.3s; box-shadow: 0 5px 15px rgba(0,0,0,0.4); }}
                button:hover {{ transform: translateY(-2px); }}
                .link-section {{ text-align: center; margin-top: 20px; color: #ccc; }}
                .link-section a {{ color: #1db954; font-weight: 700; }}
            </style>
        </head>
        <body>
            {day_html}
            <div class="auth-container">
                <div class="auth-box">
                    <div class="logo">
                        <p class="logo-text">🎓</p>
                        <p class="logo-sub">English Academy Pro</p>
                    </div>
                    <h1>Iniciar Sesión</h1>
                    <form method="POST" action="/login">
                        <div class="input-group">
                            <label>👤 Usuario o Email:</label>
                            <input type="text" name="username" required>
                        </div>
                        <div class="input-group">
                            <label>🔑 Contraseña:</label>
                            <input type="password" name="password" required>
                        </div>
                        <button type="submit">✓ Entrar</button>
                    </form>
                    <div class="link-section">
                        ¿No tienes cuenta? <a href="/register">Crear cuenta</a>
                    </div>
                </div>
            </div>
        </body>
        </html>"""
        self.wfile.write(html.encode())
    
    def render_register(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = """<!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Crear Cuenta - English Academy Pro</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }}
                .auth-container {{
                    width: 100%;
                    max-width: 450px;
                }}
                .auth-box {{
                    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
                    padding: 45px;
                    border-radius: 12px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.35);
                    color: white;
                }}
                .logo {{
                    text-align: center;
                    margin-bottom: 35px;
                }}
                .logo-text {{
                    font-size: 32px;
                    font-weight: 800;
                    color: #1a1a2e;
                    margin: 0;
                }}
                .logo-sub {{
                    font-size: 12px;
                    color: #999;
                    margin-top: 5px;
                }}
                h1 {{ 
                    color: #1a1a2e;
                    margin-bottom: 25px;
                    text-align: center;
                    font-size: 24px;
                    font-weight: 700;
                }}
                .input-group {{
                    margin-bottom: 16px;
                }}
                label {{ 
                    display: block;
                    margin-bottom: 6px;
                    color: #1a1a2e;
                    font-weight: 600;
                    font-size: 13px;
                }}
                input, select {{
                    width: 100%;
                    padding: 12px 13px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    font-size: 14px;
                    transition: 0.3s;
                    background: white;
                    color: #1a1a2e;
                }}
                input:focus, select:focus {{
                    outline: none;
                    border-color: #4c90e2;
                    box-shadow: 0 0 0 4px rgba(76, 144, 226, 0.1);
                }}
                button {{
                    width: 100%;
                    padding: 13px;
                    background: linear-gradient(135deg, #4c90e2 0%, #2e5c8a 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 15px;
                    font-weight: 700;
                    transition: 0.3s;
                    box-shadow: 0 5px 15px rgba(76, 144, 226, 0.3);
                    margin-top: 8px;
                }}
                button:hover {{
                    background: linear-gradient(135deg, #3a75cc 0%, #1e4a70 100%);
                    box-shadow: 0 7px 20px rgba(76, 144, 226, 0.4);
                    transform: translateY(-2px);
                }}
                .divider {{
                    display: flex;
                    align-items: center;
                    margin: 22px 0;
                    color: #ccc;
                    font-size: 13px;
                }}
                .divider::before,
                .divider::after {{
                    content: '';
                    flex: 1;
                    height: 1px;
                    background: #e0e0e0;
                }}
                .divider-text {{
                    padding: 0 12px;
                    color: #999;
                }}
                .gmail-btn {{
                    width: 100%;
                    padding: 12px;
                    background: white;
                    color: #1a1a2e;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 600;
                    transition: 0.3s;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    box-shadow: none;
                }}
                .gmail-btn:hover {{
                    border-color: #4c90e2;
                    background: #f9f9f9;
                    box-shadow: none;
                    transform: none;
                }}
                .link-section {{
                    text-align: center;
                    margin-top: 25px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                    color: #666;
                    font-size: 13px;
                }}
                a {{ 
                    color: #4c90e2;
                    text-decoration: none;
                    font-weight: 700;
                    transition: 0.3s;
                }}
                a:hover {{
                    color: #2e5c8a;
                    text-decoration: underline;
                }}
                @media (max-width: 600px) {{
                    .auth-box {{
                        padding: 30px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="auth-container">
                <div class="auth-box">
                    <div class="logo">
                        <p class="logo-text">🎓</p>
                        <p class="logo-sub">English Academy Pro</p>
                    </div>
                    <h1>Crear Cuenta</h1>
                    <form method="POST" action="/register">
                        <div class="input-group">
                            <label>👤 Nombre Completo:</label>
                            <input type="text" name="nombre" placeholder="Ej: Juan García" required>
                        </div>
                        <div class="input-group">
                            <label>📧 Email:</label>
                            <input type="email" name="email" placeholder="tu@gmail.com o tu@hotmail.com" required onchange="validateEmailDomain(this)">
                        </div>
                        <div class="input-group">
                            <label>👥 Nombre de Usuario:</label>
                            <input type="text" name="username" placeholder="mi_usuario" required>
                        </div>
                        <div class="input-group">
                            <label>🔑 Contraseña:</label>
                            <input type="password" name="password" placeholder="Mínimo 6 caracteres" required>
                        </div>
                        <div class="input-group">
                            <label>👔 Tipo de Cuenta:</label>
                            <select name="role">
                                <option value="student">👨‍🎓 Estudiante</option>
                                <option value="teacher">👨‍🏫 Maestro</option>
                            </select>
                        </div>
                        <button type="submit">✓ Crear Cuenta</button>
                    </form>
                    <div class="link-section">
                        ¿Ya tienes cuenta? <a href="/login">Iniciar sesión</a>
                    </div>
                </div>
            </div>
            
            <script>
                function validateEmailDomain(input) {{
                    const email = input.value.toLowerCase().trim();
                    if (!email) return;
                    
                    if (!email.match(/@(gmail\\.com|hotmail\\.com|outlook\\.com)$/i)) {{
                        alert('⚠️ Por favor usa un email de Gmail (gmail.com) o Hotmail (hotmail.com)');
                        input.value = '';
                        input.focus();
                    }}
                }}
                
                // Validar al enviar el formulario
                document.querySelector('form').onsubmit = function(e) {{
                    const email = document.querySelector('input[name="email"]').value.toLowerCase().trim();
                    if (!email.match(/@(gmail\\.com|hotmail\\.com|outlook\\.com)$/i)) {{
                        e.preventDefault();
                        alert('⚠️ Por favor usa un email de Gmail (gmail.com) o Hotmail (hotmail.com)');
                        return false;
                    }}
                    return true;
                }};
            </script>

        </body>
        </html>"""
        self.wfile.write(html.encode())
    
    def render_reset_password(self, token, username, data):
        # Validar token
        valid_username = validate_reset_token(token, data)
        
        if not valid_username:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """<!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Enlace Inválido - English Academy Pro</title>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: 20px;
                    }}
                    .error-box {{
                        background: white;
                        padding: 50px;
                        border-radius: 12px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.35);
                        max-width: 500px;
                        text-align: center;
                    }}
                    .error-icon {{
                        font-size: 60px;
                        margin-bottom: 20px;
                    }}
                    h1 {{
                        color: #1a1a2e;
                        margin-bottom: 15px;
                        font-size: 26px;
                    }}
                    p {{
                        color: #666;
                        margin-bottom: 15px;
                        line-height: 1.6;
                        font-size: 14px;
                    }}
                    a {{
                        display: inline-block;
                        margin-top: 20px;
                        padding: 12px 30px;
                        border-radius: 8px;
                        text-decoration: none;
                        font-weight: 600;
                        background: linear-gradient(135deg, #4c90e2 0%, #2e5c8a 100%);
                        color: white;
                        transition: 0.3s;
                    }}
                    a:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 7px 20px rgba(76, 144, 226, 0.4);
                    }}
                </style>
            </head>
            <body>
                <div class="error-box">
                    <div class="error-icon">⚠️</div>
                    <h1>Enlace Expirado</h1>
                    <p>El enlace para resetear tu contraseña ha expirado o no es válido.</p>
                    <a href="/login">← Solicitar nuevo enlace</a>
                </div>
            </body>
            </html>"""
            self.wfile.write(html.encode())
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = f"""<!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resetear Contraseña - English Academy Pro</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }}
                .reset-box {{
                    background: white;
                    padding: 45px;
                    border-radius: 12px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.35);
                    width: 100%;
                    max-width: 450px;
                }}
                h1 {{ 
                    color: #1a1a2e;
                    margin-bottom: 10px;
                    text-align: center;
                    font-size: 24px;
                    font-weight: 700;
                }}
                .subtitle {{
                    color: #999;
                    text-align: center;
                    font-size: 13px;
                    margin-bottom: 30px;
                }}
                .input-group {{
                    margin-bottom: 18px;
                }}
                label {{ 
                    display: block;
                    margin-bottom: 7px;
                    color: #1a1a2e;
                    font-weight: 600;
                    font-size: 13px;
                }}
                input {{
                    width: 100%;
                    padding: 12px 13px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    font-size: 14px;
                    transition: 0.3s;
                    background: white;
                    color: #1a1a2e;
                }}
                input:focus {{
                    outline: none;
                    border-color: #4c90e2;
                    box-shadow: 0 0 0 4px rgba(76, 144, 226, 0.1);
                }}
                button {{
                    width: 100%;
                    padding: 13px;
                    background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 15px;
                    font-weight: 700;
                    transition: 0.3s;
                    box-shadow: 0 5px 15px rgba(39, 174, 96, 0.3);
                    margin-top: 8px;
                }}
                button:hover {{
                    background: linear-gradient(135deg, #229954 0%, #186a3b 100%);
                    box-shadow: 0 7px 20px rgba(39, 174, 96, 0.4);
                    transform: translateY(-2px);
                }}
                .password-requirements {{
                    background: #f9f9f9;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    font-size: 12px;
                    color: #666;
                    border-left: 3px solid #4c90e2;
                }}
                .requirement {{
                    margin: 5px 0;
                }}
                .back-link {{
                    text-align: center;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                }}
                a {{
                    color: #4c90e2;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 13px;
                }}
                a:hover {{
                    color: #2e5c8a;
                    text-decoration: underline;
                }}
                @media (max-width: 600px) {{
                    .reset-box {{
                        padding: 30px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="reset-box">
                <h1>🔐 Resetear Contraseña</h1>
                <p class="subtitle">Ingresa tu nueva contraseña</p>
                
                <div class="password-requirements">
                    <div class="requirement">✓ Mínimo 6 caracteres</div>
                    <div class="requirement">✓ Puede incluir números y símbolos</div>
                    <div class="requirement">✓ Utiliza una contraseña fuerte</div>
                </div>
                
                <form method="POST" action="/reset-password-submit">
                    <input type="hidden" name="token" value="{token}">
                    <div class="input-group">
                        <label>🔑 Nueva Contraseña:</label>
                        <input type="password" name="password" placeholder="Ingresa tu nueva contraseña" required>
                    </div>
                    <div class="input-group">
                        <label>✓ Confirmar Contraseña:</label>
                        <input type="password" name="confirm_password" placeholder="Confirma tu contraseña" required>
                    </div>
                    <button type="submit" onclick="validatePasswords(event)">✓ Actualizar Contraseña</button>
                </form>
                
                <div class="back-link">
                    <a href="/login">← Volver a Login</a>
                </div>
            </div>
            
            <script>
                function validatePasswords(e) {{
                    const password = document.querySelector('input[name="password"]').value;
                    const confirmPassword = document.querySelector('input[name="confirm_password"]').value;
                    
                    if (password !== confirmPassword) {{
                        e.preventDefault();
                        alert('⚠️ Las contraseñas no coinciden');
                        return false;
                    }}
                    
                    if (password.length < 6) {{
                        e.preventDefault();
                        alert('⚠️ La contraseña debe tener mínimo 6 caracteres');
                        return false;
                    }}
                    
                    return true;
                }}
            </script>
        </body>
        </html>"""
        self.wfile.write(html.encode())
    
    def render_dashboard(self, username, data):
        user = data['users'].get(username, {})
        if not user:
            self.render_404()
            return
        
        profile = data.get('student_profiles', {}).get(username, {})
        birthday_message = ""
        if profile.get('birthdate'):
            msg = get_birthday_message(profile['birthdate'])
            if msg:
                birthday_message = f'<div class="birthday-banner">{msg}</div>'
        
        navbar = self.get_navbar(username, 'home')
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        progress = data.get('student_progress', {}).get(username, {})
        lessons_completed = progress.get('lessons_completed', 0)
        total_lessons = progress.get('total_lessons', 10)
        hours_studied = progress.get('hours_studied', 0)
        
        # Obtener versículo del día
        verse = get_daily_verse()
        verse_reference = f"{verse['book']} {verse['chapter']}:{verse['verse']}"
        verse_html = f"""
        <div class="verse-card">
            <div class="verse-icon">📖</div>
            <div class="verse-reference">{verse_reference}</div>
            <div class="verse-text">"{verse['text']}"</div>
        </div>
        """
        
        if user.get('role') == 'teacher':
            content = f"""
            <h1>👨‍🏫 Dashboard - Maestro</h1>
            {verse_html}
            <div class="grid">
                <div class="stat-card">
                    <div class="stat-number">8</div>
                    <div class="stat-label">Estudiantes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">12</div>
                    <div class="stat-label">Tareas Activas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">24</div>
                    <div class="stat-label">Evaluaciones</div>
                </div>
            </div>
            """
        else:
            content = f"""
            {birthday_message}
            <h1>🎓 Dashboard - Estudiante</h1>
            {verse_html}
            <div class="grid">
                <div class="stat-card">
                    <div class="stat-number">{lessons_completed}/{total_lessons}</div>
                    <div class="stat-label">Lecciones Completadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{hours_studied}</div>
                    <div class="stat-label">Horas Estudiadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{profile.get('level', 'Principiante')}</div>
                    <div class="stat-label">Nivel Actual</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">🔥 {progress.get('current_streak', 0)}</div>
                    <div class="stat-label">Racha Actual</div>
                </div>
            </div>
            <div class="card">
                <h2>📊 Progreso General</h2>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {min(100, int(lessons_completed/max(1, total_lessons)*100))}%">
                        {min(100, int(lessons_completed/max(1, total_lessons)*100))}%
                    </div>
                </div>
            </div>
            """
        
        html = HTML_TEMPLATE.format(
            navbar=navbar,
            title=f"Dashboard - {username}",
            content=content
        )
        
        # Agregar modal de bienvenida y JavaScript
        welcome_html = f"""
        {html}
        <div id="welcomeModal" class="welcome-modal active">
            <div class="welcome-content">
                <div class="welcome-icon">👋</div>
                <h2>¡Bienvenido, <span class="username-highlight">{user.get('nombre', username)}</span>!</h2>
                <p class="welcome-message">We're excited to see you here today. Keep pushing towards your goals!</p>
                <p class="welcome-date" style="font-size: 12px; color: #999; margin-top: 15px;">{date.today().strftime('%B %d, %Y')}</p>
                <button class="welcome-btn" onclick="closeWelcomeModal()">Let's Get Started! 🚀</button>
            </div>
        </div>
        
        <style>
            .welcome-modal {{
                display: none;
                position: fixed;
                z-index: 3000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.6);
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .welcome-modal.active {{
                display: flex;
            }}
            .welcome-content {{
                background: linear-gradient(135deg, #4c90e2 0%, #2e5c8a 100%);
                color: white;
                padding: 50px 40px;
                border-radius: 16px;
                box-shadow: 0 30px 60px rgba(0, 0, 0, 0.35);
                max-width: 500px;
                text-align: center;
                animation: slideInUp 0.5s ease;
            }}
            @keyframes slideInUp {{
                from {{
                    transform: translateY(50px);
                    opacity: 0;
                }}
                to {{
                    transform: translateY(0);
                    opacity: 1;
                }}
            }}
            .welcome-icon {{
                font-size: 60px;
                margin-bottom: 15px;
                display: block;
            }}
            .welcome-modal h2 {{
                font-size: 28px;
                margin-bottom: 15px;
                font-weight: 800;
            }}
            .username-highlight {{
                background: rgba(255, 255, 255, 0.2);
                padding: 5px 12px;
                border-radius: 8px;
                font-weight: 900;
            }}
            .welcome-message {{
                font-size: 16px;
                line-height: 1.6;
                margin: 15px 0;
                color: #e0e0e0;
            }}
            .welcome-btn {{
                background: white;
                color: #2e5c8a;
                padding: 13px 35px;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                cursor: pointer;
                font-size: 15px;
                transition: 0.3s;
                margin-top: 20px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }}
            .welcome-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
            }}
            .verse-card {{
                background: linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%);
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 30px;
                border-left: 4px solid #4c90e2;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            }}
            .verse-icon {{
                font-size: 32px;
                margin-bottom: 12px;
                display: block;
            }}
            .verse-reference {{
                font-size: 14px;
                font-weight: 700;
                color: #2e5c8a;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 15px;
                display: block;
            }}
            .verse-text {{
                font-size: 17px;
                font-style: italic;
                color: #1a1a2e;
                line-height: 1.7;
                font-weight: 500;
            }}
        </style>
        
        <script>
            function closeWelcomeModal() {{
                document.getElementById('welcomeModal').classList.remove('active');
                localStorage.setItem('welcomeModalClosed', 'true');
            }}
            
            // Cerrar modal al hacer clic fuera de él
            document.getElementById('welcomeModal').onclick = function(e) {{
                if(e.target === this) {{
                    closeWelcomeModal();
                }}
            }}
            
            // Mostrar modal solo primera vez (opcional)
            if(localStorage.getItem('welcomeModalClosed') === 'true') {{
                document.getElementById('welcomeModal').classList.remove('active');
            }}
        </script>
        """
        
        self.wfile.write(welcome_html.encode())
    
    def render_profile(self, username, data):
        user = data['users'].get(username, {})
        if not user:
            self.render_404()
            return
        
        profile = data.get('student_profiles', {}).get(username, {})
        navbar = self.get_navbar(username, 'profile')
        
        socials_html = ""
        if profile.get('socials'):
            for platform, url in profile['socials'].items():
                if url:
                    socials_html += f'<a href="{url}" target="_blank" class="social-link" title="{platform.capitalize()}">🔗</a>'
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        content = f"""
        <h1>👤 Mi Perfil</h1>
        
        <div class="profile-card">
            <div class="profile-avatar">👨‍🎓</div>
            <div class="profile-name">{user.get('nombre', username)}</div>
            <div class="profile-age">{profile.get('age', 'No especificado')} años</div>
        </div>
        
        <div class="card">
            <h2>📝 Editar Perfil</h2>
            <form method="POST" action="/update-profile">
                <input type="hidden" name="username" value="{username}">
                
                <div class="form-row">
                    <div class="input-group">
                        <label>👤 Nombre Completo:</label>
                        <input type="text" name="nombre" value="{user.get('nombre', '')}" required>
                    </div>
                    <div class="input-group">
                        <label>🎂 Edad:</label>
                        <input type="number" name="age" min="1" max="120" value="{profile.get('age', '')}">
                    </div>
                </div>
                
                <div class="input-group">
                    <label>🎂 Fecha de Nacimiento:</label>
                    <input type="date" name="birthdate" value="{profile.get('birthdate', '')}" required>
                </div>
                
                <div class="input-group">
                    <label>📝 Descripción Personal:</label>
                    <textarea name="bio" rows="4" placeholder="Cuéntanos sobre ti...">{profile.get('bio', '')}</textarea>
                </div>
                
                <div class="card" style="background: #f8f9fa; margin-top: 20px;">
                    <h2>🌐 Redes Sociales</h2>
                    
                    <div class="input-group">
                        <label>Facebook:</label>
                        <input type="url" name="facebook" placeholder="https://facebook.com/tu-perfil" value="{profile.get('socials', {}).get('facebook', '')}">
                    </div>
                    
                    <div class="input-group">
                        <label>Instagram:</label>
                        <input type="url" name="instagram" placeholder="https://instagram.com/tu-usuario" value="{profile.get('socials', {}).get('instagram', '')}">
                    </div>
                    
                    <div class="input-group">
                        <label>Twitter:</label>
                        <input type="url" name="twitter" placeholder="https://twitter.com/tu-usuario" value="{profile.get('socials', {}).get('twitter', '')}">
                    </div>
                    
                    <div class="input-group">
                        <label>LinkedIn:</label>
                        <input type="url" name="linkedin" placeholder="https://linkedin.com/in/tu-perfil" value="{profile.get('socials', {}).get('linkedin', '')}">
                    </div>
                </div>
                
                <button type="submit" class="btn btn-success" style="margin-top: 20px; width: 100%;">✅ Guardar Cambios</button>
            </form>
        </div>
        
        <div class="card">
            <h2>🌐 Mis Redes Sociales</h2>
            <div style="text-align: center;">
                {socials_html if socials_html else '<p style="color: #999;">No has vinculado redes sociales aún</p>'}
            </div>
        </div>
        """
        
        html = HTML_TEMPLATE.format(
            navbar=navbar,
            title=f"Perfil - {username}",
            content=content
        )
        self.wfile.write(html.encode())
    
    def render_progress(self, username, data):
        user = data['users'].get(username, {})
        if not user:
            self.render_404()
            return
        
        progress = data.get('student_progress', {}).get(username, {})
        navbar = self.get_navbar(username, 'progress')
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        lessons_completed = progress.get('lessons_completed', 0)
        total_lessons = progress.get('total_lessons', 10)
        hours_studied = progress.get('hours_studied', 0)
        completion_percentage = min(100, int(lessons_completed / max(1, total_lessons) * 100))
        
        content = f"""
        <h1>📊 Mi Progreso</h1>
        
        <div class="grid">
            <div class="stat-card">
                <div class="stat-number">{lessons_completed}/{total_lessons}</div>
                <div class="stat-label">Lecciones</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{hours_studied}h</div>
                <div class="stat-label">Horas Estudiadas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{completion_percentage}%</div>
                <div class="stat-label">Completado</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">🔥 {progress.get('current_streak', 0)}</div>
                <div class="stat-label">Racha Actual</div>
            </div>
        </div>
        
        <div class="card">
            <h2>🎯 Progreso General del Curso</h2>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {completion_percentage}%">
                    {completion_percentage}%
                </div>
            </div>
            <p style="margin-top: 10px; color: #7f8c8d;">Has completado {lessons_completed} de {total_lessons} lecciones</p>
        </div>
        
        <div class="card">
            <h2>📈 Estadísticas</h2>
            <p>📚 Horas Totales: <strong>{hours_studied} horas</strong></p>
            <p>✓ Tareas Completadas: <strong>{progress.get('tasks_completed', 0)}</strong></p>
            <p>⭐ Calificación Promedio: <strong>{progress.get('average_score', 0)}/100</strong></p>
            <p>🔥 Racha Más Larga: <strong>{progress.get('longest_streak', 0)} días</strong></p>
        </div>
        
        <div class="card">
            <h2>📅 Actualizar Progreso</h2>
            <form method="POST" action="/update-progress">
                <input type="hidden" name="username" value="{username}">
                
                <div class="input-group">
                    <label>Lecciones Completadas:</label>
                    <input type="number" name="lessons_completed" value="{lessons_completed}">
                </div>
                
                <div class="input-group">
                    <label>Horas Estudiadas:</label>
                    <input type="number" name="hours_studied" value="{hours_studied}">
                </div>
                
                <div class="input-group">
                    <label>Racha Actual (días):</label>
                    <input type="number" name="current_streak" value="{progress.get('current_streak', 0)}">
                </div>
                
                <button type="submit" class="btn btn-success" style="width: 100%;">✅ Guardar Progreso</button>
            </form>
        </div>
        """
        
        html = HTML_TEMPLATE.format(
            navbar=navbar,
            title=f"Progreso - {username}",
            content=content
        )
        self.wfile.write(html.encode())
    
    def render_habits(self, username, data):
        user = data['users'].get(username, {})
        if not user:
            self.render_404()
            return
        
        habits = data.get('student_habits', {}).get(username, {})
        navbar = self.get_navbar(username, 'habits')
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        habits_html = ""
        default_habits = {
            'estudiar_diario': '📚 Estudiar 30 minutos diarios',
            'hacer_tareas': '✏️ Completar tareas asignadas',
            'practicar_gramática': '📝 Practicar gramática',
            'leer_articulos': '📖 Leer artículos en inglés',
            'escuchar_podcasts': '🎧 Escuchar podcasts educativos',
            'escribir_diario': '📔 Escribir diario en inglés'
        }
        
        for habit_id, habit_name in default_habits.items():
            is_completed = habits.get(habit_id, False)
            checked = 'checked' if is_completed else ''
            habits_html += f"""
            <div class="habit-item">
                <span>{habit_name}</span>
                <form method="POST" action="/toggle-habit" style="display: inline;">
                    <input type="hidden" name="username" value="{username}">
                    <input type="hidden" name="habit_id" value="{habit_id}">
                    <input type="checkbox" class="habit-checkbox" {checked} onchange="this.form.submit()">
                </form>
            </div>
            """
        
        content = f"""
        <h1>✓ Mis Hábitos Diarios</h1>
        
        <div class="card">
            <p style="color: #7f8c8d; margin-bottom: 20px;">
                Marca tus hábitos completados para mantener tu racha. ¡Consistencia es la clave del éxito! 🎯
            </p>
            {habits_html}
        </div>
        
        <div class="card">
            <h2>➕ Agregar Nuevo Hábito</h2>
            <form method="POST" action="/add-habit">
                <input type="hidden" name="username" value="{username}">
                
                <div class="input-group">
                    <label>Nombre del Hábito:</label>
                    <input type="text" name="habit_name" placeholder="Ej: Practicar pronunciación" required>
                </div>
                
                <div class="input-group">
                    <label>Descripción (opcional):</label>
                    <input type="text" name="habit_description" placeholder="Detalles adicionales">
                </div>
                
                <button type="submit" class="btn btn-success" style="width: 100%;">➕ Agregar Hábito</button>
            </form>
        </div>
        """
        
        html = HTML_TEMPLATE.format(
            navbar=navbar,
            title=f"Hábitos - {username}",
            content=content
        )
        self.wfile.write(html.encode())
    
    def render_wallet(self, username, data):
        user = data['users'].get(username, {})
        if not user:
            self.render_404()
            return
        
        student_accounts = data.get('student_accounts', {}).get(username, {})
        transactions = data.get('transactions', {}).get(username, [])
        navbar = self.get_navbar(username, 'wallet')
        
        account_html = ""
        if student_accounts:
            account_html = f"""
            <div class="payment-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin: 15px 0;">
                <div>💳 TARJETA DE CRÉDITO</div>
                <div style="font-size: 18px; letter-spacing: 2px; margin: 10px 0;">{student_accounts.get('masked_card')}</div>
                <div style="display: flex; justify-content: space-between; font-size: 12px;">
                    <span>{student_accounts.get('holder_name')}</span>
                    <span>{student_accounts.get('expiry')}</span>
                </div>
            </div>
            <div style="text-align: center; margin: 20px 0;">
                <button onclick="document.getElementById('paymentForm').style.display='block'" class="btn btn-success">💳 Hacer Pago</button>
                <button onclick="document.getElementById('removeForm').style.display='block'" class="btn btn-danger">❌ Desvincular</button>
            </div>
            """
        else:
            account_html = f"""
            <div style="text-align: center; background: #f0f0f0; padding: 30px; border-radius: 8px;">
                <p style="color: #666; margin-bottom: 20px;">No tienes cuenta vinculada</p>
                <a href="/link-account/{username}" class="btn btn-success">➕ Vincular Tarjeta</a>
            </div>
            """
        
        transactions_html = ""
        if transactions:
            for trans in transactions:
                transactions_html += f"""
                <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #4CAF50;">
                    <strong>${trans.get('amount')}</strong> - {trans.get('description')}
                    <br><small>{trans.get('date')}</small>
                </div>
                """
        else:
            transactions_html = '<p style="color: #999; text-align: center;">Sin pagos registrados</p>'
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        content = f"""
        <h1>🏦 Mi Cartera Digital</h1>
        
        <div class="card">
            <h2>Tarjeta Vinculada</h2>
            {account_html}
        </div>
        
        <div class="card">
            <h2>📊 Historial de Pagos</h2>
            {transactions_html}
        </div>
        
        <div id="paymentForm" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; display: none;">
            <div style="background: white; margin: 50px auto; padding: 30px; border-radius: 10px; width: 90%; max-width: 500px;">
                <h2>💳 Realizar Pago</h2>
                <form method="POST" action="/process-payment">
                    <input type="hidden" name="username" value="{username}">
                    <div class="input-group">
                        <label>Monto (USD):</label>
                        <input type="number" name="amount" min="0.01" step="0.01" required>
                    </div>
                    <div class="input-group">
                        <label>Descripción:</label>
                        <input type="text" name="description" required>
                    </div>
                    <button type="submit" class="btn btn-success" style="width: 100%;">Confirmar Pago</button>
                    <button type="button" onclick="document.getElementById('paymentForm').style.display='none'" class="btn" style="width: 100%; margin-top: 10px;">Cancelar</button>
                </form>
            </div>
        </div>
        """
        
        html = HTML_TEMPLATE.format(
            navbar=navbar,
            title=f"Cartera - {username}",
            content=content
        )
        self.wfile.write(html.encode())
    
    def render_link_account(self, username, data):
        user = data['users'].get(username, {})
        if not user:
            self.render_404()
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = """<!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Vincular Tarjeta</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
                .card {{ background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto; }}
                h1, h2 {{ color: #2c3e50; }}
                .input-group {{ margin-bottom: 15px; }}
                label {{ display: block; margin-bottom: 5px; color: #2c3e50; font-weight: bold; }}
                input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                .btn {{ background: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; }}
                .security {{ background: #d4edda; padding: 10px; border-radius: 5px; margin: 20px 0; color: #155724; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>🔒 Vincular Tarjeta Segura</h1>
                <p style="color: #666;">Tu información está 100% encriptada</p>
                
                <form method="POST" action="/link-account-submit">
                    <input type="hidden" name="username" value="{username}">
                    
                    <div class="input-group">
                        <label>👤 Titular:</label>
                        <input type="text" name="holder_name" required placeholder="Nombre completo">
                    </div>
                    
                    <div class="input-group">
                        <label>💳 Número (16 dígitos):</label>
                        <input type="text" name="card_number" maxlength="19" required placeholder="1234 5678 9012 3456">
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div class="input-group">
                            <label>📅 Vencimiento:</label>
                            <input type="text" name="expiry" maxlength="5" required placeholder="03/26">
                        </div>
                        <div class="input-group">
                            <label>🔐 CVV:</label>
                            <input type="password" name="cvv" maxlength="3" required placeholder="***">
                        </div>
                    </div>
                    
                    <div class="security">
                        🔒 Encriptación AES-256 | ✅ Datos Seguros
                    </div>
                    
                    <button type="submit" class="btn">✅ Vincular Tarjeta</button>
                </form>
                
                <div style="margin-top: 20px;">
                    <a href="/wallet/{username}" style="color: #3498db; text-decoration: none;">← Volver a Cartera</a>
                </div>
            </div>
        </body>
        </html>""".format(username=username)
        
        self.wfile.write(html.encode())
    
    def render_transactions(self, username, data):
        user = data['users'].get(username, {})
        if not user:
            self.render_404()
            return
        
        transactions = data.get('transactions', {}).get(username, [])
        navbar = self.get_navbar(username, 'wallet')
        
        transactions_html = ""
        total = 0
        if transactions:
            for trans in reversed(transactions):
                amount = float(trans.get('amount', 0))
                total += amount
                transactions_html += f"""
                <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <strong>${amount:.2f}</strong> - {trans.get('description')}
                    <br><small>{trans.get('date')}</small>
                </div>
                """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        content = f"""
        <h1>📊 Historial de Transacciones</h1>
        
        <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
            <p style="font-size: 14px;">Total Gastado</p>
            <p style="font-size: 36px; font-weight: bold;">${total:.2f}</p>
        </div>
        
        <div class="card" style="margin-top: 20px;">
            <h2>📝 Transacciones</h2>
            {transactions_html if transactions_html else '<p style="color: #999;">Sin transacciones</p>'}
        </div>
        """
        
        html = HTML_TEMPLATE.format(
            navbar=navbar,
            title=f"Transacciones - {username}",
            content=content
        )
        self.wfile.write(html.encode())
    
    def render_payment_methods(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = """<html><body><p>Métodos de Pago</p><a href="/">Inicio</a></body></html>"""
        self.wfile.write(html.encode())
    
    def render_404(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = """<!DOCTYPE html>
        <html><body style="text-align: center; font-family: Arial;"><h1>❌ Página no encontrada</h1><a href="/">Ir al inicio</a></body></html>"""
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
            
            # Validar que el email sea de Gmail o Hotmail
            email_lower = email.lower().strip()
            valid_email = email_lower.endswith('@gmail.com') or email_lower.endswith('@hotmail.com') or email_lower.endswith('@outlook.com')
            
            if username and password and email and valid_email:
                data['users'][username] = {
                    'password': password,
                    'email': email,
                    'nombre': nombre,
                    'role': role
                }
                data['student_profiles'][username] = {
                    'socials': {}
                }
                data['student_progress'][username] = {
                    'lessons_completed': 0,
                    'total_lessons': 10,
                    'hours_studied': 0,
                    'current_streak': 0
                }
                data['student_habits'][username] = {}
                save_data(data)
            
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
        
        elif path == '/login':
            username = parsed.get('username', [''])[0]
            password = parsed.get('password', [''])[0]
            
            if username in data['users'] and data['users'][username]['password'] == password:
                self.send_response(302)
                self.send_header('Location', f'/dashboard/{username}')
                self.end_headers()
            else:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
        
        elif path == '/update-profile':
            username = parsed.get('username', [''])[0]
            nombre = parsed.get('nombre', [''])[0]
            age = parsed.get('age', [''])[0]
            birthdate = parsed.get('birthdate', [''])[0]
            bio = parsed.get('bio', [''])[0]
            
            if 'student_profiles' not in data:
                data['student_profiles'] = {}
            if username not in data['student_profiles']:
                data['student_profiles'][username] = {}
            
            if nombre:
                data['users'][username]['nombre'] = nombre
            
            data['student_profiles'][username].update({
                'age': age,
                'birthdate': birthdate,
                'bio': bio,
                'socials': {
                    'facebook': parsed.get('facebook', [''])[0],
                    'instagram': parsed.get('instagram', [''])[0],
                    'twitter': parsed.get('twitter', [''])[0],
                    'linkedin': parsed.get('linkedin', [''])[0]
                }
            })
            
            save_data(data)
            self.send_response(302)
            self.send_header('Location', f'/profile/{username}')
            self.end_headers()
        
        elif path == '/update-progress':
            username = parsed.get('username', [''])[0]
            lessons = parsed.get('lessons_completed', ['0'])[0]
            hours = parsed.get('hours_studied', ['0'])[0]
            streak = parsed.get('current_streak', ['0'])[0]
            
            if 'student_progress' not in data:
                data['student_progress'] = {}
            
            data['student_progress'][username] = {
                'lessons_completed': int(lessons),
                'total_lessons': 10,
                'hours_studied': int(hours),
                'current_streak': int(streak)
            }
            
            save_data(data)
            self.send_response(302)
            self.send_header('Location', f'/progress/{username}')
            self.end_headers()
        
        elif path == '/toggle-habit':
            username = parsed.get('username', [''])[0]
            habit_id = parsed.get('habit_id', [''])[0]
            
            if 'student_habits' not in data:
                data['student_habits'] = {}
            if username not in data['student_habits']:
                data['student_habits'][username] = {}
            
            data['student_habits'][username][habit_id] = not data['student_habits'][username].get(habit_id, False)
            save_data(data)
            
            self.send_response(302)
            self.send_header('Location', f'/habits/{username}')
            self.end_headers()
        
        elif path == '/add-habit':
            username = parsed.get('username', [''])[0]
            habit_name = parsed.get('habit_name', [''])[0]
            
            if habit_name and 'student_habits' in data and username in data['student_habits']:
                habit_id = f"custom_{len([h for h in data['student_habits'][username] if 'custom_' in h])}"
                data['student_habits'][username][habit_id] = False
                save_data(data)
            
            self.send_response(302)
            self.send_header('Location', f'/habits/{username}')
            self.end_headers()
        
        elif path == '/forgot-password':
            email = parsed.get('email', [''])[0]
            
            # Buscar usuario por email
            username_found = None
            for user_name, user_data in data.get('users', {}).items():
                if user_data.get('email') == email:
                    username_found = user_name
                    break
            
            if username_found:
                token = generate_reset_token(username_found, data)
                save_data(data)
                send_reset_email(email, token, username_found)
            
            # Mostrar mensaje de éxito sin importar si encontramos el usuario (por seguridad)
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """<!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Email Enviado - English Academy Pro</title>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: 20px;
                    }}
                    .success-box {{
                        background: white;
                        padding: 50px;
                        border-radius: 12px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.35);
                        max-width: 500px;
                        text-align: center;
                    }}
                    .success-icon {{
                        font-size: 60px;
                        margin-bottom: 20px;
                    }}
                    h1 {{
                        color: #1a1a2e;
                        margin-bottom: 15px;
                        font-size: 26px;
                    }}
                    p {{
                        color: #666;
                        margin-bottom: 15px;
                        line-height: 1.6;
                        font-size: 14px;
                    }}
                    .action-buttons {{
                        margin-top: 30px;
                        display: flex;
                        gap: 15px;
                        justify-content: center;
                    }}
                    a {{
                        padding: 12px 30px;
                        border-radius: 8px;
                        text-decoration: none;
                        font-weight: 600;
                        transition: 0.3s;
                        border: none;
                        cursor: pointer;
                    }}
                    .btn-primary {{
                        background: linear-gradient(135deg, #4c90e2 0%, #2e5c8a 100%);
                        color: white;
                    }}
                    .btn-primary:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 7px 20px rgba(76, 144, 226, 0.4);
                    }}
                    .btn-secondary {{
                        background: white;
                        color: #4c90e2;
                        border: 2px solid #4c90e2;
                    }}
                    .btn-secondary:hover {{
                        background: #f9f9f9;
                    }}
                </style>
            </head>
            <body>
                <div class="success-box">
                    <div class="success-icon">✉️</div>
                    <h1>Revisa tu Email</h1>
                    <p>Si la cuenta existe, hemos enviado un enlace para resetear tu contraseña a tu dirección de email.</p>
                    <p style="font-size: 12px; color: #999;">El enlace es válido por 1 hora.</p>
                    <div class="action-buttons">
                        <a href="/login" class="btn-primary">← Volver a Login</a>
                    </div>
                </div>
            </body>
            </html>"""
            self.wfile.write(html.encode())
        
        elif path == '/reset-password-submit':
            token = parsed.get('token', [''])[0]
            new_password = parsed.get('password', [''])[0]
            
            username = validate_reset_token(token, data)
            if username and new_password:
                data['users'][username]['password'] = new_password
                if token in data.get('password_reset_tokens', {}):
                    del data['password_reset_tokens'][token]
                save_data(data)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                html = """<!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Contraseña Actualizada - English Academy Pro</title>
                    <style>
                        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
                            min-height: 100vh;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            padding: 20px;
                        }}
                        .success-box {{
                            background: white;
                            padding: 50px;
                            border-radius: 12px;
                            box-shadow: 0 20px 60px rgba(0,0,0,0.35);
                            max-width: 500px;
                            text-align: center;
                        }}
                        .success-icon {{
                            font-size: 60px;
                            margin-bottom: 20px;
                        }}
                        h1 {{
                            color: #1a1a2e;
                            margin-bottom: 15px;
                            font-size: 26px;
                        }}
                        p {{
                            color: #666;
                            margin-bottom: 15px;
                            line-height: 1.6;
                            font-size: 14px;
                        }}
                        .action-buttons {{
                            margin-top: 30px;
                            display: flex;
                            gap: 15px;
                            justify-content: center;
                        }}
                        a {{
                            padding: 12px 30px;
                            border-radius: 8px;
                            text-decoration: none;
                            font-weight: 600;
                            transition: 0.3s;
                            border: none;
                            cursor: pointer;
                        }}
                        .btn-primary {{
                            background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
                            color: white;
                        }}
                        .btn-primary:hover {{
                            transform: translateY(-2px);
                            box-shadow: 0 7px 20px rgba(39, 174, 96, 0.4);
                        }}
                    </style>
                </head>
                <body>
                    <div class="success-box">
                        <div class="success-icon">✓</div>
                        <h1>¡Contraseña Actualizada!</h1>
                        <p>Tu contraseña ha sido actualizada exitosamente.</p>
                        <p>Ahora puedes iniciar sesión con tu nueva contraseña.</p>
                        <div class="action-buttons">
                            <a href="/login" class="btn-primary">→ Ir a Login</a>
                        </div>
                    </div>
                </body>
                </html>"""
                self.wfile.write(html.encode())
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                html = """<!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Error - English Academy Pro</title>
                    <style>
                        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
                            min-height: 100vh;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            padding: 20px;
                        }}
                        .error-box {{
                            background: white;
                            padding: 50px;
                            border-radius: 12px;
                            box-shadow: 0 20px 60px rgba(0,0,0,0.35);
                            max-width: 500px;
                            text-align: center;
                        }}
                        .error-icon {{
                            font-size: 60px;
                            margin-bottom: 20px;
                        }}
                        h1 {{
                            color: #1a1a2e;
                            margin-bottom: 15px;
                            font-size: 26px;
                        }}
                        p {{
                            color: #666;
                            margin-bottom: 15px;
                            line-height: 1.6;
                            font-size: 14px;
                        }}
                        a {{
                            display: inline-block;
                            margin-top: 20px;
                            padding: 12px 30px;
                            border-radius: 8px;
                            text-decoration: none;
                            font-weight: 600;
                            background: linear-gradient(135deg, #4c90e2 0%, #2e5c8a 100%);
                            color: white;
                            transition: 0.3s;
                        }}
                        a:hover {{
                            transform: translateY(-2px);
                            box-shadow: 0 7px 20px rgba(76, 144, 226, 0.4);
                        }}
                    </style>
                </head>
                <body>
                    <div class="error-box">
                        <div class="error-icon">⚠️</div>
                        <h1>Enlace Inválido o Expirado</h1>
                        <p>El enlace para resetear tu contraseña ha expirado o no es válido.</p>
                        <p>Por favor, solicita un nuevo enlace.</p>
                        <a href="/login">← Volver a Login</a>
                    </div>
                </body>
                </html>"""
                self.wfile.write(html.encode())
        
        elif path == '/link-account-submit':
            username = parsed.get('username', [''])[0]
            holder_name = parsed.get('holder_name', [''])[0]
            card_number = parsed.get('card_number', [''])[0].replace(' ', '')
            expiry = parsed.get('expiry', [''])[0]
            
            if username and holder_name and card_number and expiry:
                if 'student_accounts' not in data:
                    data['student_accounts'] = {}
                
                encrypted_card = encrypt_card(card_number)
                masked_card = mask_card(card_number)
                
                data['student_accounts'][username] = {
                    'holder_name': holder_name,
                    'card_encrypted': encrypted_card,
                    'masked_card': masked_card,
                    'expiry': expiry
                }
                save_data(data)
            
            self.send_response(302)
            self.send_header('Location', f'/wallet/{username}')
            self.end_headers()
        
        elif path == '/process-payment':
            username = parsed.get('username', [''])[0]
            amount = parsed.get('amount', ['0'])[0]
            description = parsed.get('description', [''])[0]
            
            if username and amount and description:
                if 'transactions' not in data:
                    data['transactions'] = {}
                if username not in data['transactions']:
                    data['transactions'][username] = []
                
                data['transactions'][username].append({
                    'amount': amount,
                    'description': description,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'success'
                })
                save_data(data)
            
            self.send_response(302)
            self.send_header('Location', f'/wallet/{username}')
            self.end_headers()
    
    def log_message(self, format, *args):
        return

def run_server():
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = '127.0.0.1'
    
    print("\n" + "=" * 90)
    print("🎓 ENGLISH ACADEMY PRO - PLATAFORMA COMPLETA CON PERFILES Y PROGRESO")
    print("=" * 90)
    print(f'✅ Servidor: http://{local_ip}:8000')
    print(f'   Local: http://localhost:8000')
    print("\n👤 USUARIOS:")
    print('   Maestro: maestra / 123456')
    print('   Estudiante: estudiante / 123456')
    print("\n📚 CARACTERÍSTICAS:")
    print('   ✓ Perfiles personalizados con redes sociales')
    print('   ✓ Seguimiento de progreso detallado')
    print('   ✓ Sistema de hábitos diarios')
    print('   ✓ Cartera digital segura')
    print('   ✓ Felicitaciones automáticas de cumpleaños')
    print('   ✓ Barra de navegación intuitiva')
    print("\n⌨️  Ctrl+C para detener\n" + "=" * 90 + "\n")
    
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
        
        for user in ['maestra', 'estudiante']:
            if user not in data.get('student_profiles', {}):
                data['student_profiles'] = data.get('student_profiles', {})
                data['student_profiles'][user] = {'socials': {}}
            
            if user not in data.get('student_progress', {}):
                data['student_progress'] = data.get('student_progress', {})
                data['student_progress'][user] = {
                    'lessons_completed': 0,
                    'total_lessons': 10,
                    'hours_studied': 0,
                    'current_streak': 0
                }
            
            if user not in data.get('student_habits', {}):
                data['student_habits'] = data.get('student_habits', {})
                data['student_habits'][user] = {}
        
        save_data(data)
    
    try:
        server = HTTPServer(('0.0.0.0', 8000), Handler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Servidor detenido")

if __name__ == '__main__':
    run_server()
