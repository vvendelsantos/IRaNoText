import streamlit as st
import pandas as pd
import re
import spacy
import io
from word2number import w2n

# Carregar modelo spaCy para NER
nlp = spacy.load("pt_core_news_sm")

# Funções de Detecção
def detectar_siglas(texto):
    return sorted(set(re.findall(r"\b[A-Z]{2,}\b", texto)))

def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    compostas = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return sorted(set(compostas))

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
        total_textos += 1

        for sigla, significado in dict_siglas.items():
            texto_corrigido = re.sub(rf"\({sigla}\)", "", texto_corrigido)
            texto_corrigido = re.sub(rf"\b{sigla}\b", significado, texto_corrigido, flags=re.IGNORECASE)
            total_siglas += 1

        for termo, substituto in dict_compostos.items():
            if termo in texto_corrigido:
                texto_corrigido = re.sub(rf"\b{termo}\b", substituto, texto_corrigido, flags=re.IGNORECASE)
                total_compostos += 1

        texto_corrigido = re.sub(r"\s+", " ", texto_corrigido.strip())

        metadata = f"**** *ID_{id_val}"
        for col in row.index:
            if col.lower() not in ["id", "textos selecionados"]:
                metadata += f" *{col.replace(' ', '_')}_{str(row[col]).replace(' ', '_')}"

        corpus_final += f"{metadata}\n{texto_corrigido}\n"

    return corpus_final

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de corpus textual para IRaMuTeQ")

# Texto do usuário
texto_input = st.text_area("Cole ou digite um texto para análise:", height=200)

# Detecção automática
if texto_input:
    if st.button("Analisar Texto"):
        # Detectar siglas e palavras compostas
        compostas = detectar_palavras_compostas(texto_input)
        siglas = detectar_siglas(texto_input)

        # Exibir resultados lado a lado
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📌 Palavras Compostas Detectadas:**")
            for item in compostas:
                st.markdown(f"- {item}")
        with col2:
            st.markdown("**🔠 Siglas Detectadas:**")
            for item in siglas:
                st.markdown(f"- {item}")

# Inserir planilha para gerar corpus
st.markdown("---")
st.markdown("### 📎 Envio de Planilha para Geração do Corpus")

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

        if st.button("🚀 GERAR CORPUS TEXTUAL"):
            corpus = gerar_corpus(df_textos, df_compostos, df_siglas)

            if corpus.strip():
                st.success("Corpus gerado com sucesso!")
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
