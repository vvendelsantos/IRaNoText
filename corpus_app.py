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
st.set_page_config(page_title="IRaText: Geração de Corpus Textual para IRaMuTeQ", layout="wide")
st.title("IRaText: Geração de Corpus Textual para IRaMuTeQ")

tabs = st.tabs(["📝 Análise preliminar dos textos", "🛠️ Normalização do corpus textual"])

# ========================== ABAS ESTILIZADAS ==========================
with tabs[0]:
    # ========================== PARTE 1 - PRÉ-ANÁLISE ==========================
    st.header("Detecção de Siglas e Palavras Compostas")

    texto_input = st.text_area("📌 Insira um texto para pré-análise", height=200, help="Digite ou cole o texto que deseja analisar.")

    if st.button("🔍 Analisar texto"):
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

    # Botões para download com estilo
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

    # Função para gerar corpus e estatísticas (sem alterações)

    if file:
        try:
            xls = pd.ExcelFile(file)
            df_textos = xls.parse("textos_selecionados")
            df_compostos = xls.parse("dic_palavras_compostas")
            df_siglas = xls.parse("dic_siglas")
            df_textos.columns = [col.strip().lower() for col in df_textos.columns]

            if st.button("🚀 GERAR CORPUS TEXTUAL"):
                corpus, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas)

                if corpus.strip():
                    st.success("Corpus gerado com sucesso!")

                    # Nova aba para mostrar o corpus antes do download
                    st.subheader("📄 Corpus Textual Gerado")
                    st.text_area("Veja o corpus gerado antes de baixar", corpus, height=300)

                    st.text_area("📊 Estatísticas do processamento", estatisticas, height=250)

                    buf = io.BytesIO()
                    buf.write(corpus.encode("utf-8"))
                    st.download_button("📄 BAIXAR CORPUS TEXTUAL", data=buf.getvalue(), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")
                else:
                    st.warning("Nenhum corpus gerado.")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")

# Rodapé com estilo
st.markdown("""  
---  
👨‍🏫 **Sobre o autor**  

**Autor:** José Wendel dos Santos  
**Instituição:** Universidade Federal de Sergipe (UFS)  
**Contato:** eng.wendel@gmail.com
""", unsafe_allow_html=True)


st.markdown("""  
---  
👨‍🏫 **Sobre o autor**  

**Autor:** José Wendel dos Santos  
**Instituição:** Universidade Federal de Sergipe (UFS)  
**Contato:** eng.wendel@gmail.com
""")
