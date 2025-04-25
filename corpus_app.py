# 🟢 CÓDIGO ATUALIZADO: METADADOS POR TEXTO INDIVIDUAL 🟢

import streamlit as st 
import pandas as pd
import re
import io
import spacy
from word2number import w2n

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

    metadados_por_texto = {}
    for i, texto in enumerate(textos):
        st.markdown(f"**Metadados para {texto['id']}**")
        n = st.number_input(f"Número de campos de metadados para {texto['id']}", min_value=0, max_value=10, value=0, key=f"meta_n_{i}")
        metadados_individuais = {}
        for j in range(n):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input(f"Nome do metadado {j+1}", key=f"meta_nome_{i}_{j}")
            with col2:
                valor = st.text_input(f"Valor do metadado {j+1}", key=f"meta_valor_{i}_{j}")
            if nome:
                metadados_individuais[nome] = valor
        metadados_por_texto[texto["id"]] = metadados_individuais

    # ==================== FUNÇÕES DE PROCESSAMENTO ====================

    def converter_numeros_por_extenso(texto):
        try:
            return str(w2n.word_to_num(texto))
        except:
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

    def gerar_corpus(textos, entidades, siglas, metadados_por_texto):
        dict_entidades = {e["Entidades nomeadas"].lower(): e["Palavra normalizada"].lower() for e in entidades}
        dict_siglas = {s["Sigla"].lower(): s["Significado"] for s in siglas}
        caracteres_especiais = {
            "-": "Hífen", ";": "Ponto e vírgula", '"': "Aspas duplas", "'": "Aspas simples",
            "…": "Reticências", "–": "Travessão", "(": "Parêntese esquerdo", ")": "Parêntese direito",
            "/": "Barra", "%": "Porcentagem"
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
