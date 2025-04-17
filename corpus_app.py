import streamlit as st
import pandas as pd
import re
import io
from word2number import w2n

def replace_full_word(text, term, replacement):
    return re.sub(rf"\b{re.escape(term)}\b", replacement, text, flags=re.IGNORECASE)

def replace_with_pattern(text, pattern, replacement):
    return re.sub(pattern, replacement, text, flags=re.IGNORECASE)

# Função para converter números por extenso para algarismos
def converter_numeros_por_extenso(texto):
    unidades = {
        "zero": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2, "três": 3, "quatro": 4, "cinco": 5,
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
    buffer = []

    def processar_buffer(buffer):
        try:
            return str(w2n.word_to_num(" ".join(buffer)))
        except:
            return " ".join(buffer)

    for palavra in palavras:
        palavra_lower = palavra.lower()

        # Verificar unidades
        if palavra_lower in unidades:
            resultado.append(str(unidades[palavra_lower]))
        # Verificar dezenas
        elif palavra_lower in dezenas:
            resultado.append(str(dezenas[palavra_lower]))
        # Verificar centenas
        elif palavra_lower in centenas:
            resultado.append(str(centenas[palavra_lower]))
        # Verificar multiplicadores
        elif palavra_lower in multiplicadores:
            resultado.append(str(multiplicadores[palavra_lower]))
        else:
            # Acumular palavras para processar juntas
            buffer.append(palavra)
            convertido = processar_buffer(buffer)
            if convertido != " ".join(buffer):  # Se conseguiu converter
                resultado.append(convertido)
                buffer = []  # Limpar buffer após conversão

    # Caso ainda tenha algo no buffer que não foi processado
    if buffer:
        resultado.append(" ".join(buffer))

    return " ".join(resultado)

# Função para processar palavras compostas com "-se" (ex: "notou-se")
def processar_palavras_com_se(texto):
    return re.sub(r"(\b\w+)-se\b", r"se \1", texto)

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
        "%": "Porcentagem"
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

# Interface
st.set_page_config(layout="wide")
st.title("Gerador de corpus textual para IRaMuTeQ")

st.markdown("""
### 📌 Instruções para uso da planilha

Envie um arquivo do Excel **.xlsx** com a estrutura correta para que o corpus possa ser gerado automaticamente.

Sua planilha deve conter **três abas (planilhas internas)** com os seguintes nomes e finalidades:

1. **`textos_selecionados`** – onde ficam os textos a serem processados.  
2. **`dic_palavras_compostas`** – dicionário de expressões compostas.  
3. **`dic_siglas`** – dicionário de siglas.
""")

with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
    st.download_button(
        label="📅 Baixar modelo de planilha",
        data=exemplo,
        file_name="gerar_corpus_iramuteq.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

file = st.file_uploader("Envie sua planilha preenchida", type=["xlsx"])

if file:
    try:
        xls = pd.ExcelFile(file)
        df_textos = xls.parse("textos_selecionados")
        df_compostos = xls.parse("dic_palavras_compostas")
        df_siglas = xls.parse("dic_siglas")

        # Padroniza nomes das colunas para evitar erros de maiúsculas/minúsculas
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

# Rodapé
st.markdown("""
---
👨‍🏫 **Sobre o autor**

**Autor:** José Wendel dos Santos  
**Instituição:** Universidade Federal de Sergipe (UFS)  
**Contato:** eng.wendel@live.com

Este aplicativo foi desenvolvido para fins educacionais e de apoio à análise textual no software **IRaMuTeQ**.
""")
