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

    # ==================== SEÇÃO ATUALIZADA DE METADADOS ====================
    st.subheader("📊 Metadados por Texto")

    # 1. Definir estrutura de metadados (campos comuns a todos textos)
    st.markdown("**1. Definir Campos de Metadados**")
    num_campos_metadados = st.number_input("Quantidade de campos de metadados para todos os textos", 
                                         min_value=0, max_value=10, value=0, 
                                         key="meta_global_n")

    campos_metadados = []
    for i in range(num_campos_metadados):
        campo = st.text_input(f"Nome do campo {i+1} (ex: 'Autor', 'Data')", 
                             key=f"meta_campo_{i}")
        if campo:
            campos_metadados.append(campo.strip())

    # 2. Preencher valores para cada texto
    metadados_por_texto = {}
    if campos_metadados and textos:
        st.markdown("**2. Preencher Valores para Cada Texto**")
        
        # Cria tabela editável
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

        # Converte para o formato original
        for _, row in df_editado.iterrows():
            metadados = {}
            for campo in campos_metadados:
                if pd.notna(row[campo]) and row[campo].strip():
                    metadados[campo] = row[campo].strip()
            metadados_por_texto[row['ID Texto']] = metadados

    # ==================== FUNÇÕES DE PROCESSAMENTO ====================

    def converter_numeros_por_extenso(texto):
        if not texto:
            return texto
            
        doc = nlp(texto.lower())
        palavras = [token.text for token in doc]
        
        i = 0
        resultado = []
        n = len(palavras)
        
        while i < n:
            palavra = palavras[i]
            try:
                # Tenta converter a palavra atual
                num = w2n.word_to_num(palavra)
                resultado.append(str(num))
                i += 1
            except:
                # Se não for número, verifica combinações (ex: "vinte e cinco")
                if i + 2 < n and palavras[i+1] == "e":
                    try:
                        comb = f"{palavra} {palavras[i+1]} {palavras[i+2]}"
                        num = w2n.word_to_num(comb)
                        resultado.append(str(num))
                        i += 3
                        continue
                    except:
                        pass
                # Se não conseguir converter, mantém a palavra original
                resultado.append(palavra)
                i += 1
                
        return " ".join(resultado)

    def processar_palavras_com_se(texto):
        return re.sub(r"(\b\w+)-se\b", r"se \1", texto)

    def processar_pronomes_pospostos(texto):
        if texto is None:
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
        dict_siglas = {s["Sigla"].upper(): s["Significado"] for s in siglas}  # Alterado para upper case
        
        # Lista expandida de caracteres especiais
        caracteres_especiais = {
            "-": "Hífen", ";": "Ponto e vírgula", '"': "Aspas duplas", "'": "Aspas simples",
            "…": "Reticências", "–": "Travessão", "(": "Parêntese esquerdo", ")": "Parêntese direito",
            "/": "Barra", "%": "Porcentagem", "!": "Exclamação", "?": "Interrogação",
            ":": "Dois pontos", ",": "Vírgula", ".": "Ponto", "[": "Colchete esquerdo",
            "]": "Colchete direito", "{": "Chave esquerda", "}": "Chave direita",
            "&": "E comercial", "*": "Asterisco", "@": "Arroba", "#": "Cerquilha",
            "$": "Cifrão", "+": "Mais", "=": "Igual", "<": "Menor que", ">": "Maior que",
            "\\": "Barra invertida", "|": "Barra vertical", "~": "Til", "`": "Acento grave",
            "^": "Circunflexo", "_": "Sublinhado"
        }

        contagem_caracteres = {k: 0 for k in caracteres_especiais}
        total_textos = total_siglas = total_entidades = total_remocoes = 0
        corpus_final = ""

        for texto_info in textos:
            texto = texto_info["texto"]
            id_val = texto_info["id"]
            if not texto.strip():
                continue

            # Processamento do texto
            texto_corrigido = texto.lower()
            texto_corrigido = converter_numeros_por_extenso(texto_corrigido)
            texto_corrigido = processar_palavras_com_se(texto_corrigido)
            texto_corrigido = processar_pronomes_pospostos(texto_corrigido)
            total_textos += 1

            # Substituição de siglas
            for sigla, significado in dict_siglas.items():
                # Remove siglas entre parênteses
                texto_corrigido = re.sub(rf"\s*\({re.escape(sigla)}\)\s*", " ", texto_corrigido)
                # Substitui siglas soltas
                texto_corrigido = re.sub(rf"\b{re.escape(sigla)}\b", significado, texto_corrigido)
                total_siglas += texto_corrigido.count(significado)

            # Substituição de entidades
            for termo, substituto in dict_entidades.items():
                if termo.lower() in texto_corrigido.lower():
                    texto_corrigido = re.sub(rf"\b{re.escape(termo.lower())}\b", substituto, texto_corrigido)
                    total_entidades += 1

            # Remoção de caracteres especiais
            for char, desc in caracteres_especiais.items():
                count = texto_corrigido.count(char)
                if count > 0:
                    texto_corrigido = texto_corrigido.replace(char, " ")
                    contagem_caracteres[char] += count
                    total_remocoes += count

            # Normalização de espaços
            texto_corrigido = re.sub(r"\s+", " ", texto_corrigido.strip())

            # Adiciona metadados
            metadata = f"**** *ID_{id_val}"
            for k, v in metadados_por_texto.get(id_val, {}).items():
                if v:
                    metadata += f" *{k.replace(' ', '_')}_{v.replace(' ', '_').replace('-', '_')}"

            corpus_final += f"{metadata}\n{texto_corrigido}\n\n"

        # Estatísticas
        estatisticas = f"Textos processados: {total_textos}\nSiglas substituídas: {total_siglas}\n"
        estatisticas += f"Entidades substituídas: {total_entidades}\nCaracteres especiais removidos: {total_remocoes}\n"
        for c, label in caracteres_especiais.items():
            if contagem_caracteres[c] > 0:
                estatisticas += f" - {label} ({c}): {contagem_caracteres[c]}\n"

        return corpus_final, estatisticas

    if st.button("🚀 GERAR CORPUS TEXTUAL"):
        if textos:
            corpus, estatisticas = gerar_corpus(textos, entidades, siglas, metadados_por_texto)
            if corpus.strip():
                st.success("Corpus gerado com sucesso!")
                st.subheader("📄 Corpus Textual Gerado")
                st.text_area("Veja o Corpus Gerado", corpus, height=400)
                
                # Botão de download
                buffer = io.StringIO()
                buffer.write(corpus)
                st.download_button(
                    label="⬇️ Baixar Corpus",
                    data=buffer.getvalue(),
                    file_name="corpus_textual.txt",
                    mime="text/plain"
                )
                
                st.subheader("📊 Estatísticas do Corpus")
                st.text_area("Estatísticas", estatisticas, height=200)
            else:
                st.warning("Não há dados suficientes para gerar o corpus.")
        else:
            st.warning("Por favor, insira textos antes de gerar o corpus.")
