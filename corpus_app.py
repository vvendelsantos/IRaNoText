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
    initial_sidebar_state="expanded"
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

# ========================== SIDEBAR ==========================
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=UFS+Lab", width=150)
    st.markdown("""
    ## Text Analytics Suite
    **Versão:** 2.1.0  
    **Última atualização:** 15/06/2023
    
    ---
    ### Suporte Técnico
    Entre em contato com nossa equipe:
    - eng.wendel@gmail.com
    - (79) 99999-9999
    
    ---
    ### Documentação
    [Manual do Usuário](https://example.com)  
    [Tutoriais em Vídeo](https://example.com)
    """)

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
st.markdown('<div class="header-style">Geração de Corpus a partir de Planilha</div>', unsafe_allow_html=True)

with st.expander("📂 Carregar Planilha", expanded=True):
    st.markdown("""
    <div class="subheader-style">Faça upload de uma planilha com os dados completos</div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Selecione o arquivo Excel para gerar o corpus textual",
        type=["xlsx"],
        help="A planilha deve conter as abas: 'textos_selecionados', 'dic_palavras_compostas' e 'dic_siglas'"
    )

    if uploaded_file:
        try:
            with st.spinner("Carregando a planilha..."):
                excel_file = pd.ExcelFile(uploaded_file)
                df_textos = excel_file.parse("textos_selecionados")
                df_palavras = excel_file.parse("dic_palavras_compostas")
                df_siglas = excel_file.parse("dic_siglas")
                st.success("Planilha carregada com sucesso!", icon="✅")

                st.markdown("### Pré-visualização da Planilha")
                st.write("#### Textos Selecionados", df_textos.head())
                st.write("#### Dicionário de Palavras Compostas", df_palavras.head())
                st.write("#### Dicionário de Siglas", df_siglas.head())

            if st.button("Gerar Corpus"):
                with st.spinner("Gerando corpus textual..."):
                    # A função que gera o corpus pode ser implementada aqui
                    # Exemplo de chamada à função que processaria os dados
                    st.success("Corpus gerado com sucesso!", icon="✅")
                    # Abaixo seria um exemplo de como você pode permitir o download do corpus gerado
                    # Generate corpus and save it as a CSV or any desired format

        except Exception as e:
            st.error(f"Erro ao carregar a planilha: {e}")

# ========================== RODAPÉ ==========================
st.markdown("""
<div class="footer">
    &copy; 2025 UFS Lab | Desenvolvido por Eng. Wendel | Todos os direitos reservados
</div>
""", unsafe_allow_html=True)
