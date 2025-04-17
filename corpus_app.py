import streamlit as st
import pandas as pd
import re
import io

# Funções para substituir palavras e expressões no texto
def replace_full_word(text, term, replacement):
    return re.sub(rf"\b{re.escape(term)}\b", replacement, text, flags=re.IGNORECASE)

def replace_with_pattern(text, pattern, replacement):
    return re.sub(pattern, replacement, text, flags=re.IGNORECASE)

# Função para gerar o corpus
def gerar_corpus(textos, compostos, siglas):
    dict_compostos = {
        str(composta).lower(): str(normalizada).lower()
        for composta, normalizada in compostos
    }

    dict_siglas = {
        str(sigla).lower(): str(significado)
        for sigla, significado in siglas
    }

    caracteres_especiais = {
        "-": "Hífen",
        ";": "Ponto e vírgula",
        '"': "Aspas duplas",
        "'": "Aspas simples",
        "…": "Reticências",
        "–": "Travessão",
        "(": "Parêntese esquerdo",
        ")": "Parêntese direito",
        "/": "Barra",
    }
    contagem_caracteres = {k: 0 for k in caracteres_especiais}

    total_textos = 0
    total_siglas = 0
    total_compostos = 0
    total_remocoes = 0

    corpus_final = ""

    for texto in textos:
        if not texto.strip():
            continue

        texto_corrigido = texto.lower()
        total_textos += 1

        # Substituindo siglas
        for sigla, significado in dict_siglas.items():
            texto_corrigido = replace_with_pattern(texto_corrigido, rf"\({sigla}\)", "")
            texto_corrigido = replace_full_word(texto_corrigido, sigla, significado)
            total_siglas += 1

        # Substituindo palavras compostas
        for termo, substituto in dict_compostos.items():
            if termo in texto_corrigido:
                texto_corrigido = replace_full_word(texto_corrigido, termo, substituto)
                total_compostos += 1

        # Removendo caracteres especiais
        for char in caracteres_especiais:
            count = texto_corrigido.count(char)
            if count:
                texto_corrigido = texto_corrigido.replace(char, "_" if char == "/" else "")
                contagem_caracteres[char] += count
                total_remocoes += count

        texto_corrigido = re.sub(r"\s+", " ", texto_corrigido.strip())

        corpus_final += f"{texto_corrigido}\n"

    estatisticas = f"Textos processados: {total_textos}\n"
    estatisticas += f"Siglas removidas/substituídas: {total_siglas}\n"
    estatisticas += f"Palavras compostas substituídas: {total_compostos}\n"
    estatisticas += f"Caracteres especiais removidos: {total_remocoes}\n"
    for char, nome in caracteres_especiais.items():
        if contagem_caracteres[char] > 0:
            estatisticas += f" - {nome} ({char}) : {contagem_caracteres[char]}\n"

    return corpus_final, estatisticas

# Interface Streamlit
st.title("Gerador de Corpus para IRaMuTeQ")

st.markdown("""
### 📌 Instruções

Preencha os campos abaixo com os dados necessários para gerar o corpus. Não é necessário baixar uma planilha, apenas insira as informações diretamente.

1. **Textos selecionados** – Adicione os textos a serem processados.
2. **Dicionário de palavras compostas** – Adicione as palavras compostas e suas normalizações.
3. **Dicionário de siglas** – Adicione as siglas e seus significados.
""")

# Entradas para os textos
num_textos = st.number_input("Quantos textos deseja adicionar?", min_value=1, max_value=10, step=1)

textos = []
for i in range(num_textos):
    texto = st.text_area(f"Texto {i + 1}", height=150)
    textos.append(texto)

# Entradas para palavras compostas
num_compostos = st.number_input("Quantas palavras compostas deseja adicionar?", min_value=1, max_value=10, step=1)

compostos = []
for i in range(num_compostos):
    composta = st.text_input(f"Palavra Composta {i + 1}", "")
    normalizada = st.text_input(f"Normalização {i + 1}", "")
    compostos.append([composta, normalizada])

# Entradas para siglas
num_siglas = st.number_input("Quantas siglas deseja adicionar?", min_value=1, max_value=10, step=1)

siglas = []
for i in range(num_siglas):
    sigla = st.text_input(f"Sigla {i + 1}", "")
    significado = st.text_input(f"Significado {i + 1}", "")
    siglas.append([sigla, significado])

# Gerar o corpus
if st.button("🚀 Gerar Corpus"):
    if textos and compostos and siglas:
        corpus, estatisticas = gerar_corpus(textos, compostos, siglas)

        if corpus.strip():
            st.success("Corpus gerado com sucesso!")
            st.text_area("📊 Estatísticas do processamento", estatisticas, height=250)

            buf = io.BytesIO()
            buf.write(corpus.encode("utf-8"))
            st.download_button("📄 Baixar Corpus", data=buf.getvalue(), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")
        else:
            st.warning("Nenhum texto processado. Verifique os dados.")
    else:
        st.warning("Preencha todos os campos antes de gerar o corpus.")
