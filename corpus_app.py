import streamlit as st
import pandas as pd
import re
import spacy

# Carregar o modelo spaCy para NER
nlp = spacy.load("pt_core_news_sm")

# Função para detectar siglas
def detectar_siglas(texto):
    """
    Detecta siglas no texto. Siglas são sequências de letras maiúsculas (2 ou mais).
    """
    siglas = re.findall(r"\b[A-Z]{2,}\b", texto)
    return sorted(set(siglas))

# Função para detectar palavras compostas
def detectar_palavras_compostas(texto):
    """
    Detecta palavras compostas no texto. 
    Uma palavra composta é uma sequência de palavras onde cada palavra significativa 
    começa com letra maiúscula (exemplo: Inteligência Artificial, Universidade de Aveiro).
    """
    doc = nlp(texto)
    compostas = []

    # A função NER detecta entidades nomeadas como palavras compostas (exemplo: 'Universidade de Aveiro')
    for ent in doc.ents:
        if len(ent.text.split()) > 1:
            compostas.append(ent.text)

    return sorted(set(compostas))

# Função para gerar o corpus
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

        if not texto.strip():
            continue

        texto_corrigido = texto.lower()

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

        metadata = f"**** *ID_{row.get('id', '')}"
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

# Parte 1 - Análise de texto inserido pelo usuário
texto_input = st.text_area("Insira o texto a ser analisado:")

# Botão para iniciar a análise
if st.button("🔍 Analisar texto"):
    if texto_input.strip():
        siglas_detectadas = detectar_siglas(texto_input)
        palavras_compostas_detectadas = detectar_palavras_compostas(texto_input)

        # Exibir resultados lado a lado
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Siglas detectadas")
            st.write("\n".join(siglas_detectadas) if siglas_detectadas else "Nenhuma sigla detectada")

        with col2:
            st.subheader("Palavras compostas detectadas")
            st.write("\n".join(palavras_compostas_detectadas) if palavras_compostas_detectadas else "Nenhuma palavra composta detectada")
    else:
        st.warning("Por favor, insira um texto para análise.")

# Parte 2 - Upload da planilha e geração do corpus
uploaded_file = st.file_uploader("Faça upload da planilha de textos e palavras compostas", type=["csv", "xlsx"])

if uploaded_file:
    try:
        df_textos = pd.read_csv(uploaded_file, encoding='utf-8')  # Tente utf-8 primeiro
    except UnicodeDecodeError:
        df_textos = pd.read_csv(uploaded_file, encoding='latin1')  # Caso haja erro, tenta latin1
    
    df_compostos = pd.read_csv(uploaded_file)  # Leitura da planilha de palavras compostas
    df_siglas = pd.read_csv(uploaded_file)  # Leitura da planilha de siglas

    # Gerar o corpus
    corpus_final, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas)

    # Exibir o resultado
    st.subheader("Estatísticas do Corpus")
    st.write(estatisticas)

    st.subheader("Corpus Final")
    st.text_area("Texto final para o corpus:", corpus_final, height=300)

# Rodapé com informações sobre o autor
st.markdown("""
---
Criado por [Seu Nome](https://www.seu-portfolio.com) | Todos os direitos reservados.
""")
