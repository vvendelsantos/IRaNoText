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

# Funções de detecção de siglas e palavras compostas
def detectar_siglas(texto, dic_siglas):
    siglas_detectadas = []
    for sigla, significado in dic_siglas.items():
        if sigla in texto:
            siglas_detectadas.append((sigla, significado))
    return siglas_detectadas

def detectar_palavras_compostas(texto, dic_compostos):
    compostos_detectados = []
    for termo, substituto in dic_compostos.items():
        if termo in texto:
            compostos_detectados.append((termo, substituto))
    return compostos_detectados

# Função principal para gerar o corpus
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

    caracteres_especiais = {
        "-": "Hífen", ";": "Ponto e vírgula", '"': "Aspas duplas", "'": "Aspas simples",
        "…": "Reticências", "–": "Travessão", "(": "Parêntese esquerdo", ")": "Parêntese direito",
        "/": "Barra", "%": "Porcentagem"
    }
    contagem_caracteres = {k: 0 for k in caracteres_especiais}
    total_textos = 0
    total_siglas = 0
    total_compostos = 0
    total_remocoes = 0
    corpus_final = ""

    for _, row in df_textos.iterrows():
        texto = str(row.get("textos selecionados", ""))
        id_val = row.get("id", "")
        if not texto.strip():
            continue

        texto_corrigido = texto.lower()
        texto_corrigido = converter_numeros_por_extenso(texto_corrigido)
        texto_corrigido = processar_palavras_com_se(texto_corrigido)
        texto_corrigido = processar_pronomes_pospostos(texto_corrigido)
        total_textos += 1

        for sigla, significado in dict_siglas.items():
            texto_corrigido = re.sub(rf"\({sigla}\)", "", texto_corrigido)
            texto_corrigido = re.sub(rf"\b{sigla}\b", significado, texto_corrigido, flags=re.IGNORECASE)
            total_siglas += 1

        for termo, substituto in dict_compostos.items():
            if termo in texto_corrigido:
                texto_corrigido = re.sub(rf"\b{termo}\b", substituto, texto_corrigido, flags=re.IGNORECASE)
                total_compostos += 1

        for char in caracteres_especiais:
            count = texto_corrigido.count(char)
            if count:
                if char == "%":
                    texto_corrigido = texto_corrigido.replace(char, "")
                else:
                    texto_corrigido = texto_corrigido.replace(char, "_")
                contagem_caracteres[char] += count
                total_remocoes += count

        texto_corrigido = re.sub(r"\s+", " ", texto_corrigido.strip())

        metadata = f"**** *ID_{id_val}"
        for col in row.index:
            if col.lower() not in ["id", "textos selecionados"]:
                metadata += f" *{col.replace(' ', '_')}_{str(row[col]).replace(' ', '_')}"

        corpus_final += f"{metadata}\n{texto_corrigido}\n"

    estatisticas = f"Textos processados: {total_textos}\n"
    estatisticas += f"Siglas removidas/substituídas: {total_siglas}\n"
    estatisticas += f"Palavras compostas substituídas: {total_compostos}\n"
    estatisticas += f"Caracteres especiais removidos: {total_remocoes}\n"
    for char, nome in caracteres_especiais.items():
        if contagem_caracteres[char] > 0:
            estatisticas += f" - {nome} ({char}) : {contagem_caracteres[char]}\n"

    return corpus_final, estatisticas

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de corpus textual para IRaMuTeQ")

st.markdown("""
### 📌 Instruções

Esta ferramenta foi desenvolvida para facilitar a geração de corpus textual compatível com o IRaMuTeQ.

Envie um arquivo do Excel **.xlsx** com a estrutura correta para que o corpus possa ser gerado automaticamente.

Sua planilha deve conter **três abas (planilhas internas)** com os seguintes nomes e finalidades:

1. **`textos_selecionados`** : coleção de textos que serão transformados de acordo com as regras de normalização.  
2. **`dic_palavras_compostas`** : permite substituir palavras compostas por suas formas normalizadas, garantindo uma maior consistência no corpus textual gerado.  
3. **`dic_siglas`** : tem a finalidade de expandir siglas para suas formas completas, aumentando a legibilidade e a clareza do texto.
""")

with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
    st.download_button(
        label="📅 Baixar modelo de planilha",
        data=exemplo,
        file_name="gerar_corpus_iramuteq.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

file = st.file_uploader("Envie sua planilha preenchida", type=["xlsx"])

input_texto = st.text_area("📋 Insira o texto para análise:", height=200)

# Detecção de siglas e palavras compostas
if file is not None and input_texto:
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

    if st.button("🔍 Analisar Texto"):
        siglas_detectadas = detectar_siglas(input_texto.lower(), dict_siglas)
        compostos_detectados = detectar_palavras_compostas(input_texto.lower(), dict_compostos)

        st.subheader("🔍 Siglas detectadas:")
        st.write([f"{sigla} ({significado})" for sigla, significado in siglas_detectadas])

        st.subheader("🔍 Palavras compostas detectadas:")
        st.write([f"{termo} → {substituto}" for termo, substituto in compostos_detectados])

# Geração do corpus
if file is not None:
    if st.button("🚀 GERAR CORPUS TEXTUAL"):
        corpus, estatisticas = gerar_corpus(pd.read_excel(file, sheet_name="textos_selecionados"), df_compostos, df_siglas)
        
        st.success("Corpus gerado com sucesso!")
        st.text_area("📊 Estatísticas do processamento", estatisticas, height=250)

        buf = io.BytesIO()
        buf.write(corpus.encode("utf-8"))
        st.download_button("📄 Baixar Corpus Textual", data=buf.getvalue(), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")

st.markdown("""
---
👨‍🏫 **Sobre o autor**

**Autor:** José Wendel dos Santos  
**Instituição:** Universidade Federal de Sergipe (UFS)  
**Contato:** eng.wendel@gmail.com
""")
