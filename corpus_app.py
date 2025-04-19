import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n

# Carregar modelo do spaCy
nlp = spacy.load("pt_core_news_sm")

# ========================== CONFIGURAÇÃO DA PÁGINA ==========================
st.set_page_config(
    page_title="Analisador de Texto e Gerador de Corpus",
    page_icon="📊",
    layout="wide"
)

# ========================== FUNÇÕES AUXILIARES ==========================
def detectar_siglas(texto):
    """Detecta siglas no texto (palavras com 2+ letras maiúsculas)"""
    tokens = re.findall(r"\b[A-Z]{2,}\b", texto)
    return sorted(set(tokens))

def detectar_palavras_compostas(texto):
    """Identifica palavras compostas usando spaCy NER"""
    doc = nlp(texto)
    compostas = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return list(set(compostas))

def converter_numeros_por_extenso(texto):
    """Converte números por extenso para algarismos"""
    try:
        palavras = texto.split()
        resultado = []
        for palavra in palavras:
            try:
                num = w2n.word_to_num(palavra)
                resultado.append(str(num))
            except:
                resultado.append(palavra)
        return " ".join(resultado)
    except:
        return texto

def gerar_corpus(df_textos, df_compostos, df_siglas):
    """Gera corpus textual formatado para IRaMuTeQ"""
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

    corpus_final = ""
    for _, row in df_textos.iterrows():
        texto = str(row.get("textos selecionados", ""))
        if texto.strip():
            texto_corrigido = texto.lower()
            texto_corrigido = converter_numeros_por_extenso(texto_corrigido)
            
            # Substituir siglas e palavras compostas
            for sigla, significado in dict_siglas.items():
                texto_corrigido = re.sub(rf"\b{sigla}\b", significado, texto_corrigido, flags=re.IGNORECASE)
            for termo, substituto in dict_compostos.items():
                texto_corrigido = re.sub(rf"\b{termo}\b", substituto, texto_corrigido, flags=re.IGNORECASE)

            corpus_final += f"{texto_corrigido}\n"
    
    return corpus_final

# ========================== PARTE 1 - PRÉ-ANÁLISE ==========================
st.title("🔍 Analisador de Texto")
st.markdown("""
**Detecção de Siglas e Palavras Compostas**  
Ferramenta para análise preliminar de textos, identificando automaticamente siglas e termos compostos.
""")

with st.expander("📝 Área de Texto", expanded=True):
    texto_input = st.text_area(
        "Insira seu texto para análise:",
        height=200,
        placeholder="Cole ou digite o texto que deseja analisar aqui..."
    )

if st.button("Analisar Texto", type="primary", use_container_width=True):
    if texto_input.strip():
        with st.spinner("Processando texto..."):
            siglas = detectar_siglas(texto_input)
            compostas = detectar_palavras_compostas(texto_input)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🧩 Palavras Compostas")
            if compostas:
                st.dataframe(
                    pd.DataFrame(compostas, columns=["Termos"]),
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("Nenhuma palavra composta encontrada.", icon="ℹ️")

        with col2:
            st.subheader("🧾 Siglas Identificadas")
            if siglas:
                st.dataframe(
                    pd.DataFrame(siglas, columns=["Siglas"]),
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("Nenhuma sigla encontrada.", icon="ℹ️")
    else:
        st.warning("Por favor, insira um texto para análise.", icon="⚠️")

# ========================== PARTE 2 - GERAÇÃO DE CORPUS ==========================
st.divider()
st.title("📚 Gerador de Corpus para IRaMuTeQ")
st.markdown("""
**Transforme seus dados textuais em corpus formatado**  
Esta ferramenta processa planilhas Excel contendo textos, dicionários de siglas e termos compostos,
gerando um arquivo pronto para análise no software IRaMuTeQ.
""")

with st.expander("📌 Instruções de Uso", expanded=False):
    st.markdown("""
    ### Estrutura da Planilha Requerida
    
    Sua planilha deve conter **três abas (planilhas internas)** com os seguintes nomes:
    
    1. **`textos_selecionados`**  
       - Coleção de textos que serão processados
       - Deve conter uma coluna chamada "textos selecionados"
    
    2. **`dic_palavras_compostas`**  
       - Dicionário de palavras compostas e suas formas normalizadas
       - Colunas: "Palavra composta" | "Palavra normalizada"
    
    3. **`dic_siglas`**  
       - Dicionário de siglas e seus significados
       - Colunas: "Sigla" | "Significado"
    """)

# Botões para download de modelos
col1, col2 = st.columns(2)
with col1:
    with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
        st.download_button(
            label="📥 Modelo de Planilha Vazia",
            data=exemplo,
            file_name="modelo_corpus_iramuteq.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

with col2:
    with open("textos_selecionados.xlsx", "rb") as textos:
        st.download_button(
            label="📂 Exemplo com Textos",
            data=textos,
            file_name="exemplo_textos_analise.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# Upload e processamento do arquivo
st.subheader("Envie sua planilha para geração do corpus")
uploaded_file = st.file_uploader(
    "Selecione o arquivo Excel (.xlsx)",
    type=["xlsx"],
    label_visibility="collapsed"
)

if uploaded_file:
    try:
        with st.spinner("Processando arquivo..."):
            xls = pd.ExcelFile(uploaded_file)
            df_textos = xls.parse("textos_selecionados")
            df_compostos = xls.parse("dic_palavras_compostas")
            df_siglas = xls.parse("dic_siglas")

        st.success("Arquivo carregado com sucesso!")
        
        with st.expander("Visualizar Dados Carregados"):
            tab1, tab2, tab3 = st.tabs(["Textos", "Palavras Compostas", "Siglas"])
            
            with tab1:
                st.dataframe(df_textos, use_container_width=True)
            
            with tab2:
                st.dataframe(df_compostos, use_container_width=True)
            
            with tab3:
                st.dataframe(df_siglas, use_container_width=True)

        if st.button("Gerar Corpus", type="primary", use_container_width=True):
            with st.spinner("Gerando corpus..."):
                corpus = gerar_corpus(df_textos, df_compostos, df_siglas)

            if corpus.strip():
                st.success("Corpus gerado com sucesso!")
                
                st.subheader("Pré-visualização do Corpus")
                st.text_area(
                    "Corpus Gerado",
                    corpus,
                    height=300,
                    label_visibility="collapsed"
                )

                # Botão de download
                buf = io.BytesIO()
                buf.write(corpus.encode("utf-8"))
                st.download_button(
                    "📩 Baixar Corpus Textual",
                    data=buf.getvalue(),
                    file_name="corpus_IRaMuTeQ.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.warning("Nenhum texto válido encontrado na planilha.", icon="⚠️")

    except Exception as e:
        st.error(f"Erro no processamento: {str(e)}", icon="❌")

# ========================== RODAPÉ ==========================
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.9em;">
    <p>Desenvolvido por <strong>José Wendel dos Santos</strong></p>
    <p>Universidade Federal de Sergipe (UFS) | eng.wendel@gmail.com</p>
</div>
""", unsafe_allow_html=True)
