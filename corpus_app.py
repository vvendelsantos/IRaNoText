import streamlit as st
import pandas as pd
import spacy
from word2number import w2n
import re

# Baixar o modelo spaCy de português
try:
    nlp = spacy.load('pt_core_news_sm')
except:
    spacy.cli.download('pt_core_news_sm')
    nlp = spacy.load('pt_core_news_sm')

# Função para sugerir palavras compostas
def sugerir_palavras_compostas(texto):
    # Tokenização com spaCy
    doc = nlp(texto)
    tokens = [token.text for token in doc]
    
    # Outras etapas de processamento de palavras compostas
    # Aqui você pode adicionar outras lógicas para detectar palavras compostas

    return tokens  # Retorna as palavras tokenizadas (ou compostas)

# Função para detectar e substituir números por extenso
def substituir_numeros(texto):
    try:
        texto = re.sub(r'\b(?:um|dois|três|quatro|cinco|seis|sete|oito|nove|dez)\b', lambda x: str(w2n.word_to_num(x.group())), texto)
    except ValueError:
        pass
    return texto

# Função principal
def main():
    st.title('App de Processamento de Texto')

    texto_inicial = st.text_area('Cole seu texto aqui:')
    if texto_inicial:
        compostas_sugeridas = sugerir_palavras_compostas(texto_inicial)
        st.write("Palavras compostas sugeridas:", compostas_sugeridas)

        texto_processado = substituir_numeros(texto_inicial)
        st.write("Texto após substituição de números por extenso:", texto_processado)

if __name__ == "__main__":
    main()
