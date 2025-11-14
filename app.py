from flask import Flask, request, redirect, render_template
import sqlite3
from pathlib import Path

app = Flask(__name__)

# Caminho correto do banco
DB_PATH = Path(__file__).parent / "database" / "Users.db"

def verificar_login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE user = ? AND password = ?", (username, password))
    usuario = cursor.fetchone()
    conn.close()
    return usuario

@app.route("/", methods=["GET"])
def index():
    erro = request.args.get("erro") == "1"  # True se ?erro=1
    return render_template("index.html", erro=erro)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    usuario = verificar_login(username, password)

    if usuario:
        tipo = usuario[3].lower()  # user, password, tipo
        if tipo == "cliente":
            return "<h2>Bem-vindo, Cliente!</h2>"
        elif tipo == "consultor":
            return "<h2>Bem-vindo, Consultor!</h2>"
        elif tipo == "administrador":
            return "<h2>Bem-vindo, Administrador!</h2>"
        else:
            return "<h3>Tipo de usuário não autorizado.</h3>", 403

    else:
        return redirect("/?erro=1")  # Força a exibição da mensagem

@app.route("/esqueci-senha", methods=["GET"])
def lost_password():
    return render_template("lost_password.html")

@app.route("/redefinir_senha", methods=["POST"])
def redefinir_senha():
    popup = False

    if request.method == "POST":
        usuario = request.form.get("username")
        nova_senha = request.form.get("password")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE user SET password = ? WHERE user = ?", (nova_senha, usuario))
        conn.commit()
        conn.close()

        popup = True  # ativa o popup no HTML

    return render_template("lost_password.html", popup=popup)


if __name__ == "__main__":
    app.run(debug=True)
