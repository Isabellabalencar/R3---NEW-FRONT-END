# backend/create_db.py
import sqlite3
from pathlib import Path

# Caminho do banco (ficará em backend/Users.db)
DB_PATH = Path(__file__).parent / "Users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Cria tabela com todos os campos usados no modal
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT,
            user TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            type TEXT NOT NULL
        );
    """)

    # # Verifica se já tem dados
    # cursor.execute("SELECT COUNT(*) FROM user;")
    # qtd = cursor.fetchone()[0]

    # if qtd == 0:
    #     usuarios_teste = [
    #         ("Cliente Teste",   "cliente@teste.com",   "cliente_teste",   "1234", "cliente"),
    #         ("Consultor Teste", "consultor@teste.com", "consultor_teste", "1234", "consultor"),
    #         ("Admin Teste",     "admin@teste.com",     "admin_teste",     "1234", "administrador"),
    #     ]

    #     cursor.executemany(
    #         "INSERT INTO user (full_name, email, user, password, type) VALUES (?, ?, ?, ?, ?);",
    #         usuarios_teste
    #     )

    #     print("Usuários de teste inseridos.")
    # else:
    #     print("Tabela 'user' já possui dados, nada inserido.")

    # conn.commit()
    # conn.close()
    # print(f"✅ Banco criado/atualizado em: {DB_PATH}")

if __name__ == "__main__":
    init_db()
