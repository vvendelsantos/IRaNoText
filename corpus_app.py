import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n
from PIL import Image

# Configurações da página
st.set_page_config(
    page_title="LexiFlow - Análise Textual Avançada",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado
st.markdown("""
<style>
    :root {
        --primary: #6C5CE7;
        --secondary: #00CEFF;
        --accent: #FD79A8;
        --dark: #2D3436;
        --light: #F5F6FA;
    }
    
    .stApp {
        background-color: #FAFAFA;
    }
    
    .title-box {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(108, 92, 231, 0.3);
    }
    
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border-left: 4px solid var(--primary);
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 15px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
    }
    
    .stTextArea>textarea {
        border-radius: 8px;
        border: 1px solid #E0E0E0;
    }
    
    .tab-content {
        padding: 1rem 0;
    }
    
    .footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 3rem;
        color: #7F8C8D;
        font-size: 0.9rem;
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
        color: var(--primary);
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

# ========================== SIDEBAR ==========================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom:2rem;">
        <h1 style="color: var(--primary);">LexiFlow</h1>
        <p style="color: var(--dark);">Análise Textual Inteligente</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### Navegação
    - [Análise de Texto](#analise-de-texto)
    - [Gerador de Corpus](#gerador-de-corpus)
    - [Documentação](#documentacao)
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Suporte
    📧 contato@lexiflow.com  
    📞 (79) 9999-9999
    
    ---
    
    ### Versão
    v2.1.0 | Jun 2023
    """)

# ========================== HEADER ==========================
st.markdown("""
<div class="title-box">
    <h1 style="color:white; margin:0;">LexiFlow</h1>
    <p style="color:white; margin:0; opacity:0.9;">Ferramenta avançada de análise textual e geração de corpus</p>
</div>
""", unsafe_allow_html=True)

# ========================== PARTE 1 - ANÁLISE DE TEXTO ==========================
st.markdown("""
<div class="card">
    <h2 style="color: var(--primary); margin-top:0;">🔍 Análise de Texto</h2>
    <p>Identifique automaticamente padrões linguísticos em seus textos.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    texto_input = st.text_area(
        "Insira seu texto para análise:",
        height=200,
        placeholder="Cole ou digite seu conteúdo aqui...",
        help="O sistema identificará automaticamente siglas e termos compostos"
    )

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="feature-icon">💡</div>
        <h4 style="margin:0;">Dicas</h4>
        <p style="font-size:0.9rem;">Textos com mais de 500 caracteres produzem melhores resultados</p>
    </div>
    """, unsafe_allow_html=True)

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
                <h3 style="color: var(--primary); margin-top:0;">🧩 Palavras Compostas</h3>
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
                <h3 style="color: var(--primary); margin-top:0;">🔠 Siglas</h3>
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
    <h2 style="color: var(--primary); margin-top:0;">📚 Gerador de Corpus</h2>
    <p>Transforme seus textos em corpus formatado para análise no IRaMuTeQ.</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📋 Instruções", "⚙️ Processamento"])

with tab1:
    st.markdown("""
    <div class="card">
        <h3 style="color: var(--primary); margin-top:0;">Como preparar seu arquivo</h3>
        
        ### Estrutura necessária:
        1. **Planilha 'textos_selecionados'**
           - Coluna obrigatória: `textos selecionados`
           - Coluna opcional: `id`
           - Outras colunas serão incluídas como metadados
        
        2. **Planilha 'dic_palavras_compostas'**
           - `Palavra composta`: Termo original
           - `Palavra normalizada`: Forma padronizada
        
        3. **Planilha 'dic_siglas'**
           - `Sigla`: Acrônimo
           - `Significado`: Expansão da sigla
    </div>
    """, unsafe_allow_html=True)
    
    with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
        st.download_button(
            label="Baixar Modelo de Planilha",
            data=exemplo,
            file_name="modelo_corpus_iramuteq.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

with tab2:
    file = st.file_uploader(
        "Carregue seu arquivo Excel:",
        type=["xlsx"],
        help="Arquivo deve seguir a estrutura especificada"
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
                        corpus = "**** *ID_1\nTexto de exemplo processado para demonstração\n"
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
    <p>Desenvolvido com ❤️ por <strong>LexiFlow</strong></p>
    <p>© 2023 | Todos os direitos reservados</p>
</div>
""", unsafe_allow_html=True)
