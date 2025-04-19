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

# Função para gerar o corpus a partir do texto processado
def generate_corpus(compound_words, acronyms, df_textos, df_compostos, df_siglas):
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

    corpus = []
    for _, row in df_textos.iterrows():
        texto = str(row.get("textos selecionados", ""))
        if texto.strip():
            texto_corrigido = texto.lower()
            texto_corrigido = converter_numeros_por_extenso(texto_corrigido)
            texto_corrigido = processar_palavras_com_se(texto_corrigido)
            texto_corrigido = processar_pronomes_pospostos(texto_corrigido)

            # Substitui siglas e palavras compostas
            for sigla, significado in dict_siglas.items():
                texto_corrigido = re.sub(rf"\b{sigla}\b", significado, texto_corrigido, flags=re.IGNORECASE)

            for termo, substituto in dict_compostos.items():
                if termo in texto_corrigido:
                    texto_corrigido = re.sub(rf"\b{termo}\b", substituto, texto_corrigido, flags=re.IGNORECASE)

            # Exibição de sugestões de siglas e palavras compostas
            compound_words, acronyms = process_text(texto)
            show_suggestions(compound_words, acronyms)

            corpus.append(texto_corrigido)

    return "\n".join(corpus)

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de corpus textual para IRaMuTeQ")

st.markdown("""### 📌 Instruções
Envie um arquivo do Excel **.xlsx** com as abas necessárias para gerar o corpus automaticamente:
1. **textos_selecionados** : coleção de textos a serem processados.
2. **dic_palavras_compostas** : dicionário de palavras compostas.
3. **dic_siglas** : dicionário de siglas.
""")

file = st.file_uploader("Envie sua planilha preenchida", type=["xlsx"])

if file:
    try:
        xls = pd.ExcelFile(file)
        df_textos = xls.parse("textos_selecionados")
        df_compostos = xls.parse("dic_palavras_compostas")
        df_siglas = xls.parse("dic_siglas")
        
        if st.button("🚀 GERAR CORPUS TEXTUAL"):
            corpus = generate_corpus(df_textos, df_compostos, df_siglas)

            st.text_area("📊 Corpus Gerado", corpus, height=250)

            buf = io.BytesIO()
            buf.write(corpus.encode("utf-8"))
            st.download_button("📄 BAIXAR CORPUS TEXTUAL", data=buf.getvalue(), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
