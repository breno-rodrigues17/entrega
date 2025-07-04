import streamlit as st
from streamlit_drawable_canvas import st_canvas
from datetime import datetime
from PIL import Image
from fpdf import FPDF
import sqlite3
import io
import os
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="Sistema de Entrega", layout="centered")
st.title("📦 Expedição de Material")

# Criação da base de dados
def criar_banco():
    conn = sqlite3.connect('expedicao.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entregas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nota_fiscal TEXT,
            nome_cliente TEXT,
            rg_cpf_entregador TEXT,
            data TEXT,
            transportadora TEXT
        )
    ''')
    conn.commit()
    conn.close()

criar_banco()

# Inputs
nota_fiscal = st.text_input("Número da Nota Fiscal")
nome_cliente = st.text_input("Nome do Cliente")
rg_cpf = st.text_input("RG/CPF do Entregador")
data = st.date_input("Data", datetime.today())
transportadora = st.text_input("Transportadora")

# Canvas para assinatura
canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0)",
    stroke_width=2,
    stroke_color="#000000",
    background_color="#fff",
    height=150,
    width=400,
    drawing_mode="freedraw",
    key="canvas",
)

# Função para gerar PDF
def gerar_pdf_com_assinatura(dados, img_bytes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Comprovante de Entrega - Utech Tecnologia", ln=True, align='C')
    pdf.ln(10)

    for chave, valor in dados.items():
        pdf.cell(200, 10, f"{chave.replace('_', ' ').capitalize()}: {valor}", ln=True)
    pdf.ln(10)

    assinatura_path = "assinatura_temp.png"
    with open(assinatura_path, "wb") as f:
        f.write(img_bytes)

    pdf.image(assinatura_path, x=10, y=pdf.get_y(), w=100)
    os.remove(assinatura_path)

    pdf_path = f"comprovante_{dados['nota_fiscal']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(pdf_path)
    return pdf_path

# Funções de banco de dados
def salvar_no_banco(dados):
    conn = sqlite3.connect('expedicao.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO entregas (nota_fiscal, nome_cliente, rg_cpf_entregador, data, transportadora)
        VALUES (?, ?, ?, ?, ?)
    ''', (dados["nota_fiscal"], dados["nome_cliente"], dados["rg_cpf_entregador"], dados["data"], dados["transportadora"]))
    conn.commit()
    conn.close()

def listar_entregas():
    conn = sqlite3.connect('expedicao.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nota_fiscal, nome_cliente, rg_cpf_entregador, data, transportadora FROM entregas ORDER BY id DESC")
    entregas = cursor.fetchall()
    conn.close()
    return entregas

def excluir_entrega(id_entrega):
    conn = sqlite3.connect('expedicao.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entregas WHERE id = ?", (id_entrega,))
    conn.commit()
    conn.close()
    st.success(f"Entrega ID {id_entrega} excluída com sucesso.")
    st.experimental_rerun()

# Botão salvar
if st.button("💾 Salvar"):
    if not nota_fiscal or not nome_cliente or not transportadora or not rg_cpf:
        st.error("Preencha todos os campos obrigatórios.")
    elif canvas_result.image_data is None or canvas_result.image_data.sum() == 0:
        st.error("Por favor, faça a assinatura.")
    else:
        # Converte imagem da assinatura
        img = Image.froma
