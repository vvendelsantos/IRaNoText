import streamlit as st
import spacy
import re
import pandas as pd
import base64
from io import BytesIO

# Carrega modelo spaCy
nlp = spacy.load("pt_core_news_sm")

# Título principal
st.title("IRaText: Geração de Corpus Textual para IRaMuTeQ")

# --- PARTE 1: Análise de texto ---
st.header("🔎 Analisador de Texto - Detecção de Siglas e Palavras Compostas")

# Inicializa session_state para limpar texto
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# Área de texto com estado
texto_inserido = st.text_area("Insira seu texto abaixo:", height=200, key="input_text")

# Botões lado a lado
col1, col2 = st.columns(2)
with col1:
    analisar = st.button("🔍 Analisar texto")
with col2:
    limpar = st.button("🧹 Limpar")

# Botão limpar: apaga o texto da caixa
if limpar:
    st.session_state.input_text = ""

# Função: detectar siglas
def detectar_siglas(texto):
    padrao = r"\b(?:[A-Z]{2,}|[A-Z]+\d+)\b"
    return sorted(list(set(re.findall(padrao, texto))))

# Função: detectar palavras compostas (entidades com + de 1 palavra)
def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    compostas = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return sorted(list(set(compostas)))

# Executa análise se clicado
if analisar and texto_inserido.strip():
    siglas = detectar_siglas(texto_inserido)
    compostas = detectar_palavras_compostas(texto_inserido)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Siglas Detectadas")
        if siglas:
            for sigla in siglas:
                st.markdown(f"- {sigla}")
        else:
            st.markdown("_Nenhuma sigla detectada._")

    with col4:
        st.subheader("Palavras Compostas Detectadas")
        if compostas:
            for pc in compostas:
                st.markdown(f"- {pc}")
        else:
            st.markdown("_Nenhuma palavra composta detectada._")

# --- PARTE 2: Upload da planilha e geração de corpus ---
st.header("📄 Geração de Corpus Textual para IRaMuTeQ")

st.markdown("Faça o download dos arquivos modelo abaixo e envie a planilha preenchida para gerar o corpus:")

col5, col6 = st.columns(2)
with col5:
    st.markdown("[📥 Baixar modelo de planilha](https://github.com/wendel-ufs/ira-text/raw/main/modelo_planilha.xlsx)")
with col6:
    st.markdown("[📥 Baixar textos para análise](https://github.com/wendel-ufs/ira-text/raw/main/textos_selecionados.xlsx)")

# Upload
uploaded_file = st.file_uploader("Envie aqui a planilha preenchida", type=["xlsx"])

if uploaded_file:
    try:
        abas = pd.read_excel(uploaded_file, sheet_name=None)
        textos = abas["textos_selecionados"]
        dic_compostas = abas["dic_palavras_compostas"]
        dic_siglas = abas["dic_siglas"]

        def aplicar_substituicoes(texto, dicionario):
            for _, row in dicionario.iterrows():
                original = row['original']
                substituto = row['substituto']
                texto = re.sub(rf"\b{re.escape(original)}\b", substituto, texto)
            return texto

        textos['texto_processado'] = textos['texto'].apply(lambda t: aplicar_substituicoes(t, dic_compostas))
        textos['texto_processado'] = textos['texto_processado'].apply(lambda t: aplicar_substituicoes(t, dic_siglas))

        corpus = "\n\n****\n\n".join(textos['texto_processado'])

        st.subheader("📝 Corpus Gerado")
        st.text_area("Corpus pronto para uso no IRaMuTeQ:", corpus, height=300)

        st.subheader("📊 Estatísticas")
        st.write(f"**Total de textos:** {len(textos)}")
        st.write(f"**Total de palavras compostas substituídas:** {len(dic_compostas)}")
        st.write(f"**Total de siglas substituídas:** {len(dic_siglas)}")

        def gerar_download_link(texto, nome_arquivo):
            buffer = BytesIO()
            buffer.write(texto.encode())
            buffer.seek(0)
            b64 = base64.b64encode(buffer.read()).decode()
            href = f'<a href="data:file/txt;base64,{b64}" download="{nome_arquivo}">📩 Baixar corpus gerado</a>'
            return href

        st.markdown(gerar_download_link(corpus, "corpus_iramuteq.txt"), unsafe_allow_html=True)

    except Exception as e:
        st.error("Erro ao processar a planilha. Verifique se ela está no formato correto.")
        st.exception(e)

# --- Rodapé ---
st.markdown("---")
st.markdown("""
👨‍🏫 **Sobre o autor**  
**Autor:** José Wendel dos Santos  
**Instituição:** Universidade Federal de Sergipe (UFS)  
**Contato:** [eng.wendel@gmail.com](mailto:eng.wendel@gmail.com)
""")
