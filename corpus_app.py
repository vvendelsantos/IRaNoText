import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n

# Carregar modelo do spaCy
nlp = spacy.load("pt_core_news_sm")

# Funções
def detectar_siglas(texto):
    tokens = re.findall(r"\b[A-Z]{2,}\b", texto)
    return sorted(set(tokens))

def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    compostas = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return list(set(compostas))

# ========================== ABAS ==========================
st.title("IRaText: Gerador de Corpus Textual")

tabs = st.tabs([
    "📝 ANÁLISE PRELIMINAR DOS TEXTOS",
    "🛠️ GERAÇÃO DO CORPUS TEXTUAL",
    "🚧 EM CONSTRUÇÃO"
])

with tabs[0]:
    st.header("Análise Preliminar")
    texto_input = st.text_area("Insira seu texto:", height=250)

    if st.button("🔍 Analisar textos"):
        if texto_input.strip():
            siglas = detectar_siglas(texto_input)
            compostas = detectar_palavras_compostas(texto_input)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🕵️‍♂️ Entidades Nomeadas")
                if compostas:
                    st.text_area("Copie e cole no Excel", "\n".join(sorted(compostas)), height=250)
                else:
                    st.info("Nenhuma entidade nomeada encontrada.")

            with col2:
                st.markdown("### 🔠 Siglas detectadas")
                if siglas:
                    st.text_area("Copie e cole no Excel", "\n".join(sorted(siglas)), height=250)
                else:
                    st.info("Nenhuma sigla encontrada.")
        else:
            st.warning("Por favor, insira um texto antes de analisar.")

with tabs[1]:
    st.header("Geração do Corpus Textual")

    st.markdown("""<style> [data-testid="stSidebar"] div.stMarkdown p { text-align: justify; } </style>""", unsafe_allow_html=True)

    st.sidebar.markdown("""
    # ℹ️ Sobre a ferramenta

    Bem-vindo ao IRaText — ferramenta para preparar e gerar seu corpus textual compatível com o IRaMuTeQ. Com ele, você realiza duas etapas essenciais para análise de dados qualitativos de forma eficiente.

    ### 📝 **Análise preliminar dos textos:**
    Utiliza Reconhecimento de Entidades Nomeadas (REN) para identificar e classificar automaticamente termos como nomes, siglas e outras entidades no texto, facilitando a organização das informações para o preenchimento da planilha.

    ### 🛠️ **Geração do corpus textual:**
    Processa textos com expressões regulares, ajustando palavras e formatos. Inclui: (1) normalização de números por extenso, (2) tratamento de flexões verbo-pronominais, (3) substituição de siglas e entidades nomeadas, (4) remoção de caracteres especiais e (5) geração de metadados. Ao final, exibe o corpus gerado e as estatísticas de processamento antes de salvá-lo.
    """)

    st.subheader("📝 Inserir Textos para Processamento")

    textos = []
    input_textos_brutos = st.text_area("Cole aqui os textos (um por linha):", height=200)
    if input_textos_brutos.strip():
        linhas = input_textos_brutos.strip().split("\n")
        for i, linha in enumerate(linhas):
            textos.append({"id": f"texto_{i+1}", "texto": linha})

    # Novo campo para inserir os valores dos metadados em massa
    st.subheader("📊 Metadados Adicionais (opcional)")

    metadados_input = st.text_area(
        "Cole aqui os valores dos metadados para cada texto (um por linha):",
        height=200,
        help="Exemplo: 'Autor: João', 'Data: 2025-04-25'."
    )

    # Processando os valores de metadados
    metadados = []
    if metadados_input.strip():
        metadados = [linha.strip() for linha in metadados_input.strip().split("\n")]

    # Função para gerar o corpus
    def gerar_corpus(textos, metadados):
        corpus_final = ""
        
        # Associar metadados aos textos (um ou mais valores de metadado para cada texto)
        for idx, texto_info in enumerate(textos):
            texto = texto_info["texto"]
            id_val = texto_info["id"]

            if not texto.strip():
                continue

            texto_corrigido = texto.strip()

            # Concatenar metadados (associar cada metadado ao seu texto)
            metadata = f"**** *ID_{id_val}"
            if len(metadados) > idx:  # Se houver metadado suficiente
                metadata += f" *Metadado_{idx+1}_{metadados[idx].replace(' ', '_')}"
            corpus_final += f"{metadata}\n{texto_corrigido}\n"
        
        return corpus_final

    if st.button("🚀 GERAR CORPUS TEXTUAL"):
        if textos:
            corpus = gerar_corpus(textos, metadados)

            if corpus.strip():
                st.success("Corpus gerado com sucesso!")

                st.subheader("📄 Corpus Textual Gerado")
                st.text_area("Veja o corpus gerado antes de baixar", corpus, height=300)

                buf = io.BytesIO()
                buf.write(corpus.encode("utf-8"))
                st.download_button("💾 SALVAR CORPUS TEXTUAL", data=buf.getvalue(), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")
            else:
                st.warning("Nenhum corpus gerado.")
        else:
            st.warning("Por favor, insira pelo menos um texto para processar.")

with tabs[2]:
    st.header("🚧 EM CONSTRUÇÃO")
    st.info("Novos recursos ainda estão em desenvolvimento.")

# Rodapé
st.markdown("""
---
**👨‍💻 Autor:** José Wendel dos Santos  
**🏛️ Instituição:** Universidade Federal de Sergipe (UFS)  
**📧 Contato:** eng.wendel@live.com
""")
