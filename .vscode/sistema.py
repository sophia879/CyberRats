import tkinter as tk
from tkinter import ttk
import sqlite3
import numpy as np
from datetime import datetime
import random

# ================= BANCO DE DADOS =================
conn = sqlite3.connect("seguranca.db")
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

# ================= DADOS INICIAIS =================
def inserir_log(usuario, data, localizacao, status, horario, local_flag, tentativas):
    cursor.execute("""
    INSERT INTO logs (usuario, data, localizacao, status, horario, local_flag, tentativas)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (usuario, data, localizacao, status, horario, local_flag, tentativas))
    conn.commit()

def inserir_dados_iniciais():
    cursor.execute("SELECT COUNT(*) FROM logs")
    if cursor.fetchone()[0] > 0:
        return  # evita duplicar dados

    exemplos = [
        ("Ana", "25/04 09:00", "SP", "OK", 0, 0, 1),
        ("Ana", "25/04 10:00", "SP", "OK", 0, 0, 1),
        ("Maria", "25/04 11:00", "SP", "OK", 0, 0, 1),
        ("Carlos", "25/04 23:00", "RJ", "Suspeito", 1, 1, 2),
        ("João", "25/04 02:00", "MG", "Crítico", 1, 1, 3),
    ]

    for e in exemplos:
        inserir_log(*e)

inserir_dados_iniciais()

# ================= APRENDIZADO =================
def calcular_perfil_normal():
    cursor.execute("""
    SELECT horario, local_flag, tentativas 
    FROM logs 
    WHERE status = 'OK'
    """)

    dados = cursor.fetchall()

    if len(dados) == 0:
        return np.array([0, 0, 1])

    matriz = np.array(dados)
    media = np.mean(matriz, axis=0)

    return media

# ================= LÓGICA DE RISCO =================
pesos = np.array([0.4, 0.4, 0.2])

def calcular_risco(entrada):
    entrada = np.array(entrada)
    return np.dot(entrada, pesos)

def classificar_inteligente(entrada):
    perfil = calcular_perfil_normal()

    risco_base = calcular_risco(entrada)
    anomalia = np.linalg.norm(np.array(entrada) - perfil)

    score_final = (risco_base * 0.5) + (anomalia * 0.5)

    if score_final < 0.7:
        return "OK"
    elif score_final < 1.4:
        return "Suspeito"
    else:
        return "Crítico"

# ================= FUNÇÕES UI =================
def carregar_logs():
    for row in tabela.get_children():
        tabela.delete(row)

    cursor.execute("SELECT usuario, data, localizacao, status FROM logs ORDER BY id DESC")
    for linha in cursor.fetchall():
        tabela.insert("", tk.END, values=linha)

def atualizar_cards():
    cursor.execute("SELECT COUNT(*) FROM logs")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM logs WHERE status='Suspeito'")
    suspeitos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM logs WHERE status='Crítico'")
    criticos = cursor.fetchone()[0]

    card1.config(text=f"Acessos\n{total}")
    card2.config(text=f"Suspeitos\n{suspeitos}")
    card3.config(text=f"Críticos\n{criticos}")

# ================= SIMULAÇÃO =================
usuarios = ["Ana", "Carlos", "Maria", "João"]
locais = ["SP", "RJ", "MG", "BA"]

def simular_acesso():
    usuario = random.choice(usuarios)
    local = random.choice(locais)

    horario = random.choice([0, 1])
    local_flag = 0 if local == "SP" else 1
    tentativas = random.randint(1, 3)

    entrada = [horario, local_flag, tentativas]

    status = classificar_inteligente(entrada)

    data = datetime.now().strftime("%d/%m %H:%M")

    inserir_log(usuario, data, local, status, horario, local_flag, tentativas)
    carregar_logs()
    atualizar_cards()

# ================= INTERFACE =================
root = tk.Tk()
root.title("Painel de Segurança - Clínica Estética")
root.geometry("900x600")
root.configure(bg="#f5f5f5")

# MENU
menu_frame = tk.Frame(root, bg="#2c2c2c", width=200)
menu_frame.pack(side="left", fill="y")

def criar_botao_menu(texto):
    return tk.Button(menu_frame, text=texto, fg="white", bg="#2c2c2c",
                     activebackground="#444", bd=0, font=("Arial", 12),
                     anchor="w", padx=20)

for item in ["Dashboard", "Logs", "Alertas", "Usuários"]:
    criar_botao_menu(item).pack(fill="x", pady=10)

# MAIN
main_frame = tk.Frame(root, bg="#f5f5f5")
main_frame.pack(side="right", expand=True, fill="both")

titulo = tk.Label(main_frame, text="Dashboard de Segurança",
                  font=("Arial", 18, "bold"), bg="#f5f5f5")
titulo.pack(pady=20)

# CARDS
cards_frame = tk.Frame(main_frame, bg="#f5f5f5")
cards_frame.pack(pady=10)

card1 = tk.Label(cards_frame, width=20, height=5, bg="#4CAF50", fg="white")
card2 = tk.Label(cards_frame, width=20, height=5, bg="#FF9800", fg="white")
card3 = tk.Label(cards_frame, width=20, height=5, bg="#F44336", fg="white")

card1.pack(side="left", padx=10)
card2.pack(side="left", padx=10)
card3.pack(side="left", padx=10)

# TABELA
tabela_frame = tk.Frame(main_frame)
tabela_frame.pack(pady=20, fill="both", expand=True)

colunas = ("Usuário", "Data", "Local", "Status")
tabela = ttk.Treeview(tabela_frame, columns=colunas, show="headings")

for col in colunas:
    tabela.heading(col, text=col)
    tabela.column(col, anchor="center")

tabela.pack(fill="both", expand=True)

# BOTÃO
btn_simular = tk.Button(main_frame, text="Simular Acesso",
                        command=simular_acesso, bg="#2196F3", fg="white")
btn_simular.pack(pady=10)

# INICIALIZAR
carregar_logs()
atualizar_cards()

root.mainloop()