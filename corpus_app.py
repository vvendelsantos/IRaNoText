import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n

# Carregar modelo do spaCy
nlp = spacy.load("pt_core_news_sm")

# Configuração de página mais profissional
st.set_page_config(
    page_title="Analisador de Texto Profissional",
    page_icon=":memo:",
    layout="wide"
)

# CSS personalizado para aparência premium
st.markdown("""
    <style>
        .main {
            max-width: 95%;
            padding: 2rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 20px;
            border-radius: 8px 8px 0 0;
        }
        .stTabs [aria-selected="true"] {
            background-color: #f0f2f6;
            font-weight: 600;
        }
        .stButton>button {
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
        }
        .stDownloadButton>button {
            width: 100%;
            justify-content: center;
        }
        .stTextArea textarea {
            min-height: 200px;
        }
        .result-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .footer {
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid #e6e6e6;
            color: #666;
            font-size: 0.9rem;
        }
        .header-title {
            color: #1e3a8a;
            margin-bottom: 0.5rem;
        }
        .header-subtitle {
            color: #4b5563;
            margin-bottom: 1.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Funções ORIGINAIS (sem alterações)
def detectar_siglas(texto):
    tokens = re.findall(r"\b[A-Z]{2,}\b", texto)
    return sorted(set(tokens))

def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    compostas = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return list(set(compostas))

# ========================== ABAS ==========================
st.markdown('<h1 class="header-title">Analisador de Texto Profissional</h1>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Detecção de Siglas e Palavras Compostas | Geração de Corpus para IRaMuTeQ</p>', unsafe_allow_html=True)

tabs = st.tabs(["📝 Pré-análise", "📑 Geração de Corpus"])

with tabs[0]:
    # ========================== PARTE 1 - PRÉ-ANÁLISE ==========================
    st.header("Detecção de Siglas e Palavras Compostas")

    texto_input = st.text_area(
        "✍️ Insira um texto para pré-análise", 
        height=200,
        placeholder="Cole ou digite seu texto aqui..."
    )

    if st.button("🔍 Analisar texto", type="primary"):
        if texto_input.strip():
            siglas = detectar_siglas(texto_input)
            compostas = detectar_palavras_compostas(texto_input)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🧩 Palavras Compostas Detectadas")
                if compostas:
                    for termo in compostas:
                        st.write(f"- {termo}")
                else:
                    st.info("Nenhuma palavra composta encontrada.")

            with col2:
                st.markdown("### 🧾 Siglas Detectadas")
                if siglas:
                    for sigla in siglas:
                        st.write(f"- {sigla}")
                else:
                    st.info("Nenhuma sigla encontrada.")
        else:
            st.warning("Por favor, insira um texto antes de analisar.")

with tabs[1]:
    # ========================== PARTE 2 - GERAÇÃO DE CORPUS ==========================
    st.header("Gerador de Corpus Textual para IRaMuTeQ")

    with st.expander("📌 Instruções Detalhadas", expanded=True):
        st.markdown("""   
        ### Estrutura Requerida da Planilha

        Envie um arquivo Excel **.xlsx** com **três abas**:

        1. **`textos_selecionados`**  
           - Coleção de textos para normalização
           - Colunas obrigatórias: `id` e `textos selecionados`

        2. **`dic_palavras_compostas`**  
           - Dicionário de palavras compostas
           - Colunas: `Palavra composta` e `Palavra normalizada`

        3. **`dic_siglas`**  
           - Dicionário de siglas
           - Colunas: `Sigla` e `Significado`
        """)

    # Botões para download (mantido original)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
                st.download_button(
                    label="📥 Baixar modelo de planilha",
                    data=exemplo,
                    file_name="gerar_corpus_iramuteq.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        with col2:
            with open("textos_selecionados.xlsx", "rb") as textos:
                st.download_button(
                    label="📥 Baixar textos para análise",
                    data=textos,
                    file_name="textos_selecionados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

    file = st.file_uploader("Envie sua planilha preenchida", type=["xlsx"])

    # Funções auxiliares ORIGINAIS (sem alterações)
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
                return palabra

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

        estatisticas = f"Textos processados: {total_textos}\n"
        estatisticas += f"Siglas removidas/substituídas: {total_siglas}\n"
        estatisticas += f"Palavras compostas substituídas: {total_compostos}\n"
        estatisticas += f"Caracteres especiais removidos: {total_remocoes}\n"
        for char, nome in caracteres_especiais.items():
            if contagem_caracteres[char] > 0:
                estatisticas += f" - {nome} ({char}) : {contagem_caracteres[char]}\n"

        return corpus_final, estatisticas

    if file:
        try:
            xls = pd.ExcelFile(file)
            df_textos = xls.parse("textos_selecionados")
            df_compostos = xls.parse("dic_palavras_compostas")
            df_siglas = xls.parse("dic_siglas")
            df_textos.columns = [col.strip().lower() for col in df_textos.columns]

            if st.button("🚀 GERAR CORPUS TEXTUAL", type="primary"):
                corpus, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas)

                if corpus.strip():
                    st.success("Corpus gerado com sucesso!")

                    # Exibição organizada dos resultados
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("📄 Corpus Textual Gerado")
                        st.text_area("Pré-visualização do corpus", corpus[:2000] + ("..." if len(corpus) > 2000 else ""), height=300)

                        buf = io.BytesIO()
                        buf.write(corpus.encode("utf-8"))
                        st.download_button(
                            "📄 BAIXAR CORPUS TEXTUAL", 
                            data=buf.getvalue(), 
                            file_name="corpus_IRaMuTeQ.txt", 
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col2:
                        st.subheader("📊 Estatísticas")
                        st.text_area("Métricas de processamento", estatisticas, height=300)
                else:
                    st.warning("Nenhum texto processado. Verifique os dados da planilha.")

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")

# Rodapé profissional
st.markdown("""
    <div class="footer">
        <h4>👨‍💻 Sobre o Autor</h4>
        <p><strong>José Wendel dos Santos</strong><br>
        Pesquisador | Universidade Federal de Sergipe (UFS)<br>
        📧 <a href="mailto:eng.wendel@gmail.com">eng.wendel@gmail.com</a></p>
    </div>
""", unsafe_allow_html=True)
