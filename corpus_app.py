import streamlit as st
import pandas as pd
import re
import io
import spacy
import base64
from io import BytesIO
from collections import Counter

# Carrega modelo spaCy
nlp = spacy.load("pt_core_news_sm")

st.set_page_config(layout="wide")

st.markdown("""
<style>
.big-font {
    font-size:20px !important;
    font-weight: bold;
}
.box {
    background-color: #f0f2f6;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.sigla {
    color: #0e76a8;
    font-weight: bold;
}
.composta {
    color: #ff4b4b;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🔍 Analisador de Texto - Detecção de Siglas e Palavras Compostas")

st.markdown("Digite ou cole um texto abaixo. Clique em **Analisar texto** para detectar siglas e palavras compostas.")

texto_input = st.text_area("Texto para análise", height=200)

col1, col2, col3 = st.columns([1,1,2])

with col1:
    analisar = st.button("🔎 Analisar texto")
with col2:
    limpar = st.button("🧹 Limpar texto")

if limpar:
    texto_input = ""
    st.experimental_rerun()

if analisar and texto_input:
    doc = nlp(texto_input)

    siglas = sorted(set(re.findall(r'\b[A-Z]{2,}\b', texto_input)))
    palavras_compostas = sorted(set([ent.text for ent in doc.ents if len(ent.text.split()) > 1]))
    compostas_com_tipo = [(ent.text, ent.label_) for ent in doc.ents if len(ent.text.split()) > 1]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📌 Siglas Detectadas")
        if siglas:
            for sigla in siglas:
                st.markdown(f"<div class='box sigla'>- {sigla}</div>", unsafe_allow_html=True)
            siglas_csv = "\n".join(siglas)
            st.download_button("⬇️ Baixar siglas", siglas_csv, file_name="siglas.txt")
        else:
            st.info("Nenhuma sigla detectada.")

    with col2:
        st.subheader("🧩 Palavras Compostas Detectadas")
        if palavras_compostas:
            for palavra, tipo in compostas_com_tipo:
                st.markdown(f"<div class='box composta'>- {palavra} ({tipo})</div>", unsafe_allow_html=True)
            compostas_csv = "\n".join(palavras_compostas)
            st.download_button("⬇️ Baixar compostas", compostas_csv, file_name="palavras_compostas.txt")
        else:
            st.info("Nenhuma palavra composta detectada.")

    with st.expander("📘 Visualizar texto original"):
        st.markdown(f"""
        <div style='background-color:#fafafa; padding:10px; border-radius:10px;'>
        {texto_input}
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
👨‍🏫 **Sobre o autor**  
**Autor:** José Wendel dos Santos  
**Instituição:** Universidade Federal de Sergipe (UFS)  
**Contato:** eng.wendel@gmail.com
""")
