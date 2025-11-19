from flask import Flask, request, redirect, render_template, session, url_for, jsonify
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
    SELECT id, full_name, email, user, password, type
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
        if "user" not in session:
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# ROTA INICIAL
# ==========================================
@app.route("/")
def index():
    erro = request.args.get("erro")
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
        tipo = usuario[5].lower()

        session["user"] = username
        session["type"] = tipo

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

    # Corrigido aqui
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
    tipo = session.get("type")

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
        # Redirecionar para a tela de login com erro
        return redirect(url_for("index", erro=2))

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
    tipo = session.get("type")

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

@app.route("/add_user", methods=['POST'])
def add_user():
    data = request.get_json()

    full_name = data.get("name")
    email = data.get("email")
    username = data.get("user")
    password = data.get("password")
    type_user = data.get("type")

    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO user (full_name, email, user, password, type)
            VALUES (?, ?, ?, ?, ?)
        """, (full_name, email, username, password, type_user))

        conn.commit()
        conn.close()

        return jsonify({"success": True}), 200

    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "Usuário já existe!"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/delete_user/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    tipo = session.get("type")
    if tipo != "administrador":
        return jsonify({"success": False, "error": "Apenas administradores podem excluir usuários."}), 403

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/edit_user/<int:user_id>", methods=["PUT"])
@login_required
def edit_user(user_id):
    tipo = session.get("type")  # ou "tipo", dependendo do seu projeto

    # Apenas administradores podem editar usuários
    if tipo != "administrador":
        return jsonify({"success": False, "error": "Permissão negada."}), 403

    data = request.get_json()

    # Dados recebidos
    full_name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    user = data.get("user", "").strip()
    password = data.get("password", "").strip()
    user_type = data.get("type", "").strip()

    if not user or not user_type:
        return jsonify({"success": False, "error": "Usuário e tipo são obrigatórios."}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Atualiza com ou sem senha, conforme preenchimento
        if password:
            cursor.execute("""
                UPDATE user
                SET full_name = ?, email = ?, user = ?, password = ?, type = ?
                WHERE id = ?
            """, (full_name, email, user, password, user_type, user_id))
        else:
            cursor.execute("""
                UPDATE user
                SET full_name = ?, email = ?, user = ?, type = ?
                WHERE id = ?
            """, (full_name, email, user, user_type, user_id))

        conn.commit()
        conn.close()

        return jsonify({"success": True}), 200

    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "Nome de usuário já existe."}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# RODAR
# ==========================================
if __name__ == "__main__":
    app.run(debug=True)
