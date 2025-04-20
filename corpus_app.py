import streamlit as st
import pandas as pd
import re
import io
import spacy
from word2number import w2n
from streamlit_extras.colored_header import colored_header

# Carregar modelo do spaCy
nlp = spacy.load("pt_core_news_sm")

# Configuração inicial da página
st.set_page_config(
    page_title="IRaText",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stTextArea textarea {
            border-radius: 8px;
        }
        .stButton button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .stDownloadButton button {
            width: 100%;
            border-radius: 8px;
        }
        .stTab {
            border-radius: 8px;
            padding: 15px;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .css-1aumxhk {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .footer {
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #e1e4e8;
            font-size: 0.9rem;
            color: #6c757d;
        }
        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# Funções da parte 1
def detectar_siglas(texto):
    tokens = re.findall(r"\b[A-Z]{2,}\b", texto)
    return sorted(set(tokens))

def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    compostas = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return list(set(compostas))

# ========================== CABEÇALHO ==========================
colored_header(
    label="IRaText: Geração de Corpus Textual para IRaMuTeQ",
    description="Ferramenta para análise e preparação de textos para análise textual no IRaMuTeQ",
    color_name="blue-70"
)

# ========================== ABAS PRINCIPAIS ==========================
tab1, tab2 = st.tabs(["📝 Análise preliminar dos textos", "🛠️ Normalização do corpus textual"])

with tab1:
    # ========================== PARTE 1 - PRÉ-ANÁLISE ==========================
    st.subheader("Detecção de Siglas e Palavras Compostas", divider='blue')
    
    with st.container():
        texto_input = st.text_area(
            "**Insira o texto para análise**",
            height=200,
            placeholder="Cole seu texto aqui para identificar siglas e palavras compostas..."
        )
        
        col1, col2, _ = st.columns([1,1,3])
        with col1:
            analyze_btn = st.button("🔍 Analisar texto", type="primary", use_container_width=True)
        with col2:
            clear_btn = st.button("🧹 Limpar", use_container_width=True)
    
    if analyze_btn and texto_input.strip():
        with st.spinner("Analisando texto..."):
            siglas = detectar_siglas(texto_input)
            compostas = detectar_palavras_compostas(texto_input)
            
            st.success("Análise concluída!")
            
            col1, col2 = st.columns(2, gap="large")
            with col1:
                with st.container():
                    st.markdown("##### 🧩 Palavras Compostas Detectadas")
                    if compostas:
                        for termo in compostas:
                            st.markdown(f"- `{termo}`")
                    else:
                        st.info("Nenhuma palavra composta encontrada.", icon="ℹ️")
            
            with col2:
                with st.container():
                    st.markdown("##### 🧾 Siglas Detectadas")
                    if siglas:
                        for sigla in siglas:
                            st.markdown(f"- `{sigla}`")
                    else:
                        st.info("Nenhuma sigla encontrada.", icon="ℹ️")
    elif analyze_btn and not texto_input.strip():
        st.warning("Por favor, insira um texto antes de analisar.", icon="⚠️")

with tab2:
    # ========================== PARTE 2 - GERAÇÃO DE CORPUS ==========================
    st.subheader("Gerador de Corpus Textual", divider='blue')
    
    # Sidebar com instruções
    with st.sidebar:
        st.markdown("""
        <div style="background: #f0f2f6; padding: 15px; border-radius: 10px;">
            <h4 style="color: #2c3e50; margin-top: 0;">📌 Instruções</h4>
            <p style="font-size: 0.9rem;">Esta ferramenta foi desenvolvida para facilitar a geração de corpus textual compatível com o IRaMuTeQ.</p>
            
            <h5 style="color: #2c3e50; margin-bottom: 5px;">Estrutura da Planilha</h5>
            <p style="font-size: 0.85rem;">Sua planilha deve conter <strong>três abas</strong>:</p>
            <ol style="font-size: 0.85rem; padding-left: 20px;">
                <li><strong>textos_selecionados</strong>: Coleção de textos para normalização</li>
                <li><strong>dic_palavras_compostas</strong>: Palavras compostas e suas formas normalizadas</li>
                <li><strong>dic_siglas</strong>: Siglas e seus significados</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    # Seção de download de modelos
    with st.container():
        st.markdown("##### 📥 Modelos para Download")
        col1, col2 = st.columns(2, gap="medium")
        
        with col1:
            with st.container(border=True):
                st.markdown("**Modelo de planilha**")
                st.markdown("Baixe o template com a estrutura necessária")
                with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
                    st.download_button(
                        label="Baixar modelo",
                        data=exemplo,
                        file_name="gerar_corpus_iramuteq.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
        
        with col2:
            with st.container(border=True):
                st.markdown("**Exemplo de textos**")
                st.markdown("Planilha com textos de exemplo para análise")
                with open("textos_selecionados.xlsx", "rb") as textos:
                    st.download_button(
                        label="Baixar exemplos",
                        data=textos,
                        file_name="textos_selecionados.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
    
    # Upload de arquivo
    with st.container(border=True):
        st.markdown("##### 📤 Envie sua planilha")
        file = st.file_uploader(
            "Selecione o arquivo Excel (.xlsx) com seus dados",
            type=["xlsx"],
            label_visibility="collapsed"
        )
    
    # Funções auxiliares da parte 2 (mantidas as mesmas do código original)
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

        estatisticas = f"Textos processados: {total_textos}\n"
        estatisticas += f"Siglas removidas/substituídas: {total_siglas}\n"
        estatisticas += f"Palavras compostas substituídas: {total_compostos}\n"
        estatisticas += f"Caracteres especiais removidos: {total_remocoes}\n"
        for char, nome in caracteres_especiais.items():
            if contagem_caracteres[char] > 0:
                estatisticas += f" - {nome} ({char}) : {contagem_caracteres[char]}\n"

        return corpus_final, estatisticas

    if file:
        try:
            xls = pd.ExcelFile(file)
            df_textos = xls.parse("textos_selecionados")
            df_compostos = xls.parse("dic_palavras_compostas")
            df_siglas = xls.parse("dic_siglas")
            df_textos.columns = [col.strip().lower() for col in df_textos.columns]

            if st.button("🚀 Gerar Corpus Textual", type="primary", use_container_width=True):
                with st.spinner("Processando arquivo e gerando corpus..."):
                    corpus, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas)

                if corpus.strip():
                    st.success("Corpus gerado com sucesso!", icon="✅")
                    
                    # Exibição do corpus
                    with st.expander("📄 Visualizar Corpus Textual Gerado", expanded=True):
                        st.code(corpus, language="text")
                    
                    # Estatísticas em cards
                    st.markdown("##### 📊 Estatísticas do Processamento")
                    stats = estatisticas.split('\n')
                    for stat in stats:
                        if stat.strip():
                            st.markdown(f"""
                            <div class="stat-card">
                                {stat}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Botão de download
                    buf = io.BytesIO()
                    buf.write(corpus.encode("utf-8"))
                    st.download_button(
                        "💾 Baixar Corpus Textual",
                        data=buf.getvalue(),
                        file_name="corpus_IRaMuTeQ.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    st.warning("Nenhum corpus foi gerado. Verifique os dados na planilha.", icon="⚠️")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {str(e)}", icon="❌")

# ========================== RODAPÉ ==========================
st.markdown("""
<div class="footer">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <strong>IRaText</strong> - Ferramenta para Geração de Corpus Textual
        </div>
        <div>
            <strong>Autor:</strong> José Wendel dos Santos | <strong>Instituição:</strong> Universidade Federal de Sergipe (UFS)
        </div>
    </div>
    <div style="margin-top: 10px; text-align: center;">
        <small>© 2023 - Versão 1.0 | Contato: eng.wendel@gmail.com</small>
    </div>
</div>
""", unsafe_allow_html=True)
