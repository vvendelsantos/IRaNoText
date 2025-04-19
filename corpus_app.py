import streamlit as st
import pandas as pd
import re
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

# Função para sugerir palavras compostas
def sugerir_palavras_compostas(texto):
    stopwords = set(["de", "a", "o", "da", "na", "em", "para", "com", "que", "por", "e"])
    palavras = texto.split()
    compostas = []
    
    for i in range(len(palavras)-1):
        palavra1 = palavras[i]
        palavra2 = palavras[i+1]
        if palavra1 not in stopwords and palavra2 not in stopwords:
            compostas.append(f"{palavra1}_{palavra2}")
    
    return compostas

# Função para detectar siglas
def detectar_siglas(texto, siglas_dict):
    siglas_encontradas = []
    for sigla, significado in siglas_dict.items():
        if sigla.lower() in texto.lower():
            siglas_encontradas.append((sigla, significado))
    return siglas_encontradas

# Função principal
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

    corpus_final = ""
    for _, row in df_textos.iterrows():
        texto = str(row.get("textos selecionados", ""))
        if not texto.strip():
            continue

        texto_corrigido = texto.lower()
        texto_corrigido = converter_numeros_por_extenso(texto_corrigido)

        # Sugestão de palavras compostas
        palavras_compostas = sugerir_palavras_compostas(texto_corrigido)
        
        # Detecção de siglas
        siglas_detectadas = detectar_siglas(texto_corrigido, dict_siglas)

        corpus_final += f"Texto original:\n{texto}\n\nPalavras compostas sugeridas: {palavras_compostas}\n"
        corpus_final += f"Siglas detectadas: {siglas_detectadas}\n\n"

    return corpus_final

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de corpus textual para IRaMuTeQ")

st.markdown("""
### 📌 Instruções

Envie um texto e a ferramenta sugerirá possíveis palavras compostas e detectará siglas.

""")

# Caixa para o usuário colar o texto
texto_usuario = st.text_area("Cole seu texto aqui:")

if texto_usuario:
    palavras_compostas = sugerir_palavras_compostas(texto_usuario)
    siglas_detectadas = detectar_siglas(texto_usuario, {"IA": "Inteligência Artificial", "USP": "Universidade de São Paulo"})  # Exemplo de siglas
    
    st.write("### Palavras compostas sugeridas:")
    st.write(palavras_compostas)
    
    st.write("### Siglas detectadas:")
    st.write(siglas_detectadas)
