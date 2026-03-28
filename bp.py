import streamlit as st
import requests
from datetime import date

st.set_page_config(layout="wide")

# LOGIN
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Login")

    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if senha == "20253":
            st.session_state.logado = True
            st.rerun()

    st.stop()

# BOTÃO SAIR
if st.button("🚪 Sair"):
    st.session_state.logado = False
    st.rerun()

# FORM
st.title("📊 Faturamento Diário")

col1, col2, col3 = st.columns(3)

with col1:
    data = st.date_input("Data", value=date.today())

with col2:
    loja = st.selectbox("Loja", ["", "Boa Opção São Lourenço Lourenço", "Boa Opção Timbaúba", "Boa Opção Peixinho", "BM SL", "BM Porto", "BM Santa Rita", "BM Timabaúba", "BM Abreu", "BM Surubim", "BM Natal", "BM Campina"])

with col3:
    nome = st.text_input("Nome")

# FATURAMENTO
st.subheader("💰 Faturamento")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    dinheiro = st.number_input("Dinheiro")

with c2:
    infinity = st.number_input("Infinity")

with c3:
    stone = st.number_input("Stone")

with c4:
    vale = st.number_input("Vale")

with c5:
    pix = st.number_input("Pix")

# DESPESAS
st.subheader("🧾 Despesas")

tipos = [
    "Doação","Lanche","MT-Escritorio","MT-Limpeza","MT-Loja",
    "MT-Manutenção","Ornamentação","Pagamento","Publicidade",
    "Refeição","Segurança","Serviços","Veículo"
]

if "qtd_despesa" not in st.session_state:
    st.session_state.qtd_despesa = 1

if st.button("➕ Adicionar Despesa"):
    st.session_state.qtd_despesa += 1

lista_despesas = []
total_despesa = 0

for i in range(st.session_state.qtd_despesa):

    a, b, c = st.columns(3)

    with a:
        valor = st.number_input(f"Valor {i}", key=f"valor{i}")

    with b:
        tipo = st.selectbox(f"Tipo {i}", tipos, key=f"tipo{i}")

    with c:
        descricao = st.text_input(f"Descrição {i}", key=f"desc{i}")

    if valor > 0:
        lista_despesas.append({
            "valor": valor,
            "tipo": tipo,
            "descricao": descricao
        })

    total_despesa += valor

# TOTAL
total_faturamento = dinheiro + infinity + stone + vale + pix
total_final = total_faturamento - total_despesa

st.metric("Total Faturamento", f"R$ {total_faturamento:.2f}")
st.metric("Total Despesa do Dia", f"R$ {total_despesa:.2f}")
st.metric("Total Final", f"R$ {total_final:.2f}")

# SALVAR
if st.button("Salvar na Planilha"):

    url = "https://script.google.com/macros/s/AKfycbyYBDLTrTKwKlnUG05CwYnYg1EFvCYn6VLEm0KISFO-07wouOlzR8DJgIAK1FWAL1Dygw/exec"

    dados = {
        "data": str(data),
        "loja": loja,
        "nome": nome,
        "dinheiro": dinheiro,
        "infinity": infinity,
        "stone": stone,
        "vale": vale,
        "pix": pix,
        "total_despesa": total_despesa,
        "total_final": total_final,
        "lista_despesas": lista_despesas
    }

    resposta = requests.post(url, json=dados)

    st.success("Salvo com sucesso!")
