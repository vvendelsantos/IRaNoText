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

# Função para detectar siglas
def detectar_siglas(texto, dic_siglas):
    for sigla, significado in dic_siglas.items():
        texto = re.sub(rf"\b{sigla}\b", significado, texto, flags=re.IGNORECASE)
    return texto

# Função para sugerir palavras compostas
def sugerir_palavras_compostas(texto, palavras_compostas):
    sugestoes = []
    palavras = texto.split()
    for i in range(len(palavras)-1):
        combinacao = palavras[i] + "_" + palavras[i+1]
        if combinacao in palavras_compostas:
            sugestoes.append(combinacao)
    return sugestoes

# Função principal
def gerar_corpus(df_textos, df_compostos, df_siglas, texto_usuario):
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

    # Processar o texto do usuário
    texto_corrigido = texto_usuario.lower()
    texto_corrigido = converter_numeros_por_extenso(texto_corrigido)
    texto_corrigido = processar_palavras_com_se(texto_corrigido)
    texto_corrigido = processar_pronomes_pospostos(texto_corrigido)

    # Detectar siglas
    texto_corrigido = detectar_siglas(texto_corrigido, dict_siglas)

    # Substituir palavras compostas
    for termo, substituto in dict_compostos.items():
        texto_corrigido = re.sub(rf"\b{termo}\b", substituto, texto_corrigido, flags=re.IGNORECASE)

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

    # Sugestões de palavras compostas
    sugestoes = sugerir_palavras_compostas(texto_corrigido, dict_compostos)
    if sugestoes:
        st.write(f"Sugestões de palavras compostas: {', '.join(sugestoes)}")

    corpus_final += texto_corrigido + "\n"
    total_textos += 1

    estatisticas = f"Textos processados: {total_textos}\n"
    estatisticas += f"Siglas substituídas: {total_siglas}\n"
    estatisticas += f"Palavras compostas substituídas: {total_compostos}\n"
    estatisticas += f"Caracteres especiais removidos: {total_remocoes}\n"
    for char, nome in caracteres_especiais.items():
        if contagem_caracteres[char] > 0:
            estatisticas += f" - {nome} ({char}) : {contagem_caracteres[char]}\n"

    return corpus_final, estatisticas

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de corpus textual para IRaMuTeQ")

# Caixa de texto para o usuário colar o texto
texto_usuario = st.text_area("📋 Insira ou cole seu texto aqui para análise", height=300)

st.markdown("""
### 📌 Instruções
Digite ou cole seu texto na caixa acima. O texto será analisado para sugerir palavras compostas, siglas e outras modificações.
""")

file = st.file_uploader("Envie sua planilha preenchida", type=["xlsx"])

if file and texto_usuario:
    try:
        xls = pd.ExcelFile(file)
        df_textos = xls.parse("textos_selecionados")
        df_compostos = xls.parse("dic_palavras_compostas")
        df_siglas = xls.parse("dic_siglas")
        df_textos.columns = [col.strip().lower() for col in df_textos.columns]

        if st.button("🚀 GERAR CORPUS TEXTUAL"):
            corpus, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas, texto_usuario)

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
