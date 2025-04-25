import pandas as pd
import numpy as np
from collections import Counter
import spacy
import gensim
from gensim import corpora
from gensim.models import LdaModel
import streamlit as st

# Carregar o modelo spaCy
nlp = spacy.load('pt_core_news_sm')

# Função de Normalização de Dados e Correção Automática
def normalizar_dados(textos):
    for texto in textos:
        # Normalizar texto, converter para minúsculas, remoção de stopwords, etc.
        doc = nlp(texto["texto"])
        texto["texto_normalizado"] = " ".join([token.text.lower() for token in doc if not token.is_stop and not token.is_punct])
    return textos

# Função para visualizar as palavras mais frequentes
def visualizar_frequencias(textos):
    palavras = " ".join([texto["texto"] for texto in textos]).split()
    frequencias = Counter(palavras)
    df_frequencias = pd.DataFrame(frequencias.items(), columns=["Palavra", "Frequência"])
    df_frequencias = df_frequencias.sort_values(by="Frequência", ascending=False)
    st.dataframe(df_frequencias)

# Função de Análise de Concordância (Coocorrência de Palavras)
def analisar_concordancia(texto, palavra_chave):
    doc = nlp(texto)
    concordancia = []
    for token in doc:
        if token.text.lower() == palavra_chave.lower():
            contexto = [neighbor.text for neighbor in token.subtree if neighbor.text != palavra_chave]
            concordancia.append(" ".join(contexto))
    return concordancia

# Função de Extração de Temas e Tópicos
def extrair_topicos(textos, num_topicos=5):
    textos_processados = [texto["texto"].split() for texto in textos]
    dicionario = corpora.Dictionary(textos_processados)
    corpus = [dicionario.doc2bow(texto) for texto in textos_processados]
    lda = LdaModel(corpus, num_topics=num_topicos, id2word=dicionario)
    topicos = lda.print_topics()
    return topicos

# Função para gerar Matriz de Coocorrência de Palavras
def matriz_coocorrencia(textos):
    palavras = " ".join([texto["texto"] for texto in textos]).split()
    palavras_unicas = list(set(palavras))
    coocorrencia = np.zeros((len(palavras_unicas), len(palavras_unicas)))
    palavra_to_index = {palavra: idx for idx, palavra in enumerate(palavras_unicas)}

    for texto in textos:
        doc = nlp(texto["texto"])
        for token1 in doc:
            for token2 in doc:
                if token1 != token2:
                    idx1, idx2 = palavra_to_index[token1.text], palavra_to_index[token2.text]
                    coocorrencia[idx1][idx2] += 1

    df_coocorrencia = pd.DataFrame(coocorrencia, index=palavras_unicas, columns=palavras_unicas)
    return df_coocorrencia

# Streamlit UI
st.title("Ferramenta de Análise de Textos para IRaMuTeQ")

# Carregar os textos para análise
uploaded_file = st.file_uploader("Carregar arquivo de texto", type=["txt", "csv", "docx"])

if uploaded_file is not None:
    if uploaded_file.type == "text/plain":
        textos = [{"texto": uploaded_file.read().decode()}]
    elif uploaded_file.type == "text/csv":
        df = pd.read_csv(uploaded_file)
        textos = [{"texto": str(row)} for row in df.iloc[:, 0]]
    else:
        # Função para processar .docx ou outros formatos (a ser implementada)
        pass

    # Aba 1: Normalização de Dados e Correção Automática
    with st.expander("1. Normalização de Dados e Correção Automática"):
        textos_normalizados = normalizar_dados(textos)
        st.write("Textos normalizados:", textos_normalizados)

    # Aba 2: Visualização de Frequências
    with st.expander("2. Visualização de Frequências"):
        visualizar_frequencias(textos)

    # Aba 3: Análise de Concordância, Extração de Temas e Tópicos, Matriz de Coocorrência
    with st.expander("3. Análise de Concordância (Concordância de Palavras), Extração de Temas e Tópicos, Matriz de Coocorrência de Palavras"):
        palavra_chave = st.text_input("Digite uma palavra-chave para análise de concordância")
        if palavra_chave:
            concordancia = analisar_concordancia(textos[0]["texto"], palavra_chave)
            st.write("Concordância encontrada:", concordancia)

        num_topicos = st.slider("Número de tópicos para extração:", 1, 10, 5)
        topicos = extrair_topicos(textos, num_topicos)
        st.write("Tópicos Extraídos:", topicos)

        coocorrencia = matriz_coocorrencia(textos)
        st.write("Matriz de Coocorrência de Palavras:", coocorrencia)
