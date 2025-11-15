from flask import Flask, request, redirect, render_template, session, url_for
import sqlite3
from pathlib import Path
from functools import wraps

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


# ==========================================
# RODAR
# ==========================================
if __name__ == "__main__":
    app.run(debug=True)
