from flask import Flask, render_template, redirect
import sqlite3
import numpy as np
from datetime import datetime
import random

app = Flask(__name__)

# ================= BANCO =================
conn = sqlite3.connect("seguranca.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    data TEXT,
    localizacao TEXT,
    status TEXT,
    horario INTEGER,
    local_flag INTEGER,
    tentativas INTEGER
)
""")
conn.commit()

# ================= INSERÇÃO =================
def inserir_log(usuario, data, localizacao, status, horario, local_flag, tentativas):
    cursor.execute("""
    INSERT INTO logs (usuario, data, localizacao, status, horario, local_flag, tentativas)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (usuario, data, localizacao, status, horario, local_flag, tentativas))
    conn.commit()

# ================= IA SIMPLES =================
def calcular_perfil_normal():
    cursor.execute("SELECT horario, local_flag, tentativas FROM logs WHERE status = 'OK'")
    dados = cursor.fetchall()

    if len(dados) == 0:
        return np.array([0, 0, 1])

    return np.mean(np.array(dados), axis=0)

pesos = np.array([0.4, 0.4, 0.2])

def classificar(entrada):
    perfil = calcular_perfil_normal()
    risco = np.dot(np.array(entrada), pesos)
    anomalia = np.linalg.norm(np.array(entrada) - perfil)

    score = (risco + anomalia) / 2

    if score < 0.7:
        return "OK"
    elif score < 1.4:
        return "Suspeito"
    else:
        return "Crítico"

# ================= SIMULAÇÃO =================
def simular():
    usuario = random.choice(["Ana", "Carlos", "Maria", "João"])
    local = random.choice(["SP", "RJ", "MG"])
    horario = random.choice([0, 1])
    local_flag = 0 if local == "SP" else 1
    tentativas = random.randint(1, 3)

    entrada = [horario, local_flag, tentativas]
    status = classificar(entrada)

    data = datetime.now().strftime("%d/%m %H:%M")
    inserir_log(usuario, data, local, status, horario, local_flag, tentativas)

# ================= ROTAS =================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    cursor.execute("SELECT usuario, data, localizacao, status FROM logs ORDER BY id DESC")
    logs = cursor.fetchall()

    total = len(logs)
    suspeitos = sum(1 for l in logs if l[3] == "Suspeito")
    criticos = sum(1 for l in logs if l[3] == "Crítico")

    return render_template(
        "dashboard.html",
        logs=logs,
        total=total,
        suspeitos=suspeitos,
        criticos=criticos
    )

@app.route("/simular")
def simular_rota():
    simular()
    return redirect("/dashboard")

# ===== NOVAS ROTAS (SEUS 2 TEMPLATES NOVOS) =====

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/contato")
def contato():
    return render_template("contato.html")

# ================= RUN =================
if __name__ == "__main__":
    app.run()