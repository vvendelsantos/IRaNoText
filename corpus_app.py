import streamlit as st
import re
import pandas as pd
import io
from word2number import w2n

# Função para exibir as sugestões de palavras compostas e siglas com opção de cópia
def show_suggestions(compound_words, acronyms):
    # Exibição das sugestões de palavras compostas
    st.markdown("### 🔹 Sugestões de palavras compostas:")
    for i, word in enumerate(compound_words):
        st.write(f"🔹 [{word['start']} - {word['end']}]: {word['phrase']}")
    
    # Caixa de texto para copiar as palavras compostas
    st.text_area("Copiar Sugestões de Palavras Compostas", value="\n".join([f"[{word['start']} - {word['end']}]: {word['phrase']}" for word in compound_words]), height=200)

    # Exibição das siglas detectadas
    st.markdown("### 🔹 Siglas detectadas no texto:")
    for i, acronym in enumerate(acronyms):
        st.write(f"🔹 {acronym}")
    
    # Caixa de texto para copiar as siglas
    st.text_area("Copiar Siglas Detectadas", value="\n".join(acronyms), height=100)

# Função para processar o texto e identificar palavras compostas e siglas
def process_text(text):
    # Definindo padrões para palavras compostas e siglas
    compound_word_pattern = re.compile(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b')  # Exemplo de palavras compostas
    acronym_pattern = re.compile(r'\b[A-Z]{2,}\b')  # Exemplo de siglas (todas em maiúsculas)

    compound_words = []
    acronyms = []

    # Encontrando palavras compostas
    for match in compound_word_pattern.finditer(text):
        compound_words.append({'start': match.start(), 'end': match.end(), 'phrase': match.group()})

    # Encontrando siglas
    acronyms = acronym_pattern.findall(text)

    return compound_words, acronyms

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

# Função para processar palavras compostas com "-se"
def processar_palavras_com_se(texto):
    return re.sub(r"(\b\w+)-se\b", r"se \1", texto)

# Função para processar pronomes oblíquos pós-verbais
def processar_pronomes_pospostos(texto):
    texto = re.sub(r'\b(\w+)-se\b', r'se \1', texto)
    texto = re.sub(r'\b(\w+)-([oa]s?)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)-(lhe|lhes)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)-(me|te|nos|vos)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)[áéíóúâêô]?-([oa]s?)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)[áéíóúâêô]-(lo|la|los|las)-ia\b', r'\2 \1ia', texto)
    return texto

# Função principal
def main():
    st.title("Analisador de Texto - Geração de Corpus")

    # Carregar arquivo de texto
    uploaded_file = st.file_uploader("Escolha um arquivo de texto para gerar o corpus", type="txt")

    # Se um arquivo for enviado
    if uploaded_file is not None:
        text = uploaded_file.getvalue().decode("utf-8")
        
        # Processa o texto para identificar palavras compostas e siglas
        compound_words, acronyms = process_text(text)
        
        # Exibe as sugestões na interface
        show_suggestions(compound_words, acronyms)

        # Gerar o texto com as modificações de números por extenso, palavras compostas e pronomes
        text = converter_numeros_por_extenso(text)
        text = processar_palavras_com_se(text)
        text = processar_pronomes_pospostos(text)

        # Exibe o texto final
        st.text_area("Texto Processado", value=text, height=200)

if __name__ == "__main__":
    main()
