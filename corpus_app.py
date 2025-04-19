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

# Funções de pré-processamento de texto
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

# Funções auxiliares de análise
def detectar_siglas(texto):
    return list(set(re.findall(r'\b[A-Z]{2,}\b', texto)))

def sugerir_palavras_compostas(texto):
    padrao = re.compile(r'(\b\w{4,}\b(?:\s+\w{2,}){1,4})')
    sugestoes = [(m.span(), m.group()) for m in padrao.finditer(texto) if len(m.group().split()) >= 2]
    return sugestoes

# Função principal do corpus
# (mantida sem alterações para foco na parte de sugestão/análise visual)
# ... [função gerar_corpus() mantida aqui como no original] ...

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de corpus textual para IRaMuTeQ")

texto_input = st.text_area("✍️ Insira o texto para análise preliminar:", height=200)
if st.button("🔍 Analisar"):
    if texto_input.strip():
        siglas_detectadas = detectar_siglas(texto_input)
        sugestoes_compostos = sugerir_palavras_compostas(texto_input)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📌 Sugestões de palavras compostas")
            st.markdown(f"""
            <div style='background-color:#f0f2f6;padding:15px;border-radius:10px;min-height:200px'>
                <ul style='list-style-type: none;padding-left:0;'>
                    {''.join(f"<li>🔹 <b>[{inicio} - {fim}]</b>: {palavra}</li>" for (inicio, fim), palavra in sugestoes_compostos)}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("### 📌 Siglas detectadas no texto")
            st.markdown(f"""
            <div style='background-color:#f0f2f6;padding:15px;border-radius:10px;min-height:200px'>
                <ul style='list-style-type: none;padding-left:0;'>
                    {''.join(f"<li>🔸 <b>{i}</b>: {sigla}</li>" for i, sigla in enumerate(siglas_detectadas))}
                </ul>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Por favor, insira um texto para análise.")

st.markdown("---")
st.markdown("### 📤 Envio da planilha para geração do corpus")

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
