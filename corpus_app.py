import streamlit as st
import pandas as pd
import re
import io
import spacy
from unidecode import unidecode
import base64

# Carregar modelo spaCy para detecção de entidades nomeadas
nlp = spacy.load("pt_core_news_sm")

st.set_page_config(page_title="Analisador de Texto", layout="wide")

# Função para detectar siglas no texto
def detectar_siglas(texto):
    padrao = r'\b[A-Z]{2,}(?:-[A-Z]{2,})*\b'
    return list(set(re.findall(padrao, texto)))

# Função para detectar palavras compostas usando NER
def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    entidades = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return list(set(entidades))

# Função para normalizar texto
def normalizar_texto(texto):
    texto = texto.lower()
    texto = unidecode(texto)
    texto = re.sub(r"[^\w\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()

# Função principal para gerar corpus
def gerar_corpus(df_textos, df_compostos, df_siglas):
    corpus = ""
    estatisticas = ""
    total_textos = 0
    palavras_total = 0

    # Criar dicionários de substituição
    dicionario_siglas = dict(zip(df_siglas["sigla"], df_siglas["significado"]))
    dicionario_compostos = dict(zip(df_compostos["original"], df_compostos["substituto"]))

    for _, linha in df_textos.iterrows():
        id_ = linha["id"]
        texto = str(linha["texto"])

        # Substituir siglas
        for sigla, significado in dicionario_siglas.items():
            texto = re.sub(rf"\b{re.escape(sigla)}\b", significado, texto)

        # Substituir palavras compostas
        for original, substituto in dicionario_compostos.items():
            texto = re.sub(rf"\b{re.escape(original)}\b", substituto, texto, flags=re.IGNORECASE)

        texto = normalizar_texto(texto)

        if texto.strip():
            corpus += f"**** *{id_}\n{texto}\n\n"
            total_textos += 1
            palavras_total += len(texto.split())

    estatisticas = f"Total de textos processados: {total_textos}\nTotal de palavras no corpus: {palavras_total}"
    return corpus, estatisticas

# Interface Streamlit
st.title("📚 Analisador de Texto - Detecção de Siglas e Palavras Compostas")

st.markdown("### 📝 Parte 1: Inserir texto para análise de siglas e palavras compostas")
texto_usuario = st.text_area("Cole seu texto aqui", height=200)

if st.button("🔍 Analisar texto"):
    if texto_usuario.strip():
        siglas_detectadas = detectar_siglas(texto_usuario)
        compostas_detectadas = detectar_palavras_compostas(texto_usuario)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🧩 Palavras Compostas Detectadas")
            if compostas_detectadas:
                for item in sorted(compostas_detectadas):
                    st.markdown(f"- {item}")
            else:
                st.write("Nenhuma palavra composta detectada.")

        with col2:
            st.markdown("#### 🔠 Siglas Detectadas")
            if siglas_detectadas:
                for item in sorted(siglas_detectadas):
                    st.markdown(f"- {item}")
            else:
                st.write("Nenhuma sigla detectada.")
    else:
        st.warning("Insira um texto para análise.")

st.markdown("---")

st.markdown("### 📂 Parte 2: Upload da planilha para geração do corpus textual")

# Botões para baixar arquivos de exemplo
col3, col4 = st.columns(2)

with col3:
    link_planilha = "https://github.com/seuusuario/seurepositorio/raw/main/modelo_planilha.xlsx"
    st.markdown(
        f'<a href="{link_planilha}" download class="stDownloadButton">📥 Baixar modelo de planilha</a>',
        unsafe_allow_html=True
    )

with col4:
    link_textos = "https://github.com/seuusuario/seurepositorio/raw/main/textos_selecionados.xlsx"
    st.markdown(
        f'<a href="{link_textos}" download class="stDownloadButton">📥 Baixar textos para análise</a>',
        unsafe_allow_html=True
    )

arquivo = st.file_uploader("Envie a planilha preenchida (formato .xlsx)", type=["xlsx"])

if arquivo:
    try:
        df_textos = pd.read_excel(arquivo, sheet_name="textos_selecionados")
        df_compostos = pd.read_excel(arquivo, sheet_name="dic_palavras_compostas")
        df_siglas = pd.read_excel(arquivo, sheet_name="dic_siglas")

        if st.button("🚀 GERAR CORPUS TEXTUAL"):
            corpus, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas)

            if corpus.strip():
                st.success("Corpus gerado com sucesso!")

                # ✅ NOVA SEÇÃO: Exibição do corpus antes das estatísticas
                st.markdown("### 📘 Corpus Textual Gerado")
                st.text_area("Pré-visualização do corpus", corpus, height=300)

                st.markdown("### 📊 Estatísticas do processamento")
                st.text_area("", estatisticas, height=250)

                buf = io.BytesIO()
                buf.write(corpus.encode("utf-8"))
                st.download_button(
                    "📄 BAIXAR CORPUS TEXTUAL",
                    data=buf.getvalue(),
                    file_name="corpus_IRaMuTeQ.txt",
                    mime="text/plain"
                )
            else:
                st.warning("Nenhum texto processado. Verifique os dados da planilha.")
    except Exception as e:
        st.error(f"Erro ao processar a planilha: {e}")

# Rodapé
st.markdown("---")
st.markdown("Desenvolvido por Seu Nome © 2025")
