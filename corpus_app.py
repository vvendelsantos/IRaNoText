import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n

# Carregar modelo do spaCy
nlp = spacy.load("pt_core_news_sm")

# Funções da parte 1
def detectar_siglas(texto):
    tokens = re.findall(r"\b[A-Z]{2,}\b", texto)
    return sorted(set(tokens))

def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    compostas = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return list(set(compostas))

# ========================== CONFIGURAÇÃO DA PÁGINA ==========================
st.set_page_config(
    page_title="Analisador e Gerador de Corpus IRaMuTeQ",
    page_icon="📊",
    layout="wide"
)

# ========================== CSS PERSONALIZADO ==========================
st.markdown("""
<style>
    .stTextArea textarea {
        min-height: 200px;
    }
    .stDownloadButton, .stButton>button {
        width: 100%;
        border-radius: 5px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stDownloadButton:hover, .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 5px 5px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f0f2f6;
    }
    .stMarkdown h3 {
        border-bottom: 1px solid #e1e4e8;
        padding-bottom: 8px;
    }
    .footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #e1e4e8;
        font-size: 0.9rem;
        color: #555;
    }
    .info-box {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ========================== LAYOUT COM ABAS ==========================
st.title("🔎 Analisador e Gerador de Corpus para IRaMuTeQ")

aba1, aba2 = st.tabs(["📄 Pré-Análise de Texto", "📂 Geração de Corpus"])

# ========================== ABA 1 - PRÉ-ANÁLISE ==========================
with aba1:
    st.header("Analisador de Texto")
    st.markdown("Detecção de siglas e palavras compostas para preparação de textos")

    with st.container():
        texto_input = st.text_area(
            "✍️ Insira o texto para análise",
            placeholder="Cole ou digite o texto que deseja analisar aqui...",
            help="O texto será analisado para identificar siglas (ex: UFS) e palavras compostas (ex: ensino superior)"
        )

        if st.button("🔍 Analisar Texto", type="primary"):
            if texto_input.strip():
                with st.spinner("Processando texto..."):
                    siglas = detectar_siglas(texto_input)
                    compostas = detectar_palavras_compostas(texto_input)

                col1, col2 = st.columns(2, gap="large")
                with col1:
                    st.subheader("🧩 Palavras Compostas Detectadas")
                    if compostas:
                        st.dataframe(
                            pd.DataFrame(compostas, columns=["Termo"]),
                            hide_index=True,
                            use_container_width=True
                        )
                    else:
                        st.info("ℹ️ Nenhuma palavra composta encontrada.", icon="ℹ️")

                with col2:
                    st.subheader("🧾 Siglas Detectadas")
                    if siglas:
                        st.dataframe(
                            pd.DataFrame(siglas, columns=["Sigla"]),
                            hide_index=True,
                            use_container_width=True
                        )
                    else:
                        st.info("ℹ️ Nenhuma sigla encontrada.", icon="ℹ️")
            else:
                st.warning("⚠️ Por favor, insira um texto antes de analisar.", icon="⚠️")

# ========================== ABA 2 - GERAÇÃO DE CORPUS ==========================
with aba2:
    st.header("Gerador de Corpus Textual")
    st.markdown("Transformação de dados para compatibilidade com o software IRaMuTeQ")

    with st.expander("📌 Instruções Detalhadas", expanded=True):
        st.markdown("""
        ### Estrutura da Planilha Requerida

        Para gerar o corpus corretamente, seu arquivo Excel (.xlsx) deve conter **três planilhas** com os seguintes nomes:

        1. **`textos_selecionados`**  
           - Coleção de textos para normalização  
           - Deve conter coluna `id` e `textos selecionados`  
           - Pode incluir metadados adicionais

        2. **`dic_palavras_compostas`**  
           - Mapeamento de palavras compostas para formas normalizadas  
           - Colunas: `Palavra composta` | `Palavra normalizada`

        3. **`dic_siglas`**  
           - Expansão de siglas para formas completas  
           - Colunas: `Sigla` | `Significado`
        """)

    col1, col2 = st.columns([3, 1], gap="medium")
    with col1:
        file = st.file_uploader(
            "📤 Envie sua planilha Excel preenchida",
            type=["xlsx"],
            help="Arquivo deve seguir a estrutura descrita nas instruções"
        )
    with col2:
        with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
            st.download_button(
                label="📥 Baixar Modelo de Planilha",
                data=exemplo,
                file_name="modelo_corpus_iramuteq.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Baixe o modelo para preencher com seus dados"
            )

    # Funções auxiliares da parte 2 (mantidas iguais)
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

        estatisticas = f"📊 Estatísticas de Processamento\n\n"
        estatisticas += f"• Textos processados: {total_textos}\n"
        estatisticas += f"• Siglas substituídas: {total_siglas}\n"
        estatisticas += f"• Palavras compostas normalizadas: {total_compostos}\n"
        estatisticas += f"• Caracteres especiais tratados: {total_remocoes}\n\n"
        estatisticas += "🔍 Detalhe de caracteres especiais:\n"
        for char, nome in caracteres_especiais.items():
            if contagem_caracteres[char] > 0:
                estatisticas += f" - {nome} ({char}): {contagem_caracteres[char]}\n"

        return corpus_final, estatisticas

    if file:
        try:
            with st.spinner("Processando planilha..."):
                xls = pd.ExcelFile(file)
                df_textos = xls.parse("textos_selecionados")
                df_compostos = xls.parse("dic_palavras_compostas")
                df_siglas = xls.parse("dic_siglas")
                df_textos.columns = [col.strip().lower() for col in df_textos.columns]

            if st.button("🚀 Gerar Corpus Textual", type="primary"):
                with st.spinner("Gerando corpus..."):
                    corpus, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas)

                if corpus.strip():
                    st.success("✅ Corpus gerado com sucesso!")
                    
                    tab1, tab2 = st.tabs(["📋 Visualizar Corpus", "📈 Estatísticas"])
                    
                    with tab1:
                        st.code(corpus, language="text")
                    
                    with tab2:
                        st.text(estatisticas)

                    buf = io.BytesIO()
                    buf.write(corpus.encode("utf-8"))
                    st.download_button(
                        "💾 Baixar Corpus",
                        data=buf.getvalue(),
                        file_name="corpus_iramuteq.txt",
                        mime="text/plain",
                        help="Baixe o arquivo de texto formatado para uso no IRaMuTeQ"
                    )
                else:
                    st.error("❌ Nenhum texto válido encontrado na planilha. Verifique os dados.")

        except Exception as e:
            st.error(f"❌ Erro no processamento: {str(e)}")
            st.info("Verifique se a planilha segue exatamente a estrutura requerida.")

# ========================== RODAPÉ ==========================
st.markdown("""
<div class="footer">
    <p><strong>👨‍💻 Sobre o Autor</strong></p>
    <p><strong>Autor:</strong> José Wendel dos Santos</p>
    <p><strong>Instituição:</strong> Universidade Federal de Sergipe (UFS)</p>
    <p><strong>Contato:</strong> eng.wendel@gmail.com</p>
</div>
""", unsafe_allow_html=True)
