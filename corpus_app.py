import streamlit as st
import pandas as pd
import re
import spacy
from io import StringIO

# Carrega modelo spaCy
nlp = spacy.load("pt_core_news_sm")

def detectar_siglas(texto):
    return list(set(re.findall(r'\b[A-Z]{2,}\b', texto)))

def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    compostas = set()
    for ent in doc.ents:
        if len(ent.text.split()) > 1:
            compostas.add(ent.text.strip())
    return list(compostas)

# Título fixo
st.title("Analisador de Texto - Detecção de Siglas e Palavras Compostas")

# Parte 1: Analisador manual
with st.expander("🔍 Analisar texto manualmente"):
    texto_input = st.text_area("Insira o texto a ser analisado:", height=300)
    if st.button("🔎 Analisar texto"):
        if texto_input:
            siglas = detectar_siglas(texto_input)
            palavras_compostas = detectar_palavras_compostas(texto_input)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Siglas detectadas**")
                for s in siglas:
                    st.markdown(f"- {s}")

            with col2:
                st.markdown("**Palavras compostas detectadas**")
                for pc in palavras_compostas:
                    st.markdown(f"- {pc}")

# Parte 2: Geração de corpus
st.markdown("---")
st.header("Gerador de corpus textual para IRaMuTeQ")

arquivo = st.file_uploader("Envie a planilha com os dados:", type=["csv", "xlsx"])

if arquivo is not None:
    try:
        if arquivo.name.endswith(".csv"):
            df = pd.read_csv(arquivo)
        else:
            df = pd.read_excel(arquivo)

        st.success("Arquivo carregado com sucesso!")

        st.subheader("Pré-visualização dos dados:")
        st.dataframe(df.head())

        col_texto = st.selectbox("Selecione a coluna com os textos:", df.columns)
        col_id = st.selectbox("Selecione a coluna com os identificadores (ID, nome, etc.):", df.columns)

        if st.button("📄 Gerar corpus textual"):
            corpus = ""
            for _, row in df.iterrows():
                corpus += f"**** *{row[col_id]}*\n{row[col_texto]}\n\n"

            st.download_button(
                label="📥 Baixar corpus.txt",
                data=corpus.encode("utf-8"),
                file_name="corpus.txt",
                mime="text/plain"
            )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

# Rodapé
st.markdown("---")
st.markdown("Desenvolvido por [Seu Nome].")
