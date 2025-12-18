from flask import Flask, request, redirect, render_template, session, url_for, jsonify
import sqlite3
from pathlib import Path
from functools import wraps
import math
import openai
from flask_mail import Mail, Message
import os
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from backend.templates_corporate import corporate_quote_template
import uuid
from backend.templates_corporate import generate_aereo_section
import traceback
import re



def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)

# Configurações de e-mail (direto no código)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'isabellabeatriz1603@gmail.com'  # Seu e-mail
app.config['MAIL_PASSWORD'] = 'tktytdozzrqshyzq'                      # Sua senha
app.config['MAIL_DEFAULT_SENDER'] = 'isabellabeatriz1603@gmail.com'


mail = Mail(app)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuração básica de segurança de sessão
app.secret_key = "SEGREDO_SUPER_SEGURO"
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Caminho correto do banco
DB_PATH = Path(__file__).parent / "database" / "Users.db"

UPLOAD_FOLDER = "static/profile_pics"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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
        session["profile_pic"] = (
            usuario[6] if usuario[6] else "profile_pics/icon_user.png"
        )

        session.modified = True

        return redirect(url_for("home"))

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
        return redirect(url_for("index", erro=2))

    # GARANTIR QUE A VARIÁVEL SEMPRE EXISTE
    profile_pic = session.get("profile_pic")
    if not profile_pic:
        profile_pic = "profile_pics/icon_user.png"
        session["profile_pic"] = profile_pic  # salva na sessão

    print("HOME - PROFILE PIC FINAL:", profile_pic)

    return render_template(
        "home.html",
        menu=menu,
        tipo=tipo,
        profile_pic=profile_pic   # <-- ESSA É A VARIÁVEL QUE O HTML USA
    )




# ==========================================
# IMPEDIR CACHE (HARD)
# ==========================================
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

def get_menu_by_type(tipo):
    # tipo pode ser: "administrador" ou "consultor"

    if tipo == "administrador":
        return {
            "cotacoes": True,
            "relatorios": True,
            "usuarios": True
        }

    else:  # consultor
        return {
            "cotacoes": True,
            "relatorios": True,
            "usuarios": False
        }


@app.route("/perfil")
@login_required
def perfil():
    username = session.get("user")   # valor armazenado no login
    tipo = session.get("type")

    # Buscar informações reais do usuário no banco
    conn = sqlite3.connect("database/Users.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT full_name, email, user, type, profile_pic
        FROM user
        WHERE user = ?
    """, (username,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return "Usuário não encontrado", 404

    # Se não tiver foto salva, usamos um avatar padrão
    profile_pic = result[4] if result[4] else "profile_pics/icon_user.png"
    session["profile_pic"] = profile_pic



    # Montar objeto user para enviar ao HTML
    user = {
        "full_name": result[0],
        "email": result[1],
        "username": result[2],
        "type": result[3],
        "profile_pic": profile_pic
    }

    print("PROFILE PIC NA SESSAO:", session.get("profile_pic"))  # DEBUG
    return render_template(
        "profile.html",
        user=user,
        menu=get_menu_by_type(tipo)
    )



@app.route("/usuarios")
@login_required
def usuarios():
    tipo = session.get("type")

    # Somente administrador acessa a gestão de usuários
    if tipo != "administrador":
        return "<h3>Somente administradores podem acessar a gestão de usuários.</h3>", 403
    
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
        
        menu=get_menu_by_type(tipo),
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

@app.route("/upload_profile_pic", methods=["POST"])
@login_required
def upload_profile_pic():

    if "profile_pic" not in request.files:
        return {"success": False, "message": "Nenhum arquivo enviado"}, 400

    file = request.files["profile_pic"]

    if file.filename == "":
        return {"success": False, "message": "Arquivo inválido"}, 400

    if file and allowed_file(file.filename):

        username = session.get("user")

        # ---------------------------
        # 1. Buscar foto antiga no banco
        # ---------------------------
        conn = sqlite3.connect("database/Users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT profile_pic FROM user WHERE user = ?", (username,))
        old_pic = cursor.fetchone()
        old_pic = old_pic[0] if old_pic else None

        # Só apagamos se:
        # - existir
        # - não for a imagem padrão
        if old_pic and old_pic != "profile_pics/icon_user.png":
            old_file_path = os.path.join("static", old_pic)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

        # ---------------------------
        # 2. Criar nome novo limpinho
        # ---------------------------
        ext = file.filename.rsplit(".", 1)[-1].lower()
        filename = secure_filename(f"{username}.{ext}")

        # Caminho físico
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        # Caminho que salva no banco
        relative_path = f"profile_pics/{filename}"

        # ---------------------------
        # 3. Atualizar no banco
        # ---------------------------
        cursor.execute("""
            UPDATE user SET profile_pic = ? WHERE user = ?
        """, (relative_path, username))
        conn.commit()
        conn.close()

        # ---------------------------
        # 4. Atualizar na sessão
        # ---------------------------
        session["profile_pic"] = relative_path

        return {"success": True, "filepath": relative_path}

    return {"success": False, "message": "Extensão não permitida"}, 400

@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    username_old = session.get("user")

    # valores vindos do formulário
    new_username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    full_name = request.form.get("full_name", "").strip()
    user_type = request.form.get("type", "").strip()

    # Conexão com DB
    conn = sqlite3.connect("database/Users.db")
    cursor = conn.cursor()

    # Buscar dados atuais
    cursor.execute("SELECT user, email, full_name, type FROM user WHERE user = ?", (username_old,))
    current = cursor.fetchone()

    if not current:
        conn.close()
        return {"success": False, "message": "Usuário não encontrado."}

    # valores atuais
    user_curr, email_curr, name_curr, type_curr = current

    # ⬇⬇ Se não houver alteração, manter o original
    new_username = new_username or user_curr
    email = email or email_curr
    full_name = full_name or name_curr
    user_type = user_type or type_curr

    try:
        cursor.execute("""
            UPDATE user
            SET user = ?, email = ?, full_name = ?, type = ?
            WHERE user = ?
        """, (new_username, email, full_name, user_type, username_old))

        conn.commit()
    except Exception as e:
        conn.close()
        return {"success": False, "message": str(e)}

    conn.close()

    # atualizar sessão somente se alterar username ou tipo
    session["user"] = new_username
    session["type"] = user_type

    return {"success": True}

@app.route("/update_password", methods=["POST"])
@login_required
def update_password():
    data = request.get_json()
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    username = session.get("user")

    conn = sqlite3.connect("database/Users.db")
    cursor = conn.cursor()

    # Buscar senha atual
    cursor.execute("SELECT password FROM user WHERE user = ?", (username,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return {"success": False, "message": "Usuário não encontrado"}

    stored_password = result[0]

    # Verificar senha atual
    if stored_password != current_password:
        conn.close()
        return {"success": False, "message": "Senha atual incorreta"}

    # Atualizar senha
    cursor.execute(
        "UPDATE user SET password = ? WHERE user = ?",
        (new_password, username)
    )
    conn.commit()
    conn.close()

    return {"success": True}


@app.route("/relatorios")
def relatorios():
    # Garantir que a imagem de perfil esteja definida na sessão
    tipo = session.get("type")
    profile_pic = session.get("profile_pic")
    if not profile_pic:
        profile_pic = "profile_pics/icon_user.png"
        session["profile_pic"] = profile_pic

    print("RELATÓRIOS - PROFILE PIC FINAL:", profile_pic)
 

    return render_template(
        "powerbi.html",
        menu=get_menu_by_type(tipo),
        profile_pic=profile_pic
    )

@app.route('/cotacoes/corporativo')
def cotacoes_corporativo():
    tipo = session.get("type")
    # Exemplo: controle de sessão
    if 'user' not in session:
        return redirect(url_for('index'))

    # Garantir que a imagem de perfil esteja definida na sessão
    profile_pic = session.get("profile_pic")
    if not profile_pic:
        profile_pic = "profile_pics/icon_user.png"
        session["profile_pic"] = profile_pic

    return render_template('corporate.html', session=session, profile_pic=profile_pic, menu=get_menu_by_type(tipo))


@app.route('/cotacoes/lazer')
def cotacoes_lazer():
    tipo = session.get("type")
    # Verificação de login
    if 'user' not in session:
        return redirect(url_for('login'))
 
    # Garantir que a imagem de perfil esteja definida na sessão
    profile_pic = session.get("profile_pic")
    if not profile_pic:
        profile_pic = "profile_pics/icon_user.png"
        session["profile_pic"] = profile_pic

    return render_template(
        'leisure.html',
        menu=get_menu_by_type(tipo),
        profile_pic=profile_pic
    )


@app.route("/send-email", methods=["POST"])
def send_email():
    nome_cliente = request.form.get("nome_cliente")
    email_cliente = request.form.get("email_cliente")
    cotacoes = request.form.get("cotacoesSelecionadas")
    tipo_viagem = request.form.get("tipo_viagem")
    empresa = request.form.get("empresa")
    texto = request.form.get("texto_cotacao")

    nome_consultor = session.get("user", "Consultor R3")

    servicos = [s.strip().lower() for s in cotacoes.split(",")] if cotacoes else []

    aereo_texto_formatado = ""

    if ("aéreo" in servicos or "aereo" in servicos) and texto:
        texto_normalizado = "\n".join(
            [ln.strip() for ln in texto.splitlines() if ln.strip()]
        )

        texto_normalizado = re.sub(
            r"(Econ(?:ô)?mic)(\d{2,4})", r"\1\n\2",
            texto_normalizado, flags=re.IGNORECASE
        )
        texto_normalizado = re.sub(
            r"(OW\s*E)(\d{2,4})", r"\1\n\2",
            texto_normalizado, flags=re.IGNORECASE
        )

        aereo_texto_formatado = generate_aereo_section(
            raw_data=texto_normalizado,
            tipo_viagem=tipo_viagem
        )

    corpo_email = corporate_quote_template(
        client_name=nome_cliente,
        consultant_name=nome_consultor,
        raw_data=texto,
        selected_services=cotacoes,
        aereo_texto_formatado=aereo_texto_formatado
    )

    msg = Message(
        subject=f"Cotação Corporativa | {empresa}",
        recipients=[email_cliente],
        html=corpo_email
    )

    try:
        mail.send(msg)
        return {
            "status": "success",
            "message": "E-mail enviado com sucesso."
        }

    except Exception:
        traceback.print_exc()
        return {
            "status": "error",
            "message": "Erro ao enviar o e-mail."
        }, 500




@app.route("/preview-email", methods=["POST"])
def preview_email():
    texto = request.form.get("texto_cotacao")
    cotacoes = request.form.get("cotacoesSelecionadas")
    tipo_viagem = request.form.get("tipo_viagem")

    servicos = [s.strip().lower() for s in cotacoes.split(",")] if cotacoes else []

    aereo_texto_formatado = ""

    if ("aéreo" in servicos or "aereo" in servicos) and texto:
        texto_normalizado = "\n".join(
            [ln.strip() for ln in texto.splitlines() if ln.strip()]
        )

        aereo_texto_formatado = generate_aereo_section(
            raw_data=texto_normalizado,
            tipo_viagem=tipo_viagem
        )

    # 🔥 Preview retorna APENAS TEXTO PURO
    return aereo_texto_formatado or "Nenhum conteúdo para pré-visualização."



# ==========================================
# RODAR
# ==========================================
if __name__ == "__main__":
    app.run(debug=True)
