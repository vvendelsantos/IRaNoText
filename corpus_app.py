import streamlit as st
import pandas as pd
import re
import io
from word2number import w2n
import spacy

# Carrega modelo spaCy para português
try:
    nlp = spacy.load("pt_core_news_lg")
except:
    nlp = None

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

# Funções para pré-processamento de texto
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

# Detecção de siglas
def detectar_siglas(texto):
    siglas = re.findall(r'\b[A-Z]{2,}\b', texto)
    return list(set(siglas))

# Detecção de palavras compostas com NLP + regex
def detectar_palavras_compostas(texto):
    compostas = set()
    if nlp:
        doc = nlp(texto)
        for ent in doc.ents:
            if len(ent.text.split()) >= 2 and not ent.text.isupper():
                compostas.add(ent.text.strip())
    regex_compostas = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+|[A-Za-z]+-[A-Za-z]+)\b', texto)
    regex_compostas = [p for p in regex_compostas if len(p.split()) > 1]
    compostas.update(regex_compostas)
    return list(sorted(compostas))

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Analisador de Texto - Detecção de Siglas e Palavras Compostas")

texto_input = st.text_area("✍️ Insira um texto para análise:", height=200)
if st.button("🔎 Analisar Texto") and texto_input.strip():
    siglas = detectar_siglas(texto_input)
    compostas = detectar_palavras_compostas(texto_input)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔍 Siglas Detectadas:")
        for s in siglas:
            st.markdown(f"- {s}")
    with col2:
        st.markdown("#### 🔍 Palavras Compostas Detectadas:")
        for c in compostas:
            st.markdown(f"- {c}")

st.markdown("""
---
👨‍🏫 **Sobre o autor**

**Autor:** José Wendel dos Santos  
**Instituição:** Universidade Federal de Sergipe (UFS)  
**Contato:** eng.wendel@gmail.com
""")
