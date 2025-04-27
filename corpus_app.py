import streamlit as st 
import pandas as pd
import re
import io
import spacy
from word2number import w2n

st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://static.vecteezy.com/system/resources/previews/035/442/418/non_2x/abstract-monochrome-transparent-background-with-grey-chevron-landing-page-template-free-png.png");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    .main .block-container {
        background-color: rgba(14, 17, 23, 1);
        padding: 2rem;
        border-radius: 10px;
        /* min-height REMOVIDO */
        padding-bottom: 5rem; /* espaço extra só no final */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("""   
   <div style='text-align: justify'>
        <h1>ℹ️ Sobre a ferramenta</h1>
        <p>O IRaNoText apresenta originalidade tanto na concepção quanto na implementação técnica. A ferramenta foi criada para suprir uma lacuna existente no processo de preparação de textos para o software IRaMuTeQ, otimizando a compatibilidade textual de forma automatizada e inteligente — um avanço que elimina horas de trabalho manual dos usuários.</p>
        <h2>💡 Funcionalidades</h2>
        <h3>📝 <strong>Análise preliminar dos textos:</strong></h3>
        <p>Envie seus textos para uma análise automatizada inteligente, focada na identificação de siglas e entidades nomeadas — como nomes próprios, locais geográficos e instituições. Além disso, personalize a análise incorporando manualmente termos compostos relevantes para o seu projeto de pesquisa, garantindo um mapeamento lexical ainda mais preciso.</p>
        <h3>🛠️ <strong>Geração do corpus textual:</strong></h3>
        <p>Insira os textos que deseja processar, defina seus próprios dicionários de entidades e siglas, e configure variáveis específicas para enriquecer sua análise. O IRaNoText realizará as seguintes funções: (1) conversão automática de números por extenso em algarismos, (2) normalização linguística avançada (incluindo tratamento de pronomes pospostos e flexões verbo-pronominais), (3) substituição sistemática de entidades e siglas com base em dicionários personalizados, (4) remoção inteligente de caracteres incompatíveis com o IRaMuTeQ e (5) geração automatizada de metadados customizáveis para análise estatística textual. Ao final do processamento, você terá acesso ao corpus textual finalizado e a estatísticas detalhadas sobre a transformação dos dados, possibilitando uma revisão criteriosa antes de salvar os resultados.</p>
        </div>
""", unsafe_allow_html=True)

nlp = spacy.load("pt_core_news_sm")

def detectar_siglas(texto):
    tokens = re.findall(r"\b[A-Z]{2,}\b", texto)
    return sorted(set(tokens))

def detectar_palavras_compostas(texto):
    doc = nlp(texto)
    compostas = [ent.text for ent in doc.ents if len(ent.text.split()) > 1]
    return list(set(compostas))

st.title("IRaNoText: Interface de Reconhecimento Automatizado e Normalização Textual")

tabs = st.tabs([
    "📝 ANÁLISE PRELIMINAR DOS TEXTOS",
    "🛠️ GERAÇÃO DO CORPUS TEXTUAL",
    "📚 TUTORIAL PASSO A PASSO"  # Nova aba de tutorial
])

with tabs[0]:
    st.header("")
    texto_input = st.text_area("", height=350)

    if st.button("🔍 ANALISAR TEXTOS"):
        if texto_input.strip():
            siglas = detectar_siglas(texto_input)
            compostas = detectar_palavras_compostas(texto_input)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 🕵️‍♂️ ENTIDADES NOMEADAS")
                if compostas:
                    st.text_area("Adicione no seu dicionário de entidades nomeadas", "\n".join(sorted(compostas)), height=300)
                else:
                    st.info("Nenhuma entidade nomeada encontrada.")

            with col2:
                st.markdown("### 🔠 SIGLAS DETECTADAS")
                if siglas:
                    st.text_area("Adicione no seu dicionário de siglas", "\n".join(sorted(siglas)), height=300)
                else:
                    st.info("Nenhuma sigla encontrada.")
        else:
            st.warning("Por favor, insira um texto antes de analisar.")

with tabs[1]:
    st.header("")

    st.subheader("📥 INSERIR TEXTOS PARA PROCESSAMENTO")

    textos = []
    input_textos_brutos = st.text_area("Cole aqui os textos (um por linha):", height=200)
    if input_textos_brutos.strip():
        linhas = input_textos_brutos.strip().split("\n")
        for i, linha in enumerate(linhas):
            textos.append({"id": f"texto_{i+1}", "texto": linha})

    st.subheader("📚 DICIONÁRIO DE ENTIDADES NOMEADAS")
    entidades_brutas = st.text_area("Cole aqui ou digite as entidades nomeadas (uma por linha):", height=200)
    entidades = []
    if entidades_brutas.strip():
        for linha in entidades_brutas.strip().split("\n"):
            entidade = linha.strip()
            if entidade:
                forma_normalizada = entidade.replace(" ", "_")
                entidades.append({"Entidades nomeadas": entidade, "Palavra normalizada": forma_normalizada})

    st.subheader("🔠 DICIONÁRIO DE SIGLAS")
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

    
    st.subheader("📊 VARIÁVEIS POR TEXTO")

    st.markdown("**1. Definir campos de variáveis**")
    num_campos_metadados = st.number_input("Quantidade de campos de variáveis para todos os textos", 
                                         min_value=0, max_value=10, value=0, 
                                         key="meta_global_n")

    campos_metadados = []
    for i in range(num_campos_metadados):
        campo = st.text_input(f"Variável {i+1}", 
                             key=f"meta_campo_{i}")
        if campo:
            campos_metadados.append(campo.strip())

    metadados_por_texto = {}
    if campos_metadados and textos:
        st.markdown("**2. Preencher as opções das variáveis para cada texto**")
        
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
            "-": "Hífen", ";": "Ponto e vírgula", '"': "Aspas duplas", "'": "Aspas simples", "…": "Reticências", "–": "Travessão", "(": "Parêntese esquerdo", ")": "Parêntese direito", "/": "Barra", "%": "Porcentagem", "[": "Colchete esquerdo", "]": "Colchete direito","{": "Chave esquerda", "}": "Chave direita", "&": "E comercial", "*": "Asterisco","@": "Arroba", "#": "Cerquilha", "$": "Cifrão", "+": "Mais", "=": "Igual","<": "Menor que", ">": "Maior que", "\\": "Barra invertida", "|": "Barra vertical",       "~": "Til", "`": "Acento grave", "^": "Circunflexo"
           
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
                st.subheader("📄 CORPUS TEXTUAL GERADO")
                st.text_area("🔍 Revise antes de salvar", corpus, height=300)
                st.text_area("📊 Estatísticas do processamento", estatisticas, height=250)

                buf = io.BytesIO()
                buf.write(corpus.encode("utf-8"))
                st.download_button("💾 SALVAR CORPUS TEXTUAL", data=buf.getvalue(), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")
            else:
                st.warning("Nenhum corpus gerado.")
        else:
            st.warning("Por favor, insira pelo menos um texto para processar.")

# Nova aba de tutorial
with tabs[2]:
    st.header("📚 Tutorial Passo a Passo do IRaNoText")
    st.markdown("""
    <div style='text-align: justify; margin-bottom: 20px;'>
        Este tutorial irá guiá-lo através das principais funcionalidades do IRaNoText. 
        Siga os passos abaixo para aproveitar ao máximo a ferramenta.
    </div>
    """, unsafe_allow_html=True)
    
    # Tutorial Item 1
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://drive.google.com/file/d/1DVBUal_aBTcs6PmbYoUf_P4IrqdkoIIQ/view?usp=sharing", caption="Passo 1: Inserção do Texto")
    with col2:
        st.markdown("""
        <div style='background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 5px; height: 200px;'>
            <h3 style='color: #4a90e2;'>1. Inserção do Texto</h3>
            <p>Cole ou digite seu texto na área designada. Você pode inserir um ou vários textos, 
            um por linha. Esta é a matéria-prima que será processada pela ferramenta.</p>
            <p><strong>Dica:</strong> Certifique-se de que o texto esteja limpo e formatado 
            corretamente antes de iniciar a análise.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tutorial Item 2
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://via.placeholder.com/300x200?text=Passo+2", caption="Passo 2: Análise Automática")
    with col2:
        st.markdown("""
        <div style='background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 5px; height: 200px;'>
            <h3 style='color: #4a90e2;'>2. Análise Automática</h3>
            <p>Clique no botão "ANALISAR TEXTOS" para que o sistema identifique automaticamente 
            entidades nomeadas e siglas presentes no texto.</p>
            <p><strong>Dica:</strong> Revise cuidadosamente as sugestões do sistema, pois ele pode 
            não capturar todos os termos específicos do seu domínio.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tutorial Item 3
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://via.placeholder.com/300x200?text=Passo+3", caption="Passo 3: Dicionários Personalizados")
    with col2:
        st.markdown("""
        <div style='background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 5px; height: 200px;'>
            <h3 style='color: #4a90e2;'>3. Dicionários Personalizados</h3>
            <p>Adicione seus próprios dicionários de entidades nomeadas e siglas. Para entidades, 
            insira uma por linha. Para siglas, especifique a sigla e seu significado.</p>
            <p><strong>Dica:</strong> Quanto mais completo seu dicionário, melhor será o processamento.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tutorial Item 4
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://via.placeholder.com/300x200?text=Passo+4", caption="Passo 4: Metadados")
    with col2:
        st.markdown("""
        <div style='background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 5px; height: 200px;'>
            <h3 style='color: #4a90e2;'>4. Definição de Metadados</h3>
            <p>Especifique as variáveis que deseja associar a cada texto. Estas serão incluídas 
            como metadados no corpus final, permitindo análises mais ricas no IRaMuTeQ.</p>
            <p><strong>Dica:</strong> Pense nas variáveis que serão úteis para sua análise (ex.: gênero, idade, etc.).</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tutorial Item 5
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://via.placeholder.com/300x200?text=Passo+5", caption="Passo 5: Geração do Corpus")
    with col2:
        st.markdown("""
        <div style='background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 5px; height: 200px;'>
            <h3 style='color: #4a90e2;'>5. Geração do Corpus</h3>
            <p>Clique em "GERAR CORPUS TEXTUAL" para processar seus textos. O sistema realizará:</p>
            <ul>
                <li>Conversão de números por extenso</li>
                <li>Normalização linguística</li>
                <li>Substituição de entidades e siglas</li>
                <li>Remoção de caracteres incompatíveis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Tutorial Item 6
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://via.placeholder.com/300x200?text=Passo+6", caption="Passo 6: Revisão e Download")
    with col2:
        st.markdown("""
        <div style='background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 5px; height: 200px;'>
            <h3 style='color: #4a90e2;'>6. Revisão e Download</h3>
            <p>Revise o corpus gerado e as estatísticas de processamento. Quando satisfeito, 
            clique no botão para baixar o arquivo no formato compatível com o IRaMuTeQ.</p>
            <p><strong>Dica:</strong> Sempre revise o corpus antes de usar no IRaMuTeQ para 
            garantir que todas as transformações foram aplicadas corretamente.</p>
        </div>
        """, unsafe_allow_html=True)
    
st.markdown("""  
---  
<div style='text-align: center; margin-top: 20px; font-size: 0.9em; color: #b0b0b0; line-height: 1.4;'>
    <p style="margin: 0;">👨‍💻 <strong>Desenvolvedores:</strong> Me. José Wendel dos Santos | Prof. Dr. Luciano Fernandes Monteiro</p>
    <p style="margin: 0;">🏛️ <strong>Instituição:</strong> Universidade Federal de Sergipe (UFS)</p>
    <p style="margin: 0;">📧 <strong>Contato:</strong> <a href="mailto:iranotext@gmail.com" style="color: #4a90e2; text-decoration: none;">iranotext@gmail.com</a></p>
</div>
<div style='text-align: center; margin-top: 20px; font-size: 0.9em; color: #b0b0b0;'>
    Este software é um complemento independente e não é afiliado oficialmente ao IRaMuTeQ. Acesse o
    <a href="http://www.iramuteq.org/" target="_blank" style="color: #4a90e2; text-decoration: none;">site oficial</a>.
</div>
""", unsafe_allow_html=True)
