import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n

# Configuração inicial da página
st.set_page_config(
    page_title="Analisador de Texto e Gerador de Corpus",
    page_icon=":books:",
    layout="wide"
)

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

# ========================== PARTE 1 - PRÉ-ANÁLISE ==========================
st.title("📚 Analisador de Texto e Gerador de Corpus")
st.markdown("---")

with st.expander("🔍 **Ferramenta de Pré-Análise de Texto**", expanded=True):
    st.markdown("""
    **Detecte automaticamente siglas e palavras compostas em seus textos**  
    Esta ferramenta ajuda na preparação de textos para análise linguística.
    """)
    
    texto_input = st.text_area(
        "✍️ Insira seu texto para análise",
        height=200,
        placeholder="Cole ou digite seu texto aqui...",
        help="O texto será analisado para identificar siglas (ex: UFS) e palavras compostas (ex: ensino superior)"
    )

    if st.button("🔍 Analisar texto", type="primary"):
        if texto_input.strip():
            with st.spinner("Processando texto..."):
                siglas = detectar_siglas(texto_input)
                compostas = detectar_palavras_compostas(texto_input)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🧩 Palavras Compostas Detectadas")
                if compostas:
                    st.success(f"Encontradas {len(compostas)} palavras compostas:")
                    for termo in compostas:
                        st.write(f"- {termo}")
                else:
                    st.info("Nenhuma palavra composta encontrada.")

            with col2:
                st.markdown("### 🧾 Siglas Detectadas")
                if siglas:
                    st.success(f"Encontradas {len(siglas)} siglas:")
                    for sigla in siglas:
                        st.write(f"- {sigla}")
                else:
                    st.info("Nenhuma sigla encontrada.")
        else:
            st.warning("Por favor, insira um texto antes de analisar.")

# ========================== PARTE 2 - GERAÇÃO DE CORPUS ==========================
st.markdown("---")
with st.expander("📂 **Gerador de Corpus para IRaMuTeQ**", expanded=True):
    st.markdown("""
    ## 📌 Como usar esta ferramenta
    
    Esta ferramenta transforma seus textos em um corpus formatado para análise no software IRaMuTeQ.
    
    ### 📋 Pré-requisitos:
    1. Prepare uma planilha Excel com **três abas**:
       - `textos_selecionados`: Contendo os textos a serem processados
       - `dic_palavras_compostas`: Dicionário de palavras compostas e suas formas normalizadas
       - `dic_siglas`: Dicionário de siglas e seus significados
    2. Faça o upload da planilha abaixo
    """)
    
    # Exemplo de download
    with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
        st.download_button(
            label="📥 Baixar modelo de planilha",
            data=exemplo,
            file_name="modelo_corpus_iramuteq.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Clique para baixar um modelo de planilha já formatado"
        )

    # Upload de arquivo
    file = st.file_uploader(
        "⬆️ Faça upload da sua planilha Excel",
        type=["xlsx"],
        help="Arquivo deve conter as três abas necessárias"
    )

    # Funções auxiliares da parte 2
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

        estatisticas = f"📊 **Estatísticas do Processamento**\n\n"
        estatisticas += f"✅ **Textos processados:** {total_textos}\n"
        estatisticas += f"🔤 **Siglas substituídas:** {total_siglas}\n"
        estatisticas += f"🔗 **Palavras compostas normalizadas:** {total_compostos}\n"
        estatisticas += f"❌ **Caracteres especiais removidos:** {total_remocoes}\n"
        if total_remocoes > 0:
            estatisticas += "\n🔍 **Detalhe de caracteres removidos:**\n"
            for char, nome in caracteres_especiais.items():
                if contagem_caracteres[char] > 0:
                    estatisticas += f" - {nome} ({char}): {contagem_caracteres[char]}\n"

        return corpus_final, estatisticas

    if file:
        try:
            st.info(f"📂 Processando arquivo '{file.name}'")
            df = pd.read_excel(file, sheet_name=None)
            df_textos = df.get("textos_selecionados", pd.DataFrame())
            df_compostos = df.get("dic_palavras_compostas", pd.DataFrame())
            df_siglas = df.get("dic_siglas", pd.DataFrame())

            if not df_textos.empty and not df_compostos.empty and not df_siglas.empty:
                corpus, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas)

                st.markdown(estatisticas)
                st.download_button(
                    label="📥 Baixar corpus gerado",
                    data=corpus,
                    file_name="corpus_gerado.txt",
                    mime="text/plain"
                )
            else:
                st.warning("O arquivo não contém as abas necessárias.")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")

# Rodapé
st.markdown("---")
footer = """
<div style="text-align: center; padding: 10px; border-radius: 5px;">
    <p style="margin: 0;">👨‍💻 <strong>Desenvolvido por:</strong> José Wendel dos Santos</p>
    <p style="margin: 0;">🏛️ <strong>Instituição:</strong> Universidade Federal de Sergipe (UFS)</p>
    <p style="margin: 0;">📧 <strong>Contato:</strong> eng.wendel@gmail.com</p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
