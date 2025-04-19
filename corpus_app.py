import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n

# Carregar modelo do spaCy
nlp = spacy.load("pt_core_news_sm")

# ====================== CONFIGURAÇÃO DA PÁGINA ======================
st.set_page_config(
    page_title="Analisador de Texto Avançado",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== FUNÇÕES AUXILIARES ======================
def detectar_siglas(texto):
    """Detecta siglas no texto (palavras com 2+ letras maiúsculas)"""
    tokens = re.findall(r"\b[A-Z]{2,}\b", texto)
    return sorted(set(tokens))

def detectar_palavras_compostas(texto):
    """Identifica palavras compostas usando o modelo de NER do spaCy"""
    doc = nlp(texto)
    compostas = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return list(set(compostas))

def estilo_pagina():
    """Aplica estilos CSS personalizados"""
    st.markdown("""
    <style>
        .stApp {
            background-color: #f9f9f9;
        }
        .stTextArea textarea {
            min-height: 200px;
        }
        .stButton>button {
            width: 100%;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: scale(1.02);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #2c3e50;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            border-radius: 8px 8px 0 0 !important;
        }
        .stAlert {
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

# Aplicar estilos
estilo_pagina()

# ====================== LAYOUT PRINCIPAL ======================
st.title("📊 Analisador de Texto Avançado")
st.markdown("""
    **Ferramenta para detecção de siglas, palavras compostas e geração de corpus textual compatível com IRaMuTeQ**
""")

# ====================== ABAS PRINCIPAIS ======================
tab1, tab2 = st.tabs(["📝 Pré-análise de Texto", "📑 Geração de Corpus"])

with tab1:
    # ====================== PARTE 1 - PRÉ-ANÁLISE ======================
    st.header("🔍 Detecção de Siglas e Palavras Compostas")
    
    with st.expander("ℹ️ Sobre esta ferramenta", expanded=False):
        st.info("""
        Esta ferramenta identifica automaticamente:
        - **Siglas**: Palavras com 2 ou mais letras maiúsculas (ex: UFS, ONU)
        - **Palavras compostas**: Expressões de múltiplas palavras que formam um conceito único (ex: ensino superior, inteligência artificial)
        """)
    
    texto_input = st.text_area(
        "✍️ Insira seu texto para análise",
        height=250,
        placeholder="Cole ou digite seu texto aqui...",
        help="O texto será analisado para detectar siglas e palavras compostas automaticamente"
    )
    
    if st.button("🔍 Analisar Texto", type="primary", use_container_width=True):
        if texto_input.strip():
            with st.spinner("Processando texto..."):
                siglas = detectar_siglas(texto_input)
                compostas = detectar_palavras_compostas(texto_input)
            
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                st.subheader("🧩 Palavras Compostas Detectadas")
                if compostas:
                    st.success(f"✅ {len(compostas)} termo(s) encontrado(s)")
                    with st.container(border=True):
                        for termo in compostas:
                            st.markdown(f"- **{termo}**")
                else:
                    st.info("ℹ️ Nenhuma palavra composta encontrada.")
            
            with col2:
                st.subheader("🧾 Siglas Detectadas")
                if siglas:
                    st.success(f"✅ {len(siglas)} sigla(s) encontrada(s)")
                    with st.container(border=True):
                        for sigla in siglas:
                            st.markdown(f"- **{sigla}**")
                else:
                    st.info("ℹ️ Nenhuma sigla encontrada.")
        else:
            st.warning("⚠️ Por favor, insira um texto antes de analisar.")

with tab2:
    # ====================== PARTE 2 - GERAÇÃO DE CORPUS ======================
    st.header("📑 Gerador de Corpus Textual para IRaMuTeQ")
    
    with st.expander("📌 Instruções detalhadas", expanded=True):
        st.markdown("""
        ### Estrutura necessária da planilha
        
        Para gerar o corpus corretamente, sua planilha Excel deve conter **3 abas** com os seguintes nomes:
        
        1. **`textos_selecionados`**: Textos que serão processados (obrigatório ter coluna 'id')
        2. **`dic_palavras_compostas`**: Dicionário de palavras compostas e suas formas normalizadas
        3. **`dic_siglas`**: Dicionário de siglas e seus significados completos
        
        ### Processamento realizado
        
        - Normalização de números por extenso para algarismos
        - Tratamento de pronomes pospostos ("-se", "-lo", "-la", etc.)
        - Substituição de siglas por seus significados
        - Normalização de palavras compostas
        - Remoção/redução de caracteres especiais
        - Geração de metadados para cada texto
        """)
    
    # Botões para download de modelos
    st.subheader("📥 Modelos para download")
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
            st.download_button(
                label="📋 Baixar modelo de planilha",
                data=exemplo,
                file_name="modelo_corpus_iramuteq.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Planilha modelo com a estrutura necessária",
                use_container_width=True
            )
    
    with col_dl2:
        with open("textos_selecionados.xlsx", "rb") as textos:
            st.download_button(
                label="📂 Baixar textos exemplo",
                data=textos,
                file_name="textos_exemplo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Exemplo de textos para análise",
                use_container_width=True
            )
    
    # Upload de arquivo
    st.subheader("📤 Envie sua planilha")
    file = st.file_uploader(
        "Arraste e solte ou selecione seu arquivo Excel",
        type=["xlsx"],
        help="Planilha deve conter as 3 abas necessárias",
        label_visibility="collapsed"
    )
    
    # Funções auxiliares da parte 2
    def converter_numeros_por_extenso(texto):
        """Converte números por extenso para algarismos numéricos"""
        try:
            return str(w2n.word_to_num(texto))
        except:
            return texto

    def processar_palavras_com_se(texto):
        """Trata pronomes 'se' pospostos"""
        return re.sub(r"(\b\w+)-se\b", r"se \1", texto)

    def processar_pronomes_pospostos(texto):
        """Trata vários tipos de pronomes pospostos"""
        texto = re.sub(r'\b(\w+)-se\b', r'se \1', texto)
        texto = re.sub(r'\b(\w+)-([oa]s?)\b', r'\2 \1', texto)
        texto = re.sub(r'\b(\w+)-(lhe|lhes)\b', r'\2 \1', texto)
        texto = re.sub(r'\b(\w+)-(me|te|nos|vos)\b', r'\2 \1', texto)
        texto = re.sub(r'\b(\w+)[áéíóúâêô]?-([oa]s?)\b', r'\2 \1', texto)
        texto = re.sub(r'\b(\w+)[áéíóúâêô]-(lo|la|los|las)-ia\b', r'\2 \1ia', texto)
        return texto

    def gerar_corpus(df_textos, df_compostos, df_siglas):
        """Gera o corpus textual com base nas planilhas fornecidas"""
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

        estatisticas = f"📊 Estatísticas de Processamento\n{'='*30}\n"
        estatisticas += f"- Textos processados: {total_textos}\n"
        estatisticas += f"- Siglas substituídas: {total_siglas}\n"
        estatisticas += f"- Palavras compostas normalizadas: {total_compostos}\n"
        estatisticas += f"- Caracteres especiais tratados: {total_remocoes}\n"
        for char, nome in caracteres_especiais.items():
            if contagem_caracteres[char] > 0:
                estatisticas += f"  - {nome} ({char}): {contagem_caracteres[char]}\n"

        return corpus_final, estatisticas

    if file:
        try:
            with st.spinner("Processando planilha..."):
                xls = pd.ExcelFile(file)
                df_textos = xls.parse("textos_selecionados")
                df_compostos = xls.parse("dic_palavras_compostas")
                df_siglas = xls.parse("dic_siglas")
                df_textos.columns = [col.strip().lower() for col in df_textos.columns]

            if st.button("🚀 Gerar Corpus", type="primary", use_container_width=True):
                with st.spinner("Gerando corpus..."):
                    corpus, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas)

                if corpus.strip():
                    st.success("✅ Corpus gerado com sucesso!")
                    
                    # Visualização do corpus
                    st.subheader("📄 Pré-visualização do Corpus")
                    with st.expander("Visualizar conteúdo gerado", expanded=True):
                        st.text_area("", corpus, height=300, label_visibility="collapsed")
                    
                    # Estatísticas
                    st.subheader("📊 Métricas do Processamento")
                    with st.container(border=True):
                        st.text(estatisticas)
                    
                    # Download do corpus
                    st.subheader("📥 Download do Corpus")
                    buf = io.BytesIO()
                    buf.write(corpus.encode("utf-8"))
                    st.download_button(
                        "💾 Baixar Corpus Textual",
                        data=buf.getvalue(),
                        file_name="corpus_IRaMuTeQ.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    st.warning("⚠️ Nenhum texto válido encontrado na planilha.")

        except Exception as e:
            st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
            st.info("Verifique se todas as abas necessárias estão presentes e no formato correto.")

# ====================== RODAPÉ ======================
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    <p>👨‍💻 Desenvolvido por <strong>José Wendel dos Santos</strong></p>
    <p>🏛 Universidade Federal de Sergipe (UFS) | 📧 eng.wendel@gmail.com</p>
</div>
""", unsafe_allow_html=True)
