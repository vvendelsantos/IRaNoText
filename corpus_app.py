import streamlit as st
import pandas as pd
import re
import io

# Função para detectar siglas
def detectar_siglas(texto):
    # Regex para encontrar siglas com 2 ou mais letras maiúsculas
    siglas = re.findall(r'\b[A-Z]{2,}\b', texto)
    return list(set(siglas))

# Função para detectar palavras compostas dinâmicas (termos compostos de múltiplas palavras)
def detectar_palavras_compostas(texto):
    # Regex para encontrar palavras compostas por mais de uma palavra separadas por espaços
    # Exemplo de padrões comuns como 'termo composto', 'expressão chave', etc.
    palavras_compostas = re.findall(r'\b(?:[A-Z][a-z]+(?: [a-z]+)+)\b', texto)

    # Retorna apenas as expressões encontradas (sem duplicados)
    return list(set(palavras_compostas))

# Função para processar palavras compostas com "-" e pronomes oblíquos pós-verbais
def processar_texto(texto):
    texto = re.sub(r"(\b\w+)-se\b", r"se \1", texto)  # Ajuste para palavras com '-se'
    texto = re.sub(r"\b(\w+)-([oa]s?)\b", r"\2 \1", texto)  # Ajuste para pronomes pós-verbais
    return texto

# Função para gerar o corpus conforme a planilha de entrada
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
        texto_corrigido = processar_texto(texto_corrigido)

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
st.title("Analisador de Texto - Detecção de Siglas e Palavras Compostas")

# Caixa de texto para o usuário inserir o texto
texto_usuario = st.text_area("📝 Insira o texto para análise", "", height=300)

# Botão para iniciar a análise
if st.button("🔍 Analisar Texto"):
    if texto_usuario.strip():
        # Detectando siglas e palavras compostas no texto
        siglas_detectadas = detectar_siglas(texto_usuario)
        palavras_compostas_detectadas = detectar_palavras_compostas(texto_usuario)

        # Exibindo resultados de forma bonita em listas
        st.subheader("🔤 Siglas Detectadas")
        if siglas_detectadas:
            st.write("- " + "\n- ".join(siglas_detectadas))
        else:
            st.write("Nenhuma sigla detectada.")

        st.subheader("🔤 Sugestões de Palavras Compostas")
        if palavras_compostas_detectadas:
            st.write("- " + "\n- ".join(palavras_compostas_detectadas))
        else:
            st.write("Nenhuma palavra composta detectada.")
    else:
        st.warning("Por favor, insira um texto para análise.")

# Upload da planilha para gerar o corpus
st.markdown("""---""")
st.subheader("📤 Envie sua planilha para gerar o corpus textual")
file = st.file_uploader("Envie sua planilha preenchida", type=["xlsx"])

if file:
    try:
        xls = pd.ExcelFile(file)
        df_textos = xls.parse("textos_selecionados")
        df_compostos = xls.parse("dic_palavras_compostas")
        df_siglas = xls.parse("dic_siglas")

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

# Texto do autor
st.markdown("""
---
👨‍🏫 **Sobre o autor**

**Autor:** José Wendel dos Santos  
**Instituição:** Universidade Federal de Sergipe (UFS)  
**Contato:** eng.wendel@gmail.com
""")
