import streamlit as st 
import pandas as pd
import re
import io
import spacy
from word2number import w2n

# Carregar modelo do spaCy
nlp = spacy.load("pt_core_news_sm")

def detectar_siglas(texto):
    tokens = re.findall(r"\b[A-Z]{2,}\b", texto)
    return sorted(set(tokens))

def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    compostas = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return list(set(compostas))

st.title("IRaText: Gerador de Corpus Textual")

tabs = st.tabs([
    "📝 ANÁLISE PRELIMINAR DOS TEXTOS",
    "🛠️ GERAÇÃO DO CORPUS TEXTUAL",
    "🚧 EM CONSTRUÇÃO"
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
                    entidades_coladas = "\n".join(sorted(compostas))
                    st.text_area("Copie e cole no Excel", entidades_coladas, height=250, key="entidades_copiadas")
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

    st.markdown("""
        <style>
        [data-testid="stSidebar"] div.stMarkdown p {
            text-align: justify;
        }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("""   
    # ℹ️ Sobre a ferramenta

    Bem-vindo ao IRaText — ferramenta para preparar e gerar seu corpus textual compatível com o IRaMuTeQ. Com ele, você realiza duas etapas essenciais para análise de dados qualitativos de forma eficiente.
    ### 📝 **Análise preliminar dos textos:**
    Utiliza Reconhecimento de Entidades Nomeadas (REN) para identificar e classificar automaticamente termos como nomes, siglas e outras entidades no texto, facilitando a organização das informações para o preenchimento da planilha.
    ### 🛠️ **Geração do corpus textual:**
    Processa textos com expressões regulares, ajustando palavras e formatos. Inclui: (1) normalização de números por extenso, (2) tratamento de flexões verbo-pronominais, (3) substituição de siglas e entidades nomeadas, (4) remoção de caracteres especiais e (5) geração de metadados. Ao final, exibe o corpus gerado e as estatísticas de processamento antes de salvá-lo.
    """)

    st.subheader("📝 Inserir Textos para Processamento")
    textos_colados = st.text_area("Cole os textos aqui (1 por linha)", height=200)
    textos = []

    if textos_colados.strip():
        for i, linha in enumerate(textos_colados.strip().splitlines()):
            textos.append({"id": f"texto_{i+1}", "texto": linha})

    st.subheader("📚 Dicionário de Entidades Nomeadas")
    entidades_coladas = st.text_area("Cole as entidades nomeadas (uma por linha)", height=150)
    entidades = []

    if entidades_coladas.strip():
        for linha in entidades_coladas.strip().splitlines():
            entidade = linha.strip()
            normalizada = entidade.replace(" ", "_").lower()
            entidades.append({"Entidades nomeadas": entidade, "Palavra normalizada": normalizada})

    st.subheader("🔠 Dicionário de Siglas")
    siglas_coladas = st.text_area("Cole as siglas (uma por linha)", height=150)
    siglas = []

    if siglas_coladas.strip():
        for linha in siglas_coladas.strip().splitlines():
            sigla = linha.strip()
            significado = ""
            for ent in entidades:
                if sigla.upper() == "".join([x[0] for x in ent["Entidades nomeadas"].split()]).upper():
                    significado = ent["Palavra normalizada"]
                    break
            siglas.append({"Sigla": sigla, "Significado": significado})

    st.subheader("📊 Metadados Adicionais (opcional)")
    metadados = {}
    num_metadados = st.number_input("Quantidade de campos de metadados", min_value=0, max_value=10, value=0)

    for i in range(num_metadados):
        col1, col2 = st.columns(2)
        with col1:
            nome_meta = st.text_input(f"Nome do metadado {i+1}", key=f"meta_nome_{i}")
        with col2:
            valor_meta = st.text_input(f"Valor do metadado {i+1}", key=f"meta_valor_{i}")
        if nome_meta:
            metadados[nome_meta] = valor_meta

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
        return re.sub(r"(\b\w+)-se\b", r"se \\1", texto)

    def processar_pronomes_pospostos(texto):
        texto = re.sub(r'\b(\w+)-se\b', r'se \\1', texto)
        texto = re.sub(r'\b(\w+)-([oa]s?)\b', r'\\2 \\1', texto)
        texto = re.sub(r'\b(\w+)-(lhe|lhes)\b', r'\\2 \\1', texto)
        texto = re.sub(r'\b(\w+)-(me|te|nos|vos)\b', r'\\2 \\1', texto)
        texto = re.sub(r'\b(\w+)[áéíóúâêô]?-([oa]s?)\b', r'\\2 \\1', texto)
        texto = re.sub(r'\b(\w+)[áéíóúâêô]-(lo|la|los|las)-ia\b', r'\\2 \\1ia', texto)
        return texto

    def gerar_corpus(textos, entidades, siglas, metadados):
        dict_entidades = {
            str(row["Entidades nomeadas"]).lower(): str(row["Palavra normalizada"]).lower()
            for row in entidades
        }

        dict_siglas = {
            str(row["Sigla"]).lower(): str(row["Significado"])
            for row in siglas
        }

        caracteres_especiais = {
            "-": "Hífen", ";": "Ponto e vírgula", '"': "Aspas duplas", "'": "Aspas simples",
            "…": "Reticências", "–": "Travessão", "(": "Parêntese esquerdo", ")": "Parêntese direito",
            "/": "Barra", "%": "Porcentagem"
        }
        contagem_caracteres = {k: 0 for k in caracteres_especiais}
        total_textos = 0
        total_siglas = 0
        total_entidades = 0
        total_remocoes = 0
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
                texto_corrigido = re.sub(rf"\\({sigla}\\)", "", texto_corrigido)
                texto_corrigido = re.sub(rf"\\b{sigla}\\b", significado, texto_corrigido, flags=re.IGNORECASE)
                total_siglas += 1

            for termo, substituto in dict_entidades.items():
                if termo in texto_corrigido:
                    texto_corrigido = re.sub(rf"\\b{termo}\\b", substituto, texto_corrigido, flags=re.IGNORECASE)
                    total_entidades += 1

            for char in caracteres_especiais:
                count = texto_corrigido.count(char)
                if count:
                    if char == "%":
                        texto_corrigido = texto_corrigido.replace(char, "_por_cento")
                    else:
                        texto_corrigido = texto_corrigido.replace(char, "_")
                    contagem_caracteres[char] += count
                    total_remocoes += count

            texto_corrigido = re.sub(r"\s+", " ", texto_corrigido.strip())

            metadata = f"**** *ID_{id_val}"
            for nome_meta, valor_meta in metadados.items():
                if valor_meta:
                    metadata += f" *{nome_meta.replace(' ', '_')}_{str(valor_meta).replace(' ', '_')}"

            corpus_final += f"{metadata}\n{texto_corrigido}\n"

        estatisticas = f"Textos processados: {total_textos}\n"
        estatisticas += f"Siglas removidas/substituídas: {total_siglas}\n"
        estatisticas += f"Entidades nomeadas substituídas: {total_entidades}\n"
        estatisticas += f"Caracteres especiais removidos: {total_remocoes}\n"
        for char, nome in caracteres_especiais.items():
            if contagem_caracteres[char] > 0:
                estatisticas += f" - {nome} ({char}) : {contagem_caracteres[char]}\n"

        return corpus_final, estatisticas

    if st.button("🚀 GERAR CORPUS TEXTUAL"):
        if textos:
            corpus, estatisticas = gerar_corpus(textos, entidades, siglas, metadados)

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

with tabs[2]:
    st.header("🚧 EM CONSTRUÇÃO")
    st.info("Novos recursos ainda estão em desenvolvimento.")

st.markdown("""  
---  
**👨‍💻 Autor:** José Wendel dos Santos  
**🏛️ Instituição:** Universidade Federal de Sergipe (UFS)  
**📧 Contato:** eng.wendel@live.com
""")
