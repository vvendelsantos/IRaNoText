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
st.title("IRaText: Geração de Corpus Textual para IRaMuTeQ")

tabs = st.tabs(["📝 Análise preliminar dos textos", "🛠️ Normalização do corpus textual"])

with tabs[0]:
    # ========================== PARTE 1 - PRÉ-ANÁLISE ==========================
    st.header("Detecção de Siglas e Palavras Compostas")

    texto_input = st.text_area("📌 Insira um texto para pré-análise", height=200)

    if st.button("🔍 Analisar texto"):
        if texto_input.strip():
            siglas = detectar_siglas(texto_input)
            compostas = detectar_palavras_compostas(texto_input)

            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("### 🕵️‍♂️ Palavras compostas detectadas")
                if compostas:
                    for termo in compostas:
                        st.write(f"- {termo}")
                else:
                    st.info("Nenhuma palavra composta encontrada.")

            with col2:
                st.markdown("### 🔠 Siglas Detectadas")
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

    # Exibir as instruções na sidebar
    st.sidebar.markdown("""   
    ### 📌 Instruções

    Esta ferramenta foi desenvolvida para facilitar a geração de corpus textual compatível com o IRaMuTeQ.

    Envie um arquivo do Excel **.xlsx** com a estrutura correta para que o corpus possa ser gerado automaticamente.

    Sua planilha deve conter **três abas (planilhas internas)** com os seguintes nomes e finalidades:

    1. **`textos_selecionados`** : coleção de textos que serão transformados de acordo com as regras de normalização.  
    2. **`dic_palavras_compostas`** : permite substituir palavras compostas por suas formas normalizadas, garantindo uma maior consistência no corpus textual gerado.  
    3. **`dic_siglas`** : tem a finalidade de expandir siglas para suas formas completas, aumentando a legibilidade e a clareza do texto.
    """)

    # Botões para download
    with st.container():
        col1, col2 = st.columns([1, 1])
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
                if col not in ["id", "textos selecionados"]:
                    texto_corrigido += f" *** {col}: {row[col]}"

            corpus_final += f"{metadata} {texto_corrigido}\n\n"

        return corpus_final, contagem_caracteres, total_textos, total_siglas, total_compostos, total_remocoes

    if file is not None:
        try:
            df = pd.read_excel(file, sheet_name=None)
            df_textos = df.get("textos_selecionados", pd.DataFrame())
            df_compostos = df.get("dic_palavras_compostas", pd.DataFrame())
            df_siglas = df.get("dic_siglas", pd.DataFrame())
            corpus_final, contagem_caracteres, total_textos, total_siglas, total_compostos, total_remocoes = gerar_corpus(
                df_textos, df_compostos, df_siglas)

            st.markdown("### Resultado do Corpus Gerado")
            st.write(corpus_final)
            st.download_button(
                label="Baixar Corpus Gerado",
                data=corpus_final,
                file_name="corpus_textual_iramuteq.txt",
                mime="text/plain",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")

# Rodapé
st.markdown("""
    <style>
        footer { 
            visibility: hidden; 
        }
    </style>
    <footer>
        👨‍🏫 **Sobre o autor**<br>
        **Autor:** José Wendel dos Santos<br>
        **Instituição:** Universidade Federal de Sergipe (UFS)<br>
        **Contato:** eng.wendel@gmail.com
    </footer>
""", unsafe_allow_html=True)
