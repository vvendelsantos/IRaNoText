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

# Função para sugerir palavras compostas e siglas
def detectar_palavras_compostas_e_siglas(texto, dict_compostos, dict_siglas):
    palavras_compostas_detectadas = []
    siglas_detectadas = []

    for termo, substituto in dict_compostos.items():
        if termo in texto:
            palavras_compostas_detectadas.append(f"{termo} → {substituto}")
    
    for sigla, significado in dict_siglas.items():
        if sigla in texto:
            siglas_detectadas.append(f"{sigla} → {significado}")

    return palavras_compostas_detectadas, siglas_detectadas

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

    return dict_compostos, dict_siglas

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de corpus textual para IRaMuTeQ")

# Campo de texto para inserção manual
texto_usuario = st.text_area("💬 Insira o texto a ser analisado:", height=300)

# Botão para análise
if st.button("🔍 Analisar"):
    if texto_usuario.strip():
        # Detectar siglas e palavras compostas
        dict_compostos, dict_siglas = gerar_corpus(pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
        palavras_compostas_detectadas, siglas_detectadas = detectar_palavras_compostas_e_siglas(texto_usuario, dict_compostos, dict_siglas)

        # Exibir resultados lado a lado
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔤 Sugestões de Palavras Compostas")
            if palavras_compostas_detectadas:
                st.write("\n".join(palavras_compostas_detectadas))
            else:
                st.write("Nenhuma palavra composta detectada.")

        with col2:
            st.subheader("🔤 Siglas Detectadas")
            if siglas_detectadas:
                st.write("\n".join(siglas_detectadas))
            else:
                st.write("Nenhuma sigla detectada.")
    else:
        st.warning("Por favor, insira um texto para análise.")

# Upload da planilha
st.markdown("""
### 📌 Instruções

Envie um arquivo do Excel **.xlsx** com a estrutura correta para que o corpus possa ser gerado automaticamente.
""")

file = st.file_uploader("Envie sua planilha preenchida", type=["xlsx"])

if file:
    try:
        xls = pd.ExcelFile(file)
        df_textos = xls.parse("textos_selecionados")
        df_compostos = xls.parse("dic_palavras_compostas")
        df_siglas = xls.parse("dic_siglas")
        df_textos.columns = [col.strip().lower() for col in df_textos.columns]

        if st.button("🚀 GERAR CORPUS TEXTUAL"):
            corpus, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas)

            if corpus.strip():
                st.success("Corpus gerado com sucesso!")
                st.text_area("📊 Estatísticas do processamento", estatisticas, height=250)

                buf = io.BytesIO()
                buf.write(corpus.encode("utf-8"))
                st.download_button("📄 BAIXAR CORPUS TEXTUAL", data=buf.getvalue(), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")
            else:
                st.warning("Nenhum texto processado. Verifique os dados da planilha.")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

st.markdown("""
---
👨‍🏫 **Sobre o autor**

**Autor:** José Wendel dos Santos  
**Instituição:** Universidade Federal de Sergipe (UFS)  
**Contato:** eng.wendel@gmail.com
""")
