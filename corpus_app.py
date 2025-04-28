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
        <p>O IRaNoText se destaca pela inovação tanto na concepção quanto na implementação técnica. Desenvolvido para preencher uma lacuna no processo de preparação de textos para o IRaMuTeQ, a ferramenta automatiza e otimiza a compatibilidade textual, reduzindo significativamente o tempo e o esforço manual dos usuários.</p>
        <h2>💡 Funcionalidades</h2>
        <h3>📝 <strong>Análise preliminar dos textos:</strong></h3>
        <p>O IRaNoText executa uma análise automatizada avançada dos textos inseridos, com foco na identificação de siglas e entidades nomeadas, como nomes próprios, locais geográficos e instituições. Além disso, possibilita a inclusão manual de termos compostos relevantes, assegurando um mapeamento lexical mais preciso e adaptado às necessidades específicas de cada projeto de pesquisa.</p>
        <h3>🛠️ <strong>Geração do corpus textual:</strong></h3>
        <p>O IRaNoText permite a inserção de textos para processamento, a definição de dicionários personalizados de entidades e siglas, e a configuração de variáveis específicas para otimização da análise. O processamento inclui: (i) conversão automática de números por extenso em algarismos, (ii) normalização linguística avançada (incluindo tratamento de pronomes pospostos e flexões verbo-pronominais), (iii) substituição sistemática de entidades e siglas com base em dicionários personalizados, (iv) remoção inteligente de caracteres incompatíveis com o IRaMuTeQ e (v) geração automatizada de metadados customizáveis para análise estatística textual. Ao final do processo, o corpus textual final é gerado junto a estatísticas detalhadas sobre as transformações realizadas.</p> 
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
    "📚 INSTRUÇÕES DE USO"
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


with tabs[2]:
    st.header("")
    st.markdown("""
    <div style='text-align: justify; margin-bottom: 20px;'>
        Este tutorial irá guiá-lo através das principais funcionalidades do IRaNoText. 
        Siga os passos abaixo para aproveitar ao máximo a ferramenta.
    </div>
    """, unsafe_allow_html=True)
    
   
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://i.imgur.com/0xPuvoc.png", caption="Passo 1: Inserção do texto")
    with col2:
        st.markdown("""
        <div style='background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 5px; height: 200px;'>
            <h3 style='color: #4a90e2;'>1. Inserção do texto</h3>
            <p>Cole ou digite seu texto na área designada, um por linha. Certifique-se de que esteja sem formatação, pois o uso de negrito, itálico ou marcadores pode interferir no processamento.</p>
            </div>
        """, unsafe_allow_html=True)
    
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://i.imgur.com/yLmiVB5.png", caption="Passo 2: Análise automática")
    with col2:
        st.markdown("""
        <div style='background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 5px; height: 200px;'>
            <h3 style='color: #4a90e2;'>2. Análise automática</h3>
            <p>Clique no botão "🔍 ANALISAR TEXTOS" para que o sistema identifique automaticamente entidades nomeadas e siglas presentes no texto. Revise as sugestões, pois o sistema pode não capturar todos os termos específicos da sua área.</p>
        </div>
        """, unsafe_allow_html=True)
    
  
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://i.imgur.com/llfE3QW.png", caption="Passo 3: Dicionários personalizados")
    with col2:
        st.markdown("""
        <div style='background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 5px; height: 200px;'>
            <h3 style='color: #4a90e2;'>3. Dicionários personalizados</h3>
            <p>Cole seu texto na área indicada. Complete os dicionários com as entidades e siglas sugeridas, além de outras que considerar relevantes. Para entidades nomeadas, insira uma por linha. Para siglas, informe a quantidade e depois cadastre cada sigla com seu respectivo significado.</p>    
        </div>
        """, unsafe_allow_html=True)
    
   
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://i.imgur.com/736PSFz.png", caption="Passo 4: Definição de variáveis")
    with col2:
        st.markdown("""
        <div style='background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 5px; height: 200px;'>
            <h3 style='color: #4a90e2;'>4. Definição de variáveis</h3>
            <p>Especifique as variáveis que deseja associar a cada texto. Elas serão incluídas como metadados no corpus textual, permitindo análises mais abrangentes no IRaMuTeQ. Atenção: não utilize acentuação!</p>
            </div>
        """, unsafe_allow_html=True)
    
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://i.imgur.com/e5dMw18.png", caption="Passo 5: Geração do corpus textual")
    with col2:
        st.markdown("""
        <div style='background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 5px; height: 200px;'>
            <h3 style='color: #4a90e2;'>5. Geração do corpus textual</h3>
            <p>Clique em '🚀 GERAR CORPUS TEXTUAL' para processar seus textos. Revise o corpus textual gerado e as estatísticas de processamento. Quando estiver satisfeito(a), salve o arquivo em uma pasta específica para suas análises no IRaMuTeQ.</p>
            </div>
        """, unsafe_allow_html=True)
    

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://i.imgur.com/fVGGTqB.png", caption="Passo 6: Arquivo para importação")
    with col2:
        st.markdown("""
        <div style='background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 5px; height: 200px;'>
            <h3 style='color: #4a90e2;'>6. Arquivo para importação</h3>
            <p>Após baixar o arquivo .txt gerado, abra-o em um editor de texto. Verifique se todas as transformações foram aplicadas corretamente e se o corpus textual está em conformidade com as exigências do IRaMuTeQ antes de importá-lo.
            </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://i.imgur.com/3E6qtj2.png", caption="Passo 7: Arquivo para importação")
    with col2:
        st.markdown("""
        <div style='background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 5px; height: 200px;'>
            <h3 style='color: #4a90e2;'>6. Arquivo para importação</h3>
            <p>Após baixar o arquivo .txt gerado, abra-o em um editor de texto. Verifique se todas as transformações foram aplicadas corretamente e se o corpus textual está em conformidade com as exigências do IRaMuTeQ antes de importá-lo.
            </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://i.imgur.com/taD3GZM.png", caption="Passo 8: Arquivo para importação")
    with col2:
        st.markdown("""
        <div style='background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 5px; height: 200px;'>
            <h3 style='color: #4a90e2;'>6. Arquivo para importação</h3>
            <p>Após baixar o arquivo .txt gerado, abra-o em um editor de texto. Verifique se todas as transformações foram aplicadas corretamente e se o corpus textual está em conformidade com as exigências do IRaMuTeQ antes de importá-lo.
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='margin-top: 30px; text-align: justify;'>
        <p>Agora que seu corpus textual foi processado, você pode realizar diversas análises no IRaMuTeQ para explorar e interpretar seus dados qualitativos. 
        As análises disponíveis são:</p>
        <ul>
            <li><strong>Análise lexicográfica:</strong> Estuda o uso das palavras e suas relações dentro do texto, identificando padrões linguísticos e temáticos.</li>
            <li><strong>Especificidades:</strong> Realiza uma análise multivariada para identificar associações entre variáveis e revelar padrões no corpus textual.</li>
            <li><strong>Análise Fatorial de Correspondência (AFC):</strong> Explora as relações entre palavras e variáveis em mapas bidimensionais, ajudando a identificar as características particulares de um texto ou conjunto de textos.</li>
            <li><strong>Distância Labbé:</strong> Mede a distância semântica entre palavras, permitindo identificar o grau de similaridade entre termos dentro do texto.</li>
            <li><strong>Classificação Hierárquica Descendente (CHD):</strong> Identifica as palavras mais representativas e organiza-as hierarquicamente, ajudando a entender a estrutura de significados no texto.</li>
            <li><strong>Análise de Similitude:</strong> Explora a relação entre palavras dentro de um corpus, identificando quais termos são semanticamente semelhantes ou frequentemente ocorrem próximos uns dos outros.</li>
        </ul>
        <p>Consulte o manual do IRaMuTeQ para explorar todos os recursos!</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""  
---  
<div style='text-align: center; margin-top: 20px; font-size: 0.9em; color: #b0b0b0; line-height: 1.4;'>
    <p style="margin: 0;">© 2025 IRaNoText. Todos os direitos reservados. Licenciado sob a <a href="https://opensource.org/licenses/MIT" style="color: #4a90e2; text-decoration: none;">Licença MIT</a>.</p>
    <p style="margin: 0;">Esta aplicação utiliza tecnologias licenciadas sob <a href="https://opensource.org/licenses/Apache-2.0" style="color: #4a90e2; text-decoration: none;">Apache 2.0</a>, <a href="https://opensource.org/licenses/MIT" style="color: #4a90e2; text-decoration: none;">MIT</a> e <a href="https://creativecommons.org/licenses/by-sa/4.0/" style="color: #4a90e2; text-decoration: none;">CC BY-SA 4.0</a>.</p>
    <p style="margin: 0;">📧 <strong>Contato:</strong> <a href="mailto:iranotext@gmail.com" style="color: #4a90e2; text-decoration: none;">iranotext@gmail.com</a></p>
</div>
<div style='text-align: center; margin-top: 20px; font-size: 0.9em; color: #b0b0b0;'>
    Este software é um complemento independente e não é afiliado oficialmente ao IRaMuTeQ. Acesse o
    <a href="http://www.iramuteq.org/" target="_blank" style="color: #4a90e2; text-decoration: none;">site oficial</a>.
</div>
""", unsafe_allow_html=True)
