import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

nlp = spacy.load("pt_core_news_lg")

# ========================== FUNÇÕES GERAIS ==========================

def detectar_siglas(texto):
    tokens = re.findall(r"\b[A-Z]{2,}\b", texto)
    return sorted(set(tokens))

def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    compostas = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return list(set(compostas))

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

def gerar_corpus(df_textos, df_entidades, df_siglas):
    dict_entidades = {
        str(row["Entidades nomeadas"]).lower(): str(row["Palavra normalizada"]).lower()
        for _, row in df_entidades.iterrows()
        if pd.notna(row["Entidades nomeadas"]) and pd.notna(row["Palavra normalizada"])
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
    total_entidades = 0
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

        for termo, substituto in dict_entidades.items():
            if termo in texto_corrigido:
                texto_corrigido = re.sub(rf"\b{termo}\b", substituto, texto_corrigido, flags=re.IGNORECASE)
                total_entidades += 1

        for char in caracteres_especiais:
            count = texto_corrigido.count(char)
            if count:
                if char == "%":
                    texto_corrigido = texto_corrigido.replace(char, "_por_cento")
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
    estatisticas += f"Entidades nomeadas substituídas: {total_entidades}\n"
    estatisticas += f"Caracteres especiais removidos: {total_remocoes}\n"
    for char, nome in caracteres_especiais.items():
        if contagem_caracteres[char] > 0:
            estatisticas += f" - {nome} ({char}) : {contagem_caracteres[char]}\n"

    return corpus_final, estatisticas

def gerar_nuvem_palavras(textos):
    texto_concatenado = " ".join(textos).lower()
    palavras = re.findall(r"\b\w+\b", texto_concatenado)
    frequencias = Counter(palavras)
    nuvem = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(frequencias)
    return nuvem, frequencias

# ========================== INTERFACE ==========================

st.set_page_config(page_title="IRaText", layout="wide")
st.title("IRaText: Gerador de Corpus Textual")

abas = st.tabs(["📝 ANÁLISE PRELIMINAR DOS TEXTOS", "🛠️ GERAÇÃO DO CORPUS TEXTUAL", "📊 EXPLORAÇÃO LEXICAL"])

# ========================== ABA 1 ==========================
with abas[0]:
    texto_input = st.text_area("Insira aqui os textos para análise:", height=250)
    if st.button("🔍 Analisar textos"):
        if texto_input.strip():
            siglas = detectar_siglas(texto_input)
            compostas = detectar_palavras_compostas(texto_input)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🕵️‍♂️ Entidades Nomeadas")
                st.text_area("Copie e cole no Excel", "\n".join(compostas), height=250)
            with col2:
                st.markdown("### 🔠 Siglas detectadas")
                st.text_area("Copie e cole no Excel", "\n".join(siglas), height=250)
        else:
            st.warning("Por favor, insira um texto.")

# ========================== ABA 2 ==========================
with abas[1]:
    st.sidebar.markdown("# ℹ️ Sobre a ferramenta [...]")
    file = st.file_uploader("Envie sua planilha preenchida", type=["xlsx"])
    if file:
        try:
            xls = pd.ExcelFile(file)
            df_textos = xls.parse("textos_selecionados")
            df_entidades = xls.parse("dic_entidades_nomeadas")
            df_siglas = xls.parse("dic_siglas")
            df_textos.columns = [col.strip().lower() for col in df_textos.columns]

            if st.button("🚀 GERAR CORPUS TEXTUAL"):
                corpus, estatisticas = gerar_corpus(df_textos, df_entidades, df_siglas)
                st.success("Corpus gerado com sucesso!")
                st.text_area("📄 Corpus", corpus, height=300)
                st.text_area("📊 Estatísticas", estatisticas, height=250)
                buf = io.BytesIO()
                buf.write(corpus.encode("utf-8"))
                st.download_button("💾 SALVAR CORPUS", data=buf.getvalue(), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")
        except Exception as e:
            st.error(f"Erro ao processar: {e}")

# ========================== ABA 3 ==========================
with abas[2]:
    st.markdown("## 🔍 Visualização Exploratória de Palavras")
    arquivo_explorar = st.file_uploader("Envie uma planilha com a aba 'textos_selecionados'", type=["xlsx"], key="explorar")
    if arquivo_explorar:
        try:
            df_explorar = pd.read_excel(arquivo_explorar, sheet_name="textos_selecionados")
            col_texto = st.selectbox("Coluna com os textos:", df_explorar.columns)
            textos = df_explorar[col_texto].dropna().astype(str).tolist()

            nuvem, freq = gerar_nuvem_palavras(textos)

            st.markdown("### ☁️ Nuvem de Palavras")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(nuvem, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)

            st.markdown("### 📊 Palavras mais frequentes")
            top_n = st.slider("Quantas palavras exibir?", 5, 30, 10)
            top_palavras = freq.most_common(top_n)
            st.bar_chart(pd.DataFrame(top_palavras, columns=["Palavra", "Frequência"]).set_index("Palavra"))
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")

# ========================== RODAPÉ ==========================
st.markdown("""---  
👨‍💻 **Autor:** José Wendel dos Santos  
🏛️ **Instituição:** Universidade Federal de Sergipe (UFS)  
📧 **Contato:** eng.wendel@gmail.com  
""")
