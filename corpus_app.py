import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n

# Carregar modelo do spaCy
nlp = spacy.load("pt_core_news_lg")

# Funções auxiliares
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
    return re.sub(r"(\b\w+)-se\b", r"se \\1", texto)

def processar_pronomes_pospostos(texto):
    texto = re.sub(r'\b(\w+)-se\b', r'se \1', texto)
    texto = re.sub(r'\b(\w+)-([oa]s?)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)-(lhe|lhes)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)-(me|te|nos|vos)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)[áéíóúâêô]?-([oa]s?)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)[áéíóúâêô]-(lo|la|los|las)-ia\b', r'\2 \1ia', texto)
    return texto

def gerar_corpus(df_textos, df_entidades, df_siglas):
    dict_entidades = {row["Entidades nomeadas"].lower(): row["Palavra normalizada"].lower()
                      for _, row in df_entidades.iterrows() if pd.notna(row["Entidades nomeadas"])}
    dict_siglas = {row["Sigla"].lower(): row["Significado"]
                   for _, row in df_siglas.iterrows() if pd.notna(row["Sigla"])}

    caracteres_especiais = {"-": "Hífen", ";": "Ponto e vírgula", '"': "Aspas duplas",
                            "'": "Aspas simples", "…": "Reticências", "–": "Travessão",
                            "(": "Parêntese esquerdo", ")": "Parêntese direito",
                            "/": "Barra", "%": "Porcentagem"}
    contagem_caracteres = {k: 0 for k in caracteres_especiais}

    corpus_final = ""
    for _, row in df_textos.iterrows():
        texto = str(row["textos selecionados"])
        id_val = row.get("id", "")

        texto_corrigido = texto.lower()
        texto_corrigido = converter_numeros_por_extenso(texto_corrigido)
        texto_corrigido = processar_palavras_com_se(texto_corrigido)
        texto_corrigido = processar_pronomes_pospostos(texto_corrigido)

        for sigla, significado in dict_siglas.items():
            texto_corrigido = re.sub(rf"\\({sigla}\\)", "", texto_corrigido)
            texto_corrigido = re.sub(rf"\\b{sigla}\\b", significado, texto_corrigido, flags=re.IGNORECASE)

        for termo, substituto in dict_entidades.items():
            texto_corrigido = re.sub(rf"\\b{termo}\\b", substituto, texto_corrigido, flags=re.IGNORECASE)

        for char in caracteres_especiais:
            count = texto_corrigido.count(char)
            if count:
                texto_corrigido = texto_corrigido.replace(char, "_" if char != "%" else "_por_cento")
                contagem_caracteres[char] += count

        texto_corrigido = re.sub(r"\s+", " ", texto_corrigido.strip())

        metadata = f"**** *ID_{id_val}"
        for col in row.index:
            if col.lower() not in ["id", "textos selecionados"]:
                metadata += f" *{col.replace(' ', '_')}_{str(row[col]).replace(' ', '_')}"

        corpus_final += f"{metadata}\n{texto_corrigido}\n"

    return corpus_final

# ========== INTERFACE ==========
st.title("IRaText: Gerador de Corpus Textual")
tabs = st.tabs(["📝 ANÁLISE PRELIMINAR", "🛠️ GERAÇÃO DO CORPUS"])

with tabs[0]:
    st.subheader("Digite o texto para análise preliminar")
    texto = st.text_area("Texto de entrada", height=200)
    if st.button("🔍 Analisar texto"):
        siglas = detectar_siglas(texto)
        compostas = detectar_palavras_compostas(texto)
        st.write("### Siglas detectadas:", siglas)
        st.write("### Entidades nomeadas:", compostas)

with tabs[1]:
    st.subheader("Preencha os dados para gerar o corpus")

    with st.expander("📋 Textos selecionados"):
        df_textos = st.experimental_data_editor(pd.DataFrame(columns=["id", "textos selecionados"]), num_rows="dynamic")

    with st.expander("🧠 Dicionário de entidades nomeadas"):
        df_entidades = st.experimental_data_editor(pd.DataFrame(columns=["Entidades nomeadas", "Palavra normalizada"]), num_rows="dynamic")

    with st.expander("🔠 Dicionário de siglas"):
        df_siglas = st.experimental_data_editor(pd.DataFrame(columns=["Sigla", "Significado"]), num_rows="dynamic")

    if st.button("🚀 Gerar Corpus"):
        corpus = gerar_corpus(df_textos, df_entidades, df_siglas)
        st.text_area("Corpus Gerado", corpus, height=300)

        buf = io.BytesIO()
        buf.write(corpus.encode("utf-8"))
        st.download_button("💾 Baixar Corpus", data=buf.getvalue(), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")
