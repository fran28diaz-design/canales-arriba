"""
CAÑALES ARRIBA - Plataforma Educativa Simple
Versión enfocada en control escolar por roles.
"""

from flask import Flask, render_template_string, request, redirect, url_for, session, flash, send_from_directory
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "tu-clave-secreta-2026"

DATA_FILE = "data.json"
UPLOAD_FOLDER = "uploads"
ALLOWED_REPORT_EXTENSIONS = {"pdf", "doc", "docx"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "webm", "m4v"}
PREDEFINED_GRADES = [
    "Materno",
    "Prescolar",
    "Primero",
    "Segundo",
    "Tercero",
    "Cuarto",
    "Quinto",
    "Sexto"
]
PREDEFINED_SUBJECTS = [
    "Matemáticas",
    "Español",
    "Ciencias",
    "Estudios Sociales",
    "Inglés Y",
    "Inglés K",
    "Artes Plásticas",
    "Música",
    "Educación Física"
]
SEX_OPTIONS = ["Hombre", "Mujer"]

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def grade_options_html(selected_grade=""):
    options = []
    for grade in PREDEFINED_GRADES:
        selected = "selected" if grade == selected_grade else ""
        options.append(f"<option value='{grade}' {selected}>{grade}</option>")
    return "".join(options)


def sex_options_html(selected_sex=""):
    options = []
    for sex in SEX_OPTIONS:
        selected = "selected" if sex == selected_sex else ""
        options.append(f"<option value='{sex}' {selected}>{sex}</option>")
    return "".join(options)


def sanitize_subjects(subjects):
    if not isinstance(subjects, list):
        return []

    cleaned = []
    for subject in subjects:
        value = str(subject).strip()
        if value in PREDEFINED_SUBJECTS and value not in cleaned:
            cleaned.append(value)
    return cleaned[:4]


def subject_options_html(selected_subject="", allowed_subjects=None):
    options = []
    subjects = allowed_subjects if isinstance(allowed_subjects, list) and allowed_subjects else PREDEFINED_SUBJECTS
    for subject in subjects:
        selected = "selected" if subject == selected_subject else ""
        options.append(f"<option value='{subject}' {selected}>{subject}</option>")
    return "".join(options)


def multi_subject_options_html(selected_subjects=None):
    selected_subjects = sanitize_subjects(selected_subjects or [])
    options = []
    for subject in PREDEFINED_SUBJECTS:
        selected = "selected" if subject in selected_subjects else ""
        options.append(f"<option value='{subject}' {selected}>{subject}</option>")
    return "".join(options)


def allowed_report_file(filename):
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_REPORT_EXTENSIONS


def allowed_video_file(filename):
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_VIDEO_EXTENSIONS


def report_extension(filename):
    if not filename or '.' not in filename:
        return ""
    return filename.rsplit('.', 1)[1].lower()


def normalize_max_attempts(raw_value, default_value=3):
    try:
        value = int(str(raw_value).strip())
    except Exception:
        return default_value
    if value < 1:
        return 1
    if value > 20:
        return 20
    return value


def post_max_attempts(post):
    if not isinstance(post, dict):
        return 3
    return normalize_max_attempts(post.get('max_attempts', 3), 3)


def normalize_response_mode(raw_value, default_value='written_only'):
    value = str(raw_value or '').strip().lower()
    if value in ['written_only', 'video_only']:
        return value
    return default_value


def response_mode_label(mode):
    normalized = normalize_response_mode(mode)
    if normalized == 'video_only':
        return 'Solo video'
    return 'Escrita (texto/archivo)'


def _default_data():
    return {
        "users": {},
        "posts": {},
        "materials": {},
        "assignments": {},
        "submissions": {}
    }


def load_data():
    data = _default_data()
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as file:
                loaded = json.load(file)
                if isinstance(loaded, dict):
                    data.update(loaded)
        except Exception:
            return _default_data()
    return data


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def next_numeric_id(collection):
    numeric_keys = [int(key) for key in collection.keys() if str(key).isdigit()]
    next_value = max(numeric_keys, default=0) + 1
    return str(next_value)


def find_user_by_login(data, login_value):
    login_value = (login_value or '').strip()
    if not login_value:
        return None, None

    for user_id, user in data.get('users', {}).items():
        login_id = user.get('login_id', user_id)
        if str(login_id).lower() == login_value.lower():
            return user_id, user
    return None, None


def require_login():
    return 'user_id' in session


def current_role():
    return session.get('role')


def is_admin():
    return current_role() == 'admin'


def is_teacher():
    return current_role() == 'teacher'


def is_student():
    return current_role() == 'student'


def require_admin_access():
    if not require_login():
        return redirect(url_for('login'))
    if not is_admin():
        flash("Acceso denegado: solo el administrador puede realizar esta acción.", "danger")
        return redirect(url_for('dashboard'))
    return None


@app.before_request
def enforce_password_change():
    if not require_login():
        return None

    allowed_endpoints = {'force_change_password', 'logout', 'static'}
    if request.endpoint in allowed_endpoints:
        return None

    data = load_data()
    user = data.get('users', {}).get(session.get('user_id'), {})
    if user.get('must_change_password'):
        return redirect(url_for('force_change_password'))
    return None


BASE_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Cañales Arriba</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</head>
<body class="app-simple-pro">
    <nav class="navbar">
        <div class="nav-brand">🎓 Cañales Arriba</div>
        <div class="nav-menu user-info" style="display:flex; gap:8px; flex-wrap:wrap;">
            <a href="/" class="btn btn-secondary">Inicio</a>
            {% if session.get('user_id') %}
                <a href="/dashboard" class="btn btn-primary">Dashboard</a>
                {% if session.get('role') == 'admin' %}
                    <a href="/admin/users" class="btn btn-secondary">Usuarios</a>
                    <a href="/admin/overview" class="btn btn-secondary">Todo el contenido</a>
                {% elif session.get('role') == 'teacher' %}
                    <a href="/teacher/tasks" class="btn btn-secondary">Tareas</a>
                    <a href="/teacher/practices" class="btn btn-secondary">Prácticas</a>
                    <a href="/teacher/reports" class="btn btn-secondary">Informes</a>
                {% elif session.get('role') == 'student' %}
                    <a href="/student/tasks" class="btn btn-secondary">Tareas</a>
                    <a href="/student/practices" class="btn btn-secondary">Prácticas</a>
                    <a href="/student/reports" class="btn btn-secondary">Informes</a>
                {% endif %}
                <a href="/logout" class="btn btn-danger">Salir</a>
            {% else %}
                <a href="/login" class="btn btn-primary">Login</a>
            {% endif %}
        </div>
    </nav>

    <div class="container">
        {{ content|safe }}
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    if require_login():
        return redirect(url_for('dashboard'))
    return render_template_string(
        BASE_HTML,
        title="Inicio",
        content=f"""
        <div class="card" style="text-align:center;">
            <h1>Cañales Arriba</h1>
            <p style="font-size:18px; color:#7f8c8d; margin:20px 0;">
                Plataforma educativa para docentes y estudiantes.
            </p>
            <a href="/login" class="btn btn-primary">Iniciar sesión</a>
        </div>
        """
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = load_data()
        login_id = request.form.get('login_id', '').strip()
        password = request.form.get('password', '').strip()
        user_id, user = find_user_by_login(data, login_id)

        if user and user.get('password') == password:
            session['user_id'] = user_id
            session['username'] = user.get('nombre', user_id)
            session['role'] = user.get('role', 'student')
            flash("Sesión iniciada correctamente", "success")
            if user.get('must_change_password'):
                return redirect(url_for('force_change_password'))
            return redirect(url_for('dashboard'))
        flash("Usuario o contraseña incorrectos", "danger")

    content = """
    <div class="auth-container">
        <div class="auth-card" style="max-width:500px;">
            <h1>Iniciar Sesión</h1>
            <form method="POST">
                <div class="form-group">
                    <label>Acceso (correo MEP / cédula / usuario admin):</label>
                    <input type="text" name="login_id" required>
                </div>
                <div class="form-group">
                    <label>Contraseña:</label>
                    <input type="password" name="password" id="password" required>
                </div>
                <button type="submit" class="btn btn-primary btn-block">Entrar</button>
            </form>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, title="Login", content=content)


@app.route('/register')
def register_redirect():
    return redirect(url_for('login'))


@app.route('/forgot_password')
def forgot_password_redirect():
    return redirect(url_for('login'))


@app.route('/force_change_password', methods=['GET', 'POST'])
def force_change_password():
    if not require_login():
        return redirect(url_for('login'))

    data = load_data()
    user = data.get('users', {}).get(session.get('user_id'))
    if not user:
        session.clear()
        return redirect(url_for('login'))

    if not user.get('must_change_password'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if len(new_password) < 4:
            flash("La nueva contraseña debe tener al menos 4 caracteres", "danger")
            return redirect(url_for('force_change_password'))

        if new_password != confirm_password:
            flash("Las contraseñas no coinciden", "danger")
            return redirect(url_for('force_change_password'))

        user['password'] = new_password
        user['must_change_password'] = False
        user['temporary_password'] = False
        data['users'][session.get('user_id')] = user
        save_data(data)
        flash("Contraseña actualizada correctamente", "success")
        return redirect(url_for('dashboard'))

    content = """
    <div class="card" style="max-width:600px; margin:0 auto;">
        <h1>🔐 Cambio obligatorio de contraseña</h1>
        <p>Tu cuenta tiene contraseña temporal. Debes cambiarla para continuar.</p>
        <form method="POST">
            <div class="form-group"><label>Nueva contraseña:</label><input type="password" name="new_password" required></div>
            <div class="form-group"><label>Confirmar contraseña:</label><input type="password" name="confirm_password" required></div>
            <button class="btn btn-primary" type="submit">Guardar contraseña</button>
        </form>
    </div>
    """
    return render_template_string(BASE_HTML, title="Cambiar contraseña", content=content)


@app.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada", "success")
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if not require_login():
        return redirect(url_for('login'))

    role = current_role()
    data = load_data()
    users = data.get('users', {})

    if role == 'admin':
        teachers = [u for u in users.values() if u.get('role') == 'teacher']
        students = [u for u in users.values() if u.get('role') == 'student']
        posts = data.get('posts', {})
        content = f"""
        <div class="card">
            <h1>🏫 Dashboard Director</h1>
            <p>Control total de docentes, estudiantes y publicaciones.</p>
            <div style="margin-top:20px; display:grid; grid-template-columns: repeat(3, 1fr); gap:16px;">
                <div class="task-card"><h3>Docentes</h3><p>{len(teachers)}</p></div>
                <div class="task-card"><h3>Estudiantes</h3><p>{len(students)}</p></div>
                <div class="task-card"><h3>Publicaciones</h3><p>{len(posts)}</p></div>
            </div>
            <div style="margin-top:20px; display:flex; gap:10px;">
                <a class="btn btn-primary" href="/admin/users">Crear/gestionar usuarios</a>
                <a class="btn btn-secondary" href="/admin/overview">Ver todo el contenido</a>
            </div>
        </div>
        """
        return render_template_string(BASE_HTML, title="Dashboard Director", content=content)

    if role == 'teacher':
        my_posts = [p for p in data.get('posts', {}).values() if p.get('teacher') == session.get('user_id')]
        teacher_user = users.get(session.get('user_id'), {})
        materias = sanitize_subjects(teacher_user.get('materias', []))
        if not materias and teacher_user.get('materia') in PREDEFINED_SUBJECTS:
            materias = [teacher_user.get('materia')]
        materias_label = ", ".join(materias) if materias else "Sin materias asignadas"
        content = f"""
        <div class="card">
            <h1>👩‍🏫 Dashboard Docente</h1>
            <p><strong>Materias asignadas:</strong> {materias_label}</p>
            <p><strong>Publicaciones creadas:</strong> {len(my_posts)}</p>
            <div style="margin-top:20px; display:flex; gap:10px;">
                <a class="btn btn-primary" href="/teacher/tasks">Tareas</a>
                <a class="btn btn-secondary" href="/teacher/practices">Prácticas</a>
                <a class="btn btn-secondary" href="/teacher/reports">Informes</a>
            </div>
        </div>
        """
        return render_template_string(BASE_HTML, title="Dashboard Docente", content=content)

    content = """
    <div class="card">
        <h1>🎒 Dashboard Estudiante</h1>
        <p>Consulta todo lo que publican tus profesores por materia.</p>
        <div style="margin-top:16px; display:flex; gap:10px; flex-wrap:wrap;">
            <a class="btn btn-primary" href="/student/tasks">Ver tareas</a>
            <a class="btn btn-secondary" href="/student/practices">Ver prácticas</a>
            <a class="btn btn-secondary" href="/student/reports">Ver informes</a>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, title="Dashboard Estudiante", content=content)


@app.route('/admin/users')
def admin_users():
    admin_guard = require_admin_access()
    if admin_guard:
        return admin_guard

    data = load_data()

    users_rows = ""
    for username, user in data.get('users', {}).items():
        role = user.get('role', '-')
        teacher_subjects = sanitize_subjects(user.get('materias', []))
        if not teacher_subjects and user.get('materia') in PREDEFINED_SUBJECTS:
            teacher_subjects = [user.get('materia')]

        if role == 'teacher':
            subject_or_grade = ", ".join(teacher_subjects) if teacher_subjects else '-'
        elif role == 'student':
            subject_or_grade = user.get('grado', '-')
        else:
            subject_or_grade = '-'

        users_rows += f"""
        <tr>
            <td>{user.get('login_id', username)}</td>
            <td>{user.get('nombre', '-')}</td>
            <td>{user.get('identificacion', user.get('cedula', '-'))}</td>
            <td>{user.get('sexo', '-')}</td>
            <td>{role}</td>
            <td>{subject_or_grade}</td>
            <td>{user.get('password', '-')}</td>
            <td>{'Sí' if user.get('must_change_password') else 'No'}</td>
            <td>
                <a class="btn btn-secondary" style="padding:6px 10px;" href="/admin/users/edit/{username}">Editar</a>
                <a class="btn btn-primary" style="padding:6px 10px;" href="/admin/users/reset_password/{username}">Restablecer contraseña</a>
                <a class="btn btn-danger" style="padding:6px 10px;" href="/admin/users/delete/{username}">Eliminar</a>
            </td>
        </tr>
        """

    content = f"""
    <div class="card admin-header-card">
        <h1>👥 Administración de Usuarios</h1>
        <p>Gestión centralizada de docentes, estudiantes y administradores.</p>
    </div>

    <div class="card admin-form-card" style="margin-top:20px;">
        <h2>Registro separado</h2>
        <div style="display:flex; gap:12px; flex-wrap:wrap; margin-top:8px;">
            <a class="btn btn-primary" href="/admin/create-teacher">Crear docente</a>
            <a class="btn btn-secondary" href="/admin/create-student">Crear estudiante</a>
        </div>
    </div>
    <div class="card" style="margin-top:20px;">
        <h2>Lista de usuarios</h2>
        <div class="admin-grid-form" style="margin-bottom:12px;">
            <div class="form-group">
                <label>Buscar (nombre/acceso):</label>
                <input id="filter-search" placeholder="Escribe para filtrar...">
            </div>
            <div class="form-group">
                <label>Rol:</label>
                <select id="filter-role">
                    <option value="">Todos</option>
                    <option value="teacher">Docente</option>
                    <option value="student">Estudiante</option>
                    <option value="admin">Administrador</option>
                </select>
            </div>
            <div class="form-group">
                <label>Sexo:</label>
                <select id="filter-sex">
                    <option value="">Todos</option>
                    <option value="Hombre">Hombre</option>
                    <option value="Mujer">Mujer</option>
                </select>
            </div>
            <div class="form-group">
                <label>Grado:</label>
                <select id="filter-grade">
                    <option value="">Todos</option>
                    {grade_options_html()}
                </select>
            </div>
            <div class="form-group">
                <label>Materia docente:</label>
                <select id="filter-subject">
                    <option value="">Todas</option>
                    {subject_options_html()}
                </select>
            </div>
            <div class="form-group" style="display:flex; align-items:flex-end;">
                <button type="button" id="clear-filters" class="btn btn-secondary">Limpiar filtros</button>
            </div>
        </div>
        <div class="admin-table-wrapper">
        <table id="users-table" style="width:100%; border-collapse:collapse;">
            <thead>
                <tr>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Acceso</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Nombre</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Identificación</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Sexo</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Rol</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Materia/Grado</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Contraseña</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Cambio obligatorio</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Acciones</th>
                </tr>
            </thead>
            <tbody>{users_rows}</tbody>
        </table>
        </div>
    </div>
    <script>
        (function() {{
            const searchInput = document.getElementById('filter-search');
            const roleSelect = document.getElementById('filter-role');
            const sexSelect = document.getElementById('filter-sex');
            const gradeSelect = document.getElementById('filter-grade');
            const subjectSelect = document.getElementById('filter-subject');
            const clearButton = document.getElementById('clear-filters');
            const table = document.getElementById('users-table');
            if (!table) return;

            const rows = Array.from(table.querySelectorAll('tbody tr'));

            function normalize(text) {{
                return (text || '').toLowerCase().trim();
            }}

            function applyFilters() {{
                const searchValue = normalize(searchInput.value);
                const roleValue = normalize(roleSelect.value);
                const sexValue = normalize(sexSelect.value);
                const gradeValue = normalize(gradeSelect.value);
                const subjectValue = normalize(subjectSelect.value);

                rows.forEach((row) => {{
                    const cells = row.querySelectorAll('td');
                    if (cells.length < 6) return;

                    const access = normalize(cells[0].textContent);
                    const name = normalize(cells[1].textContent);
                    const sex = normalize(cells[3].textContent);
                    const role = normalize(cells[4].textContent);
                    const subjectOrGrade = normalize(cells[5].textContent);

                    const bySearch = !searchValue || access.includes(searchValue) || name.includes(searchValue);
                    const byRole = !roleValue || role === roleValue;
                    const bySex = !sexValue || sex === sexValue;
                    const byGrade = !gradeValue || (role === 'student' && subjectOrGrade.includes(gradeValue));
                    const bySubject = !subjectValue || (role === 'teacher' && subjectOrGrade.includes(subjectValue));

                    row.style.display = (bySearch && byRole && bySex && byGrade && bySubject) ? '' : 'none';
                }});
            }}

            searchInput.addEventListener('input', applyFilters);
            roleSelect.addEventListener('change', applyFilters);
            sexSelect.addEventListener('change', applyFilters);
            gradeSelect.addEventListener('change', applyFilters);
            subjectSelect.addEventListener('change', applyFilters);
            clearButton.addEventListener('click', function() {{
                searchInput.value = '';
                roleSelect.value = '';
                sexSelect.value = '';
                gradeSelect.value = '';
                subjectSelect.value = '';
                applyFilters();
            }});
            applyFilters();
        }})();
    </script>
    """
    return render_template_string(BASE_HTML, title="Usuarios", content=content)


@app.route('/admin/create-teacher', methods=['GET', 'POST'])
def admin_create_teacher():
    admin_guard = require_admin_access()
    if admin_guard:
        return admin_guard

    if request.method == 'POST':
        data = load_data()
        nombre = request.form.get('nombre', '').strip()
        identificacion = request.form.get('identificacion', '').strip()
        mep_email = request.form.get('mep_email', '').strip().lower()
        materias = sanitize_subjects(request.form.getlist('materias'))
        password = request.form.get('password', '').strip()

        if not nombre or not identificacion or not mep_email or not password:
            flash("Completa todos los campos del docente", "danger")
            return redirect(url_for('admin_create_teacher'))
        if len(materias) < 1 or len(materias) > 4:
            flash("Selecciona de 1 a 4 materias para el docente", "danger")
            return redirect(url_for('admin_create_teacher'))

        if mep_email in data.get('users', {}):
            flash("Ese correo MEP ya está registrado", "danger")
            return redirect(url_for('admin_create_teacher'))

        data['users'][mep_email] = {
            'email': mep_email,
            'password': password,
            'role': 'teacher',
            'nombre': nombre,
            'identificacion': identificacion,
            'materias': materias,
            'materia': materias[0],
            'mep_email': mep_email,
            'login_id': mep_email,
            'created_by': session.get('user_id'),
            'created_at': datetime.now().isoformat(),
            'temporary_password': True,
            'must_change_password': True
        }
        save_data(data)
        flash("Docente creado correctamente", "success")
        return redirect(url_for('admin_users'))

    teacher_subject_options = multi_subject_options_html()
    content = f"""
    <div class="card" style="max-width:800px; margin:0 auto;">
        <h1>👩‍🏫 Crear Docente</h1>
        <form method="POST" class="admin-grid-form" id="createTeacherForm">
            <div class="form-group"><label>Nombre:</label><input name="nombre" required></div>
            <div class="form-group"><label>Identificación:</label><input name="identificacion" required></div>
            <div class="form-group">
                <label>Correo MEP (acceso):</label>
                <input type="email" id="teacherMepEmail" name="mep_email" placeholder="docente@mep.go.cr" required>
                <small id="teacherMepHint" class="form-hint">Debe terminar en @mep.go.cr</small>
            </div>
            <div class="form-group">
                <label>Materias (elige de 1 a 4):</label>
                <select id="teacherSubjects" name="materias" multiple size="6" required>
                    {teacher_subject_options}
                </select>
                <small id="teacherSubjectsHint" class="form-hint">Selecciona entre 1 y 4 materias</small>
            </div>
            <div class="form-group"><label>Contraseña temporal:</label><input name="password" required></div>
            <div class="form-group admin-form-actions"><button id="teacherSubmit" class="btn btn-primary" type="submit">Crear docente</button></div>
        </form>
    </div>
    <script>
        (function() {{
            const form = document.getElementById('createTeacherForm');
            const mepInput = document.getElementById('teacherMepEmail');
            const subjectsInput = document.getElementById('teacherSubjects');
            const hint = document.getElementById('teacherMepHint');
            const subjectsHint = document.getElementById('teacherSubjectsHint');
            const submitButton = document.getElementById('teacherSubmit');

            function isValidMepEmail(value) {{
                return /@mep\.go\.cr$/i.test((value || '').trim());
            }}

            function validateTeacherForm() {{
                const validMep = isValidMepEmail(mepInput.value);
                const selectedSubjects = Array.from(subjectsInput.selectedOptions).length;
                const validSubjects = selectedSubjects >= 1 && selectedSubjects <= 4;
                hint.style.color = validMep ? '#22c55e' : '#f87171';
                hint.textContent = validMep ? 'Correo MEP válido' : 'Debe terminar en @mep.go.cr';
                subjectsHint.style.color = validSubjects ? '#22c55e' : '#f87171';
                subjectsHint.textContent = validSubjects ? `Materias seleccionadas: ${{selectedSubjects}}` : 'Selecciona entre 1 y 4 materias';
                submitButton.disabled = !(validMep && validSubjects);
                submitButton.style.opacity = (validMep && validSubjects) ? '1' : '0.6';
                submitButton.style.cursor = (validMep && validSubjects) ? 'pointer' : 'not-allowed';
            }}

            mepInput.addEventListener('input', validateTeacherForm);
            subjectsInput.addEventListener('change', validateTeacherForm);
            form.addEventListener('submit', function(event) {{
                const selectedSubjects = Array.from(subjectsInput.selectedOptions).length;
                if (!isValidMepEmail(mepInput.value) || selectedSubjects < 1 || selectedSubjects > 4) {{
                    event.preventDefault();
                }}
            }});
            validateTeacherForm();
        }})();
    </script>
    """
    return render_template_string(BASE_HTML, title="Crear Docente", content=content)


@app.route('/admin/create-student', methods=['GET', 'POST'])
def admin_create_student():
    admin_guard = require_admin_access()
    if admin_guard:
        return admin_guard

    if request.method == 'POST':
        data = load_data()
        nombre = request.form.get('nombre', '').strip()
        identificacion = request.form.get('identificacion', '').strip()
        cedula = request.form.get('cedula', '').strip()
        sexo = request.form.get('sexo', '').strip()
        grado = request.form.get('grado', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip() or f"{cedula}@estudiante.local"

        if not nombre or not identificacion or not cedula or not sexo or not grado or not password:
            flash("Completa todos los campos del estudiante", "danger")
            return redirect(url_for('admin_create_student'))
        if sexo not in SEX_OPTIONS:
            flash("Selecciona un sexo válido", "danger")
            return redirect(url_for('admin_create_student'))
        if grado not in PREDEFINED_GRADES:
            flash("Selecciona un grado válido", "danger")
            return redirect(url_for('admin_create_student'))
        if cedula in data.get('users', {}):
            flash("Esa cédula ya está registrada", "danger")
            return redirect(url_for('admin_create_student'))

        data['users'][cedula] = {
            'email': email,
            'password': password,
            'role': 'student',
            'nombre': nombre,
            'identificacion': identificacion,
            'cedula': cedula,
            'sexo': sexo,
            'grado': grado,
            'login_id': cedula,
            'created_by': session.get('user_id'),
            'created_at': datetime.now().isoformat(),
            'temporary_password': True,
            'must_change_password': True
        }
        save_data(data)
        flash("Estudiante creado correctamente", "success")
        return redirect(url_for('admin_users'))

    grade_select_options = grade_options_html()
    sex_select_options = sex_options_html()
    content = f"""
    <div class="card" style="max-width:900px; margin:0 auto;">
        <h1>🎓 Crear Estudiante</h1>
        <form method="POST" class="admin-grid-form" id="createStudentForm">
            <div class="form-group"><label>Nombre:</label><input name="nombre" required></div>
            <div class="form-group"><label>Identificación:</label><input name="identificacion" required></div>
            <div class="form-group">
                <label>Cédula (acceso):</label>
                <input id="studentCedula" name="cedula" required>
                <small id="studentCedulaHint" class="form-hint">Solo números</small>
            </div>
            <div class="form-group"><label>Email (opcional):</label><input name="email" type="email"></div>
            <div class="form-group">
                <label>Sexo:</label>
                <select id="studentSexo" name="sexo" required>
                    <option value="">Selecciona</option>
                    {sex_select_options}
                </select>
            </div>
            <div class="form-group">
                <label>Grado:</label>
                <select id="studentGrado" name="grado" required>
                    <option value="">Selecciona</option>
                    {grade_select_options}
                </select>
            </div>
            <div class="form-group"><label>Contraseña temporal:</label><input name="password" required></div>
            <div class="form-group admin-form-actions"><button id="studentSubmit" class="btn btn-primary" type="submit">Crear estudiante</button></div>
        </form>
    </div>
    <script>
        (function() {{
            const form = document.getElementById('createStudentForm');
            const cedulaInput = document.getElementById('studentCedula');
            const sexoSelect = document.getElementById('studentSexo');
            const gradoSelect = document.getElementById('studentGrado');
            const hint = document.getElementById('studentCedulaHint');
            const submitButton = document.getElementById('studentSubmit');

            function isCedulaValid(value) {{
                return /^\d+$/.test((value || '').trim());
            }}

            function validateStudentForm() {{
                const cedulaValid = isCedulaValid(cedulaInput.value);
                const sexoValid = !!sexoSelect.value;
                const gradoValid = !!gradoSelect.value;
                const formValid = cedulaValid && sexoValid && gradoValid;

                hint.style.color = cedulaValid ? '#22c55e' : '#f87171';
                hint.textContent = cedulaValid ? 'Cédula válida' : 'Solo números';
                submitButton.disabled = !formValid;
                submitButton.style.opacity = formValid ? '1' : '0.6';
                submitButton.style.cursor = formValid ? 'pointer' : 'not-allowed';
            }}

            cedulaInput.addEventListener('input', validateStudentForm);
            sexoSelect.addEventListener('change', validateStudentForm);
            gradoSelect.addEventListener('change', validateStudentForm);

            form.addEventListener('submit', function(event) {{
                if (!isCedulaValid(cedulaInput.value) || !sexoSelect.value || !gradoSelect.value) {{
                    event.preventDefault();
                }}
            }});

            validateStudentForm();
        }})();
    </script>
    """
    return render_template_string(BASE_HTML, title="Crear Estudiante", content=content)


@app.route('/admin/users/edit/<username>', methods=['GET', 'POST'])
def admin_edit_user(username):
    admin_guard = require_admin_access()
    if admin_guard:
        return admin_guard

    data = load_data()
    user = data.get('users', {}).get(username)
    if not user:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for('admin_users'))

    if request.method == 'POST':
        user['nombre'] = request.form.get('nombre', '').strip() or user.get('nombre', username)
        role = request.form.get('role', user.get('role', 'student')).strip()
        user['role'] = role
        user['identificacion'] = request.form.get('identificacion', '').strip() or user.get('identificacion', '')
        user['email'] = request.form.get('email', '').strip()
        mep_email = request.form.get('mep_email', '').strip().lower()
        cedula = request.form.get('cedula', '').strip()
        materias = sanitize_subjects(request.form.getlist('materias'))
        grado = request.form.get('grado', '').strip()
        sexo = request.form.get('sexo', '').strip()

        if role == 'teacher' and (not mep_email or len(materias) < 1 or len(materias) > 4):
            flash("Para docente, correo MEP y de 1 a 4 materias son obligatorios", "danger")
            return redirect(url_for('admin_edit_user', username=username))

        if role == 'student' and not cedula:
            flash("Para estudiante, la cédula es obligatoria", "danger")
            return redirect(url_for('admin_edit_user', username=username))
        if role == 'student' and grado not in PREDEFINED_GRADES:
            flash("Selecciona un grado válido para el estudiante", "danger")
            return redirect(url_for('admin_edit_user', username=username))
        if role == 'student' and sexo not in SEX_OPTIONS:
            flash("Selecciona sexo válido para el estudiante", "danger")
            return redirect(url_for('admin_edit_user', username=username))

        if role == 'teacher' and mep_email:
            user['mep_email'] = mep_email
            user['login_id'] = mep_email
            user['email'] = mep_email
        elif role == 'student' and cedula:
            user['cedula'] = cedula
            user['login_id'] = cedula
        elif role == 'admin':
            user['login_id'] = username

        new_password = request.form.get('password', '').strip()
        user['materias'] = materias if user['role'] == 'teacher' else []
        user['materia'] = materias[0] if user['role'] == 'teacher' and materias else ''
        user['grado'] = grado if user['role'] == 'student' else user.get('grado', '')
        user['sexo'] = sexo if user['role'] == 'student' else user.get('sexo', '')

        if new_password:
            user['password'] = new_password
            if user.get('role') in ['teacher', 'student']:
                user['must_change_password'] = True
                user['temporary_password'] = True

        force_change = request.form.get('force_change_password') == 'on'
        user['must_change_password'] = force_change or user.get('must_change_password', False)

        data['users'][username] = user
        save_data(data)
        flash("Usuario actualizado", "success")
        return redirect(url_for('admin_users'))

    current_teacher_subjects = sanitize_subjects(user.get('materias', []))
    if not current_teacher_subjects and user.get('materia') in PREDEFINED_SUBJECTS:
        current_teacher_subjects = [user.get('materia')]

    teacher_subject_options = multi_subject_options_html(current_teacher_subjects)
    grade_select_options = grade_options_html(user.get('grado', ''))
    sex_select_options = sex_options_html(user.get('sexo', ''))
    content = f"""
    <div class="card" style="max-width:700px; margin:0 auto;">
        <h1>✏️ Editar usuario: {username}</h1>
        <form method="POST" id="editUserForm">
            <div class="form-group"><label>Nombre:</label><input name="nombre" value="{user.get('nombre', '')}" required></div>
            <div class="form-group"><label>Identificación:</label><input name="identificacion" value="{user.get('identificacion', user.get('cedula', ''))}" required></div>
            <div class="form-group"><label>Email:</label><input type="email" name="email" value="{user.get('email', '')}" required></div>
            <div class="form-group"><label>Acceso actual:</label><input value="{user.get('login_id', username)}" disabled></div>
            <div class="form-group" id="group-mep"><label>Correo MEP (si docente):</label><input id="field-mep" name="mep_email" value="{user.get('mep_email', '')}"></div>
            <div class="form-group" id="group-cedula"><label>Cédula (si estudiante):</label><input id="field-cedula" name="cedula" value="{user.get('cedula', '')}"></div>
            <div class="form-group" id="group-sexo">
                <label>Sexo (estudiante):</label>
                <select name="sexo" id="field-sexo">
                    <option value="">Selecciona</option>
                    {sex_select_options}
                </select>
            </div>
            <div class="form-group"><label>Contraseña actual:</label><input value="{user.get('password', '')}" disabled></div>
            <div class="form-group"><label>Nueva contraseña temporal (opcional):</label><input name="password" type="text"></div>
            <div class="form-group">
                <label>Rol:</label>
                <select name="role" id="roleSelect" required>
                    <option value="teacher" {'selected' if user.get('role') == 'teacher' else ''}>Docente</option>
                    <option value="student" {'selected' if user.get('role') == 'student' else ''}>Estudiante</option>
                    <option value="admin" {'selected' if user.get('role') == 'admin' else ''}>Director/Administrador</option>
                </select>
            </div>
            <div class="form-group" id="group-materia">
                <label>Materias (docente, 1 a 4):</label>
                <select id="field-materias" name="materias" multiple size="6">
                    {teacher_subject_options}
                </select>
            </div>
            <div class="form-group" id="group-grado">
                <label>Grado (estudiante):</label>
                <select name="grado" id="field-grado">
                    <option value="">Selecciona un grado</option>
                    {grade_select_options}
                </select>
            </div>
            <div class="form-group"><label><input type="checkbox" name="force_change_password"> Forzar cambio de contraseña en próximo inicio</label></div>
            <button class="btn btn-primary" type="submit">Guardar cambios</button>
            <a class="btn btn-secondary" href="/admin/users">Volver</a>
        </form>
    </div>
    <script>
        (function() {{
            const roleSelect = document.getElementById('roleSelect');
            const groupMep = document.getElementById('group-mep');
            const groupMateria = document.getElementById('group-materia');
            const groupCedula = document.getElementById('group-cedula');
            const groupSexo = document.getElementById('group-sexo');
            const groupGrado = document.getElementById('group-grado');

            const fieldMep = document.getElementById('field-mep');
            const fieldMaterias = document.getElementById('field-materias');
            const fieldCedula = document.getElementById('field-cedula');
            const fieldSexo = document.getElementById('field-sexo');
            const fieldGrado = document.getElementById('field-grado');
            const form = document.getElementById('editUserForm');

            function toggleFields() {{
                const role = roleSelect.value;
                const isTeacher = role === 'teacher';
                const isStudent = role === 'student';

                groupMep.style.display = isTeacher ? 'block' : 'none';
                groupMateria.style.display = isTeacher ? 'block' : 'none';
                groupCedula.style.display = isStudent ? 'block' : 'none';
                groupSexo.style.display = isStudent ? 'block' : 'none';
                groupGrado.style.display = isStudent ? 'block' : 'none';

                fieldMep.required = isTeacher;
                fieldMaterias.required = isTeacher;
                fieldCedula.required = isStudent;
                fieldSexo.required = isStudent;
                fieldGrado.required = isStudent;
            }}

            roleSelect.addEventListener('change', toggleFields);
            form.addEventListener('submit', function(event) {{
                if (roleSelect.value !== 'teacher') return;
                const selectedSubjects = Array.from(fieldMaterias.selectedOptions).length;
                if (selectedSubjects < 1 || selectedSubjects > 4) {{
                    event.preventDefault();
                    alert('Selecciona de 1 a 4 materias para el docente.');
                }}
            }});
            toggleFields();
        }})();
    </script>
    """
    return render_template_string(BASE_HTML, title="Editar usuario", content=content)


@app.route('/admin/users/delete/<username>')
def admin_delete_user(username):
    admin_guard = require_admin_access()
    if admin_guard:
        return admin_guard

    if username == session.get('user_id'):
        flash("No puedes eliminar tu propio usuario activo", "danger")
        return redirect(url_for('admin_users'))

    data = load_data()
    if username not in data.get('users', {}):
        flash("Usuario no encontrado", "danger")
        return redirect(url_for('admin_users'))

    del data['users'][username]
    save_data(data)
    flash("Usuario eliminado", "success")
    return redirect(url_for('admin_users'))


@app.route('/admin/users/reset_password/<username>', methods=['GET', 'POST'])
def admin_reset_user_password(username):
    admin_guard = require_admin_access()
    if admin_guard:
        return admin_guard

    data = load_data()
    user = data.get('users', {}).get(username)
    if not user:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for('admin_users'))

    if request.method == 'POST':
        temporary_password = request.form.get('temporary_password', '').strip()
        if len(temporary_password) < 4:
            flash("La contraseña temporal debe tener al menos 4 caracteres", "danger")
            return redirect(url_for('admin_reset_user_password', username=username))

        user['password'] = temporary_password
        user['temporary_password'] = True
        user['must_change_password'] = True
        data['users'][username] = user
        save_data(data)

        flash(f"Contraseña restablecida para {user.get('nombre', username)}.", "success")
        return redirect(url_for('admin_users'))

    content = f"""
    <div class="card" style="max-width:600px; margin:0 auto;">
        <h1>🔐 Restablecer contraseña</h1>
        <p><strong>Usuario:</strong> {user.get('nombre', username)} ({user.get('login_id', username)})</p>
        <p>Define una contraseña temporal. El usuario estará obligado a cambiarla al iniciar sesión.</p>
        <form method="POST">
            <div class="form-group">
                <label>Contraseña temporal:</label>
                <input type="text" name="temporary_password" required>
            </div>
            <button class="btn btn-primary" type="submit">Restablecer</button>
            <a class="btn btn-secondary" href="/admin/users">Cancelar</a>
        </form>
    </div>
    """
    return render_template_string(BASE_HTML, title="Restablecer contraseña", content=content)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    if not require_login():
        return redirect(url_for('login'))
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/teacher/post', methods=['GET', 'POST'])
def teacher_post():
    if not require_login() or not is_teacher():
        return redirect(url_for('login'))

    data = load_data()
    forced_type = request.args.get('type', '').strip().lower()
    if forced_type not in ['task', 'practice']:
        forced_type = ''
    teacher_user = data['users'].get(session.get('user_id'), {})
    teacher_subjects = sanitize_subjects(teacher_user.get('materias', []))
    if not teacher_subjects and teacher_user.get('materia') in PREDEFINED_SUBJECTS:
        teacher_subjects = [teacher_user.get('materia')]

    if not teacher_subjects:
        flash("No tienes materias asignadas. Contacta al director.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        post_type = forced_type or request.form.get('post_type', '').strip()
        due_date = request.form.get('due_date', '').strip()
        target_grade = request.form.get('target_grade', '').strip()
        subject = request.form.get('subject', '').strip()
        max_attempts = normalize_max_attempts(request.form.get('max_attempts', '3'), 3)
        response_mode = normalize_response_mode(request.form.get('response_mode', 'written_only'), 'written_only')
        file = request.files.get('activity_file')

        if not title or not description or post_type not in ['task', 'practice']:
            flash("Completa todos los campos obligatorios", "danger")
            return redirect(url_for('teacher_post'))
        if subject not in teacher_subjects:
            flash("Selecciona una materia válida asignada a tu perfil", "danger")
            return redirect(url_for('teacher_post'))
        if target_grade not in PREDEFINED_GRADES:
            flash("Selecciona un grado válido para publicar", "danger")
            return redirect(url_for('teacher_post'))
        if not file or not file.filename:
            flash("Debes adjuntar el documento en PDF o Word para la tarea/práctica", "danger")
            return redirect(url_for('teacher_post'))
        if not allowed_report_file(file.filename):
            flash("Formato no permitido. Sube PDF, DOC o DOCX", "danger")
            return redirect(url_for('teacher_post'))

        original_filename = file.filename
        safe_name = secure_filename(original_filename)
        unique_name = f"{int(datetime.now().timestamp() * 1000)}_{safe_name}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_name)
        file.save(file_path)

        post_id = next_numeric_id(data['posts'])
        data['posts'][post_id] = {
            'id': post_id,
            'title': title,
            'description': description,
            'type': post_type,
            'teacher': session.get('user_id'),
            'teacher_name': teacher_user.get('nombre', session.get('user_id')),
            'subject': subject,
            'target_grade': target_grade,
            'max_attempts': max_attempts,
            'response_mode': response_mode,
            'resource_file': unique_name,
            'resource_original_name': original_filename,
            'resource_extension': report_extension(original_filename),
            'due_date': due_date,
            'created_at': datetime.now().isoformat()
        }
        save_data(data)
        flash("Contenido publicado correctamente", "success")
        return redirect(url_for('teacher_my_content'))

    grade_select_options = grade_options_html()
    teacher_subject_options = subject_options_html(allowed_subjects=teacher_subjects)
    if forced_type == 'task':
        type_select_html = '<input type="hidden" name="post_type" value="task"><input value="Tarea" disabled>'
        title_label = '📝 Publicar tarea'
    elif forced_type == 'practice':
        type_select_html = '<input type="hidden" name="post_type" value="practice"><input value="Práctica" disabled>'
        title_label = '✍️ Publicar práctica'
    else:
        type_select_html = '''
                <select name="post_type" required>
                    <option value="task">Tarea</option>
                    <option value="practice">Práctica</option>
                </select>
        '''
        title_label = '📝 Publicar contenido'

    content = f"""
    <div class="card" style="max-width:700px; margin:0 auto;">
        <h1>{title_label}</h1>
        <form method="POST" enctype="multipart/form-data">
            <div class="form-group"><label>Título:</label><input type="text" name="title" required></div>
            <div class="form-group"><label>Descripción:</label><textarea name="description" rows="5" required></textarea></div>
            <div class="form-group">
                <label>Tipo:</label>
                {type_select_html}
            </div>
            <div class="form-group">
                <label>Materia:</label>
                <select name="subject" required>
                    <option value="">Selecciona una materia</option>
                    {teacher_subject_options}
                </select>
            </div>
            <div class="form-group">
                <label>Grado al que va dirigido:</label>
                <select name="target_grade" required>
                    <option value="">Selecciona un grado</option>
                    {grade_select_options}
                </select>
            </div>
            <div class="form-group">
                <label>Documento de la tarea/práctica (PDF/Word):</label>
                <input type="file" name="activity_file" accept=".pdf,.doc,.docx" required>
            </div>
            <div class="form-group">
                <label>Máximo de intentos permitidos:</label>
                <input type="number" name="max_attempts" min="1" max="20" value="3" required>
            </div>
            <div class="form-group">
                <label>Tipo de respuesta permitida del estudiante:</label>
                <select name="response_mode" required>
                    <option value="written_only">Escrita (texto/archivo)</option>
                    <option value="video_only">Solo video</option>
                </select>
            </div>
            <div class="form-group"><label>Fecha límite (solo para tarea/práctica):</label><input type="datetime-local" name="due_date"></div>
            <button class="btn btn-primary" type="submit">Publicar</button>
        </form>
    </div>
    """
    return render_template_string(BASE_HTML, title="Publicar", content=content)


@app.route('/teacher/tasks')
def teacher_tasks():
    if not require_login() or not is_teacher():
        return redirect(url_for('login'))
    return redirect(url_for('teacher_post', type='task'))


@app.route('/teacher/practices')
def teacher_practices():
    if not require_login() or not is_teacher():
        return redirect(url_for('login'))

    content = """
    <div class="card" style="max-width:800px; margin:0 auto;">
        <h1>✍️ Prácticas</h1>
        <p>Desde aquí puedes publicar prácticas en documento o crear prácticas dinámicas estilo formulario.</p>
        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:12px;">
            <a class="btn btn-primary" href="/teacher/post?type=practice">Subir práctica (PDF/Word)</a>
            <a class="btn btn-secondary" href="/teacher/practices/form/new">Crear práctica dinámica</a>
            <a class="btn btn-secondary" href="/teacher/my_content?type=practice">Ver entregas de prácticas</a>
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, title="Prácticas", content=content)


@app.route('/teacher/practices/form/new', methods=['GET', 'POST'])
def teacher_new_practice_form():
    if not require_login() or not is_teacher():
        return redirect(url_for('login'))

    data = load_data()
    teacher_user = data['users'].get(session.get('user_id'), {})
    teacher_subjects = sanitize_subjects(teacher_user.get('materias', []))
    if not teacher_subjects and teacher_user.get('materia') in PREDEFINED_SUBJECTS:
        teacher_subjects = [teacher_user.get('materia')]

    if not teacher_subjects:
        flash("No tienes materias asignadas. Contacta al director.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        subject = request.form.get('subject', '').strip()
        target_grade = request.form.get('target_grade', '').strip()
        due_date = request.form.get('due_date', '').strip()
        max_attempts = normalize_max_attempts(request.form.get('max_attempts', '3'), 3)
        form_schema_raw = request.form.get('form_schema', '[]').strip()

        if not title or not subject or not target_grade:
            flash("Completa título, materia y grado", "danger")
            return redirect(url_for('teacher_new_practice_form'))
        if subject not in teacher_subjects:
            flash("Selecciona una materia válida asignada a tu perfil", "danger")
            return redirect(url_for('teacher_new_practice_form'))
        if target_grade not in PREDEFINED_GRADES:
            flash("Selecciona un grado válido", "danger")
            return redirect(url_for('teacher_new_practice_form'))

        try:
            questions = json.loads(form_schema_raw)
        except Exception:
            flash("Formato del formulario inválido", "danger")
            return redirect(url_for('teacher_new_practice_form'))

        if not isinstance(questions, list) or not questions:
            flash("Agrega al menos una pregunta en la práctica dinámica", "danger")
            return redirect(url_for('teacher_new_practice_form'))

        sanitized_questions = []
        for index, question in enumerate(questions, start=1):
            if not isinstance(question, dict):
                continue
            text = str(question.get('question', '')).strip()
            qtype = str(question.get('type', 'short')).strip().lower()
            required = bool(question.get('required', True))
            if not text or qtype not in ['short', 'multiple']:
                continue

            options = []
            if qtype == 'multiple':
                raw_options = question.get('options', [])
                if not isinstance(raw_options, list):
                    raw_options = []
                options = [str(option).strip() for option in raw_options if str(option).strip()]
                if len(options) < 2:
                    continue

            sanitized_questions.append({
                'id': f'q{index}',
                'question': text,
                'type': qtype,
                'required': required,
                'options': options
            })

        if not sanitized_questions:
            flash("No se pudieron validar las preguntas. Revisa la práctica dinámica.", "danger")
            return redirect(url_for('teacher_new_practice_form'))

        post_id = next_numeric_id(data['posts'])
        data['posts'][post_id] = {
            'id': post_id,
            'title': title,
            'description': description,
            'type': 'practice',
            'practice_mode': 'form',
            'form_questions': sanitized_questions,
            'teacher': session.get('user_id'),
            'teacher_name': teacher_user.get('nombre', session.get('user_id')),
            'subject': subject,
            'target_grade': target_grade,
            'max_attempts': max_attempts,
            'due_date': due_date,
            'created_at': datetime.now().isoformat()
        }
        save_data(data)
        flash("Práctica dinámica creada correctamente", "success")
        return redirect(url_for('teacher_my_content', type='practice'))

    grade_select_options = grade_options_html()
    teacher_subject_options = subject_options_html(allowed_subjects=teacher_subjects)
    content = f"""
    <div class="card" style="max-width:900px; margin:0 auto;">
        <h1>🧩 Crear práctica dinámica (estilo formulario)</h1>
        <p>Construye preguntas desde cero como en Google Forms.</p>
        <form method="POST" id="dynamicPracticeForm">
            <div class="form-group"><label>Título:</label><input name="title" required></div>
            <div class="form-group"><label>Descripción:</label><textarea name="description" rows="4"></textarea></div>
            <div class="form-group"><label>Materia:</label><select name="subject" required><option value="">Selecciona</option>{teacher_subject_options}</select></div>
            <div class="form-group"><label>Grado:</label><select name="target_grade" required><option value="">Selecciona</option>{grade_select_options}</select></div>
            <div class="form-group"><label>Máximo de intentos permitidos:</label><input type="number" name="max_attempts" min="1" max="20" value="3" required></div>
            <div class="form-group"><label>Fecha límite (opcional):</label><input type="datetime-local" name="due_date"></div>

            <div class="card" style="margin-top:12px;">
                <h2 style="margin-top:0;">Preguntas</h2>
                <div id="questions-container"></div>
                <div style="display:flex; gap:8px; margin-top:8px; flex-wrap:wrap;">
                    <button type="button" class="btn btn-secondary" id="add-short-question">Agregar pregunta corta</button>
                    <button type="button" class="btn btn-secondary" id="add-multiple-question">Agregar opción múltiple</button>
                </div>
            </div>

            <input type="hidden" name="form_schema" id="form-schema-input">
            <div style="margin-top:12px; display:flex; gap:8px; flex-wrap:wrap;">
                <button class="btn btn-primary" type="submit">Publicar práctica dinámica</button>
                <a class="btn btn-secondary" href="/teacher/practices">Volver</a>
            </div>
        </form>
    </div>

    <script>
        (function() {{
            const questionsContainer = document.getElementById('questions-container');
            const addShortButton = document.getElementById('add-short-question');
            const addMultipleButton = document.getElementById('add-multiple-question');
            const form = document.getElementById('dynamicPracticeForm');
            const schemaInput = document.getElementById('form-schema-input');

            let questions = [];

            function renderQuestions() {{
                questionsContainer.innerHTML = '';
                questions.forEach((question, index) => {{
                    const wrapper = document.createElement('div');
                    wrapper.style.border = '1px solid #374151';
                    wrapper.style.borderRadius = '10px';
                    wrapper.style.padding = '10px';
                    wrapper.style.marginBottom = '8px';

                    const optionsHtml = question.type === 'multiple'
                        ? `<div class="form-group"><label>Opciones (una por línea):</label><textarea data-field="options" data-index="${{index}}" rows="4">${{(question.options || []).join('\\n')}}</textarea></div>`
                        : '';

                    wrapper.innerHTML = `
                        <div class="form-group"><label>Pregunta #${{index + 1}}</label><input data-field="question" data-index="${{index}}" value="${{question.question || ''}}" required></div>
                        <div class="form-group"><label>Tipo:</label><input value="${{question.type === 'multiple' ? 'Opción múltiple' : 'Respuesta corta'}}" disabled></div>
                        ${{optionsHtml}}
                        <div class="form-group"><label><input type="checkbox" data-field="required" data-index="${{index}}" ${{question.required ? 'checked' : ''}}> Obligatoria</label></div>
                        <button type="button" class="btn btn-danger" data-remove="${{index}}">Eliminar</button>
                    `;

                    questionsContainer.appendChild(wrapper);
                }});

                questionsContainer.querySelectorAll('[data-field="question"]').forEach((input) => {{
                    input.addEventListener('input', function() {{
                        const index = Number(this.dataset.index);
                        questions[index].question = this.value;
                    }});
                }});

                questionsContainer.querySelectorAll('[data-field="options"]').forEach((textarea) => {{
                    textarea.addEventListener('input', function() {{
                        const index = Number(this.dataset.index);
                        questions[index].options = this.value.split('\n').map((v) => v.trim()).filter(Boolean);
                    }});
                }});

                questionsContainer.querySelectorAll('[data-field="required"]').forEach((checkbox) => {{
                    checkbox.addEventListener('change', function() {{
                        const index = Number(this.dataset.index);
                        questions[index].required = this.checked;
                    }});
                }});

                questionsContainer.querySelectorAll('[data-remove]').forEach((button) => {{
                    button.addEventListener('click', function() {{
                        const index = Number(this.dataset.remove);
                        questions.splice(index, 1);
                        renderQuestions();
                    }});
                }});
            }}

            addShortButton.addEventListener('click', function() {{
                questions.push({{ type: 'short', question: '', required: true, options: [] }});
                renderQuestions();
            }});

            addMultipleButton.addEventListener('click', function() {{
                questions.push({{ type: 'multiple', question: '', required: true, options: ['Opción 1', 'Opción 2'] }});
                renderQuestions();
            }});

            form.addEventListener('submit', function(event) {{
                if (!questions.length) {{
                    event.preventDefault();
                    alert('Debes agregar al menos una pregunta.');
                    return;
                }}
                schemaInput.value = JSON.stringify(questions);
            }});
        }})();
    </script>
    """
    return render_template_string(BASE_HTML, title="Práctica dinámica", content=content)


@app.route('/teacher/reports', methods=['GET', 'POST'])
def teacher_reports():
    if not require_login() or not is_teacher():
        return redirect(url_for('login'))

    data = load_data()
    users = data.get('users', {})
    teacher_user = users.get(session.get('user_id'), {})
    teacher_subjects = sanitize_subjects(teacher_user.get('materias', []))
    if not teacher_subjects and teacher_user.get('materia') in PREDEFINED_SUBJECTS:
        teacher_subjects = [teacher_user.get('materia')]

    if not teacher_subjects:
        flash("No tienes materias asignadas. Contacta al director.", "danger")
        return redirect(url_for('dashboard'))

    students = [
        {
            'id': user_id,
            'nombre': user.get('nombre', user_id),
            'grado': user.get('grado', '')
        }
        for user_id, user in users.items()
        if user.get('role') == 'student'
    ]
    students.sort(key=lambda student: student.get('nombre', '').lower())

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        subject = request.form.get('subject', '').strip()
        target_grade = request.form.get('target_grade', '').strip()
        target_student = request.form.get('target_student', '').strip()
        due_date = request.form.get('due_date', '').strip()
        file = request.files.get('report_file')

        student_user = users.get(target_student, {})
        if not title or not subject or not target_grade or not target_student:
            flash("Completa todos los campos obligatorios del informe", "danger")
            return redirect(url_for('teacher_reports'))
        if subject not in teacher_subjects:
            flash("Selecciona una materia válida asignada a tu perfil", "danger")
            return redirect(url_for('teacher_reports'))
        if target_grade not in PREDEFINED_GRADES:
            flash("Selecciona un grado válido", "danger")
            return redirect(url_for('teacher_reports'))
        if not student_user or student_user.get('role') != 'student':
            flash("Selecciona un estudiante válido", "danger")
            return redirect(url_for('teacher_reports'))
        if student_user.get('grado') != target_grade:
            flash("El estudiante seleccionado no pertenece al grado elegido", "danger")
            return redirect(url_for('teacher_reports'))
        if not file or not file.filename:
            flash("Debes adjuntar el documento del informe", "danger")
            return redirect(url_for('teacher_reports'))
        if not allowed_report_file(file.filename):
            flash("Formato no permitido. Sube PDF, DOC o DOCX", "danger")
            return redirect(url_for('teacher_reports'))

        original_filename = file.filename
        safe_name = secure_filename(original_filename)
        unique_name = f"{int(datetime.now().timestamp() * 1000)}_{safe_name}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_name)
        file.save(file_path)

        post_id = next_numeric_id(data['posts'])
        data['posts'][post_id] = {
            'id': post_id,
            'title': title,
            'description': description,
            'type': 'report',
            'teacher': session.get('user_id'),
            'teacher_name': teacher_user.get('nombre', session.get('user_id')),
            'subject': subject,
            'target_grade': target_grade,
            'target_student': target_student,
            'target_student_name': student_user.get('nombre', target_student),
            'report_file': unique_name,
            'report_original_name': original_filename,
            'report_extension': report_extension(original_filename),
            'due_date': due_date,
            'created_at': datetime.now().isoformat()
        }
        save_data(data)
        flash("Informe publicado correctamente", "success")
        return redirect(url_for('teacher_reports'))

    reports = [
        {'id': post_id, **post}
        for post_id, post in data.get('posts', {}).items()
        if post.get('teacher') == session.get('user_id') and post.get('type') == 'report'
    ]
    reports.sort(key=lambda report: report.get('created_at', ''), reverse=True)

    grade_select_options = grade_options_html()
    teacher_subject_options = subject_options_html(allowed_subjects=teacher_subjects)
    students_json = json.dumps(students, ensure_ascii=False)

    report_cards = ""
    for report in reports:
        file_name = report.get('report_original_name', 'Documento')
        report_cards += f"""
        <div class="task-card">
            <h3>📑 {report.get('title', '-')}</h3>
            <p><strong>Materia:</strong> {report.get('subject', '-')}</p>
            <p><strong>Grado:</strong> {report.get('target_grade', '-')}</p>
            <p><strong>Estudiante:</strong> {report.get('target_student_name', report.get('target_student', '-'))}</p>
            <p>{report.get('description', '')}</p>
            <p><strong>Archivo:</strong> {file_name}</p>
            <p><strong>Fecha límite:</strong> {report.get('due_date') or 'No aplica'}</p>
            <a class="btn btn-secondary" href="/uploads/{report.get('report_file', '')}" target="_blank">Ver/descargar archivo</a>
        </div>
        """

    content = f"""
    <div class="card" style="max-width:850px; margin:0 auto;">
        <h1>📑 Apartado de Informes</h1>
        <p>Sube informes por grado y alumno, con archivo en PDF o Word.</p>
        <form method="POST" enctype="multipart/form-data" id="reportForm">
            <div class="form-group"><label>Título del informe:</label><input type="text" name="title" required></div>
            <div class="form-group"><label>Descripción:</label><textarea name="description" rows="4" placeholder="Comentario opcional"></textarea></div>
            <div class="form-group">
                <label>Materia:</label>
                <select name="subject" required>
                    <option value="">Selecciona una materia</option>
                    {teacher_subject_options}
                </select>
            </div>
            <div class="form-group">
                <label>Grado:</label>
                <select id="report-grade" name="target_grade" required>
                    <option value="">Selecciona un grado</option>
                    {grade_select_options}
                </select>
            </div>
            <div class="form-group">
                <label>Estudiante:</label>
                <select id="report-student" name="target_student" required>
                    <option value="">Primero selecciona un grado</option>
                </select>
            </div>
            <div class="form-group"><label>Fecha límite (opcional):</label><input type="datetime-local" name="due_date"></div>
            <div class="form-group">
                <label>Documento (PDF/Word):</label>
                <input type="file" name="report_file" accept=".pdf,.doc,.docx" required>
            </div>
            <button class="btn btn-primary" type="submit">Publicar informe</button>
        </form>
    </div>

    <div class="card" style="margin-top:20px;">
        <h2>Informes publicados</h2>
        <div class="tasks-grid">
            {report_cards if report_cards else '<p>No has publicado informes todavía.</p>'}
        </div>
    </div>

    <script>
        (function() {{
            const students = {students_json};
            const gradeSelect = document.getElementById('report-grade');
            const studentSelect = document.getElementById('report-student');

            function populateStudents() {{
                const grade = gradeSelect.value;
                const filtered = students.filter((student) => (student.grado || '') === grade);

                studentSelect.innerHTML = '';
                if (!grade) {{
                    studentSelect.innerHTML = '<option value="">Primero selecciona un grado</option>';
                    return;
                }}
                if (!filtered.length) {{
                    studentSelect.innerHTML = '<option value="">No hay estudiantes en este grado</option>';
                    return;
                }}

                studentSelect.innerHTML = '<option value="">Selecciona un estudiante</option>';
                filtered.forEach((student) => {{
                    const option = document.createElement('option');
                    option.value = student.id;
                    option.textContent = `${{student.nombre}} (${{student.id}})`;
                    studentSelect.appendChild(option);
                }});
            }}

            gradeSelect.addEventListener('change', populateStudents);
            populateStudents();
        }})();
    </script>
    """
    return render_template_string(BASE_HTML, title="Informes", content=content)


@app.route('/teacher/content')
@app.route('/teacher/my_content')
def teacher_my_content():
    if not require_login() or not is_teacher():
        return redirect(url_for('login'))

    data = load_data()
    filter_type = request.args.get('type', '').strip().lower()
    if filter_type not in ['task', 'practice']:
        filter_type = ''

    my_posts = [
        {'id': post_id, **post}
        for post_id, post in data.get('posts', {}).items()
        if post.get('teacher') == session.get('user_id') and post.get('type') in ['task', 'practice'] and (not filter_type or post.get('type') == filter_type)
    ]
    my_posts.sort(key=lambda p: p.get('created_at', ''), reverse=True)
    submissions = data.get('submissions', {})

    cards = ""
    labels = {'task': 'Tarea', 'practice': 'Práctica'}
    for post in my_posts:
        related_submissions = [s for s in submissions.values() if s.get('post_id') == post.get('id')]
        submissions_html = ""
        for sub in related_submissions:
            video_link = ""
            if sub.get('video_url'):
                video_link = f"<p><a class='btn btn-secondary' style='padding:6px 10px;' href='{sub.get('video_url')}' target='_blank'>Ver video del estudiante</a></p>"
            uploaded_video_link = ""
            if sub.get('response_video_file'):
                uploaded_video_link = f"<p><a class='btn btn-secondary' style='padding:6px 10px;' href='/uploads/{sub.get('response_video_file')}' target='_blank'>Ver video subido</a> <span style='font-size:12px;'>({sub.get('response_video_original_name', 'video')})</span></p>"
            file_link = ""
            if sub.get('response_file'):
                file_link = f"<p><a class='btn btn-primary' style='padding:6px 10px;' href='/uploads/{sub.get('response_file')}' target='_blank'>Ver archivo entregado</a> <span style='font-size:12px;'>({sub.get('response_original_name', 'archivo')})</span></p>"
            grade_value = sub.get('grade', '')
            feedback_value = sub.get('teacher_feedback', '')
            attempt_label = sub.get('attempt_number', '-')
            sent_at = sub.get('created_at', '')
            form_answers_html = ""
            if isinstance(sub.get('form_answers'), list) and sub.get('form_answers'):
                answers_blocks = "".join([
                    f"<li><strong>{answer.get('question', 'Pregunta')}:</strong> {answer.get('answer', '-')}</li>"
                    for answer in sub.get('form_answers', []) if isinstance(answer, dict)
                ])
                if answers_blocks:
                    form_answers_html = f"<p><strong>Respuestas del formulario:</strong></p><ul>{answers_blocks}</ul>"
            submissions_html += f"""
            <div style="background:#f8f9fa; padding:10px; border-radius:8px; margin-top:8px;">
                <p><strong>Estudiante:</strong> {sub.get('student_name', sub.get('student'))}</p>
                <p><strong>Intento:</strong> {attempt_label} | <strong>Enviado:</strong> {sent_at or '-'}</p>
                <p><strong>Respuesta:</strong> {sub.get('response_text', '')}</p>
                {form_answers_html}
                {video_link}
                {uploaded_video_link}
                {file_link}
                <form method="POST" action="/teacher/submissions/grade/{sub.get('id')}" style="margin-top:10px; background:#fff; border:1px solid #e5e7eb; border-radius:8px; padding:10px;">
                    <div class="form-group" style="margin-bottom:8px;">
                        <label>Calificación (0 a 100):</label>
                        <input type="number" name="grade" min="0" max="100" step="0.01" value="{grade_value}">
                    </div>
                    <div class="form-group" style="margin-bottom:8px;">
                        <label>Comentario del docente:</label>
                        <textarea name="teacher_feedback" rows="2" placeholder="Retroalimentación para el estudiante">{feedback_value}</textarea>
                    </div>
                    <button class="btn btn-secondary" type="submit" style="padding:6px 10px;">Guardar calificación</button>
                </form>
            </div>
            """

        activity_file_html = ""
        if post.get('resource_file'):
            activity_file_html = f"<p><strong>Documento:</strong> {post.get('resource_original_name', 'archivo')}</p><p><a class='btn btn-secondary' style='padding:6px 10px;' href='/uploads/{post.get('resource_file')}' target='_blank'>Ver/descargar documento</a></p>"
        elif post.get('practice_mode') == 'form':
            activity_file_html = "<p><strong>Modalidad:</strong> Práctica dinámica tipo formulario</p>"

        cards += f"""
        <div class="task-card">
            <h3>{labels.get(post.get('type'), 'Contenido')} - {post.get('title')}</h3>
            <p><strong>Materia:</strong> {post.get('subject', '-')}</p>
            <p><strong>Grado:</strong> {post.get('target_grade', '-')}</p>
            <p><strong>Máximo intentos:</strong> {post_max_attempts(post)}</p>
            <p><strong>Tipo de respuesta:</strong> {response_mode_label(post.get('response_mode', 'written_only'))}</p>
            <p>{post.get('description', '')}</p>
            {activity_file_html}
            <p><strong>Fecha límite:</strong> {post.get('due_date') or 'No aplica'}</p>
            <p><strong>Respuestas de estudiantes:</strong> {len(related_submissions)}</p>
            {submissions_html if submissions_html else '<p style="color:#7f8c8d;">Sin respuestas aún.</p>'}
        </div>
        """

    section_title = "📚 Mi contenido publicado"
    if filter_type == 'task':
        section_title = "📋 Mis tareas"
    elif filter_type == 'practice':
        section_title = "✍️ Mis prácticas"

    content = f"""
    <div class="card">
        <h1>{section_title}</h1>
        <div class="tasks-grid">
            {cards if cards else '<p>No has publicado contenido todavía.</p>'}
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, title="Mi contenido", content=content)


@app.route('/teacher/submissions/grade/<submission_id>', methods=['POST'])
def teacher_grade_submission(submission_id):
    if not require_login() or not is_teacher():
        return redirect(url_for('login'))

    data = load_data()
    submission = data.get('submissions', {}).get(submission_id)
    if not submission:
        flash("Entrega no encontrada", "danger")
        return redirect(url_for('teacher_my_content'))

    post = data.get('posts', {}).get(submission.get('post_id'))
    if not post or post.get('teacher') != session.get('user_id'):
        flash("No tienes permiso para calificar esta entrega", "danger")
        return redirect(url_for('teacher_my_content'))

    grade_raw = request.form.get('grade', '').strip()
    feedback = request.form.get('teacher_feedback', '').strip()

    if grade_raw:
        try:
            grade_num = float(grade_raw)
        except ValueError:
            flash("La calificación debe ser numérica", "danger")
            return redirect(url_for('teacher_my_content'))
        if grade_num < 0 or grade_num > 100:
            flash("La calificación debe estar entre 0 y 100", "danger")
            return redirect(url_for('teacher_my_content'))
        submission['grade'] = round(grade_num, 2)
    else:
        submission['grade'] = ''

    submission['teacher_feedback'] = feedback
    submission['graded_at'] = datetime.now().isoformat()

    data['submissions'][submission_id] = submission
    save_data(data)
    flash("Calificación guardada", "success")
    return redirect(url_for('teacher_my_content'))


@app.route('/student/tasks')
def student_tasks():
    if not require_login() or not is_student():
        return redirect(url_for('login'))
    return redirect(url_for('student_content', type='task'))


@app.route('/student/practices')
def student_practices():
    if not require_login() or not is_student():
        return redirect(url_for('login'))
    return redirect(url_for('student_content', type='practice'))


@app.route('/student/content')
def student_content():
    if not require_login() or not is_student():
        return redirect(url_for('login'))

    filter_type = request.args.get('type', '').strip().lower()
    if filter_type not in ['task', 'practice']:
        filter_type = ''

    data = load_data()
    student_user = data.get('users', {}).get(session.get('user_id'), {})
    student_grade = student_user.get('grado', '')

    posts = [
        {'id': post_id, **post}
        for post_id, post in data.get('posts', {}).items()
        if post.get('target_grade') == student_grade and post.get('type') in ['task', 'practice'] and (not filter_type or post.get('type') == filter_type)
    ]
    posts.sort(key=lambda p: p.get('created_at', ''), reverse=True)
    subjects = sorted(list({post.get('subject', '-') for post in posts if post.get('subject')}))
    submissions = data.get('submissions', {})

    labels = {'task': '📋 Tarea', 'practice': '✍️ Práctica'}
    cards = ""
    for post in posts:
        file_url = f"/uploads/{post.get('resource_file', '')}" if post.get('resource_file') else ""
        ext = post.get('resource_extension') or report_extension(post.get('resource_original_name', ''))
        safe_title = str(post.get('title', 'Documento')).replace('"', '&quot;').replace("'", '&#39;')
        resource_actions = ""
        if post.get('type') == 'practice' and post.get('practice_mode') == 'form':
            resource_actions = f"<p><strong>Modalidad:</strong> Formulario dinámico</p><a class='btn btn-secondary' href='/student/practice-form/{post.get('id')}'>Responder formulario</a>"
        elif file_url:
            resource_actions = f"""
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;">
                <button type="button" class="btn btn-secondary open-activity-modal" data-url="{file_url}" data-ext="{ext}" data-title="{safe_title}">Ver documento</button>
                <a class="btn btn-secondary" href="{file_url}" target="_blank">Descargar</a>
            </div>
            """
        else:
            resource_actions = "<p style='color:#7f8c8d;'>Sin documento adjunto.</p>"

        my_submissions = [
            sub for sub in submissions.values()
            if sub.get('post_id') == post.get('id') and sub.get('student') == session.get('user_id')
        ]
        my_submissions.sort(key=lambda sub: sub.get('created_at', ''), reverse=True)
        latest_submission = my_submissions[0] if my_submissions else None
        max_attempts = post_max_attempts(post)
        attempts_count = len(my_submissions)
        attempts_left = max_attempts - attempts_count
        response_mode = normalize_response_mode(post.get('response_mode', 'written_only'), 'written_only')
        response_mode_text = response_mode_label(response_mode)

        submission_status = "<p style='color:#ef4444;'><strong>Estado:</strong> Pendiente de entrega</p>"
        if latest_submission:
            grade_value = latest_submission.get('grade')
            feedback_value = latest_submission.get('teacher_feedback', '')
            grade_text = f"Nota: {grade_value}" if str(grade_value).strip() != '' else "Nota pendiente"
            feedback_text = feedback_value if feedback_value else "Sin comentario del docente"
            last_attempt = latest_submission.get('attempt_number', attempts_count)
            sent_at = latest_submission.get('created_at', '')
            submission_status = f"<p style='color:#22c55e;'><strong>Estado:</strong> Entregado</p><p><strong>Intento actual:</strong> {last_attempt} | <strong>Total intentos:</strong> {attempts_count} / {max_attempts}</p><p><strong>Intentos restantes:</strong> {attempts_left if attempts_left > 0 else 0}</p><p><strong>Último envío:</strong> {sent_at or '-'}</p><p><strong>{grade_text}</strong></p><p><strong>Comentario:</strong> {feedback_text}</p>"
        else:
            submission_status = f"<p style='color:#ef4444;'><strong>Estado:</strong> Pendiente de entrega</p><p><strong>Intentos disponibles:</strong> {max_attempts}</p>"

        answer_button_text = 'Responder escrito (texto/archivo)'
        if response_mode == 'video_only':
            answer_button_text = 'Responder con video'
        answer_link = f"<a class='btn btn-primary' href='/student/respond/{post.get('id')}'>{answer_button_text}</a>"
        if post.get('type') == 'practice' and post.get('practice_mode') == 'form':
            answer_link = f"<a class='btn btn-primary' href='/student/practice-form/{post.get('id')}'>Responder formulario</a>"
        if attempts_left <= 0:
            answer_link = "<p style='color:#ef4444;'><strong>Límite de intentos alcanzado.</strong></p>"

        cards += f"""
        <div class="task-card">
            <h3>{labels.get(post.get('type'), 'Contenido')} - {post.get('title')}</h3>
            <p><strong>Profesor:</strong> {post.get('teacher_name', post.get('teacher'))}</p>
            <p><strong>Materia:</strong> {post.get('subject', '-')}</p>
            <p>{post.get('description', '')}</p>
            <p><strong>Respuesta permitida:</strong> {response_mode_text}</p>
            <p><strong>Fecha límite:</strong> {post.get('due_date') or 'No aplica'}</p>
            {resource_actions}
            {submission_status}
            {answer_link}
        </div>
        """

    page_title = "Contenido Académico"
    heading = "🎒 Contenido de tus profesores"
    if filter_type == 'task':
        page_title = "Tareas"
        heading = "📋 Tareas"
    elif filter_type == 'practice':
        page_title = "Prácticas"
        heading = "✍️ Prácticas"

    content = f"""
    <div class="card">
        <h1>{heading}</h1>
        <p><strong>Tu grado:</strong> {student_grade or 'Sin grado asignado'}</p>
        <p><strong>Materias que recibes:</strong> {', '.join(subjects) if subjects else 'Sin materias asignadas todavía'}</p>
        <div class="tasks-grid">
            {cards if cards else '<p>No hay contenido publicado para tu grado aún.</p>'}
        </div>
    </div>

    <div id="activity-modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.65); z-index:9999; padding:24px;">
        <div style="background:#fff; width:min(1100px, 96vw); height:min(88vh, 900px); margin:0 auto; border-radius:12px; overflow:hidden; display:flex; flex-direction:column;">
            <div style="padding:12px 16px; border-bottom:1px solid #ddd; display:flex; justify-content:space-between; align-items:center;">
                <h2 id="activity-modal-title" style="margin:0; font-size:20px; color:#111;">Vista previa de documento</h2>
                <button id="activity-modal-close" class="btn btn-danger" type="button">Cerrar</button>
            </div>
            <div id="activity-modal-body" style="flex:1; background:#f3f4f6; overflow:auto; padding:10px;">
                <iframe id="activity-pdf-frame" title="Vista previa PDF" style="display:none; width:100%; height:100%; border:none; background:#fff;"></iframe>
                <div id="activity-docx-container" style="display:none; background:#fff; min-height:100%; padding:16px;"></div>
                <div id="activity-fallback" style="display:none; color:#111; padding:16px;"></div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/docx-preview@0.3.6/dist/docx-preview.min.js"></script>
    <script>
        (function() {{
            const modal = document.getElementById('activity-modal');
            const closeButton = document.getElementById('activity-modal-close');
            const titleElement = document.getElementById('activity-modal-title');
            const pdfFrame = document.getElementById('activity-pdf-frame');
            const docxContainer = document.getElementById('activity-docx-container');
            const fallback = document.getElementById('activity-fallback');
            const buttons = Array.from(document.querySelectorAll('.open-activity-modal'));

            function resetPreview() {{
                pdfFrame.style.display = 'none';
                docxContainer.style.display = 'none';
                fallback.style.display = 'none';
                pdfFrame.src = '';
                docxContainer.innerHTML = '';
                fallback.innerHTML = '';
            }}

            function closeModal() {{
                resetPreview();
                modal.style.display = 'none';
            }}

            async function openModal(button) {{
                const url = button.dataset.url || '';
                const ext = (button.dataset.ext || '').toLowerCase();
                const title = button.dataset.title || 'Documento';
                titleElement.textContent = `Vista previa: ${{title}}`;

                resetPreview();
                modal.style.display = 'block';

                if (!url) {{
                    fallback.style.display = 'block';
                    fallback.innerHTML = '<p>No se encontró el archivo.</p>';
                    return;
                }}

                if (ext === 'pdf') {{
                    pdfFrame.style.display = 'block';
                    pdfFrame.src = `${{url}}#view=FitH`;
                    return;
                }}

                if (ext === 'docx') {{
                    docxContainer.style.display = 'block';
                    try {{
                        const response = await fetch(url);
                        const blob = await response.blob();
                        const buffer = await blob.arrayBuffer();
                        await window.docx.renderAsync(buffer, docxContainer);
                    }} catch (error) {{
                        fallback.style.display = 'block';
                        fallback.innerHTML = '<p>No fue posible previsualizar el archivo DOCX. Descárgalo para verlo.</p>';
                        docxContainer.style.display = 'none';
                    }}
                    return;
                }}

                fallback.style.display = 'block';
                fallback.innerHTML = '<p>Vista previa no disponible para .doc. Descárgalo para abrirlo en Word.</p>';
            }}

            buttons.forEach((button) => {{
                button.addEventListener('click', function() {{
                    openModal(button);
                }});
            }});

            closeButton.addEventListener('click', closeModal);
            modal.addEventListener('click', function(event) {{
                if (event.target === modal) {{
                    closeModal();
                }}
            }});
            document.addEventListener('keydown', function(event) {{
                if (event.key === 'Escape' && modal.style.display === 'block') {{
                    closeModal();
                }}
            }});
        }})();
    </script>
    """
    return render_template_string(BASE_HTML, title=page_title, content=content)


@app.route('/student/reports')
def student_reports():
    if not require_login() or not is_student():
        return redirect(url_for('login'))

    data = load_data()
    student_id = session.get('user_id')
    student_user = data.get('users', {}).get(student_id, {})
    student_grade = student_user.get('grado', '')

    reports = [
        {'id': post_id, **post}
        for post_id, post in data.get('posts', {}).items()
        if post.get('type') == 'report' and (
            post.get('target_student') == student_id or
            (not post.get('target_student') and post.get('target_grade') == student_grade)
        )
    ]
    reports.sort(key=lambda report: report.get('created_at', ''), reverse=True)

    cards = ""
    for report in reports:
        stored_file = report.get('report_file', '')
        file_url = f"/uploads/{stored_file}" if stored_file else ""
        ext = report.get('report_extension') or report_extension(report.get('report_original_name', ''))
        cards += f"""
        <div class="task-card">
            <h3>📑 {report.get('title', '-')}</h3>
            <p><strong>Docente:</strong> {report.get('teacher_name', report.get('teacher', '-'))}</p>
            <p><strong>Materia:</strong> {report.get('subject', '-')}</p>
            <p><strong>Grado:</strong> {report.get('target_grade', '-')}</p>
            <p>{report.get('description', '')}</p>
            <p><strong>Archivo:</strong> {report.get('report_original_name', 'Documento')}</p>
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;">
                <button
                    type="button"
                    class="btn btn-primary open-report-modal"
                    data-url="{file_url}"
                    data-ext="{ext}"
                    data-title="{report.get('title', 'Informe')}"
                >Ver informe</button>
                <a class="btn btn-secondary" href="{file_url}" target="_blank">Descargar</a>
            </div>
        </div>
        """

    content = f"""
    <div class="card">
        <h1>📑 Apartado de Informes</h1>
        <p><strong>Tu grado:</strong> {student_grade or 'Sin grado asignado'}</p>
        <div class="tasks-grid">
            {cards if cards else '<p>No tienes informes asignados por ahora.</p>'}
        </div>
    </div>

    <div id="report-modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.65); z-index:9999; padding:24px;">
        <div style="background:#fff; width:min(1100px, 96vw); height:min(88vh, 900px); margin:0 auto; border-radius:12px; overflow:hidden; display:flex; flex-direction:column;">
            <div style="padding:12px 16px; border-bottom:1px solid #ddd; display:flex; justify-content:space-between; align-items:center;">
                <h2 id="report-modal-title" style="margin:0; font-size:20px; color:#111;">Vista previa de informe</h2>
                <button id="report-modal-close" class="btn btn-danger" type="button">Cerrar</button>
            </div>
            <div id="report-modal-body" style="flex:1; background:#f3f4f6; overflow:auto; padding:10px;">
                <iframe id="report-pdf-frame" title="Vista previa PDF" style="display:none; width:100%; height:100%; border:none; background:#fff;"></iframe>
                <div id="report-docx-container" style="display:none; background:#fff; min-height:100%; padding:16px;"></div>
                <div id="report-fallback" style="display:none; color:#111; padding:16px;"></div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/docx-preview@0.3.6/dist/docx-preview.min.js"></script>
    <script>
        (function() {{
            const modal = document.getElementById('report-modal');
            const closeButton = document.getElementById('report-modal-close');
            const titleElement = document.getElementById('report-modal-title');
            const pdfFrame = document.getElementById('report-pdf-frame');
            const docxContainer = document.getElementById('report-docx-container');
            const fallback = document.getElementById('report-fallback');
            const buttons = Array.from(document.querySelectorAll('.open-report-modal'));

            function resetPreview() {{
                pdfFrame.style.display = 'none';
                docxContainer.style.display = 'none';
                fallback.style.display = 'none';
                pdfFrame.src = '';
                docxContainer.innerHTML = '';
                fallback.innerHTML = '';
            }}

            function closeModal() {{
                resetPreview();
                modal.style.display = 'none';
            }}

            async function openModal(button) {{
                const url = button.dataset.url || '';
                const ext = (button.dataset.ext || '').toLowerCase();
                const title = button.dataset.title || 'Informe';
                titleElement.textContent = `Vista previa: ${{title}}`;

                resetPreview();
                modal.style.display = 'block';

                if (!url) {{
                    fallback.style.display = 'block';
                    fallback.innerHTML = '<p>No se encontró el archivo del informe.</p>';
                    return;
                }}

                if (ext === 'pdf') {{
                    pdfFrame.style.display = 'block';
                    pdfFrame.src = `${{url}}#view=FitH`;
                    return;
                }}

                if (ext === 'docx') {{
                    docxContainer.style.display = 'block';
                    try {{
                        const response = await fetch(url);
                        const blob = await response.blob();
                        const buffer = await blob.arrayBuffer();
                        await window.docx.renderAsync(buffer, docxContainer);
                    }} catch (error) {{
                        fallback.style.display = 'block';
                        fallback.innerHTML = '<p>No fue posible previsualizar el archivo DOCX. Usa el botón Descargar.</p>';
                        docxContainer.style.display = 'none';
                    }}
                    return;
                }}

                fallback.style.display = 'block';
                fallback.innerHTML = '<p>Vista previa no disponible para .doc. Usa el botón Descargar para verlo en Word.</p>';
            }}

            buttons.forEach((button) => {{
                button.addEventListener('click', function() {{
                    openModal(button);
                }});
            }});

            closeButton.addEventListener('click', closeModal);
            modal.addEventListener('click', function(event) {{
                if (event.target === modal) {{
                    closeModal();
                }}
            }});
            document.addEventListener('keydown', function(event) {{
                if (event.key === 'Escape' && modal.style.display === 'block') {{
                    closeModal();
                }}
            }});
        }})();
    </script>
    """
    return render_template_string(BASE_HTML, title="Informes", content=content)


@app.route('/student/practice-form/<post_id>', methods=['GET', 'POST'])
def student_practice_form(post_id):
    if not require_login() or not is_student():
        return redirect(url_for('login'))

    data = load_data()
    post = data.get('posts', {}).get(post_id)
    if not post or post.get('type') != 'practice' or post.get('practice_mode') != 'form':
        flash("Práctica dinámica no encontrada", "danger")
        return redirect(url_for('student_practices'))

    student_user = data.get('users', {}).get(session.get('user_id'), {})
    student_grade = student_user.get('grado', '')
    if post.get('target_grade') != student_grade:
        flash("No tienes acceso a esta práctica", "danger")
        return redirect(url_for('student_practices'))

    questions = post.get('form_questions', [])
    if not isinstance(questions, list) or not questions:
        flash("Esta práctica no tiene preguntas configuradas", "danger")
        return redirect(url_for('student_practices'))

    if request.method == 'POST':
        existing_submissions = [
            sub for sub in data.get('submissions', {}).values()
            if sub.get('post_id') == post_id and sub.get('student') == session.get('user_id')
        ]
        max_attempts = post_max_attempts(post)
        if len(existing_submissions) >= max_attempts:
            flash(f"Has alcanzado el máximo de {max_attempts} intentos permitidos", "danger")
            return redirect(url_for('student_practice_form', post_id=post_id))
        attempt_number = len(existing_submissions) + 1

        answers = []
        for question in questions:
            if not isinstance(question, dict):
                continue
            qid = question.get('id')
            qtext = question.get('question', 'Pregunta')
            required = bool(question.get('required', True))
            answer = request.form.get(f"q_{qid}", '').strip()
            if required and not answer:
                flash("Completa todas las preguntas obligatorias", "danger")
                return redirect(url_for('student_practice_form', post_id=post_id))
            answers.append({'question': qtext, 'answer': answer})

        submission_id = next_numeric_id(data['submissions'])
        data['submissions'][submission_id] = {
            'id': submission_id,
            'post_id': post_id,
            'post_title': post.get('title'),
            'student': session.get('user_id'),
            'student_name': student_user.get('nombre', session.get('user_id')),
            'teacher': post.get('teacher'),
            'attempt_number': attempt_number,
            'response_text': 'Formulario dinámico enviado',
            'form_answers': answers,
            'video_url': '',
            'response_file': '',
            'response_original_name': '',
            'response_extension': '',
            'created_at': datetime.now().isoformat()
        }
        save_data(data)
        flash("Práctica enviada correctamente", "success")
        return redirect(url_for('student_practices'))

    questions_html = ""
    for idx, question in enumerate(questions, start=1):
        if not isinstance(question, dict):
            continue
        qid = question.get('id', f'q{idx}')
        qtext = question.get('question', f'Pregunta {idx}')
        qtype = question.get('type', 'short')
        required_attr = 'required' if question.get('required', True) else ''

        answer_input_html = f"<textarea name='q_{qid}' rows='3' {required_attr}></textarea>"
        if qtype == 'multiple':
            options = question.get('options', []) if isinstance(question.get('options', []), list) else []
            opts = [str(opt).strip() for opt in options if str(opt).strip()]
            radios = "".join([
                f"<label style='display:block; margin-top:6px;'><input type='radio' name='q_{qid}' value='{opt}' {required_attr}> {opt}</label>"
                for opt in opts
            ])
            answer_input_html = radios or answer_input_html

        questions_html += f"""
        <div class="card" style="margin-top:10px;">
            <p><strong>{idx}. {qtext}</strong>{' *' if question.get('required', True) else ''}</p>
            {answer_input_html}
        </div>
        """

    content = f"""
    <div class="card" style="max-width:900px; margin:0 auto;">
        <h1>✍️ Responder práctica dinámica</h1>
        <p><strong>Título:</strong> {post.get('title', '-')}</p>
        <p><strong>Materia:</strong> {post.get('subject', '-')}</p>
        <p><strong>Profesor:</strong> {post.get('teacher_name', post.get('teacher', '-'))}</p>
        <p><strong>Máximo de intentos:</strong> {post_max_attempts(post)}</p>
        <form method="POST">
            {questions_html}
            <div style="margin-top:12px; display:flex; gap:8px; flex-wrap:wrap;">
                <button class="btn btn-primary" type="submit">Enviar práctica</button>
                <a class="btn btn-secondary" href="/student/practices">Volver</a>
            </div>
        </form>
    </div>
    """
    return render_template_string(BASE_HTML, title="Práctica dinámica", content=content)


@app.route('/student/respond/<post_id>', methods=['GET', 'POST'])
def student_respond(post_id):
    if not require_login() or not is_student():
        return redirect(url_for('login'))

    data = load_data()
    post = data.get('posts', {}).get(post_id)
    if not post:
        flash("Publicación no encontrada", "danger")
        return redirect(url_for('student_content'))
    if post.get('type') not in ['task', 'practice']:
        flash("Solo puedes responder tareas y prácticas desde este apartado", "danger")
        return redirect(url_for('student_content'))
    if post.get('type') == 'practice' and post.get('practice_mode') == 'form':
        return redirect(url_for('student_practice_form', post_id=post_id))

    my_submissions = [
        sub for sub in data.get('submissions', {}).values()
        if sub.get('post_id') == post_id and sub.get('student') == session.get('user_id')
    ]
    my_submissions.sort(key=lambda sub: sub.get('created_at', ''), reverse=True)
    latest_submission = my_submissions[0] if my_submissions else None
    max_attempts = post_max_attempts(post)
    attempts_count = len(my_submissions)
    response_mode = normalize_response_mode(post.get('response_mode', 'written_only'), 'written_only')
    response_mode_text = response_mode_label(response_mode)

    if request.method == 'POST':
        existing_submissions = [
            sub for sub in data.get('submissions', {}).values()
            if sub.get('post_id') == post_id and sub.get('student') == session.get('user_id')
        ]
        if len(existing_submissions) >= max_attempts:
            flash(f"Has alcanzado el máximo de {max_attempts} intentos permitidos", "danger")
            return redirect(url_for('student_respond', post_id=post_id))
        attempt_number = len(existing_submissions) + 1

        response_text = request.form.get('response_text', '').strip()
        video_url = request.form.get('video_url', '').strip()
        response_file = request.files.get('response_file')
        video_file = request.files.get('video_file')
        response_file_name = ""
        response_original_name = ""
        response_ext = ""
        response_video_file_name = ""
        response_video_original_name = ""
        response_video_ext = ""

        has_file = bool(response_file and response_file.filename)
        if has_file and not allowed_report_file(response_file.filename):
            flash("Formato no permitido. Sube PDF, DOC o DOCX", "danger")
            return redirect(url_for('student_respond', post_id=post_id))
        if has_file:
            response_original_name = response_file.filename
            safe_name = secure_filename(response_original_name)
            response_file_name = f"{int(datetime.now().timestamp() * 1000)}_{safe_name}"
            response_path = os.path.join(UPLOAD_FOLDER, response_file_name)
            response_file.save(response_path)
            response_ext = report_extension(response_original_name)

        has_video_file = bool(video_file and video_file.filename)
        if has_video_file and not allowed_video_file(video_file.filename):
            flash("Formato de video no permitido. Sube MP4, MOV, WEBM o M4V", "danger")
            return redirect(url_for('student_respond', post_id=post_id))
        if has_video_file:
            response_video_original_name = video_file.filename
            safe_video_name = secure_filename(response_video_original_name)
            response_video_file_name = f"{int(datetime.now().timestamp() * 1000)}_{safe_video_name}"
            response_video_path = os.path.join(UPLOAD_FOLDER, response_video_file_name)
            video_file.save(response_video_path)
            response_video_ext = report_extension(response_video_original_name)

        has_written_response = bool(response_text or has_file)
        has_video_response = bool(video_url or has_video_file)

        if response_mode == 'video_only':
            if has_written_response:
                flash("Esta actividad es solo en video. Quita la respuesta escrita o archivo.", "danger")
                return redirect(url_for('student_respond', post_id=post_id))
            if not has_video_response:
                flash("Esta actividad requiere respuesta en video (enlace o video subido).", "danger")
                return redirect(url_for('student_respond', post_id=post_id))
        else:
            if has_video_response:
                flash("Esta actividad es escrita. Quita el video y responde con texto o archivo.", "danger")
                return redirect(url_for('student_respond', post_id=post_id))
            if not has_written_response:
                flash("Esta actividad requiere respuesta escrita (texto o archivo).", "danger")
                return redirect(url_for('student_respond', post_id=post_id))

        submission_id = next_numeric_id(data['submissions'])
        student_user = data.get('users', {}).get(session.get('user_id'), {})
        data['submissions'][submission_id] = {
            'id': submission_id,
            'post_id': post_id,
            'post_title': post.get('title'),
            'student': session.get('user_id'),
            'student_name': student_user.get('nombre', session.get('user_id')),
            'teacher': post.get('teacher'),
            'attempt_number': attempt_number,
            'response_text': response_text,
            'video_url': video_url,
            'response_video_file': response_video_file_name,
            'response_video_original_name': response_video_original_name,
            'response_video_extension': response_video_ext,
            'response_file': response_file_name,
            'response_original_name': response_original_name,
            'response_extension': response_ext,
            'created_at': datetime.now().isoformat()
        }
        save_data(data)
        flash("Respuesta enviada correctamente", "success")
        return redirect(url_for('student_content'))

    video_fields_html = """
            <div class=\"form-group\">
                <label>Enlace de video (YouTube, Drive u otro):</label>
                <input type=\"url\" name=\"video_url\" placeholder=\"https://...\">
            </div>
            <div class=\"form-group\">
                <label>Grabar/subir video de respuesta (MP4/MOV/WEBM/M4V):</label>
                <input type=\"file\" name=\"video_file\" accept=\"video/*\" capture=\"user\">
            </div>
    """
    written_fields_html = """
            <div class=\"form-group\">
                <label>Respuesta en texto:</label>
                <textarea name=\"response_text\" rows=\"5\" placeholder=\"Escribe tu respuesta...\"></textarea>
            </div>
            <div class=\"form-group\">
                <label>Subir archivo resuelto para calificación (PDF/Word):</label>
                <input type=\"file\" name=\"response_file\" accept=\".pdf,.doc,.docx\">
            </div>
    """
    if response_mode == 'video_only':
        form_mode_hint = "Solo se permite responder con video."
        response_fields_html = video_fields_html
    else:
        form_mode_hint = "Solo se permite respuesta escrita (texto o archivo)."
        response_fields_html = written_fields_html

    content = f"""
    <div class="card" style="max-width:700px; margin:0 auto;">
        <h1>📤 Responder publicación</h1>
        <p><strong>Título:</strong> {post.get('title')}</p>
        <p><strong>Materia:</strong> {post.get('subject', '-')}</p>
        <p><strong>Tipo de respuesta permitido:</strong> {response_mode_text}</p>
        <p><strong>Indicador:</strong> {form_mode_hint}</p>
        <p><strong>Intentos permitidos:</strong> {max_attempts} | <strong>Usados:</strong> {attempts_count} | <strong>Restantes:</strong> {max_attempts - attempts_count if (max_attempts - attempts_count) > 0 else 0}</p>
        {
            f"<p><strong>Último intento:</strong> {latest_submission.get('attempt_number', len(my_submissions))} | <strong>Último envío:</strong> {latest_submission.get('created_at', '-')}</p><p><strong>Última nota:</strong> {latest_submission.get('grade') if str(latest_submission.get('grade', '')).strip() != '' else 'Pendiente'} | <strong>Comentario:</strong> {latest_submission.get('teacher_feedback', 'Sin comentario')}</p>"
            if latest_submission else ""
        }
        <form method="POST" enctype="multipart/form-data">
            {response_fields_html}
            <button class="btn btn-primary" type="submit" {'disabled' if attempts_count >= max_attempts else ''}>Enviar respuesta</button>
            <a class="btn btn-secondary" href="/student/content">Cancelar</a>
        </form>
        {
            "<div style='margin-top:12px;'><h3>Historial de intentos</h3><ul>" + "".join([
                f"<li>Intento {sub.get('attempt_number', idx + 1)} - {sub.get('created_at', '-')} - Nota: {sub.get('grade') if str(sub.get('grade', '')).strip() != '' else 'Pendiente'}</li>"
                for idx, sub in enumerate(my_submissions)
            ]) + "</ul></div>"
            if my_submissions else ""
        }
    </div>
    """
    return render_template_string(BASE_HTML, title="Responder", content=content)


@app.route('/admin/overview')
def admin_overview():
    admin_guard = require_admin_access()
    if admin_guard:
        return admin_guard

    data = load_data()
    posts = [{'id': post_id, **post} for post_id, post in data.get('posts', {}).items()]
    posts.sort(key=lambda p: p.get('created_at', ''), reverse=True)
    submissions = data.get('submissions', {})

    labels = {'task': 'Tarea', 'report': 'Informe', 'practice': 'Práctica'}
    rows = ""
    for post in posts:
        response_count = len([s for s in submissions.values() if s.get('post_id') == post.get('id')])
        target_student_name = post.get('target_student_name', '-') if post.get('type') == 'report' else '-'
        report_actions = ""
        if post.get('type') == 'report':
            stored_file = post.get('report_file', '')
            file_url = f"/uploads/{stored_file}" if stored_file else ""
            ext = post.get('report_extension') or report_extension(post.get('report_original_name', ''))
            safe_title = str(post.get('title', 'Informe')).replace('"', '&quot;')
            report_actions = f"""
            <div style="display:flex; gap:6px; flex-wrap:wrap; margin-bottom:6px;">
                <button
                    type="button"
                    class="btn btn-primary open-report-modal"
                    style="padding:6px 10px;"
                    data-url="{file_url}"
                    data-ext="{ext}"
                    data-title="{safe_title}"
                >Ver informe</button>
                <a class="btn btn-secondary" style="padding:6px 10px;" href="{file_url}" target="_blank">Descargar</a>
            </div>
            """

        rows += f"""
        <tr>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{labels.get(post.get('type'), '-')}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{post.get('title', '-')}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{post.get('teacher_name', post.get('teacher', '-'))}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{post.get('subject', '-')}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{post.get('target_grade', '-')}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{target_student_name}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{post.get('due_date') or 'No aplica'}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">{response_count}</td>
            <td style="padding:8px; border-bottom:1px solid #ddd;">
                {report_actions}
                <a class="btn btn-secondary" style="padding:6px 10px;" href="/admin/posts/edit/{post.get('id')}">Editar</a>
                <a class="btn btn-danger" style="padding:6px 10px;" href="/admin/posts/delete/{post.get('id')}">Eliminar</a>
            </td>
        </tr>
        """

    content = f"""
    <div class="card">
        <h1>📊 Vista global del director</h1>
        <p>Todo lo que suben los docentes en cada materia.</p>
        <div class="admin-grid-form" style="margin-top:12px; margin-bottom:12px;">
            <div class="form-group">
                <label>Tipo:</label>
                <select id="overview-filter-type">
                    <option value="">Todos</option>
                    <option value="tarea">Tarea</option>
                    <option value="informe">Informe</option>
                    <option value="práctica">Práctica</option>
                </select>
            </div>
            <div class="form-group">
                <label>Docente:</label>
                <input id="overview-filter-teacher" placeholder="Nombre del docente">
            </div>
            <div class="form-group">
                <label>Grado:</label>
                <select id="overview-filter-grade">
                    <option value="">Todos</option>
                    {grade_options_html()}
                </select>
            </div>
            <div class="form-group">
                <label>Alumno:</label>
                <input id="overview-filter-student" placeholder="Nombre del alumno">
            </div>
            <div class="form-group" style="display:flex; align-items:flex-end;">
                <button type="button" id="overview-clear-filters" class="btn btn-secondary">Limpiar</button>
            </div>
        </div>
        <table id="overview-table" style="width:100%; border-collapse:collapse; margin-top:15px;">
            <thead>
                <tr>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Tipo</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Título</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Docente</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Materia</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Grado</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Alumno</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Fecha límite</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Respuestas</th>
                    <th style="text-align:left; border-bottom:1px solid #ddd; padding:8px;">Acciones</th>
                </tr>
            </thead>
            <tbody>
                {rows if rows else '<tr><td colspan="9" style="padding:10px;">No hay contenido publicado.</td></tr>'}
            </tbody>
        </table>
    </div>
    <div class="card" style="margin-top:20px;">
        <h2>🎥 Respuestas de estudiantes (incluye videos)</h2>
        <div class="tasks-grid">
            {
                ''.join([
                    f"<div class='task-card'><h3>{s.get('post_title', '-')}</h3><p><strong>Estudiante:</strong> {s.get('student_name', s.get('student'))}</p><p>{s.get('response_text', '')}</p>" +
                    (f"<p><a class='btn btn-secondary' style='padding:6px 10px;' href='{s.get('video_url')}' target='_blank'>Ver video</a></p>" if s.get('video_url') else '') +
                    "</div>"
                    for s in submissions.values()
                ]) or '<p>No hay respuestas enviadas todavía.</p>'
            }
        </div>
    </div>

    <div id="report-modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.65); z-index:9999; padding:24px;">
        <div style="background:#fff; width:min(1100px, 96vw); height:min(88vh, 900px); margin:0 auto; border-radius:12px; overflow:hidden; display:flex; flex-direction:column;">
            <div style="padding:12px 16px; border-bottom:1px solid #ddd; display:flex; justify-content:space-between; align-items:center;">
                <h2 id="report-modal-title" style="margin:0; font-size:20px; color:#111;">Vista previa de informe</h2>
                <button id="report-modal-close" class="btn btn-danger" type="button">Cerrar</button>
            </div>
            <div id="report-modal-body" style="flex:1; background:#f3f4f6; overflow:auto; padding:10px;">
                <iframe id="report-pdf-frame" title="Vista previa PDF" style="display:none; width:100%; height:100%; border:none; background:#fff;"></iframe>
                <div id="report-docx-container" style="display:none; background:#fff; min-height:100%; padding:16px;"></div>
                <div id="report-fallback" style="display:none; color:#111; padding:16px;"></div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/docx-preview@0.3.6/dist/docx-preview.min.js"></script>
    <script>
        (function() {{
            const typeFilter = document.getElementById('overview-filter-type');
            const teacherFilter = document.getElementById('overview-filter-teacher');
            const gradeFilter = document.getElementById('overview-filter-grade');
            const studentFilter = document.getElementById('overview-filter-student');
            const clearFilters = document.getElementById('overview-clear-filters');
            const table = document.getElementById('overview-table');

            function normalize(text) {{
                return (text || '').toLowerCase().trim();
            }}

            function applyOverviewFilters() {{
                if (!table) return;
                const rows = Array.from(table.querySelectorAll('tbody tr'));
                const typeValue = normalize(typeFilter.value);
                const teacherValue = normalize(teacherFilter.value);
                const gradeValue = normalize(gradeFilter.value);
                const studentValue = normalize(studentFilter.value);

                rows.forEach((row) => {{
                    const cells = row.querySelectorAll('td');
                    if (cells.length < 9) return;

                    const typeText = normalize(cells[0].textContent);
                    const teacherText = normalize(cells[2].textContent);
                    const gradeText = normalize(cells[4].textContent);
                    const studentText = normalize(cells[5].textContent);

                    const byType = !typeValue || typeText === typeValue;
                    const byTeacher = !teacherValue || teacherText.includes(teacherValue);
                    const byGrade = !gradeValue || gradeText.includes(gradeValue);
                    const byStudent = !studentValue || studentText.includes(studentValue);

                    row.style.display = (byType && byTeacher && byGrade && byStudent) ? '' : 'none';
                }});
            }}

            typeFilter.addEventListener('change', applyOverviewFilters);
            teacherFilter.addEventListener('input', applyOverviewFilters);
            gradeFilter.addEventListener('change', applyOverviewFilters);
            studentFilter.addEventListener('input', applyOverviewFilters);
            clearFilters.addEventListener('click', function() {{
                typeFilter.value = '';
                teacherFilter.value = '';
                gradeFilter.value = '';
                studentFilter.value = '';
                applyOverviewFilters();
            }});
            applyOverviewFilters();

            const modal = document.getElementById('report-modal');
            const closeButton = document.getElementById('report-modal-close');
            const titleElement = document.getElementById('report-modal-title');
            const pdfFrame = document.getElementById('report-pdf-frame');
            const docxContainer = document.getElementById('report-docx-container');
            const fallback = document.getElementById('report-fallback');
            const buttons = Array.from(document.querySelectorAll('.open-report-modal'));

            function resetPreview() {{
                pdfFrame.style.display = 'none';
                docxContainer.style.display = 'none';
                fallback.style.display = 'none';
                pdfFrame.src = '';
                docxContainer.innerHTML = '';
                fallback.innerHTML = '';
            }}

            function closeModal() {{
                resetPreview();
                modal.style.display = 'none';
            }}

            async function openModal(button) {{
                const url = button.dataset.url || '';
                const ext = (button.dataset.ext || '').toLowerCase();
                const title = button.dataset.title || 'Informe';
                titleElement.textContent = `Vista previa: ${{title}}`;

                resetPreview();
                modal.style.display = 'block';

                if (!url) {{
                    fallback.style.display = 'block';
                    fallback.innerHTML = '<p>No se encontró el archivo del informe.</p>';
                    return;
                }}

                if (ext === 'pdf') {{
                    pdfFrame.style.display = 'block';
                    pdfFrame.src = `${{url}}#view=FitH`;
                    return;
                }}

                if (ext === 'docx') {{
                    docxContainer.style.display = 'block';
                    try {{
                        const response = await fetch(url);
                        const blob = await response.blob();
                        const buffer = await blob.arrayBuffer();
                        await window.docx.renderAsync(buffer, docxContainer);
                    }} catch (error) {{
                        fallback.style.display = 'block';
                        fallback.innerHTML = '<p>No fue posible previsualizar el archivo DOCX. Usa el botón Descargar.</p>';
                        docxContainer.style.display = 'none';
                    }}
                    return;
                }}

                fallback.style.display = 'block';
                fallback.innerHTML = '<p>Vista previa no disponible para .doc. Usa el botón Descargar para verlo en Word.</p>';
            }}

            buttons.forEach((button) => {{
                button.addEventListener('click', function() {{
                    openModal(button);
                }});
            }});

            closeButton.addEventListener('click', closeModal);
            modal.addEventListener('click', function(event) {{
                if (event.target === modal) {{
                    closeModal();
                }}
            }});
            document.addEventListener('keydown', function(event) {{
                if (event.key === 'Escape' && modal.style.display === 'block') {{
                    closeModal();
                }}
            }});
        }})();
    </script>
    """
    return render_template_string(BASE_HTML, title="Vista global", content=content)


@app.route('/admin/posts/edit/<post_id>', methods=['GET', 'POST'])
def admin_edit_post(post_id):
    admin_guard = require_admin_access()
    if admin_guard:
        return admin_guard

    data = load_data()
    post = data.get('posts', {}).get(post_id)
    if not post:
        flash("Publicación no encontrada", "danger")
        return redirect(url_for('admin_overview'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        post_type = request.form.get('post_type', '').strip()
        due_date = request.form.get('due_date', '').strip()
        target_grade = request.form.get('target_grade', '').strip()

        if not title or not description or post_type not in ['task', 'report', 'practice']:
            flash("Completa los campos obligatorios", "danger")
            return redirect(url_for('admin_edit_post', post_id=post_id))
        if target_grade not in PREDEFINED_GRADES:
            flash("Selecciona un grado válido", "danger")
            return redirect(url_for('admin_edit_post', post_id=post_id))

        post['title'] = title
        post['description'] = description
        post['type'] = post_type
        post['due_date'] = due_date
        post['target_grade'] = target_grade
        data['posts'][post_id] = post
        save_data(data)
        flash("Publicación actualizada", "success")
        return redirect(url_for('admin_overview'))

    grade_select_options = grade_options_html(post.get('target_grade', ''))
    content = f"""
    <div class="card" style="max-width:700px; margin:0 auto;">
        <h1>✏️ Editar publicación</h1>
        <form method="POST">
            <div class="form-group"><label>Título:</label><input name="title" value="{post.get('title', '')}" required></div>
            <div class="form-group"><label>Descripción:</label><textarea name="description" rows="5" required>{post.get('description', '')}</textarea></div>
            <div class="form-group">
                <label>Tipo:</label>
                <select name="post_type" required>
                    <option value="task" {'selected' if post.get('type') == 'task' else ''}>Tarea</option>
                    <option value="report" {'selected' if post.get('type') == 'report' else ''}>Informe</option>
                    <option value="practice" {'selected' if post.get('type') == 'practice' else ''}>Práctica</option>
                </select>
            </div>
            <div class="form-group">
                <label>Grado al que va dirigido:</label>
                <select name="target_grade" required>
                    <option value="">Selecciona un grado</option>
                    {grade_select_options}
                </select>
            </div>
            <div class="form-group"><label>Fecha límite:</label><input type="datetime-local" name="due_date" value="{post.get('due_date', '')}"></div>
            <button class="btn btn-primary" type="submit">Guardar cambios</button>
            <a class="btn btn-secondary" href="/admin/overview">Volver</a>
        </form>
    </div>
    """
    return render_template_string(BASE_HTML, title="Editar publicación", content=content)


@app.route('/admin/posts/delete/<post_id>')
def admin_delete_post(post_id):
    admin_guard = require_admin_access()
    if admin_guard:
        return admin_guard

    data = load_data()
    if post_id not in data.get('posts', {}):
        flash("Publicación no encontrada", "danger")
        return redirect(url_for('admin_overview'))

    del data['posts'][post_id]

    submissions_to_delete = [sub_id for sub_id, sub in data.get('submissions', {}).items() if sub.get('post_id') == post_id]
    for sub_id in submissions_to_delete:
        del data['submissions'][sub_id]

    save_data(data)
    flash("Publicación y sus respuestas eliminadas", "success")
    return redirect(url_for('admin_overview'))


def init_data():
    data = load_data()
    users = data.get('users', {})

    if not users:
        users = {
            'director': {
                'email': 'director@escuela.com',
                'password': '123456',
                'role': 'admin',
                'nombre': 'Director General',
                'identificacion': 'ADM-001',
                'login_id': 'director',
                'must_change_password': False,
                'temporary_password': False
            },
            'profe.ingles@mep.go.cr': {
                'email': 'profe.ingles@mep.go.cr',
                'password': '123456',
                'role': 'teacher',
                'nombre': 'Dra. Patricia',
                'identificacion': 'DOC-1001',
                'materias': ['Inglés Y'],
                'materia': 'Inglés Y',
                'mep_email': 'profe.ingles@mep.go.cr',
                'login_id': 'profe.ingles@mep.go.cr',
                'must_change_password': True,
                'temporary_password': True
            },
            '123456789': {
                'email': 'estudiante@example.com',
                'password': '123456',
                'role': 'student',
                'nombre': 'Juan Pérez',
                'identificacion': '123456789',
                'sexo': 'Hombre',
                'grado': 'Quinto',
                'cedula': '123456789',
                'login_id': '123456789',
                'must_change_password': True,
                'temporary_password': True
            }
        }
    else:
        if 'director' not in users:
            users['director'] = {
                'email': 'director@escuela.com',
                'password': '123456',
                'role': 'admin',
                'nombre': 'Director General',
                'login_id': 'director',
                'must_change_password': False,
                'temporary_password': False
            }

        for user_key, user in users.items():
            role = user.get('role', 'student')
            if not user.get('login_id'):
                user['login_id'] = user_key
            if not user.get('identificacion'):
                user['identificacion'] = user.get('cedula', user_key)
            if role == 'teacher':
                teacher_subjects = sanitize_subjects(user.get('materias', []))
                if not teacher_subjects and user.get('materia') in PREDEFINED_SUBJECTS:
                    teacher_subjects = [user.get('materia')]
                if not teacher_subjects:
                    teacher_subjects = ['Inglés Y']
                user['materias'] = teacher_subjects
                user['materia'] = teacher_subjects[0]
            if role == 'student' and user.get('grado') not in PREDEFINED_GRADES:
                user['grado'] = 'Quinto'
            if role == 'student' and user.get('sexo') not in SEX_OPTIONS:
                user['sexo'] = 'Hombre'
            if 'must_change_password' not in user:
                user['must_change_password'] = role in ['teacher', 'student']
            if 'temporary_password' not in user:
                user['temporary_password'] = role in ['teacher', 'student']

    for post_key, post in data.get('posts', {}).items():
        if post.get('target_grade') not in PREDEFINED_GRADES:
            post['target_grade'] = 'Quinto'
        data['posts'][post_key] = post

    data['users'] = users
    save_data(data)


init_data()


if __name__ == '__main__':
    print("=" * 60)
    print("🎓 CAÑALES ARRIBA - Plataforma Educativa")
    print("=" * 60)
    print('\n✅ Aplicación iniciada en http://localhost:5000')
    print('\n⌨️  Presiona Ctrl+C para detener\n')
    app.run(debug=True, host='localhost', port=5000)
