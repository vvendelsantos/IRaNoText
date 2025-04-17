import streamlit as st
import pandas as pd
import re
import io

def replace_full_word(text, term, replacement):
    return re.sub(rf"\b{re.escape(term)}\b", replacement, text, flags=re.IGNORECASE)

def replace_with_pattern(text, pattern, replacement):
    return re.sub(pattern, replacement, text, flags=re.IGNORECASE)

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

    # padroniza nomes de colunas
    df_textos.columns = [col.lower().strip() for col in df_textos.columns]

    for _, row in df_textos.iterrows():
        texto = str(row.get("textos selecionados", ""))
        id_val = row.get("id", "")
        if not texto.strip():
            continue

        texto_corrigido = texto.lower()
        total_textos += 1

        for sigla, significado in dict_siglas.items():
            texto_corrigido = replace_with_pattern(texto_corrigido, rf"\({sigla}\)", "")
            texto_corrigido = replace_full_word(texto_corrigido, sigla, significado)
            total_siglas += 1

        for termo, substituto in dict_compostos.items():
            if termo in texto_corrigido:
                texto_corrigido = replace_full_word(texto_corrigido, termo, substituto)
                total_compostos += 1

        for char in caracteres_especiais:
            count = texto_corrigido.count(char)
            if count:
                texto_corrigido = texto_corrigido.replace(char, "_" if char == "/" else "")
                contagem_caracteres[char] += count
                total_remocoes += count

        texto_corrigido = re.sub(r"\s+", " ", texto_corrigido.strip())

        metadata = f"**** *ID_{id_val}"
        for col in row.index:
            if col not in ["id", "textos selecionados"]:
                metadata += f" *{col.replace(' ', '_')}_{str(row[col]).replace(' ', '_')}"

        corpus_final += f"{metadata}\n{texto_corrigido}\n"

    if not corpus_final:
        raise ValueError("Nenhum texto processado. Verifique os dados.")

    estatisticas = f"Textos processados: {total_textos}\n"
    estatisticas += f"Siglas removidas/substituídas: {total_siglas}\n"
    estatisticas += f"Palavras compostas substituídas: {total_compostos}\n"
    estatisticas += f"Caracteres especiais removidos: {total_remocoes}\n"
    for char, nome in caracteres_especiais.items():
        if contagem_caracteres[char] > 0:
            estatisticas += f" - {nome} ({char}) : {contagem_caracteres[char]}\n"

    return corpus_final, estatisticas

st.title("Gerador de Corpus IRaMuTeQ")

file = st.file_uploader("Envie o arquivo Excel com as abas 'textos_selecionados', 'dic_palavras_compostas' e 'dic_siglas'", type=["xlsx"])

if file:
    xls = pd.ExcelFile(file)
    try:
        df_textos = xls.parse("textos_selecionados")
        df_compostos = xls.parse("dic_palavras_compostas")
        df_siglas = xls.parse("dic_siglas")

        if st.button("Gerar Corpus"):
            corpus, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas)

            st.success("Corpus gerado com sucesso!")
            st.text_area("Estatísticas do processamento", estatisticas, height=200)

            buf = io.BytesIO()
            buf.write(corpus.encode("utf-8"))
            st.download_button("Baixar Corpus", data=buf.getvalue(), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
