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

# Função para detectar palavras compostas
def detectar_palavras_compostas(texto):
    palavras = texto.split()
    palavras_compostas = []
    
    # Verificar pares consecutivos de palavras
    for i in range(len(palavras) - 1):
        palavra_composta = f"{palavras[i]} {palavras[i + 1]}"
        if len(palavra_composta.split()) > 1:
            palavras_compostas.append(palavra_composta)
    
    return palavras_compostas

# Função para detectar siglas
def detectar_siglas(texto):
    siglas = re.findall(r'\b[A-Z]{2,}\b', texto)
    return list(set(siglas))  # Retorna siglas únicas

# Função principal
def gerar_corpus(df_textos):
    total_textos = 0
    total_siglas = 0
    total_compostos = 0
    corpus_final = ""
    
    for _, row in df_textos.iterrows():
        texto = str(row.get("textos selecionados", ""))
        id_val = row.get("id", "")
        if not texto.strip():
            continue
        
        texto_corrigido = texto.lower()
        texto_corrigido = converter_numeros_por_extenso(texto_corrigido)
        
        # Detectar palavras compostas e siglas dinamicamente
        palavras_compostas = detectar_palavras_compostas(texto_corrigido)
        siglas_detectadas = detectar_siglas(texto_corrigido)

        total_textos += 1

        for sigla in siglas_detectadas:
            texto_corrigido = re.sub(rf"\b{sigla}\b", sigla, texto_corrigido, flags=re.IGNORECASE)
            total_siglas += 1

        for palavra_composta in palavras_compostas:
            texto_corrigido = re.sub(rf"\b{palavra_composta}\b", palavra_composta, texto_corrigido, flags=re.IGNORECASE)
            total_compostos += 1

        texto_corrigido = re.sub(r"\s+", " ", texto_corrigido.strip())

        metadata = f"**** *ID_{id_val}"
        for col in row.index:
            if col.lower() not in ["id", "textos selecionados"]:
                metadata += f" *{col.replace(' ', '_')}_{str(row[col]).replace(' ', '_')}"

        corpus_final += f"{metadata}\n{texto_corrigido}\n"
    
    estatisticas = f"Textos processados: {total_textos}\n"
    estatisticas += f"Siglas detectadas: {total_siglas}\n"
    estatisticas += f"Palavras compostas detectadas: {total_compostos}\n"

    return corpus_final, estatisticas

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de corpus textual para IRaMuTeQ")

st.markdown("""### 📌 Instruções""")

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
        df_textos.columns = [col.strip().lower() for col in df_textos.columns]

        if st.button("🚀 GERAR CORPUS TEXTUAL"):
            corpus, estatisticas = gerar_corpus(df_textos)

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
