from flask import Flask, request, redirect, render_template, session, url_for
import sqlite3
from pathlib import Path
from functools import wraps
import math


app = Flask(__name__)

# Configuração básica de segurança de sessão
app.secret_key = "SEGREDO_SUPER_SEGURO"
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Caminho correto do banco
DB_PATH = Path(__file__).parent / "database" / "Users.db"


# ==========================================
# VERIFICAR LOGIN NO BANCO
# ==========================================
def verificar_login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE user = ? AND password = ?", (username, password))
    usuario = cursor.fetchone()
    conn.close()
    return usuario

def listar_usuarios(search=None, page=1, per_page=10):
    """
    Retorna:
      - lista de usuários (sqlite3.Row)
      - total de registros
      - total de páginas
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    where = ""
    params = []

    if search:
        where = "WHERE user LIKE ?"
        params.append(f"%{search}%")

    cursor.execute(f"SELECT COUNT(*) FROM user {where}", params)
    total = cursor.fetchone()[0]

    total_pages = max(1, math.ceil(total / per_page)) if total > 0 else 1
    offset = (page - 1) * per_page

    cursor.execute(
        f"""
        SELECT id, user, password, type
        FROM user
        {where}
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        """,
        params + [per_page, offset]
    )
    usuarios = cursor.fetchall()
    conn.close()

    return usuarios, total, total_pages


# ==========================================
# DECORADOR PARA PROTEGER ROTAS
# ==========================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# ROTA INICIAL
# ==========================================
@app.route("/", methods=["GET"])
def index():
    # se o usuário já está logado, não mostra o login
    if "username" in session:
        return redirect(url_for("home"))

    erro = request.args.get("erro") == "1"
    return render_template("index.html", erro=erro)



# ==========================================
# LOGIN
# ==========================================
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    usuario = verificar_login(username, password)

    if usuario:
        tipo = usuario[3].lower()

        session["username"] = username
        session["tipo"] = tipo

        return redirect(url_for("home"))
    else:
        return redirect("/?erro=1")


# ==========================================
# LOGOUT
# ==========================================
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))


# ==========================================
# SENHA
# ==========================================
@app.route("/esqueci-senha", methods=["GET"])
def lost_password():
    return render_template("lost_password.html")


@app.route("/redefinir_senha", methods=["POST"])
def redefinir_senha():
    popup = False

    usuario = request.form.get("username")
    nova_senha = request.form.get("password")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE user SET password = ? WHERE user = ?", (nova_senha, usuario))
    conn.commit()
    conn.close()

    popup = True

    return render_template("lost_password.html", popup=popup)


# ==========================================
# HOME (PROTEGIDA)
# ==========================================
@app.route("/home")
@login_required
def home():
    tipo = session.get("tipo")

    if tipo == "consultor":
        menu = {
            "cotacoes": True,
            "relatorios": True,
            "usuarios": False
        }

    elif tipo == "administrador":
        menu = {
            "cotacoes": True,
            "relatorios": True,
            "usuarios": True
        }

    else:
        return "<h3>Clientes não têm acesso ao dashboard.</h3>"

    return render_template("home.html", menu=menu, tipo=tipo)


# ==========================================
# IMPEDIR CACHE (HARD)
# ==========================================
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/perfil")
@login_required
def perfil():
    return render_template("profile.html", username=session.get("username"), tipo=session.get("tipo"))


@app.route("/usuarios")
@login_required
def usuarios():
    tipo = session.get("tipo")

    # Somente administrador acessa a gestão de usuários
    if tipo != "administrador":
        return "<h3>Somente administradores podem acessar a gestão de usuários.</h3>", 403
    
    menu = {
        "cotacoes": True,
        "relatorios": True,
        "usuarios": True
    }

    search = request.args.get("q", "").strip()
    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    per_page = 10

    usuarios, total, total_pages = listar_usuarios(
        search if search else None,
        page=page,
        per_page=per_page
    )

    if total > 0:
        display_start = (page - 1) * per_page + 1
        display_end = min(page * per_page, total)
    else:
        display_start = 0
        display_end = 0

    return render_template(
        "users.html",
        menu=menu,
        tipo=tipo,
        usuarios=usuarios,
        page=page,
        total_pages=total_pages,
        total=total,
        display_start=display_start,
        display_end=display_end,
        search=search
    )


# ==========================================
# RODAR
# ==========================================
if __name__ == "__main__":
    app.run(debug=True)
