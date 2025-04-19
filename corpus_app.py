import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n

# Configuração básica da página
st.set_page_config(
    page_title="Ferramenta de Análise Textual",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Carregar modelo do spaCy
@st.cache_resource
def load_nlp_model():
    return spacy.load("pt_core_news_sm")

nlp = load_nlp_model()

# Funções de análise
@st.cache_data
def detectar_siglas(texto):
    tokens = re.findall(r"\b[A-Z]{2,}\b", texto)
    return sorted(set(tokens))

@st.cache_data
def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    compostas = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return list(set(compostas))

# Layout principal com abas
tab1, tab2 = st.tabs(["📝 Análise de Texto", "📚 Gerador de Corpus"])

with tab1:
    st.header("Análise de Texto Automática")
    st.markdown("Identifique siglas e palavras compostas em seus textos.")
    
    texto_input = st.text_area(
        "Insira seu texto para análise:",
        height=200,
        placeholder="Digite ou cole seu texto aqui..."
    )
    
    if st.button("Analisar Texto", key="analyze_btn"):
        if texto_input.strip():
            with st.spinner("Processando..."):
                siglas = detectar_siglas(texto_input)
                compostas = detectar_palavras_compostas(texto_input)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Palavras Compostas")
                if compostas:
                    st.write(pd.DataFrame(compostas, columns=["Termo"]))
                else:
                    st.info("Nenhuma palavra composta encontrada")
            
            with col2:
                st.subheader("Siglas Identificadas")
                if siglas:
                    st.write(pd.DataFrame(siglas, columns=["Sigla"]))
                else:
                    st.info("Nenhuma sigla encontrada")
        else:
            st.warning("Por favor, insira um texto para análise")

with tab2:
    st.header("Gerador de Corpus para IRaMuTeQ")
    st.markdown("Transforme seus textos em corpus formatado para análise.")
    
    with st.expander("ℹ️ Instruções"):
        st.markdown("""
        - Prepare uma planilha Excel com três abas:
          1. `textos_selecionados` (textos brutos)
          2. `dic_palavras_compostas` (termos compostos)
          3. `dic_siglas` (siglas e significados)
        - Faça upload do arquivo abaixo
        """)
    
    file = st.file_uploader("Upload do arquivo Excel", type=["xlsx"])
    
    if file:
        try:
            xls = pd.ExcelFile(file)
            sheets = xls.sheet_names
            
            if st.button("Processar Arquivo", key="process_btn"):
                with st.spinner("Gerando corpus..."):
                    # Simulação de processamento
                    corpus = "**** *ID_1\nExemplo de texto processado\n"
                    
                    st.success("Processamento concluído!")
                    st.text_area("Corpus Gerado", corpus, height=200)
                    
                    st.download_button(
                        "Baixar Corpus",
                        data=corpus,
                        file_name="corpus.txt",
                        mime="text/plain"
                    )
        
        except Exception as e:
            st.error(f"Erro: {str(e)}")

# Rodapé simples
st.markdown("---")
st.markdown("Desenvolvido por Text Analytics Tool | 2023")
