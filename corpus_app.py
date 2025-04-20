import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n
from textblob import TextBlob
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from spacy import displacy

# Configuração inicial
st.set_page_config(page_title="Analisador de Texto Avançado", page_icon="📊", layout="wide")

# Carregar modelo do spaCy
try:
    nlp = spacy.load("pt_core_news_sm")
except:
    st.warning("Modelo de linguagem pt_core_news_sm não encontrado. Instale com: python -m spacy download pt_core_news_sm")
    st.stop()

# ========================== FUNÇÕES AUXILIARES ==========================
def detectar_siglas(texto):
    tokens = re.findall(r"\b[A-Z]{2,}\b", texto)
    return sorted(set(tokens))

def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    compostas = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return list(set(compostas))

def analisar_sentimento(texto):
    analysis = TextBlob(texto)
    return analysis.sentiment.polarity

def extrair_palavras_chave(texto, n=10):
    doc = nlp(texto)
    palavras = [token.text.lower() for token in doc if not token.is_stop and token.is_alpha]
    contador = Counter(palavras)
    return contador.most_common(n)

def converter_numeros_por_extenso(texto):
    try:
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
    except Exception as e:
        st.error(f"Erro na conversão de números: {e}")
        return texto

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
        texto_corrigido = processar_palavras_com_se(texto_corrigido)
        texto_corrigido = processar_pronomes_pospostos(texto_corrigido)
        total_textos += 1

        for sigla, significado in dict_siglas.items():
            texto_corrigido = re.sub(rf"\({sigla}\)", "", texto_corrigido)
            texto_corrigido = re.sub(rf"\b{sigla}\b", significado, texto_corrigido, flags=re.IGNORECASE)
            total_siglas += 1

        for termo, substituto in dict_compostos.items():
            if termo in texto_corrigido:
                texto_corrigido = re.sub(rf"\b{termo}\b", substituto, texto_corrigido, flags=re.IGNORECASE)
                total_compostos += 1

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

# ========================== BARRA LATERAL ==========================
with st.sidebar:
    st.title("⚙️ Configurações")
    tema = st.selectbox("Tema", ["Claro", "Escuro"])
    if tema == "Escuro":
        st.markdown("<style>body {color: #fff;background-color: #0e1117;}</style>", unsafe_allow_html=True)
    
    idioma = st.selectbox("Idioma para análise", ["Português", "Inglês", "Espanhol"])
    st.markdown("---")
    st.markdown("### 📊 Opções de Análise")
    analise_sentimento = st.checkbox("Análise de Sentimento", True)
    extrair_p_chave = st.checkbox("Extrair Palavras-chave", True)
    mostrar_entidades = st.checkbox("Mostrar Entidades Nomeadas", True)
    
    st.markdown("---")
    st.markdown("### 📌 Sobre")
    st.markdown("""
    **Analisador de Texto Avançado**  
    Versão 2.0  
    Desenvolvido por José Wendel dos Santos  
    [eng.wendel@gmail.com](mailto:eng.wendel@gmail.com)
    """)

# ========================== ABAS PRINCIPAIS ==========================
st.title("📊 Analisador de Texto Avançado")

tabs = st.tabs(["📝 Pré-análise", "📑 Geração de Corpus", "📊 Visualização", "❓ Ajuda"])

with tabs[0]:
    # ========================== PARTE 1 - PRÉ-ANÁLISE ==========================
    st.header("🔍 Análise de Texto Completa")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        texto_input = st.text_area("✍️ Insira seu texto para análise", height=250,
                                 placeholder="Cole ou digite seu texto aqui...")
    with col2:
        st.markdown("### 📌 Dicas")
        st.markdown("""
        - Textos maiores geram análises mais completas
        - Verifique siglas desconhecidas
        - Revise palavras compostas identificadas
        """)
        st.markdown("---")
        exemplo = st.selectbox("Carregar exemplo", 
                              ["Selecione...", "Texto acadêmico", "Notícia", "Relatório técnico"])
        if exemplo != "Selecione...":
            texto_input = "Exemplo de texto carregado para demonstração das funcionalidades."

    if st.button("🔎 Analisar Texto", type="primary"):
        if texto_input.strip():
            with st.spinner("Processando texto..."):
                # Análise básica
                siglas = detectar_siglas(texto_input)
                compostas = detectar_palavras_compostas(texto_input)
                
                # Análise avançada
                doc = nlp(texto_input)
                sentimento = analisar_sentimento(texto_input)
                palavras_chave = extrair_palavras_chave(texto_input)
                entidades = [(ent.text, ent.label_) for ent in doc.ents]
                
                # Layout de resultados
                tab1, tab2, tab3, tab4 = st.tabs(["📌 Resumo", "🧩 Elementos", "📊 Estatísticas", "🖼️ Visualização"])
                
                with tab1:
                    st.subheader("📌 Resumo da Análise")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Palavras", len(texto_input.split()))
                    with col2:
                        st.metric("Sentimento", f"{sentimento:.2f}", 
                                  "Positivo" if sentimento > 0 else "Negativo" if sentimento < 0 else "Neutro")
                    with col3:
                        st.metric("Entidades", len(entidades))
                    
                    st.markdown("### 📝 Trecho Analisado")
                    st.text(texto_input[:500] + ("..." if len(texto_input) > 500 else ""))
                
                with tab2:
                    st.subheader("🧩 Elementos Identificados")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### 🧾 Siglas Detectadas")
                        if siglas:
                            df_siglas = pd.DataFrame(siglas, columns=["Sigla"])
                            st.dataframe(df_siglas, height=200)
                        else:
                            st.info("Nenhuma sigla encontrada.")
                    
                    with col2:
                        st.markdown("### 🧩 Palavras Compostas")
                        if compostas:
                            df_compostas = pd.DataFrame(compostas, columns=["Termo"])
                            st.dataframe(df_compostas, height=200)
                        else:
                            st.info("Nenhuma palavra composta encontrada.")
                    
                    if entidades:
                        st.markdown("### 🏷️ Entidades Nomeadas")
                        df_entidades = pd.DataFrame(entidades, columns=["Entidade", "Tipo"])
                        st.dataframe(df_entidades, height=200)
                
                with tab3:
                    st.subheader("📊 Estatísticas Textuais")
                    
                    # Frequência de palavras
                    palavras = [token.text.lower() for token in doc if token.is_alpha and not token.is_stop]
                    contador = Counter(palavras)
                    top_palavras = contador.most_common(10)
                    
                    fig, ax = plt.subplots()
                    sns.barplot(x=[count for word, count in top_palavras], 
                                y=[word for word, count in top_palavras], ax=ax)
                    ax.set_title("Top 10 Palavras Mais Frequentes")
                    st.pyplot(fig)
                    
                    # Tipos de tokens
                    tipos = {
                        "Adjetivos": sum(1 for token in doc if token.pos_ == "ADJ"),
                        "Substantivos": sum(1 for token in doc if token.pos_ == "NOUN"),
                        "Verbos": sum(1 for token in doc if token.pos_ == "VERB"),
                        "Advérbios": sum(1 for token in doc if token.pos_ == "ADV")
                    }
                    
                    fig2, ax2 = plt.subplots()
                    sns.barplot(x=list(tipos.values()), y=list(tipos.keys()), ax=ax2)
                    ax2.set_title("Distribuição de Classes Gramaticais")
                    st.pyplot(fig2)
                
                with tab4:
                    st.subheader("🖼️ Visualização do Texto")
                    st.markdown("### 🌈 Análise de Entidades")
                    html = displacy.render(doc, style="ent", page=True)
                    st.components.v1.html(html, height=300, scrolling=True)
                    
                    if palavras_chave:
                        st.markdown("### 🔑 Palavras-chave")
                        tags = " ".join([f"#{word[0]}" for word in palavras_chave])
                        st.markdown(f"**{tags}**")
        else:
            st.warning("Por favor, insira um texto antes de analisar.")

with tabs[1]:
    # ========================== PARTE 2 - GERAÇÃO DE CORPUS ==========================
    st.header("📑 Gerador de Corpus Textual para IRaMuTeQ")
    
    st.markdown("""
    ### 📌 Instruções Completa
    
    Esta ferramenta foi desenvolvida para facilitar a geração de corpus textual compatível com o IRaMuTeQ.
    
    **📋 Requisitos do Arquivo Excel:**
    - Formato: `.xlsx`
    - Planilhas obrigatórias:
      1. `textos_selecionados` - Textos para normalização
      2. `dic_palavras_compostas` - Dicionário de palavras compostas
      3. `dic_siglas` - Dicionário de siglas
    """)
    
    # Botões para download
    with st.expander("📥 Modelos para Download"):
        col1, col2 = st.columns(2)
        with col1:
            with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
                st.download_button(
                    label="📝 Modelo de Planilha",
                    data=exemplo,
                    file_name="gerar_corpus_iramuteq.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Baixe o modelo vazio para preencher com seus dados"
                )
        with col2:
            with open("textos_selecionados.xlsx", "rb") as textos:
                st.download_button(
                    label="📚 Textos Exemplo",
                    data=textos,
                    file_name="textos_selecionados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Baixe um conjunto de textos de exemplo para teste"
                )
    
    st.markdown("---")
    st.subheader("📤 Envie sua Planilha")
    file = st.file_uploader("Arraste e solte seu arquivo Excel aqui", type=["xlsx"], 
                           help="Certifique-se que o arquivo segue a estrutura requerida")
    
    if file:
        try:
            with st.spinner("Processando arquivo..."):
                xls = pd.ExcelFile(file)
                df_textos = xls.parse("textos_selecionados")
                df_compostos = xls.parse("dic_palavras_compostas")
                df_siglas = xls.parse("dic_siglas")
                df_textos.columns = [col.strip().lower() for col in df_textos.columns]
                
                st.success("Arquivo carregado com sucesso!")
                
                # Pré-visualização dos dados
                with st.expander("👀 Pré-visualizar Dados"):
                    tab1, tab2, tab3 = st.tabs(["Textos", "Palavras Compostas", "Siglas"])
                    with tab1:
                        st.dataframe(df_textos.head())
                    with tab2:
                        st.dataframe(df_compostos.head())
                    with tab3:
                        st.dataframe(df_siglas.head())
                
                if st.button("🚀 Gerar Corpus Textual", type="primary"):
                    corpus, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas)
                    
                    if corpus.strip():
                        st.success("Corpus gerado com sucesso!")
                        
                        # Resultados em abas
                        tab1, tab2 = st.tabs(["📄 Corpus Gerado", "📊 Estatísticas"])
                        
                        with tab1:
                            st.text_area("Corpus Textual", corpus, height=300)
                            buf = io.BytesIO()
                            buf.write(corpus.encode("utf-8"))
                            st.download_button(
                                label="💾 Baixar Corpus",
                                data=buf.getvalue(),
                                file_name="corpus_IRaMuTeQ.txt",
                                mime="text/plain"
                            )
                        
                        with tab2:
                            st.text_area("Estatísticas de Processamento", estatisticas, height=250)
                            st.info("""
                            **Legenda:**
                            - Textos processados: Total de textos analisados
                            - Siglas: Substituições realizadas
                            - Palavras compostas: Termos normalizados
                            - Caracteres especiais: Remoções efetuadas
                            """)
                    else:
                        st.warning("Nenhum texto processado. Verifique os dados da planilha.")
        
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {str(e)}")
            st.info("Verifique se todas as planilhas necessárias estão presentes no arquivo.")

with tabs[2]:
    # ========================== PARTE 3 - VISUALIZAÇÃO ==========================
    st.header("📊 Visualização de Dados e Estatísticas")
    
    st.markdown("""
    ### 📈 Análises Gráficas
    
    Esta seção permite visualizar os dados processados de forma gráfica para melhor compreensão.
    """)
    
    if 'corpus' in locals():
        st.subheader("📌 Distribuição de Termos")
        
        # Processar corpus para análise
        termos = re.findall(r'\b\w+\b', corpus.lower())
        contagem = Counter(termos)
        top_20 = contagem.most_common(20)
        
        df_termos = pd.DataFrame(top_20, columns=['Termo', 'Frequência'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 Gráfico de Barras")
            fig, ax = plt.subplots()
            sns.barplot(data=df_termos, x='Frequência', y='Termo', ax=ax)
            st.pyplot(fig)
        
        with col2:
            st.markdown("### 📋 Tabela de Frequências")
            st.dataframe(df_termos.sort_values('Frequência', ascending=False))
        
        st.markdown("---")
        st.subheader("📌 Nuvem de Palavras")
        st.info("Funcionalidade de nuvem de palavras será implementada na próxima versão.")
    
    else:
        st.warning("Gere um corpus na aba anterior para visualizar as estatísticas.")

with tabs[3]:
    # ========================== PARTE 4 - AJUDA ==========================
    st.header("❓ Ajuda e Instruções")
    
    with st.expander("📌 Como usar a Pré-análise"):
        st.markdown("""
        1. **Insira seu texto** na caixa de texto principal
        2. Clique no botão **'Analisar Texto'**
        3. Explore os resultados nas diferentes abas:
           - **Resumo**: Visão geral do texto
           - **Elementos**: Siglas, palavras compostas e entidades
           - **Estatísticas**: Dados quantitativos
           - **Visualização**: Representação gráfica
        """)
    
    with st.expander("📑 Como preparar o arquivo para Geração de Corpus"):
        st.markdown("""
        **Estrutura do Arquivo Excel:**
        
        - **Planilha 'textos_selecionados'**:
          - Coluna obrigatória: 'textos selecionados' (textos a serem processados)
          - Coluna opcional: 'id' (identificador único para cada texto)
          - Outras colunas serão incluídas como metadados
        
        - **Planilha 'dic_palavras_compostas'**:
          - 'Palavra composta': Termo original
          - 'Palavra normalizada': Forma padronizada
        
        - **Planilha 'dic_siglas'**:
          - 'Sigla': Sigla a ser expandida
          - 'Significado': Forma por extenso
        """)
    
    with st.expander("💡 Dicas e Melhores Práticas"):
        st.markdown("""
        - Para melhores resultados na análise, use textos com mais de 200 palavras
        - Revise sempre as siglas detectadas - podem haver falsos positivos
        - Na geração de corpus, normalize os termos de forma consistente
        - Utilize metadados para enriquecer sua análise no IRaMuTeQ
        """)
    
    st.markdown("---")
    st.subheader("📞 Suporte")
    st.markdown("""
    Para dúvidas ou problemas, entre em contato:
    - **Email**: [eng.wendel@gmail.com](mailto:eng.wendel@gmail.com)
    - **GitHub**: [github.com/seuusuario](https://github.com/seuusuario)
    """)

# ========================== RODAPÉ ==========================
st.markdown("""
---
© 2023 **Analisador de Texto Avançado** - Desenvolvido por **José Wendel dos Santos**  
Universidade Federal de Sergipe (UFS) - [Lattes](http://lattes.cnpq.br/seuID)
""")
