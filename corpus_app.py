import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n
from collections import Counter

# Carregar o modelo spaCy
try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    st.error("Modelo spaCy 'pt_core_news_sm' não encontrado. Instale com:")
    st.code("python -m spacy download pt_core_news_sm")
    st.stop()

# Função para converter números por extenso
def converter_numeros_por_extenso(texto):
    unidades = {"zero":0, "um":1, "dois":2, "três":3, "quatro":4, "cinco":5,
                "seis":6, "sete":7, "oito":8, "nove":9}
    dezenas = {"dez":10, "vinte":20, "trinta":30, "quarenta":40, "cinquenta":50}
    centenas = {"cem":100, "duzentos":200, "trezentos":300}
    
    palavras = texto.split()
    resultado = []
    for palavra in palavras:
        palavra = palavra.lower()
        if palavra in unidades:
            resultado.append(str(unidades[palavra]))
        elif palavra in dezenas:
            resultado.append(str(dezenas[palavra]))
        elif palavra in centenas:
            resultado.append(str(centenas[palavra]))
        else:
            try:
                resultado.append(str(w2n.word_to_num(palavra)))
            except:
                resultado.append(palavra)
    return " ".join(resultado)

# Função principal para gerar o corpus
def gerar_corpus(df_textos, df_compostos, df_siglas):
    # Dicionários para substituição
    dict_compostos = dict(zip(df_compostos['Palavra composta'].str.lower(),
                            df_compostos['Palavra normalizada'].str.lower()))
    
    dict_siglas = dict(zip(df_siglas['Sigla'].str.lower(),
                         df_siglas['Significado'].str.lower()))

    corpus = ""
    stats = {
        "textos_processados": 0,
        "siglas_substituidas": 0,
        "compostos_substituidos": 0
    }

    for _, row in df_textos.iterrows():
        texto = str(row['textos selecionados'])
        if not texto.strip():
            continue

        # Processamento do texto
        texto = texto.lower()
        texto = converter_numeros_por_extenso(texto)
        
        # Substitui palavras compostas
        for original, substituto in dict_compostos.items():
            if original in texto:
                texto = texto.replace(original, substituto)
                stats["compostos_substituidos"] += 1
                
        # Substitui siglas
        for sigla, significado in dict_siglas.items():
            if sigla in texto:
                texto = texto.replace(sigla, significado)
                stats["siglas_substituidas"] += 1

        # Adiciona metadados
        metadata = f"**** *ID_{row['id']}"
        for col in row.index:
            if col not in ['id', 'textos selecionados']:
                metadata += f" *{col}_{row[col]}"
        
        corpus += f"{metadata}\n{texto}\n"
        stats["textos_processados"] += 1

    return corpus, stats

# Funções para detecção
def detectar_siglas(texto):
    return sorted(set(re.findall(r"\b[A-Z]{2,}\b", texto)))

def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    compostas = set()
    
    # Detecta entidades nomeadas
    for ent in doc.ents:
        if len(ent.text.split()) > 1:
            compostas.add(ent.text)
    
    # Detecta sequências capitalizadas
    for match in re.finditer(r"([A-Z][a-záéíóúâêôãõç]+(?:\s+[A-Z][a-záéíóúâêôãõç]+)+)", texto):
        compostas.add(match.group())
    
    return sorted(compostas)

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de corpus textual para IRaMuTeQ")

# Seção de pré-análise
st.markdown("## 🔍 Pré-análise de texto (opcional)")
texto = st.text_area("Cole seu texto aqui", height=150)
if st.button("Analisar"):
    if texto:
        siglas = detectar_siglas(texto)
        compostas = detectar_palavras_compostas(texto)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Palavras compostas detectadas**")
            for item in compostas:
                st.write(f"- {item}")
        
        with col2:
            st.write("**Siglas detectadas**")
            for item in siglas:
                st.write(f"- {item}")

# Seção principal
st.markdown("## 📌 Envie sua planilha completa")
uploaded_file = st.file_uploader("Selecione o arquivo Excel", type=["xlsx"])
if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        df_textos = xls.parse("textos_selecionados")
        df_compostos = xls.parse("dic_palavras_compostas")
        df_siglas = xls.parse("dic_siglas")
        
        if st.button("Gerar Corpus"):
            corpus, stats = gerar_corpus(df_textos, df_compostos, df_siglas)
            st.success("Corpus gerado com sucesso!")
            
            # Mostrar estatísticas
            st.write(f"Textos processados: {stats['textos_processados']}")
            st.write(f"Siglas substituídas: {stats['siglas_substituidas']}")
            st.write(f"Palavras compostas substituídas: {stats['compostos_substituidos']}")
            
            # Botão para download
            st.download_button(
                "Baixar Corpus",
                corpus,
                "corpus_iramuteq.txt",
                "text/plain"
            )
            
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")

# Rodapé
st.markdown("---")
st.markdown("**Autor:** José Wendel dos Santos | **Contato:** eng.wendel@gmail.com")
