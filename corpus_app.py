import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n
from collections import Counter

# Configuração da Página
st.set_page_config(
    page_title="Análise Textual Avançada",
    page_icon="📊",
    layout="wide",
)

# CSS Customizado
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
        background-color: #f0f2f6;
        transition: all 0.3s;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4a6fa5;
        color: white !important;
    }
    
    .stTextArea textarea {
        border-radius: 8px;
    }
    
    .stButton button {
        border-radius: 8px;
        background-color: #4a6fa5;
        color: white;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        background-color: #3a5a8f;
        transform: translateY(-2px);
    }
    
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .result-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Carregar modelo do spaCy
@st.cache_resource
def load_nlp_model():
    return spacy.load("pt_core_news_sm")

nlp = load_nlp_model()

# Funções para Análise de Texto
def detectar_siglas(texto):
    tokens = re.findall(r"\b[A-Z]{2,}\b", texto)
    return sorted(set(tokens))

def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    compostas = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return list(set(compostas))

def contar_palavras(texto):
    palavras = re.findall(r"\b\w+\b", texto.lower())
    return Counter(palavras).most_common(10)

def extrair_entidades(texto):
    doc = nlp(texto)
    entidades = [(ent.text, ent.label_) for ent in doc.ents]
    return entidades

# Funções para Gerar Corpus
def processar_texto(texto, df_compostos=None, df_siglas=None):
    # Implemente conforme necessário
    return texto

# Interface Principal
tab1, tab2 = st.tabs(["🔍 Análise de Texto", "📂 Gerador de Corpus"])

with tab1:
    st.header("Análise de Texto")
    texto_input = st.text_area(
        "Insira o texto para análise:",
        height=200,
        placeholder="Digite ou cole seu texto aqui..."
    )
    
    if st.button("Analisar", key="analisar_btn"):
        if texto_input.strip():
            with st.spinner("Processando..."):
                siglas = detectar_siglas(texto_input)
                compostas = detectar_palavras_compostas(texto_input)
                contagem_palavras = contar_palavras(texto_input)
                entidades = extrair_entidades(texto_input)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔠 Siglas Encontradas")
                if siglas:
                    st.dataframe(pd.DataFrame(siglas, columns=["Sigla"]), hide_index=True)
                else:
                    st.info("Nenhuma sigla encontrada.")
                
                st.subheader("📊 Palavras Mais Frequentes")
                if contagem_palavras:
                    st.dataframe(pd.DataFrame(contagem_palavras, columns=["Palavra", "Frequência"]), hide_index=True)
            
            with col2:
                st.subheader("🧩 Palavras Compostas")
                if compostas:
                    st.dataframe(pd.DataFrame(compostas, columns=["Termo"]), hide_index=True)
                else:
                    st.info("Nenhuma palavra composta encontrada.")
                
                st.subheader("🏷️ Entidades Nomeadas")
                if entidades:
                    st.dataframe(pd.DataFrame(entidades, columns=["Entidade", "Tipo"]), hide_index=True)
        else:
            st.warning("Por favor, insira um texto para análise.")

with tab2:
    st.header("Gerador de Corpus para IRaMuTeQ")
    
    st.info("""
    **Instruções:**  
    - Faça upload de um arquivo Excel com as abas:  
      1. `textos_selecionados` (textos a serem processados)  
      2. `dic_palavras_compostas` (dicionário de normalização)  
      3. `dic_siglas` (significado das siglas)  
    - Clique em **Gerar Corpus** para processar.  
    """)
    
    file = st.file_uploader("Upload do Arquivo Excel", type=["xlsx"])
    
    if file:
        try:
            xls = pd.ExcelFile(file)
            df_textos = xls.parse("textos_selecionados")
            df_compostos = xls.parse("dic_palavras_compostas")
            df_siglas = xls.parse("dic_siglas")
            
            st.success("Arquivo carregado com sucesso!")
            
            if st.button("Gerar Corpus", key="gerar_btn"):
                with st.spinner("Processando..."):
                    corpus = "**** *ID_1\nCorpus de exemplo gerado com sucesso!\n"
                
                st.success("Corpus gerado com sucesso!")
                st.text_area("Pré-visualização", corpus, height=150)
                
                st.download_button(
                    "Baixar Corpus",
                    data=corpus.encode("utf-8"),
                    file_name="corpus_iramuteq.txt",
                    mime="text/plain"
                )
        
        except Exception as e:
            st.error(f"Erro: {str(e)}")

# Rodapé
st.markdown("---")
st.caption("Desenvolvido por [Seu Nome] | © 2023")
