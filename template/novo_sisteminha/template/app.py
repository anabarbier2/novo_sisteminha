from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "Ultra200@#"

# --- Banco de Dados ---
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

criar_tabela()

# --- 1. ROTA PRINCIPAL / CONTROLO DE ACESSO ---
@app.route("/")
def home():
    # Se já estiver logado, vai direto para o sistema Instituto
    if "usuario" in session:
        return redirect(url_for("instituto"))
    # Se não, vai para o login
    return redirect(url_for("login"))


# --- 2. ROTA DE LOGIN ---
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
            # LOGIN SUCESSO: Manda para a rota interna 'instituto'
            return redirect(url_for("instituto"))
        else:
            erro = "Utilizador ou senha incorretos"

    return render_template("login.html", erro=erro)


# --- 3. ROTA DE CADASTRO ---
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
        except sqlite3.IntegrityError:
            return render_template("cadastro.html", erro="Usuário já existe")
        except Exception as e:
            print(f"ERRO REAL NO BANCO DE DADOS: {e}")
            return render_template("cadastro.html", erro="Erro interno no servidor.")

    return render_template("cadastro.html")


# --- 4. ROTA DO PROGRAMA CENTRAL (INSTITUTO) ---
@app.route("/instituto")
def instituto():
    # Segurança: Impede que entrem nesta rota digitando o link direto sem logar
    if "usuario" not in session:
        return redirect(url_for("login"))
    
    # Aqui renderizas o HTML do teu programa central Instituto
    # Podes passar variáveis da sessão para dentro do HTML se quiseres
    return render_template("index.html", nome_usuario=session["usuario"])


# --- 5. ROTA DE LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()          # Apaga os dados da sessão (limpa o utilizador)
    session.modified = True  # Força o Flask a avisar o navegador que a sessão acabou
    return redirect(url_for("login"))

@app.route("/instituto")
def instituto2():
    # Se NÃO houver o "usuario" na sessão, barra a entrada e joga para o login
    if "usuario" not in session:
        return redirect(url_for("login"))
    
    # Se estiver logado, carrega a página de dados normal
    return render_template("index.html", nome_usuario=session["usuario"]) # (ou o nome do teu html que está na pasta templates)

if __name__ == "__main__":
    app.run(debug=True, port=5000)