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

# ========================== ABAS ==========================
st.set_page_config(page_title="IRaText: Geração de Corpus Textual", layout="wide")
st.title("IRaText: Geração de Corpus Textual")

tabs = st.radio("Escolha a seção", ["📝 Análise preliminar dos textos", "🛠️ Normalização do corpus textual"])

# ========================== Análise Preliminar ==========================
if tabs == "📝 Análise preliminar dos textos":
    st.header("Análise Preliminar")
    texto_input = st.text_area("Insira o texto para análise", height=250)

    if st.button("🔍 Analisar textos"):
        if texto_input.strip():
            siglas = detectar_siglas(texto_input)
            compostas = detectar_palavras_compostas(texto_input)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🕵️‍♂️ Reconhecimento de Entidades Nomeadas (REN)")
                if compostas:
                    st.text_area("Copie e cole no Excel", "\n".join(sorted(compostas)), height=250)
                else:
                    st.info("Nenhuma palavra composta encontrada.")

            with col2:
                st.markdown("### 🔠 Siglas detectadas")
                if siglas:
                    st.text_area("Copie e cole no Excel", "\n".join(sorted(siglas)), height=250)
                else:
                    st.info("Nenhuma sigla encontrada.")
        else:
            st.warning("Por favor, insira um texto antes de analisar.")

# ========================== Normalização do Corpus ==========================
if tabs == "🛠️ Normalização do corpus textual":
    st.header("Normalização do Corpus Textual")
    
    st.sidebar.markdown("""   
    ### 📌 Como usar a ferramenta

    1. **Análise preliminar dos textos:** Insira um texto na caixa de entrada e a ferramenta fará uma varredura para detectar siglas e palavras compostas, exibindo os resultados.
    2. **Geração do corpus textual:** Após analisar os textos, você pode iniciar o processo de normalização e geração do seu corpus textual.
    
    ⚠️ Sua planilha deve conter **três abas** com os seguintes nomes:
    - `textos_selecionados`: textos que serão normalizados e processados.
    - `dic_palavras_compostas`: palavras compostas e suas formas normalizadas.
    - `dic_siglas`: lista de siglas e seus significados.
    """)
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
                st.download_button(
                    label="📥 Baixar modelo de planilha",
                    data=exemplo,
                    file_name="gerar_corpus_iramuteq.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        with col2:
            with open("textos_selecionados.xlsx", "rb") as textos:
                st.download_button(
                    label="📥 Baixar textos para análise",
                    data=textos,
                    file_name="textos_selecionados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    file = st.file_uploader("Envie sua planilha preenchida", type=["xlsx"])

    if file:
        try:
            xls = pd.ExcelFile(file)
            df_textos = xls.parse("textos_selecionados")
            df_compostos = xls.parse("dic_palavras_compostas")
            df_siglas = xls.parse("dic_siglas")
            df_textos.columns = [col.strip().lower() for col in df_textos.columns]

            # Feedback visual de carregamento da planilha
            st.success("Planilha carregada com sucesso!")

            if st.button("🚀 GERAR CORPUS TEXTUAL"):
                with st.spinner("Processando..."):
                    corpus, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas)

                    if corpus.strip():
                        st.success("Corpus gerado com sucesso!")

                        st.subheader("📄 Corpus Textual Gerado")
                        st.text_area("Veja o corpus gerado antes de baixar", corpus, height=300)
                        st.text_area("📊 Estatísticas do processamento", estatisticas, height=250)

                        buf = io.BytesIO()
                        buf.write(corpus.encode("utf-8"))
                        st.download_button("💾 SALVAR CORPUS TEXTUAL", data=buf.getvalue(), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")
                    else:
                        st.warning("Nenhum corpus gerado.")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
    
# Funções auxiliares para geração de corpus
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

        corpus_final += f"Texto {id_val}: {texto_corrigido}\n"

    estatisticas = f"""Total de textos processados: {total_textos}
Total de siglas substituídas: {total_siglas}
Total de palavras compostas substituídas: {total_compostos}
Total de caracteres especiais removidos: {total_remocoes}
"""
    return corpus_final, estatisticas
