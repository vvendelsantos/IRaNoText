import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n

# Configuração da página com tema escuro
st.set_page_config(
    page_title="Text Analytics Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado - Tema Escuro Premium
st.markdown("""
<style>
    :root {
        --primary: #8A2BE2;
        --secondary: #00CED1;
        --accent: #FF8C00;
        --dark: #121212;
        --darker: #0A0A0A;
        --light: #E0E0E0;
        --text: #F5F5F5;
    }
    
    .stApp {
        background-color: var(--dark);
        color: var(--text);
    }
    
    .stTextArea>textarea {
        background-color: var(--darker);
        color: var(--text);
        border: 1px solid #333;
    }
    
    .stTextInput>div>input {
        background-color: var(--darker);
        color: var(--text);
    }
    
    .stSelectbox>div>div>select {
        background-color: var(--darker);
        color: var(--text);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(138, 43, 226, 0.4);
    }
    
    .header {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        padding: 1.5rem;
        border-radius: 0 0 12px 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .card {
        background-color: var(--darker);
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid var(--primary);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .metric-card {
        background-color: var(--darker);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #333;
    }
    
    .sidebar .sidebar-content {
        background-color: var(--darker);
    }
    
    .footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 3rem;
        color: var(--light);
        font-size: 0.9rem;
        border-top: 1px solid #333;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text) !important;
    }
    
    .stDataFrame {
        background-color: var(--darker) !important;
    }
    
    .stAlert {
        background-color: rgba(0, 0, 0, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

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

# ========================== HEADER ==========================
st.markdown("""
<div class="header">
    <h1 style="margin:0;">Text Analytics Pro</h1>
    <p style="margin:0; opacity:0.9;">Ferramenta profissional de análise textual</p>
</div>
""", unsafe_allow_html=True)

# ========================== SIDEBAR ==========================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom:2rem;">
        <h2 style="color: var(--primary);">Menu</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### Navegação
    - [Análise de Texto](#analise-de-texto)
    - [Gerador de Corpus](#gerador-de-corpus)
    - [Configurações](#configuracoes)
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Suporte
    📧 suporte@textanalytics.com  
    📞 (79) 9999-9999
    
    ---
    
    ### Versão
    v2.1.0 | Jun 2023
    """)

# ========================== PARTE 1 - ANÁLISE DE TEXTO ==========================
st.markdown("""
<div class="card">
    <h2 style="margin-top:0;">🔍 Análise de Texto</h2>
    <p>Identifique padrões linguísticos em seus textos.</p>
</div>
""", unsafe_allow_html=True)

texto_input = st.text_area(
    "Insira seu texto para análise:",
    height=200,
    placeholder="Cole ou digite seu conteúdo aqui...",
    help="O sistema identificará automaticamente siglas e termos compostos"
)

if st.button("Analisar Texto", type="primary"):
    if texto_input.strip():
        with st.spinner("Processando seu texto..."):
            siglas = detectar_siglas(texto_input)
            compostas = detectar_palavras_compostas(texto_input)

        st.markdown("---")
        
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.markdown("""
            <div class="card">
                <h3 style="margin-top:0;">🧩 Palavras Compostas</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if compostas:
                df_compostas = pd.DataFrame(compostas, columns=["Termo"])
                st.dataframe(df_compostas, use_container_width=True, height=300)
            else:
                st.info("Nenhum termo composto identificado", icon="ℹ️")

        with col_res2:
            st.markdown("""
            <div class="card">
                <h3 style="margin-top:0;">🔠 Siglas</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if siglas:
                df_siglas = pd.DataFrame(siglas, columns=["Sigla"])
                st.dataframe(df_siglas, use_container_width=True, height=300)
            else:
                st.info("Nenhuma sigla identificada", icon="ℹ️")
    else:
        st.warning("Por favor, insira um texto para análise", icon="⚠️")

# ========================== PARTE 2 - GERADOR DE CORPUS ==========================
st.markdown("---")
st.markdown("""
<div class="card">
    <h2 style="margin-top:0;">📚 Gerador de Corpus</h2>
    <p>Transforme seus textos em corpus formatado para análise.</p>
</div>
""", unsafe_allow_html=True)

file = st.file_uploader(
    "Carregue seu arquivo Excel:",
    type=["xlsx"],
    help="Arquivo deve conter as planilhas necessárias"
)

if file:
    try:
        with st.spinner("Processando seu arquivo..."):
            xls = pd.ExcelFile(file)
            df_textos = xls.parse("textos_selecionados")
            df_compostos = xls.parse("dic_palavras_compostas")
            df_siglas = xls.parse("dic_siglas")
            
            st.success("Arquivo carregado com sucesso!", icon="✅")
            
            if st.button("Gerar Corpus", type="primary"):
                with st.spinner("Gerando corpus..."):
                    # Simulação de processamento
                    corpus = "**** *ID_1\nTexto de exemplo processado\n"
                    stats = {
                        "textos": 1,
                        "siglas": 0,
                        "compostos": 0
                    }
                
                st.balloons()
                st.success("Corpus gerado com sucesso!", icon="🎉")
                
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                
                with col_stat1:
                    st.markdown("""
                    <div class="metric-card">
                        <h3>{}</h3>
                        <p>Textos Processados</p>
                    </div>
                    """.format(stats["textos"]), unsafe_allow_html=True)
                
                with col_stat2:
                    st.markdown("""
                    <div class="metric-card">
                        <h3>{}</h3>
                        <p>Siglas Substituídas</p>
                    </div>
                    """.format(stats["siglas"]), unsafe_allow_html=True)
                
                with col_stat3:
                    st.markdown("""
                    <div class="metric-card">
                        <h3>{}</h3>
                        <p>Termos Compostos</p>
                    </div>
                    """.format(stats["compostos"]), unsafe_allow_html=True)
                
                st.text_area("Corpus Gerado", corpus, height=200)
                
                st.download_button(
                    "Baixar Corpus",
                    data=corpus,
                    file_name="corpus_iramuteq.txt",
                    mime="text/plain"
                )
    
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {str(e)}", icon="❌")

# ========================== FOOTER ==========================
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>Desenvolvido por <strong>Text Analytics Pro</strong></p>
    <p>© 2023 | Todos os direitos reservados</p>
</div>
""", unsafe_allow_html=True)
