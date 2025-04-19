import pandas as pd
import re
import streamlit as st
from collections import Counter
from nltk.util import ngrams
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

# Função para detectar siglas
def detectar_siglas(texto):
    palavras = re.findall(r'\b[A-Z]{2,}\b', texto)  # Detecta palavras com 2 ou mais letras maiúsculas
    return sorted(set(palavras))  # Retorna siglas únicas, sem duplicatas

# Função para gerar bigramas
def gerar_bigramas(texto):
    palavras = texto.split()  # Divide o texto em palavras
    bigramas = ngrams(palavras, 2)  # Cria bigramas (pares de palavras)
    return ["_".join(bi) for bi in bigramas]  # Une as palavras do bigrama com "_"

# Função para gerar trigramas
def gerar_trigramas(texto):
    palavras = texto.split()  # Divide o texto em palavras
    trigramas = ngrams(palavras, 3)  # Cria trigramas (sequências de 3 palavras)
    return ["_".join(tri) for tri in trigramas]  # Une as palavras do trigramas com "_"

# Função para processar pronomes oblíquos pós-verbais
def processar_pronomes_pospostos(texto):
    texto = re.sub(r'\b(\w+)-se\b', r'se \1', texto)
    texto = re.sub(r'\b(\w+)-([oa]s?)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)-(lhe|lhes)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)-(me|te|nos|vos)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)[áéíóúâêô]?-([oa]s?)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)[áéíóúâêô]-(lo|la|los|las)-ia\b', r'\2 \1ia', texto)
    return texto

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
                # Se o caractere for '%' não substituímos por '_', apenas removemos
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
        
        # Gerar bigramas e trigramas
        bigramas = gerar_bigramas(texto_corrigido)
        trigramas = gerar_trigramas(texto_corrigido)

        # Contagem de bigramas e trigramas
        bigramas_freq = Counter(bigramas)
        trigramas_freq = Counter(trigramas)

        corpus_final += f"{metadata}\n{texto_corrigido}\n"

    estatisticas = f"Textos processados: {total_textos}\n"
    estatisticas += f"Siglas removidas/substituídas: {total_siglas}\n"
    estatisticas += f"Palavras compostas substituídas: {total_compostos}\n"
    estatisticas += f"Caracteres especiais removidos: {total_remocoes}\n"
    for char, nome in caracteres_especiais.items():
        if contagem_caracteres[char] > 0:
            estatisticas += f" - {nome} ({char}) : {contagem_caracteres[char]}\n"

    return corpus_final, estatisticas, bigramas_freq, trigramas_freq

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de corpus textual para IRaMuTeQ")

st.markdown("""
### 📌 Instruções

Esta ferramenta foi desenvolvida para facilitar a geração de corpus textual compatível com o IRaMuTeQ.
""")

file = st.file_uploader("Carregue sua planilha (Excel ou CSV)", type=["xlsx", "csv"])

if file:
    df = pd.read_excel(file) if file.name.endswith("xlsx") else pd.read_csv(file)

    df_compostos = st.file_uploader("Carregue a planilha de palavras compostas", type=["xlsx", "csv"])
    df_siglas = st.file_uploader("Carregue a planilha de siglas", type=["xlsx", "csv"])

    if df_compostos and df_siglas:
        df_compostos = pd.read_excel(df_compostos) if df_compostos.name.endswith("xlsx") else pd.read_csv(df_compostos)
        df_siglas = pd.read_excel(df_siglas) if df_siglas.name.endswith("xlsx") else pd.read_csv(df_siglas)
        
        corpus, estatisticas, bigramas_freq, trigramas_freq = gerar_corpus(df, df_compostos, df_siglas)

        st.subheader("📊 Estatísticas de Processamento")
        st.text(estatisticas)

        st.subheader("📈 Bigramas")
        st.write(pd.DataFrame(bigramas_freq.most_common(), columns=["Bigramas", "Frequência"]))

        st.subheader("📈 Trigramas")
        st.write(pd.DataFrame(trigramas_freq.most_common(), columns=["Trigramas", "Frequência"]))

        st.subheader("📄 Corpus Final")
        st.text(corpus)
