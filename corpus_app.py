import streamlit as st
import pandas as pd
import re
from word2number import w2n

# Função para detectar siglas
def processar_siglas(texto, dic_siglas):
    siglas_detectadas = []
    for sigla, significado in dic_siglas.items():
        if re.search(rf"\b{sigla}\b", texto, flags=re.IGNORECASE):
            siglas_detectadas.append((sigla, significado))
            texto = re.sub(rf"\b{sigla}\b", significado, texto, flags=re.IGNORECASE)
    return texto, siglas_detectadas

# Função para sugerir palavras compostas
def sugerir_palavras_compostas(texto, dict_compostos):
    palavras = texto.split()
    palavras_compostas_detectadas = []
    for termo in dict_compostos:
        if termo in texto:
            palavras_compostas_detectadas.append(termo)
    return palavras_compostas_detectadas

# Função para processar o corpus
def gerar_corpus(df_textos, df_compostos, df_siglas, texto_inserido=None):
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

    # Se texto manual for inserido
    if texto_inserido:
        df_textos = pd.DataFrame({"textos selecionados": [texto_inserido]})

    corpus_final = ""
    siglas_detectadas = []
    palavras_compostas_detectadas = []

    for _, row in df_textos.iterrows():
        texto = str(row.get("textos selecionados", ""))
        if texto.strip():
            texto_corrigido = texto.lower()
            
            # Processa siglas
            texto_corrigido, siglas = processar_siglas(texto_corrigido, dict_siglas)
            siglas_detectadas.extend(siglas)
            
            # Processa palavras compostas
            palavras_compostas = sugerir_palavras_compostas(texto_corrigido, dict_compostos)
            palavras_compostas_detectadas.extend(palavras_compostas)

            # Adiciona o texto corrigido ao corpus
            corpus_final += texto_corrigido + "\n"
    
    return corpus_final, siglas_detectadas, palavras_compostas_detectadas

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de Corpus Textual para IRaMuTeQ")

st.markdown("""
### 📌 Instruções
Insira um arquivo Excel com 3 abas para processamento:
1. **textos_selecionados**: textos a serem processados.
2. **dic_palavras_compostas**: palavras compostas a serem normalizadas.
3. **dic_siglas**: siglas a serem expandidas.

Ou cole um texto diretamente na caixa abaixo para visualização.
""")

# Caixa para inserir texto manualmente
texto_manual = st.text_area("📋 Insira o texto para processamento (opcional):")

# Exemplo de download da planilha
with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
    st.download_button(
        label="📅 Baixar modelo de planilha",
        data=exemplo,
        file_name="gerar_corpus_iramuteq.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

file = st.file_uploader("Envie sua planilha preenchida", type=["xlsx"])

if file:
    try:
        xls = pd.ExcelFile(file)
        df_textos = xls.parse("textos_selecionados")
        df_compostos = xls.parse("dic_palavras_compostas")
        df_siglas = xls.parse("dic_siglas")

        df_textos.columns = [col.strip().lower() for col in df_textos.columns]

        if st.button("🚀 GERAR CORPUS TEXTUAL"):
            corpus, siglas_detectadas, palavras_compostas_detectadas = gerar_corpus(df_textos, df_compostos, df_siglas, texto_manual)

            if corpus.strip():
                st.success("Corpus gerado com sucesso!")

                st.text_area("📊 Corpus Gerado", corpus, height=250)

                # Exibe as siglas detectadas
                if siglas_detectadas:
                    st.write("### 💡 Siglas detectadas:")
                    for sigla, significado in siglas_detectadas:
                        st.write(f"{sigla} -> {significado}")

                # Exibe as palavras compostas detectadas
                if palavras_compostas_detectadas:
                    st.write("### 💡 Palavras compostas detectadas:")
                    for termo in palavras_compostas_detectadas:
                        st.write(termo)

                st.download_button("📄 BAIXAR CORPUS TEXTUAL", data=corpus.encode("utf-8"), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")
            else:
                st.warning("Nenhum texto processado. Verifique os dados da planilha.")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
