import streamlit as st
import pandas as pd
import re
import spacy
from io import BytesIO
import base64

# Carrega modelo spaCy
nlp = spacy.load("pt_core_news_sm")

st.set_page_config(page_title="IRaText", layout="wide")

st.markdown("# IRaText: Geração de Corpus Textual para IRaMuTeQ")
st.markdown("### Analisador de Texto - Detecção de Siglas e Palavras Compostas")

# Funções de detecção
def detectar_siglas(texto):
    return list(set(re.findall(r'\b(?:[A-Z]{2,}|[A-Z]{2,}(?:-[A-Z]{2,})+)\b', texto)))

def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    entidades = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return list(set(entidades))

# Parte 1: Inserção manual de texto e análise
texto_input = st.text_area("📝 Cole ou digite um texto para análise", height=250)

if st.button("🔍 Analisar texto"):
    if texto_input.strip() == "":
        st.warning("Por favor, insira um texto antes de analisar.")
    else:
        palavras_compostas_detectadas = detectar_palavras_compostas(texto_input)
        siglas_detectadas = detectar_siglas(texto_input)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🧩 Palavras Compostas Detectadas")
            for item in sorted(palavras_compostas_detectadas):
                st.markdown(f"- {item}")

        with col2:
            st.markdown("### 🧾 Siglas Detectadas")
            for item in sorted(siglas_detectadas):
                st.markdown(f"- {item}")

        # Área de cópia para Excel
        palavras_compostas_str = "\n".join(sorted(palavras_compostas_detectadas))
        siglas_str = "\n".join(sorted(siglas_detectadas))

        st.markdown("### 📋 Copiar listas para colar no Excel")
        col1, col2 = st.columns(2)

        with col1:
            st.text_area("📌 Palavras Compostas (Ctrl+C e cole no Excel)", palavras_compostas_str, height=200)
        with col2:
            st.text_area("📌 Siglas (Ctrl+C e cole no Excel)", siglas_str, height=200)

# Parte 2: Upload e geração do corpus textual
st.markdown("---")
st.markdown("### 📂 Geração de Corpus a partir da Planilha")

col1, col2 = st.columns(2)

with col1:
    with open("modelo_planilha.xlsx", "rb") as f:
        st.download_button("📥 Baixar modelo de planilha", f, file_name="modelo_planilha.xlsx")

with col2:
    with open("textos_selecionados.xlsx", "rb") as f:
        st.download_button("📥 Baixar textos para análise", f, file_name="textos_selecionados.xlsx")

uploaded_file = st.file_uploader("📤 Envie a planilha preenchida (.xlsx)", type=["xlsx"])

if uploaded_file:
    planilha = pd.ExcelFile(uploaded_file)

    textos_df = pd.read_excel(planilha, sheet_name="textos_selecionados")
    palavras_compostas_df = pd.read_excel(planilha, sheet_name="dic_palavras_compostas")
    siglas_df = pd.read_excel(planilha, sheet_name="dic_siglas")

    def substituir_palavras_compostas(texto, palavras_compostas):
        for _, row in palavras_compostas.iterrows():
            original = row['original']
            substituto = row['substituto']
            texto = re.sub(rf'\b{re.escape(original)}\b', substituto, texto)
        return texto

    def substituir_siglas(texto, siglas):
        for _, row in siglas.iterrows():
            original = row['sigla']
            substituto = row['significado']
            texto = re.sub(rf'\b{re.escape(original)}\b', substituto, texto)
        return texto

    textos_df['texto_processado'] = textos_df['texto'].apply(
        lambda x: substituir_siglas(substituir_palavras_compostas(str(x), palavras_compostas_df), siglas_df)
    )

    corpus = "\n\n".join(
        f"**** *{row['id']}* {row['texto_processado']}" for _, row in textos_df.iterrows()
    )

    st.markdown("### 📄 Corpus Gerado")
    st.code(corpus, language="markdown")

    # Download do corpus
    buffer = BytesIO()
    buffer.write(corpus.encode("utf-8"))
    buffer.seek(0)

    st.download_button("⬇️ Baixar corpus gerado", buffer, file_name="corpus_para_IRaMuTeQ.txt", mime="text/plain")

    # Estatísticas simples
    st.markdown("### 📊 Estatísticas")
    st.write(f"**Total de textos:** {len(textos_df)}")
    st.write(f"**Total de palavras compostas substituídas:** {len(palavras_compostas_df)}")
    st.write(f"**Total de siglas substituídas:** {len(siglas_df)}")

# Rodapé
st.markdown("---")
st.markdown("👨‍🏫 **Sobre o autor**  \n"
            "**Autor:** José Wendel dos Santos  \n"
            "**Instituição:** Universidade Federal de Sergipe (UFS)  \n"
            "**Contato:** eng.wendel@gmail.com")
