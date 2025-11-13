from flask import Flask, request, redirect, render_template_string
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
    # Lê o index.html do frontend
    with open("../frontend/index.html", "r", encoding="utf-8") as f:
        return render_template_string(f.read())

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    usuario = verificar_login(username, password)

    if usuario:
        tipo = usuario[3].lower()  # id, user, password, tipo
        if tipo == "cliente":
            return "<h2>Bem-vindo, Cliente!</h2>"
        elif tipo == "consultor":
            return "<h2>Bem-vindo, Consultor!</h2>"
        elif tipo == "administrador":
            return "<h2>Bem-vindo, Administrador!</h2>"
        else:
            return "<h3>Tipo de usuário não autorizado.</h3>", 403
    else:
        return "<h3>Usuário ou senha inválidos.</h3>", 401

if __name__ == "__main__":
    app.run(debug=True)
