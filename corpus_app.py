import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n

# Configuração inicial da página
st.set_page_config(
    page_title="Text Analytics Suite | UFS",
    page_icon=":microscope:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS customizado
st.markdown("""
<style>
    .header-style {
        font-size: 24px;
        font-weight: 600;
        color: #2c3e50;
        padding-bottom: 10px;
        border-bottom: 2px solid #3498db;
        margin-bottom: 20px;
    }
    .subheader-style {
        font-size: 18px;
        font-weight: 500;
        color: #34495e;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    .metric-box {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .footer {
        font-size: 14px;
        color: #7f8c8d;
        text-align: center;
        padding: 15px;
        margin-top: 30px;
        border-top: 1px solid #eee;
    }
    .stButton>button {
        border-radius: 6px;
        padding: 8px 16px;
    }
    .stTextArea>textarea {
        border-radius: 6px;
    }
    .stDownloadButton>button {
        border-radius: 6px;
        background-color: #3498db;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Carregar modelo do spaCy
@st.cache_resource
def load_nlp_model():
    return spacy.load("pt_core_news_sm")

nlp = load_nlp_model()

# Funções da parte 1
@st.cache_data
def detectar_siglas(texto):
    tokens = re.findall(r"\b[A-Z]{2,}\b", texto)
    return sorted(set(tokens))

@st.cache_data
def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    compostas = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return list(set(compostas))

# ========================== PARTE 1 - PRÉ-ANÁLISE ==========================
st.markdown('<div class="header-style">Análise Linguística Automatizada</div>', unsafe_allow_html=True)

with st.expander("🔬 Ferramenta de Detecção de Padrões Textuais", expanded=True):
    st.markdown("""
    <div class="subheader-style">Identificação automática de elementos textuais complexos</div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        texto_input = st.text_area(
            "Insira o texto para análise:",
            height=200,
            placeholder="Cole ou digite o conteúdo textual a ser analisado...",
            help="O sistema identificará automaticamente siglas e termos compostos"
        )
    
    with col2:
        st.markdown('<div class="metric-box">ℹ️ <strong>Orientações</strong></div>', unsafe_allow_html=True)
        st.markdown("""
        - Textos com mais de 500 caracteres produzem melhores resultados
        - Siglas devem estar em CAIXA ALTA
        - Nomes próprios podem ser detectados como compostos
        """)

    if st.button("Executar Análise", type="primary", key="analyze_btn"):
        if texto_input.strip():
            with st.spinner("Processando texto... Aguarde"):
                siglas = detectar_siglas(texto_input)
                compostas = detectar_palavras_compostas(texto_input)

            st.markdown("---")
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.markdown('<div class="metric-box">📊 Resultados: Palavras Compostas</div>', unsafe_allow_html=True)
                if compostas:
                    st.success(f"🔍 {len(compostas)} termos identificados", icon="✅")
                    st.dataframe(pd.DataFrame(compostas, columns=["Termo"]), hide_index=True)
                else:
                    st.info("Nenhum termo composto identificado", icon="ℹ️")

            with col_res2:
                st.markdown('<div class="metric-box">📊 Resultados: Siglas</div>', unsafe_allow_html=True)
                if siglas:
                    st.success(f"🔠 {len(siglas)} siglas identificadas", icon="✅")
                    st.dataframe(pd.DataFrame(siglas, columns=["Sigla"]), hide_index=True)
                else:
                    st.info("Nenhuma sigla identificada", icon="ℹ️")
        else:
            st.warning("Por favor, insira um texto para análise", icon="⚠️")

# ========================== PARTE 2 - GERAÇÃO DE CORPUS ==========================
st.markdown("---")
st.markdown('<div class="header-style">Geração de Corpus para Análise Textual</div>', unsafe_allow_html=True)

with st.expander("🧮 Conversor para IRaMuTeQ", expanded=True):
    st.markdown("""
    <div class="subheader-style">Transformação automatizada de textos brutos em corpus estruturado</div>
    
    Esta ferramenta realiza o pré-processamento textual necessário para análise no software IRaMuTeQ,
    incluindo normalização de termos e tratamento de elementos especiais.
    """, unsafe_allow_html=True)
    
    tab_guide, tab_template = st.tabs(["📋 Guia de Preparação", "📥 Modelo de Planilha"])
    
    with tab_guide:
        st.markdown("""
        ### Requisitos do Arquivo de Entrada
        
        O arquivo Excel deve conter **três planilhas** com estrutura específica:
        
        1. **`textos_selecionados`**
           - Coluna obrigatória: `textos selecionados` (conteúdo textual)
           - Coluna opcional: `id` (identificador único)
           - Colunas adicionais serão incluídas como metadados
        
        2. **`dic_palavras_compostas`**
           - `Palavra composta`: Termo original
           - `Palavra normalizada`: Forma padronizada
        
        3. **`dic_siglas`**
           - `Sigla`: Acrônimo em maiúsculas
           - `Significado`: Expansão da sigla
        """)
    
    with tab_template:
        with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
            st.download_button(
                label="Download do Modelo",
                data=exemplo,
                file_name="modelo_corpus_iramuteq.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Modelo pré-formatado com todas as planilhas necessárias"
            )
        st.image("https://via.placeholder.com/600x300?text=Preview+do+Modelo", caption="Visualização da estrutura do arquivo modelo")

    st.markdown("---")
    file = st.file_uploader(
        "Carregue seu arquivo Excel preparado:",
        type=["xlsx"],
        help="Arquivo deve seguir a estrutura descrita no guia"
    )

    # Funções auxiliares da parte 2
    def converter_numeros_por_extenso(texto):
        unidades = {
            "zero": 0, "dois": 2, "duas": 2, "três": 3, "quatro": 4, "cinco": 5,
            "seis": 6, "sete": 7, "oito": 8, "nove": 9
        }
        dezenas = {
            "dez": 10, "onze": 11, "doze": 12, "treze": 13, "quatorze": 14, "quinze": 15,
            "dezesseis": 16, "dezessete": 17, "dezoito": 18, "dezenove": 19, "vinte": 20
        }
        centenas = {
            "cem": 100, "cento": 100, "duzentos": 200, "trezentos": 300, "quatrocentos": 400,
            "quinhentos": 500, "seiscentos": 600, "setecentos": 700, "oitocentos": 800, "novecentos": 900
        }
        multiplicadores = {
            "mil": 1000, "milhão": 1000000, "bilhão": 1000000000
        }
        
        # Função para converter texto em números
        # Aqui, você implementaria um algoritmo para converter números escritos por extenso
        return texto  # Exemplificação básica, pode ser expandido para processar corretamente

# ========================== RODAPÉ ==========================
st.markdown('<div class="footer">Desenvolvido por UFS Lab</div>', unsafe_allow_html=True)
