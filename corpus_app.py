import streamlit as st
import pandas as pd
import re
import io
import spacy
from collections import Counter
from itertools import tee
from word2number import w2n

# Funcoes de processamento

def converter_numeros_por_extenso(texto):
    unidades = {"zero": 0, "dois": 2, "duas": 2, "três": 3, "quatro": 4, "cinco": 5,
                "seis": 6, "sete": 7, "oito": 8, "nove": 9}
    dezenas = {"dez": 10, "onze": 11, "doze": 12, "treze": 13, "quatorze": 14, "quinze": 15,
               "dezesseis": 16, "dezessete": 17, "dezoito": 18, "dezenove": 19, "vinte": 20}
    centenas = {"cem": 100, "cento": 100, "duzentos": 200, "trezentos": 300, "quatrocentos": 400,
               "quinhentos": 500, "seiscentos": 600, "setecentos": 700, "oitocentos": 800, "novecentos": 900}
    multiplicadores = {"mil": 1000, "milhão": 1000000, "milhões": 1000000,
                       "bilhão": 1000000000, "bilhões": 1000000000}

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

def processar_palavras_com_se(texto):
    return re.sub(r"(\b\w+)-se\b", r"se ", texto)

def processar_pronomes_pospostos(texto):
    texto = re.sub(r'\b(\w+)-se\b', r'se ', texto)
    texto = re.sub(r'\b(\w+)-([oa]s?)\b', r' ', texto)
    texto = re.sub(r'\b(\w+)-(lhe|lhes)\b', r' ', texto)
    texto = re.sub(r'\b(\w+)-(me|te|nos|vos)\b', r' ', texto)
    texto = re.sub(r'\b(\w+)[áéíóúâêô]?-([oa]s?)\b', r' ', texto)
    texto = re.sub(r'\b(\w+)[áéíóúâêô]-(lo|la|los|las)-ia\b', r' ia', texto)
    return texto

def gerar_corpus(df_textos, df_compostos, df_siglas):
    dict_compostos = {str(row["Palavra composta"]).lower(): str(row["Palavra normalizada"]).lower()
                      for _, row in df_compostos.iterrows()
                      if pd.notna(row["Palavra composta"]) and pd.notna(row["Palavra normalizada"])}

    dict_siglas = {str(row["Sigla"]).lower(): str(row["Significado"])
                   for _, row in df_siglas.iterrows()
                   if pd.notna(row["Sigla"]) and pd.notna(row["Significado"])}

    caracteres_especiais = {"-": "Hífen", ";": "Ponto e vírgula", '"': "Aspas duplas", "'": "Aspas simples",
                            "…": "Reticências", "–": "Travessão", "(": "Parêntese esquerdo", ")": "Parêntese direito",
                            "/": "Barra", "%": "Porcentagem"}
    contagem_caracteres = {k: 0 for k in caracteres_especiais}
    total_textos, total_siglas, total_compostos, total_remocoes = 0, 0, 0, 0
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
            texto_corrigido = re.sub(rf"\\({sigla}\\)", "", texto_corrigido)
            texto_corrigido = re.sub(rf"\\b{sigla}\\b", significado, texto_corrigido, flags=re.IGNORECASE)
            total_siglas += 1

        for termo, substituto in dict_compostos.items():
            if termo in texto_corrigido:
                texto_corrigido = re.sub(rf"\\b{termo}\\b", substituto, texto_corrigido, flags=re.IGNORECASE)
                total_compostos += 1

        for char in caracteres_especiais:
            count = texto_corrigido.count(char)
            if count:
                texto_corrigido = texto_corrigido.replace(char, "" if char == "%" else "_")
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

# Layout
st.set_page_config(layout="wide")
st.title("Gerador de corpus textual para IRaMuTeQ")

st.markdown("### ✨ Análise preliminar de texto (opcional)")
texto_colado = st.text_area("Cole um texto para detectar palavras compostas e siglas automaticamente:", height=200)

if texto_colado.strip():
    nlp = spacy.load("pt_core_news_sm")
    doc = nlp(texto_colado.lower())
    stopwords_ignorar = {"de", "do", "da", "dos", "das", "a", "o", "e", "em", "para", "por", "com", "no", "na", "nos", "nas"}

    def gerar_ngrams(tokens, n):
        iters = tee(tokens, n)
        for i, it in enumerate(iters):
            for _ in range(i):
                next(it, None)
        return zip(*iters)

    tokens = [token.text for token in doc if not token.is_punct and not token.is_space]
    bigramas = [" ".join(grama) for grama in gerar_ngrams(tokens, 2)
                if all(pal not in stopwords_ignorar for pal in grama)]
    trigramas = [" ".join(grama) for grama in gerar_ngrams(tokens, 3)
                 if all(pal not in stopwords_ignorar for pal in grama)]

    termos_contagem = Counter(bigramas + trigramas)
    sugestoes_compostas = [termo for termo, freq in termos_contagem.items() if freq > 1]

    siglas_maiuculas = set(re.findall(r"\\b[A-Z]{2,}\b", texto_colado))
    siglas_parenteses = set(re.findall(r"\\(([^()]{2,10})\\)", texto_colado))
    sugestoes_siglas = sorted(siglas_maiuculas.union(siglas_parenteses))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔹 Palavras compostas sugeridas:")
        st.write(", ".join(sugestoes_compostas) if sugestoes_compostas else "Nenhuma encontrada.")
    with col2:
        st.markdown("#### 🔹 Siglas detectadas:")
        st.write(", ".join(sugestoes_siglas) if sugestoes_siglas else "Nenhuma encontrada.")

st.markdown("---")
st.markdown("""
### 📆 Envio da planilha e geração do corpus textual

Sua planilha deve conter **três abas (planilhas internas)**:

1. `textos_selecionados`
2. `dic_palavras_compostas`
3. `dic_siglas`
""")

with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
    st.download_button("📅 Baixar modelo de planilha", data=exemplo, file_name="gerar_corpus_iramuteq.xlsx")

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

st.markdown("---")
st.markdown("""
**Autor:** José Wendel dos Santos  
**Instituição:** Universidade Federal de Sergipe (UFS)  
**Contato:** eng.wendel@gmail.com
""")
