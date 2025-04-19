import streamlit as st
import pandas as pd
import re
import io
from word2number import w2n

# Função para converter números por extenso para algarismos
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

# Função para detectar siglas
def detectar_siglas(texto, dict_siglas):
    siglas_detectadas = []
    for sigla, significado in dict_siglas.items():
        if sigla in texto.lower():
            siglas_detectadas.append((sigla, significado))
    return siglas_detectadas

# Função para detectar palavras compostas
def detectar_palavras_compostas(texto, dict_compostos):
    compostos_detectados = []
    for termo, substituto in dict_compostos.items():
        if termo in texto.lower():
            compostos_detectados.append((termo, substituto))
    return compostos_detectados

# Função principal de geração do corpus
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

    # Processamento e geração do corpus
    corpus_final = ""
    for _, row in df_textos.iterrows():
        texto = str(row.get("textos selecionados", ""))
        texto_corrigido = texto.lower()
        texto_corrigido = converter_numeros_por_extenso(texto_corrigido)
        
        # Detectar siglas e palavras compostas
        siglas_detectadas = detectar_siglas(texto_corrigido, dict_siglas)
        compostos_detectados = detectar_palavras_compostas(texto_corrigido, dict_compostos)

        for sigla, significado in siglas_detectadas:
            texto_corrigido = re.sub(rf"\b{sigla}\b", significado, texto_corrigido, flags=re.IGNORECASE)

        for termo, substituto in compostos_detectados:
            texto_corrigido = re.sub(rf"\b{termo}\b", substituto, texto_corrigido, flags=re.IGNORECASE)

        corpus_final += f"{texto_corrigido}\n"

    return corpus_final

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de Corpus Textual para IRaMuTeQ com Detecção de Siglas e Palavras Compostas")

# Instruções
st.markdown("""
### 📌 Instruções

Esta ferramenta foi desenvolvida para facilitar a geração de corpus textual compatível com o IRaMuTeQ. Através da detecção automática de siglas e palavras compostas, você pode melhorar a consistência do seu corpus.

1. **Insira o texto a ser analisado.**
2. **Detecte siglas e palavras compostas.**
3. **Faça o upload de uma planilha para gerar o corpus final.**

""")

# Caixa de texto para entrada do usuário
input_texto = st.text_area("🔎 Insira o texto para análise:", height=150)

# Detecção e exibição de siglas e palavras compostas
if input_texto:
    # Carregar planilhas
    file = st.file_uploader("Carregue a planilha com as siglas e palavras compostas", type=["xlsx"])
    if file:
        xls = pd.ExcelFile(file)
        df_compostos = xls.parse("dic_palavras_compostas")
        df_siglas = xls.parse("dic_siglas")
        
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

        # Detectar siglas e palavras compostas
        siglas_detectadas = detectar_siglas(input_texto.lower(), dict_siglas)
        compostos_detectados = detectar_palavras_compostas(input_texto.lower(), dict_compostos)

        st.subheader("🔍 Siglas detectadas:")
        st.write([f"{sigla} ({significado})" for sigla, significado in siglas_detectadas])

        st.subheader("🔍 Palavras compostas detectadas:")
        st.write([f"{termo} → {substituto}" for termo, substituto in compostos_detectados])

# Geração do corpus
if file:
    if st.button("🚀 GERAR CORPUS TEXTUAL"):
        corpus = gerar_corpus(pd.read_excel(file, sheet_name="textos_selecionados"), df_compostos, df_siglas)
        
        st.success("Corpus gerado com sucesso!")
        st.download_button("📄 Baixar Corpus Textual", data=corpus.encode("utf-8"), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")
