import streamlit as st
import pandas as pd
import re
import spacy
from io import BytesIO

# Carregar modelo spaCy para reconhecimento de entidades nomeadas
nlp = spacy.load("pt_core_news_lg")

st.set_page_config(layout="wide")

st.title("IRaText: Geração de Corpus Textual para IRaMuTeQ")

st.markdown("## 🔍 Analisador de Texto - Detecção de Siglas e Palavras Compostas")

# Caixa de texto para entrada do usuário
input_text = st.text_area("Insira o texto para análise:", height=300)

# Funções para detecção
def detectar_siglas(texto):
    padrao = r'\b[A-Z]{2,}(?:s\b|\b)'  # Detecta siglas com 2+ letras maiúsculas
    return list(set(re.findall(padrao, texto)))

def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    entidades = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return sorted(set(entidades))

# Botão de análise
if st.button("🔎 Analisar texto"):
    if input_text.strip() == "":
        st.warning("Por favor, insira um texto para análise.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            palavras_compostas = detectar_palavras_compostas(input_text)
            st.subheader("📚 Palavras Compostas Detectadas")
            palavras_compostas_str = "\n".join(palavras_compostas)
            st.text(palavras_compostas_str)

            # Botão de cópia para palavras compostas
            st.markdown(
                f"""
                <button onclick="navigator.clipboard.writeText(`{palavras_compostas_str}`)"
                        style="margin-top: 10px; background-color: #4CAF50; color: white; 
                               border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer;">
                    📋 Copiar palavras compostas
                </button>
                """,
                unsafe_allow_html=True
            )

        with col2:
            siglas = detectar_siglas(input_text)
            st.subheader("🔠 Siglas Detectadas")
            siglas_str = "\n".join(siglas)
            st.text(siglas_str)

            # Botão de cópia para siglas
            st.markdown(
                f"""
                <button onclick="navigator.clipboard.writeText(`{siglas_str}`)"
                        style="margin-top: 10px; background-color: #2196F3; color: white; 
                               border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer;">
                    📋 Copiar siglas
                </button>
                """,
                unsafe_allow_html=True
            )

st.markdown("---")
st.markdown("## 📁 Geração de Corpus Textual para IRaMuTeQ")

# Botões para download de arquivos
col_b1, col_b2 = st.columns(2)
with col_b1:
    st.markdown("[📥 Baixar modelo de planilha](https://github.com/wendelgit/iratool/raw/main/modelo_planilha.xlsx)")
with col_b2:
    st.markdown("[📥 Baixar textos para análise](https://github.com/wendelgit/iratool/raw/main/textos_selecionados.xlsx)")

# Upload da planilha
uploaded_file = st.file_uploader("Envie a planilha preenchida:", type=["xlsx"])

if uploaded_file is not None:
    planilha = pd.read_excel(uploaded_file, sheet_name=None)
    
    if {'textos_selecionados', 'dic_palavras_compostas', 'dic_siglas'}.issubset(planilha.keys()):
        df_textos = planilha['textos_selecionados']
        df_dic_pc = planilha['dic_palavras_compostas']
        df_dic_siglas = planilha['dic_siglas']

        # Substituição de palavras compostas
        for i, row in df_dic_pc.iterrows():
            original = str(row['original'])
            substituto = str(row['substituto'])
            df_textos['texto'] = df_textos['texto'].str.replace(original, substituto, regex=False)

        # Substituição de siglas
        for i, row in df_dic_siglas.iterrows():
            original = str(row['original'])
            substituto = str(row['substituto'])
            df_textos['texto'] = df_textos['texto'].str.replace(original, substituto, regex=False)

        # Gerar corpus textual
        corpus = ""
        for _, row in df_textos.iterrows():
            id_texto = str(row['id'])
            texto = str(row['texto']).replace("\n", " ")
            corpus += f"**** *{id_texto}*\n{texto}\n\n"

        # Mostrar corpus antes do download
        st.subheader("📄 Corpus Gerado")
        st.text_area("Visualização do Corpus", corpus, height=300)

        # Opção de download
        def gerar_download(corpus):
            buffer = BytesIO()
            buffer.write(corpus.encode('utf-8'))
            buffer.seek(0)
            return buffer

        st.download_button(
            label="⬇️ Baixar Corpus .txt",
            data=gerar_download(corpus),
            file_name="corpus_IRaMuTeQ.txt",
            mime="text/plain"
        )
    else:
        st.error("A planilha deve conter as abas: textos_selecionados, dic_palavras_compostas e dic_siglas.")

# Rodapé
st.markdown("---")
st.markdown(
    """
    👨‍🏫 **Sobre o autor**  
    **Autor:** José Wendel dos Santos  
    **Instituição:** Universidade Federal de Sergipe (UFS)  
    **Contato:** eng.wendel@gmail.com
    """
)
