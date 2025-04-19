import streamlit as st
import pandas as pd
import re
import io
from word2number import w2n

# Função para detectar palavras compostas e siglas
def detectar_palavras_compostas(texto, dict_compostos):
    palavras_compostas_detectadas = []
    for termo in dict_compostos:
        if termo in texto:
            palavras_compostas_detectadas.append(termo)
    return palavras_compostas_detectadas

def detectar_siglas(texto, dict_siglas):
    siglas_detectadas = []
    for sigla in dict_siglas:
        if sigla in texto:
            siglas_detectadas.append(sigla)
    return siglas_detectadas

# Função para exibir os resultados de palavras compostas e siglas
def exibir_resultados(palavras_compostas, siglas):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔤 Palavras Compostas Detectadas")
        if palavras_compostas:
            st.write(", ".join(palavras_compostas))
        else:
            st.write("Nenhuma palavra composta detectada.")
    
    with col2:
        st.subheader("🔤 Siglas Detectadas")
        if siglas:
            st.write(", ".join(siglas))
        else:
            st.write("Nenhuma sigla detectada.")

# Função para processar os textos e gerar o corpus
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

    # Processamento de texto
    total_textos = 0
    corpus_final = ""
    for _, row in df_textos.iterrows():
        texto = str(row.get("textos selecionados", ""))
        if not texto.strip():
            continue
        texto_corrigido = texto.lower()

        # Detectando palavras compostas e siglas
        palavras_compostas_detectadas = detectar_palavras_compostas(texto_corrigido, dict_compostos)
        siglas_detectadas = detectar_siglas(texto_corrigido, dict_siglas)

        # Exibindo os resultados
        exibir_resultados(palavras_compostas_detectadas, siglas_detectadas)

        # Normalizando o texto conforme a tabela
        for sigla, significado in dict_siglas.items():
            texto_corrigido = re.sub(rf"\b{sigla}\b", significado, texto_corrigido, flags=re.IGNORECASE)

        for termo, substituto in dict_compostos.items():
            texto_corrigido = re.sub(rf"\b{termo}\b", substituto, texto_corrigido, flags=re.IGNORECASE)

        # Adicionando ao corpus final
        total_textos += 1
        corpus_final += f"{texto_corrigido}\n"

    return corpus_final

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de corpus textual para IRaMuTeQ")

st.markdown("""### 📌 Instruções
Esta ferramenta foi desenvolvida para facilitar a geração de corpus textual compatível com o IRaMuTeQ.

1. Insira o seu texto na caixa abaixo e o sistema irá detectar palavras compostas e siglas.
2. Revise os resultados apresentados e, após preencher a tabela, faça o upload da planilha para gerar o corpus.
""")

# Caixa para o usuário inserir o texto
texto_usuario = st.text_area("📄 Insira o seu texto aqui:", height=200)

# Processar o texto inserido
if texto_usuario:
    # Exemplo de dicionário de palavras compostas e siglas para teste
    dict_compostos = {
        "mestre de obras": "mestre-de-obras",
        "engenheiro civil": "engenheiro-civil"
    }
    
    dict_siglas = {
        "ufse": "Universidade Federal de Sergipe",
        "usa": "United States of America"
    }

    # Detectando palavras compostas e siglas no texto
    palavras_compostas_detectadas = detectar_palavras_compostas(texto_usuario.lower(), dict_compostos)
    siglas_detectadas = detectar_siglas(texto_usuario.lower(), dict_siglas)

    # Exibindo os resultados
    exibir_resultados(palavras_compostas_detectadas, siglas_detectadas)

# Upload de planilha para gerar o corpus
file = st.file_uploader("Envie sua planilha preenchida", type=["xlsx"])

if file:
    try:
        xls = pd.ExcelFile(file)
        df_textos = xls.parse("textos_selecionados")
        df_compostos = xls.parse("dic_palavras_compostas")
        df_siglas = xls.parse("dic_siglas")
        df_textos.columns = [col.strip().lower() for col in df_textos.columns]

        if st.button("🚀 GERAR CORPUS TEXTUAL"):
            corpus = gerar_corpus(df_textos, df_compostos, df_siglas)

            if corpus.strip():
                st.success("Corpus gerado com sucesso!")
                buf = io.BytesIO()
                buf.write(corpus.encode("utf-8"))
                st.download_button("📄 BAIXAR CORPUS TEXTUAL", data=buf.getvalue(), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")
            else:
                st.warning("Nenhum texto processado. Verifique os dados da planilha.")
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
