# import streamlit as st
# import pandas as pd
# from datetime import date

# # ---------------- CONFIGURAÇÃO ----------------
# st.set_page_config(page_title="Faturamento Diário", layout="wide")

# # ---------------- ESTILO BONITO ----------------
# st.markdown("""
# <style>
# .main {
#     background-color: #f5f7fa;
# }
# .stButton>button {
#     background-color: #4CAF50;
#     color: white;
#     border-radius: 8px;
# }
# </style>
# """, unsafe_allow_html=True)

# st.title("📊 Faturamento do Dia")

# # ---------------- DADOS INICIAIS ----------------
# st.subheader("Dados Inicial")

# col1, col2, col3 = st.columns(3)

# with col1:
#     data = st.date_input("Data", date.today())

# with col2:
#     loja = st.selectbox("Loja", ["Loja1", "Loja2", "Loja3"])

# with col3:
#     nome = st.text_input("Nome")

# # ---------------- FATURAMENTO ----------------
# st.subheader("💰 Faturamento")

# c1, c2, c3, c4, c5 = st.columns(5)

# with c1:
#     dinheiro = st.number_input("Dinheiro", min_value=0.0)

# with c2:
#     infinity = st.number_input("Infinity", min_value=0.0)

# with c3:
#     stone = st.number_input("Stone", min_value=0.0)

# with c4:
#     vale = st.number_input("Vale", min_value=0.0)

# with c5:
#     pix = st.number_input("Pix Chave", min_value=0.0)

# # ---------------- DESPESAS ----------------
# st.subheader("🧾 Despesas")

# tipos = ["Água", "Energia", "Manutenção", "Outros"]

# despesas = []

# for i in range(1, 4):
#     col1, col2 = st.columns(2)

#     with col1:
#         tipo = st.selectbox(f"Despesa {i} Tipo", tipos, key=f"tipo{i}")

#     with col2:
#         valor = st.number_input(f"Valor {i}", min_value=0.0, key=f"valor{i}")

#     despesas.append(valor)

# # ---------------- TOTAL ----------------
# total_faturamento = dinheiro + infinity + stone + vale + pix
# total_despesa = sum(despesas)
# total_final = total_faturamento - total_despesa

# st.markdown("---")

# st.metric("Total Faturamento", f"R$ {total_faturamento:,.2f}")
# st.metric("Total Despesas", f"R$ {total_despesa:,.2f}")
# st.metric("Total Final", f"R$ {total_final:,.2f}")

# # ---------------- SALVAR ----------------
# if st.button("Salvar"):
#     dados = pd.DataFrame([{
#         "Data": data,
#         "Loja": loja,
#         "Nome": nome,
#         "Dinheiro": dinheiro,
#         "Infinity": infinity,
#         "Stone": stone,
#         "Vale": vale,
#         "Pix": pix,
#         "Despesa Total": total_despesa,
#         "Total Final": total_final
#     }])

#     try:
#         antigo = pd.read_csv("dados.csv")
#         novo = pd.concat([antigo, dados], ignore_index=True)
#     except:
#         novo = dados

#     novo.to_csv("dados.csv", index=False)

#     st.success("Dados salvos com sucesso!")

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# Configurações de Escopo para o Google
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Função para conectar (ajuste o nome do arquivo JSON se necessário)
def conectar_planilha():
    # No Streamlit Cloud, você usaria st.secrets, localmente use o arquivo JSON
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    client = gspread.authorize(creds)
    # Abre pelo ID da planilha que você enviou
    return client.open_by_key("1AkgkIQ7FXVXTuvUuGswnoqrU_ns-ceaBf2EQXkr0UFw").sheet1

# Interface Streamlit
st.title("📊 Lançamento de Faturamento")

with st.form("faturamento_form"):
    data = st.date_input("Data", value=datetime.now())
    loja = st.selectbox("Loja", ["Loja 1", "Loja 2", "Loja 3"])
    nome = st.text_input("Responsável")
    
    st.subheader("Valores")
    dinheiro = st.number_input("Dinheiro", min_value=0.0)
    pix = st.number_input("Pix", min_value=0.0)
    # ... adicione os outros campos conforme o código anterior
    
    total = dinheiro + pix # Simplificado para o exemplo
    
    btn_salvar = st.form_submit_button("Salvar na Planilha")

if btn_salvar:
    try:
        sheet = conectar_planilha()
        # Prepara a linha para inserir
        nova_linha = [data.strftime("%d/%m/%Y"), loja, nome, dinheiro, pix, total]
        sheet.append_row(nova_linha)
        st.success("✅ Dados salvos com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")