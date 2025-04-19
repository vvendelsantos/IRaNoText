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
            "mil": 1000, "milhão": 1000000, "milhões": 1000000, "bilhão": 1000000000,
            "bilhões": 1000000000
        }

        def processar_palavra(palavra):
            try:
                return str(w2n.word_to_num(palavra))
            except:
                return palavra

        palavras = texto.split()
        resultado = []
        for palavra in palavras:
            palavra_lower = palavra.lower()
            if palavra_lower in unidades:
                resultado.append(str(unidades[palavra_lower]))
            elif palavra_lower in dezenas:
                resultado.append(str(dezenas[palavra_lower]))
            elif palavra_lower in centenas:
                resultado.append(str(centenas[palavra_lower]))
            elif palavra_lower in multiplicadores:
                resultado.append(str(multiplicadores[palavra_lower]))
            else:
                resultado.append(processar_palavra(palavra))

        return " ".join(resultado)

    def processar_palavras_com_se(texto):
        return re.sub(r"(\b\w+)-se\b", r"se \1", texto)

    def processar_pronomes_pospostos(texto):
        texto = re.sub(r'\b(\w+)-se\b', r'se \1', texto)
        texto = re.sub(r'\b(\w+)-([oa]s?)\b', r'\2 \1', texto)
        texto = re.sub(r'\b(\w+)-(lhe|lhes)\b', r'\2 \1', texto)
        texto = re.sub(r'\b(\w+)-(me|te|nos|vos)\b', r'\2 \1', texto)
        texto = re.sub(r'\b(\w+)[áéíóúâêô]?-([oa]s?)\b', r'\2 \1', texto)
        texto = re.sub(r'\b(\w+)[áéíóúâêô]-(lo|la|los|las)-ia\b', r'\2 \1ia', texto)
        return texto

    def gerar_corpus(df_textos, df_compostos, df_siglas):
        dict_compostos = {
            str(row["Palavra composta"]).lower(): str(row["Palavra normalizada"]).lower()
            for _, row in df_compostos.iterrows()
            if pd.notna(row["Palavra composta"]) and pd.notna(row["Palavra normalizada"])
        }

        dict_siglas = {
            str(row["Sigla"]).lower(): str(row["Significado"])
            for _, row in df_siglas.iterrows()
            if pd.notna(row["Sigla"]) and pd.notna(row["Significado"])
        }

        caracteres_especiais = {
            "-": "Hífen", ";": "Ponto e vírgula", '"': "Aspas duplas", "'": "Aspas simples",
            "…": "Reticências", "–": "Travessão", "(": "Parêntese esquerdo", ")": "Parêntese direito",
            "/": "Barra", "%": "Porcentagem"
        }
        contagem_caracteres = {k: 0 for k in caracteres_especiais}
        total_textos = 0
        total_siglas = 0
        total_compostos = 0
        total_remocoes = 0
        corpus_final = ""

        for _, row in df_textos.iterrows():
            texto = str(row.get("textos selecionados", ""))
            id_val = row.get("id", "")
            if not texto.strip():
                continue

            texto_corrigido = texto.lower()
            texto_corrigido = converter_numeros_por_extenso(texto_corrigido)
            texto_corrigido = processar_palavras_com_se(texto_corrigido)
            texto_corrigido = processar_pronomes_pospostos(texto_corrigido)
            total_textos += 1

            for sigla, significado in dict_siglas.items():
                texto_corrigido = re.sub(rf"\({sigla}\)", "", texto_corrigido)
                texto_corrigido = re.sub(rf"\b{sigla}\b", significado, texto_corrigido, flags=re.IGNORECASE)
                total_siglas += 1

            for termo, substituto in dict_compostos.items():
                if termo in texto_corrigido:
                    texto_corrigido = re.sub(rf"\b{termo}\b", substituto, texto_corrigido, flags=re.IGNORECASE)
                    total_compostos += 1

            for char in caracteres_especiais:
                count = texto_corrigido.count(char)
                if count:
                    if char == "%":
                        texto_corrigido = texto_corrigido.replace(char, "")
                    else:
                        texto_corrigido = texto_corrigido.replace(char, "_")
                    contagem_caracteres[char] += count
                    total_remocoes += count

            texto_corrigido = re.sub(r"\s+", " ", texto_corrigido.strip())

            metadata = f"**** *ID_{id_val}"
            for col in row.index:
                if col.lower() not in ["id", "textos selecionados"]:
                    metadata += f" *{col.replace(' ', '_')}_{str(row[col]).replace(' ', '_')}"

            corpus_final += f"{metadata}\n{texto_corrigido}\n"

        estatisticas = {
            "textos_processados": total_textos,
            "siglas_substituidas": total_siglas,
            "compostos_normalizados": total_compostos,
            "caracteres_removidos": total_remocoes,
            "detalhes_caracteres": {k: v for k, v in contagem_caracteres.items() if v > 0}
        }

        return corpus_final, estatisticas

    if file:
        try:
            with st.spinner("Validando estrutura do arquivo..."):
                xls = pd.ExcelFile(file)
                required_sheets = ["textos_selecionados", "dic_palavras_compostas", "dic_siglas"]
                if not all(sheet in xls.sheet_names for sheet in required_sheets):
                    missing = [sheet for sheet in required_sheets if sheet not in xls.sheet_names]
                    raise ValueError(f"Planilhas obrigatórias ausentes: {', '.join(missing)}")

                df_textos = xls.parse("textos_selecionados")
                df_compostos = xls.parse("dic_palavras_compostas")
                df_siglas = xls.parse("dic_siglas")
                df_textos.columns = [col.strip().lower() for col in df_textos.columns]

                if "textos selecionados" not in df_textos.columns:
                    raise ValueError("Coluna 'textos selecionados' não encontrada na planilha de textos")

            st.success("✅ Arquivo validado com sucesso!", icon="✅")
            
            if st.button("Iniciar Processamento", type="primary", key="process_btn"):
                with st.spinner("Gerando corpus... Este processo pode levar alguns minutos"):
                    corpus, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas)

                if corpus.strip():
                    st.balloons()
                    st.success("Processamento concluído com sucesso!", icon="🎉")
                    
                    tab_result, tab_stats = st.tabs(["📄 Corpus Gerado", "📈 Estatísticas"])
                    
                    with tab_result:
                        st.text_area(
                            "Conteúdo do Corpus",
                            corpus,
                            height=300,
                            label_visibility="collapsed"
                        )
                        buf = io.BytesIO()
                        buf.write(corpus.encode("utf-8"))
                        st.download_button(
                            "Exportar Corpus",
                            data=buf.getvalue(),
                            file_name="corpus_IRaMuTeQ.txt",
                            mime="text/plain"
                        )
                    
                    with tab_stats:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Textos Processados", estatisticas["textos_processados"])
                            st.metric("Siglas Substituídas", estatisticas["siglas_substituidas"])
                        
                        with col2:
                            st.metric("Termos Compostos", estatisticas["compostos_normalizados"])
                            st.metric("Caracteres Removidos", estatisticas["caracteres_removidos"])
                        
                        with col3:
                            if estatisticas["detalhes_caracteres"]:
                                st.markdown("**Caracteres Especiais Removidos:**")
                                for char, count in estatisticas["detalhes_caracteres"].items():
                                    st.write(f"- {char}: {count}")
                            else:
                                st.info("Nenhum caractere especial removido", icon="ℹ️")
                else:
                    st.warning("O corpus gerado está vazio. Verifique os dados de entrada.", icon="⚠️")

        except Exception as e:
            st.error(f"Falha no processamento: {str(e)}", icon="❌")
            st.info("Consulte o guia de preparação para corrigir o arquivo")

# ========================== RODAPÉ ==========================
st.markdown("---")
st.markdown("""
<div class="footer">
    Laboratório de Análise Textual | Universidade Federal de Sergipe<br>
    Desenvolvido por: José Wendel dos Santos | Versão 2.1.0
</div>
""", unsafe_allow_html=True)
