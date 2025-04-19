import streamlit as st
import pandas as pd
import re
import spacy
import base64
from io import StringIO

# Carrega o modelo do spaCy
nlp = spacy.load("pt_core_news_sm")

st.set_page_config(page_title="Analisador de Texto - IRaMuTeQ", layout="wide")
st.markdown("# Analisador de Texto - Detecção de Siglas e Palavras Compostas")

# Funções auxiliares
def detectar_siglas(texto):
    siglas = set(re.findall(r'\b[A-Z]{2,}\b', texto))
    return sorted(siglas)

def detectar_palavras_compostas_spacy(texto):
    doc = nlp(texto)
    palavras_compostas = set()
    for ent in doc.ents:
        if len(ent.text.split()) > 1:
            palavras_compostas.add(ent.text)
    return sorted(palavras_compostas)

def gerar_corpus(df, dicionario_pc, dicionario_siglas):
    corpus = []
    for index, row in df.iterrows():
        texto = row['texto']
        for _, pc_row in dicionario_pc.iterrows():
            original = pc_row['original']
            substituto = pc_row['substituto']
            texto = re.sub(rf'\b{re.escape(original)}\b', substituto, texto)
        for _, sigla_row in dicionario_siglas.iterrows():
            original = sigla_row['original']
            substituto = sigla_row['substituto']
            texto = re.sub(rf'\b{re.escape(original)}\b', substituto, texto)
        corpus.append(f"**** *{row['id']}*\n{texto}\n")
    return '\n'.join(corpus)

def botao_download_premium(texto, nome_arquivo, tipo_mime):
    b64 = base64.b64encode(texto.encode()).decode()
    href = f"""
    <a href="data:{tipo_mime};base64,{b64}" download="{nome_arquivo}" 
       style="
            background-color:#4CAF50;
            color:white;
            padding:10px 20px;
            text-align:center;
            text-decoration:none;
            display:inline-block;
            font-size:16px;
            border-radius:8px;
            margin-top: 10px;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
            transition: 0.3s;
        "
        title="Clique para baixar o corpus gerado">
        📀 Baixar Corpus Gerado
    </a>
    """
    st.markdown(href, unsafe_allow_html=True)

# Layout com abas
tab1, tab2 = st.tabs(["✍️ Análise de Texto", "📤 Gerar Corpus"])

with tab1:
    texto_usuario = st.text_area("Digite ou cole o texto para análise:", height=300)
    if st.button("🔍 Analisar texto"):
        with st.spinner("Analisando texto..."):
            siglas = detectar_siglas(texto_usuario)
            palavras_compostas = detectar_palavras_compostas_spacy(texto_usuario)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🧩 Palavras Compostas Detectadas:")
            for pc in palavras_compostas:
                st.write(f"- {pc}")
        with col2:
            st.markdown("### 🔠 Siglas Detectadas:")
            for sigla in siglas:
                st.write(f"- {sigla}")

with tab2:
    st.markdown("### 📂 Envie a planilha com as abas 'textos_selecionados', 'dic_palavras_compostas' e 'dic_siglas'")
    arquivo = st.file_uploader("Escolha o arquivo Excel", type=["xlsx"])

    if arquivo:
        planilha = pd.read_excel(arquivo, sheet_name=None)
        try:
            df_textos = planilha['textos_selecionados']
            df_pc = planilha['dic_palavras_compostas']
            df_siglas = planilha['dic_siglas']

            corpus = gerar_corpus(df_textos, df_pc, df_siglas)
            st.success("Corpus gerado com sucesso!")

            st.text_area("Corpus:", corpus, height=300)
            botao_download_premium(corpus, "corpus_para_IRaMuTeQ.txt", "text/plain")

        except KeyError as e:
            st.error(f"A planilha deve conter as abas: textos_selecionados, dic_palavras_compostas e dic_siglas. Abas ausentes: {e}")

# Rodapé com assinatura
st.markdown("""
---
<p style='text-align: center;'>Desenvolvido por Seu Nome - 2025</p>
""", unsafe_allow_html=True)
