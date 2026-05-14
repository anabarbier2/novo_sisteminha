from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "segredo_super_secreto"

# --- Configuração do Banco de Dados ---
def get_db():
    conn = sqlite3.connect("banco.db")
    return conn

def criar_tabela():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Executa a criação da tabela ao iniciar
criar_tabela()

@app.route("/")
def home():
    # Verifica se existe sessão ativa
    if "usuario" in session:
        return redirect("https://sisteminha.gcss.com.br/")
    return redirect(url_for("login"))

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if not usuario or not senha:
            return render_template("cadastro.html", erro="Campos vazios")

        senha_hash = generate_password_hash(senha)

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha_hash))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except Exception:
            return render_template("cadastro.html", erro="Usuário já existe")

    return render_template("cadastro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = request.form.get("usuario") 
        senha = request.form.get("senha")    

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT senha FROM usuarios WHERE usuario = ?", (usuario,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado and check_password_hash(resultado[0], senha):
            session["usuario"] = usuario
            # Redireciona
            return redirect("https://sisteminha.gcss.com.br/")
        else:
            erro = "Login inválido"

    return render_template("login.html", erro=erro)

@app.route("/logout")
def logout():
    session.clear() 
    return redirect(url_for("login"))
if __name__ == "__main__":
    app.run(debug=True, port=5000)