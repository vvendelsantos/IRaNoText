import streamlit as st 
import pandas as pd
import re
import io
import spacy
from word2number import w2n
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# Sidebar
st.sidebar.markdown("""   
    # ℹ️ Sobre a ferramenta

    Bem-vindo ao IRaText — ferramenta para preparar e gerar seu corpus textual compatível com o IRaMuTeQ. Com ele, você realiza duas etapas essenciais para análise de dados qualitativos de forma eficiente.
    ### 📝 **Análise preliminar dos textos:**
    Utiliza Reconhecimento de Entidades Nomeadas (REN) para identificar e classificar automaticamente termos como nomes, siglas e outras entidades no texto, facilitando a organização das informações para o preenchimento da planilha.
    ### 🛠️ **Geração do corpus textual:**
    Processa textos em uma planilha com expressões regulares, ajustando palavras e formatos. Inclui: (1) normalização de números por extenso, (2) tratamento de flexões verbo-pronominais, (3) substituição de siglas e entidades nomeadas, (4) remoção de caracteres especiais e (5) geração de metadados. Ao final, exibe o corpus gerado e as estatísticas de processamento antes de salvá-lo.

    ⚠️ Sua planilha deve conter **três abas** com os seguintes nomes e finalidades:

    1. **`textos_selecionados`** : textos a serem normalizados e processados. 
    2. **`dic_entidades_nomeadas`** : entidades nomeadas e suas formas normalizadas.  
    3. **`dic_siglas`** : Lista de siglas e seus significados.
""")

# Carregar modelo do spaCy
nlp = spacy.load("pt_core_news_sm")

# Funções da parte 1
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
    "📊 ANÁLISE EXPLORATÓRIA"  # Nova aba
])

with tabs[0]:
    st.header("")
    texto_input = st.text_area("", height=250)

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
    st.header("")

    st.subheader("📝 Inserir Textos para Processamento")

    textos = []
    input_textos_brutos = st.text_area("Cole aqui os textos (um por linha):", height=200)
    if input_textos_brutos.strip():
        linhas = input_textos_brutos.strip().split("\n")
        for i, linha in enumerate(linhas):
            textos.append({"id": f"texto_{i+1}", "texto": linha})

    st.subheader("📚 Dicionário de Entidades Nomeadas")
    entidades_brutas = st.text_area("Cole aqui as entidades (uma por linha):", height=150)
    entidades = []
    if entidades_brutas.strip():
        for linha in entidades_brutas.strip().split("\n"):
            entidade = linha.strip()
            if entidade:
                forma_normalizada = entidade.replace(" ", "_")
                entidades.append({"Entidades nomeadas": entidade, "Palavra normalizada": forma_normalizada})

    st.subheader("🔠 Dicionário de Siglas")
    siglas = []
    num_siglas = st.number_input("Quantidade de siglas", min_value=0, max_value=100, value=0)

    for i in range(num_siglas):
        col1, col2 = st.columns(2)
        with col1:
            sigla = st.text_input(f"Sigla {i+1}", key=f"sigla_{i}")
        with col2:
            significado = st.text_input(f"Significado {i+1}", key=f"sign_{i}")
        if sigla and significado:
            significado_formatado = significado.lower().replace(" ", "_")
            siglas.append({"Sigla": sigla, "Significado": significado_formatado})

    st.subheader("📊 Metadados por Texto")
    num_campos_metadados = st.number_input("Quantidade de campos de metadados para todos os textos", 
                                         min_value=0, max_value=10, value=0, 
                                         key="meta_global_n")

    campos_metadados = []
    for i in range(num_campos_metadados):
        campo = st.text_input(f"Nome do campo {i+1} (ex: 'Autor', 'Data')", 
                             key=f"meta_campo_{i}")
        if campo:
            campos_metadados.append(campo.strip())

    metadados_por_texto = {}
    if campos_metadados and textos:
        dados = []
        for texto in textos:
            row = {"ID Texto": texto['id']}
            for campo in campos_metadados:
                row[campo] = ""
            dados.append(row)
        
        df_metadados = pd.DataFrame(dados)
        df_editado = st.data_editor(
            df_metadados,
            column_config={"ID Texto": st.column_config.Column(disabled=True)},
            hide_index=True,
            use_container_width=True
        )

        for _, row in df_editado.iterrows():
            metadados = {}
            for campo in campos_metadados:
                if pd.notna(row[campo]) and row[campo].strip():
                    metadados[campo] = row[campo].strip()
            metadados_por_texto[row['ID Texto']] = metadados

    def converter_numeros_por_extenso(texto):
        if not isinstance(texto, str):
            return texto
            
        numeros = {
            "zero": "0", "dois": "2", "duas": "2", 
            "três": "3", "quatro": "4", "cinco": "5", "seis": "6", 
            "sete": "7", "oito": "8", "nove": "9", "dez": "10",
            "onze": "11", "doze": "12", "treze": "13", "quatorze": "14", 
            "quinze": "15", "dezesseis": "16", "dezessete": "17", 
            "dezoito": "18", "dezenove": "19", "vinte": "20",
            "trinta": "30", "quarenta": "40", "cinquenta": "50", 
            "sessenta": "60", "setenta": "70", "oitenta": "80", 
            "noventa": "90", "cem": "100", "cento": "100",
            "duzentos": "200", "trezentos": "300", "quatrocentos": "400",
            "quinhentos": "500", "seiscentos": "600", "setecentos": "700",
            "oitocentos": "800", "novecentos": "900", "mil": "1000"
        }

        padrao = r"\b(" + "|".join(numeros.keys()) + r")\b"
        
        def substituir_numero(match):
            return numeros[match.group(1).lower()]
        
        texto = re.sub(padrao, substituir_numero, texto, flags=re.IGNORECASE)
        
        return texto

    def processar_palavras_com_se(texto):
        if not isinstance(texto, str):
            return texto
        return re.sub(r"(\b\w+)-se\b", r"se \1", texto)

    def processar_pronomes_pospostos(texto):
        if not isinstance(texto, str):
            return texto
            
        texto = re.sub(r'\b(\w+)-se\b', r'se \1', texto)
        texto = re.sub(r'\b(\w+)-([oa]s?)\b', r'\2 \1', texto)
        texto = re.sub(r'\b(\w+)-(lhe|lhes)\b', r'\2 \1', texto)
        texto = re.sub(r'\b(\w+)-(me|te|nos|vos)\b', r'\2 \1', texto)
        texto = re.sub(r'\b(\w+)[áéíóúâêô]?-([oa]s?)\b', r'\2 \1', texto)
        texto = re.sub(r'\b(\w+)[áéíóúâêô]-(lo|la|los|las)-ia\b', r'\2 \1ia', texto)
        return texto

    def gerar_corpus(textos, entidades, siglas, metadados_por_texto):
        dict_entidades = {e["Entidades nomeadas"].lower(): e["Palavra normalizada"].lower() for e in entidades}
        dict_siglas = {s["Sigla"].lower(): s["Significado"] for s in siglas}
        caracteres_especiais = {
            "-": "Hífen", ";": "Ponto e vírgula", '"': "Aspas duplas", "'": "Aspas simples", "…": "Reticências", "–": "Travessão", "(": "Parêntese esquerdo", ")": "Parêntese direito", "/": "Barra", "%": "Porcentagem", "[": "Colchete esquerdo", "]": "Colchete direito","{": "Chave esquerda", "}": "Chave direita", "&": "E comercial", "*": "Asterisco","@": "Arroba", "#": "Cerquilha", "$": "Cifrão", "+": "Mais", "=": "Igual","<": "Menor que", ">": "Maior que", "\\": "Barra invertida", "|": "Barra vertical", "~": "Til", "`": "Acento grave", "^": "Circunflexo"
        }

        contagem_caracteres = {k: 0 for k in caracteres_especiais}
        total_textos = total_siglas = total_entidades = total_remocoes = 0
        corpus_final = ""

        for texto_info in textos:
            texto = texto_info["texto"]
            id_val = texto_info["id"]
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

            for termo, substituto in dict_entidades.items():
                if termo in texto_corrigido:
                    texto_corrigido = re.sub(rf"\b{termo}\b", substituto, texto_corrigido, flags=re.IGNORECASE)
                    total_entidades += 1

            for char in caracteres_especiais:
                count = texto_corrigido.count(char)
                if count:
                    if char in ['"', "'"]:
                        texto_corrigido = texto_corrigido.replace(char, "")
                    else:
                        texto_corrigido = texto_corrigido.replace(char, "_por_cento" if char == "%" else "_")
                    contagem_caracteres[char] += count
                    total_remocoes += count

            texto_corrigido = re.sub(r"\s+", " ", texto_corrigido.strip())

            metadata = f"**** *ID_{id_val}"
            for k, v in metadados_por_texto.get(id_val, {}).items():
                if v:
                    metadata += f" *{k.replace(' ', '_')}_{v.replace(' ', '_')}"

            corpus_final += f"{metadata}\n{texto_corrigido}\n"

        estatisticas = f"Textos processados: {total_textos}\nSiglas substituídas: {total_siglas}\n"
        estatisticas += f"Entidades substituídas: {total_entidades}\nCaracteres especiais removidos: {total_remocoes}\n"
        for c, label in caracteres_especiais.items():
            if contagem_caracteres[c] > 0:
                estatisticas += f" - {label} ({c}) : {contagem_caracteres[c]}\n"

        return corpus_final, estatisticas

    if st.button("🚀 GERAR CORPUS TEXTUAL"):
        if textos:
            corpus, estatisticas = gerar_corpus(textos, entidades, siglas, metadados_por_texto)
            if corpus.strip():
                st.success("Corpus gerado com sucesso!")
                st.subheader("📄 Corpus Textual Gerado")
                st.text_area("Veja o corpus gerado antes de baixar", corpus, height=300)
                st.text_area("📊 Estatísticas do processamento", estatisticas, height=250)

                buf = io.BytesIO()
                buf.write(corpus.encode("utf-8"))
                st.download_button("💾 SALVAR CORPUS TEXTUAL", data=buf.getvalue(), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")
            else:
                st.warning("Nenhum corpus gerado.")
        else:
            st.warning("Por favor, insira pelo menos um texto para processar.")

with tabs[2]:  # Nova aba de Análise Exploratória
    st.header("📊 Análise Exploratória")
    
    # Verifica se há textos processados
    if 'textos' not in globals() or not textos:
        st.warning("⛔ Nenhum texto disponível. Processe os textos na aba 'Geração de Corpus' primeiro.")
    else:
        # Pré-processamento
        st.subheader("1. Pré-processamento")
        docs = [t["texto"] for t in textos if t["texto"].strip()]
        
        remove_stopwords = st.checkbox("Remover stopwords (palavras comuns como 'de', 'a', 'o')")
        if remove_stopwords:
            nlp = spacy.load("pt_core_news_sm")
            stopwords = nlp.Defaults.stop_words
            docs = [" ".join([word for word in doc.split() if word.lower() not in stopwords]) for doc in docs]
        
        # Palavras mais frequentes
        st.subheader("2. Palavras Mais Frequentes")
        all_words = " ".join(docs).split()
        word_counts = Counter(all_words).most_common(20)
        
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(dict(word_counts))
        with col2:
            st.dataframe(pd.DataFrame(word_counts, columns=["Palavra", "Frequência"]))
        
        # Matriz de Coocorrência
        st.subheader("3. Matriz de Coocorrência")
        st.markdown("**Palavras que aparecem juntas no mesmo contexto**")
        
        selected_words = st.multiselect(
            "Selecione palavras para análise",
            options=[w[0] for w in word_counts[:20]],
            default=[w[0] for w in word_counts[:3]]
        )
        
        if selected_words:
            window_size = st.slider("Tamanho da janela de contexto (palavras)", 2, 10, 5)
            
            # Cria matriz de coocorrência simplificada
            cooc_matrix = pd.DataFrame(0, index=selected_words, columns=selected_words)
            
            for doc in docs:
                words = doc.split()
                for i, word in enumerate(words):
                    if word in selected_words:
                        start = max(0, i - window_size)
                        end = min(len(words), i + window_size + 1)
                        context = words[start:end]
                        for other_word in context:
                            if other_word in selected_words and other_word != word:
                                cooc_matrix.loc[word, other_word] += 1
            
            st.dataframe(cooc_matrix.style.background_gradient(cmap="Blues"))
        
        # Extração de Tópicos
        st.subheader("4. Extração de Tópicos (LDA)")
        num_topics = st.number_input("Número de tópicos para extrair", 2, 10, 3)
        
        if st.button("Identificar Tópicos"):
            with st.spinner("Processando..."):
                vectorizer = CountVectorizer(max_df=0.95, min_df=2)
                X = vectorizer.fit_transform(docs)
                
                lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
                lda.fit(X)
                
                st.success("Tópicos identificados!")
                for i, topic in enumerate(lda.components_):
                    top_words = [vectorizer.get_feature_names_out()[j] for j in topic.argsort()[-5:][::-1]]
                    st.markdown(f"**Tópico {i+1}:** {', '.join(top_words)}")

# Rodapé
st.markdown("""  
---  
**👨‍💻 Autor:** José Wendel dos Santos  
**🏛️ Instituição:** Universidade Federal de Sergipe (UFS)  
**📧 Contato:** eng.wendel@live.com
""")
