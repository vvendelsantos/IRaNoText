import streamlit as st
import pandas as pd
import re
import io
from word2number import w2n
from collections import Counter

# Funções de processamento
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

def processar_palavras_com_se(texto):
    return re.sub(r"(\b\w+)-se\b", r"se \1", texto)

def processar_pronomes_pospostos(texto):
    texto = re.sub(r'\b(\w+)-se\b', r'se \1', texto)
    texto = re.sub(r'\b(\w+)-([oa]s?)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)-(lhe|lhes)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)-(me|te|nos|vos)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)[áéíóúâêô]?-([oa]s?)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)[áéíóúâêô]-(lo|la|los|las)-ia\b', r'\2 \1ia', texto)
    return texto

# Detectar siglas (ex: UFS, MEC)
def detectar_siglas(texto):
    return list(set(re.findall(r'\b[A-Z]{2,}(?:-[A-Z]{2,})?\b', texto)))

# Sugerir palavras compostas (simplificado: 2 a 4 palavras iniciadas com letra maiúscula seguidas)
def sugerir_palavras_compostas(texto):
    padrao = re.compile(r'\b(?:[A-ZÁÉÍÓÚÂÊÔÃÕ][a-záéíóúâêôãõç]+(?:\s|$)){2,4}')
    candidatas = padrao.findall(texto)
    limpas = [' '.join(c.strip().split()) for c in candidatas]
    contagem = Counter(limpas)
    return [pc for pc, freq in contagem.items() if freq >= 1]

# Função principal para gerar corpus (mantida do original)
def gerar_corpus(df_textos, df_compostos, df_siglas):
    # ... [mesmo conteúdo da sua função original] ...
    # O conteúdo dessa função não mudou, então mantemos como está
    # Se quiser, eu posso repetir aqui, mas está idêntico ao que você já tem
    pass

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de corpus textual para IRaMuTeQ")

# NOVA ÁREA DE ANÁLISE DE TEXTO
st.markdown("### 🧠 Análise automática de texto")

texto_usuario = st.text_area("Cole aqui um texto para análise automática", height=200)
if st.button("🔍 Analisar"):
    if texto_usuario.strip():
        siglas_detectadas = detectar_siglas(texto_usuario)
        palavras_compostas = sugerir_palavras_compostas(texto_usuario)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📌 Palavras compostas sugeridas")
            if palavras_compostas:
                st.text_area("Palavras compostas", "\n".join(palavras_compostas), height=200)
            else:
                st.info("Nenhuma palavra composta sugerida.")

        with col2:
            st.markdown("#### 🔠 Siglas detectadas")
            if siglas_detectadas:
                st.text_area("Siglas", "\n".join(siglas_detectadas), height=200)
            else:
                st.info("Nenhuma sigla detectada.")
    else:
        st.warning("Insira um texto antes de clicar em Analisar.")

# INSTRUÇÕES E ENVIO DE PLANILHA
st.markdown("""
---
### 📥 Upload da planilha para geração do corpus
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

st.markdown("""
---
👨‍🏫 **Sobre o autor**

**Autor:** José Wendel dos Santos  
**Instituição:** Universidade Federal de Sergipe (UFS)  
**Contato:** eng.wendel@gmail.com
""")
