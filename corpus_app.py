import streamlit as st
import pandas as pd
import re
import io
from word2number import w2n
from datetime import datetime
import zipfile
import os

# Configurações iniciais
st.set_page_config(layout="wide", page_title="Gerador de Corpus IRaMuTeQ", page_icon="📚")

# Função para converter números por extenso para algarismos
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

# Função para processar palavras compostas com "-se"
def processar_palavras_com_se(texto):
    return re.sub(r"(\b\w+)-se\b", r"se \1", texto)

# Função para processar pronomes oblíquos pós-verbais
def processar_pronomes_pospostos(texto):
    texto = re.sub(r'\b(\w+)-se\b', r'se \1', texto)
    texto = re.sub(r'\b(\w+)-([oa]s?)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)-(lhe|lhes)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)-(me|te|nos|vos)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)[áéíóúâêô]?-([oa]s?)\b', r'\2 \1', texto)
    texto = re.sub(r'\b(\w+)[áéíóúâêô]-(lo|la|los|las)-ia\b', r'\2 \1ia', texto)
    return texto

# Função para verificar estrutura da planilha
def verificar_estrutura(df_textos, df_compostos, df_siglas):
    erros = []
    
    # Verificar colunas obrigatórias
    if "textos selecionados" not in df_textos.columns.str.lower():
        erros.append("A aba 'textos_selecionados' deve conter a coluna 'textos selecionados'")
    
    if len(df_textos) == 0:
        erros.append("A aba 'textos_selecionados' está vazia")
    
    # Verificar se há pelo menos uma coluna de metadados além do texto
    if len(df_textos.columns) < 2:
        erros.append("Adicione pelo menos uma coluna de metadados (ex: id, autor, etc.) na aba 'textos_selecionados'")
    
    return erros

# Função para gerar relatório detalhado
def gerar_relatorio(total_textos, total_siglas, total_compostos, total_remocoes, contagem_caracteres, tempo_processamento):
    relatorio = f"RELATÓRIO DE PROCESSAMENTO - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
    relatorio += "="*50 + "\n"
    relatorio += f"📝 Textos processados: {total_textos}\n"
    relatorio += f"🔤 Siglas expandidas: {total_siglas}\n"
    relatorio += f"🔗 Palavras compostas normalizadas: {total_compostos}\n"
    relatorio += f"❌ Caracteres especiais removidos: {total_remocoes}\n\n"
    
    relatorio += "📊 Detalhe de caracteres especiais removidos:\n"
    for char, nome in caracteres_especiais.items():
        if contagem_caracteres[char] > 0:
            relatorio += f" - {nome} ({char}): {contagem_caracteres[char]}\n"
    
    relatorio += f"\n⏱ Tempo de processamento: {tempo_processamento:.2f} segundos\n"
    return relatorio

# Função principal
def gerar_corpus(df_textos, df_compostos, df_siglas):
    inicio = datetime.now()
    
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

    global caracteres_especiais
    caracteres_especiais = {
        "-": "Hífen", ";": "Ponto e vírgula", '"': "Aspas duplas", "'": "Aspas simples",
        "…": "Reticências", "–": "Travessão", "(": "Parêntese esquerdo", ")": "Parêntese direito",
        "/": "Barra", "%": "Porcentagem", "&": "E comercial", "@": "Arroba",
        "#": "Cerquilha", "*": "Asterisco", "+": "Mais", "=": "Igual",
        "<": "Menor que", ">": "Maior que", "[": "Colchete esquerdo", "]": "Colchete direito",
        "{": "Chave esquerda", "}": "Chave direita", "\\": "Barra invertida", "|": "Barra vertical",
        "^": "Circunflexo", "~": "Til", "`": "Acento grave"
    }
    
    contagem_caracteres = {k: 0 for k in caracteres_especiais}
    total_textos = 0
    total_siglas = 0
    total_compostos = 0
    total_remocoes = 0
    corpus_final = ""
    textos_originais = []
    textos_processados = []

    for _, row in df_textos.iterrows():
        texto = str(row.get("textos selecionados", ""))
        id_val = row.get("id", "")
        if not texto.strip():
            continue

        texto_original = texto
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
        textos_originais.append(f"=== ID: {id_val} ===\n{texto_original}\n")
        textos_processados.append(f"=== ID: {id_val} ===\n{texto_corrigido}\n")

    tempo_processamento = (datetime.now() - inicio).total_seconds()
    
    estatisticas = gerar_relatorio(total_textos, total_siglas, total_compostos, 
                                 total_remocoes, contagem_caracteres, tempo_processamento)
    
    return corpus_final, estatisticas, "\n".join(textos_originais), "\n".join(textos_processados)

# Interface Streamlit
def main():
    st.title("📚 Gerador de corpus textual para IRaMuTeQ")
    
    # Menu lateral
    st.sidebar.title("Configurações")
    opcao_visualizacao = st.sidebar.radio("Modo de visualização:", ["Completo", "Simplificado"])
    mostrar_instrucoes = st.sidebar.checkbox("Mostrar instruções", value=True)
    
    # Abas principais
    tab1, tab2, tab3 = st.tabs(["📤 Upload de Arquivos", "⚙️ Configurações Avançadas", "ℹ️ Sobre"])
    
    with tab1:
        if mostrar_instrucoes:
            st.markdown("""
            ### 📌 Instruções

            Esta ferramenta foi desenvolvida para facilitar a geração de corpus textual compatível com o IRaMuTeQ.

            Envie um arquivo do Excel **.xlsx** com a estrutura correta para que o corpus possa ser gerado automaticamente.

            Sua planilha deve conter **três abas (planilhas internas)** com os seguintes nomes e finalidades:

            1. **`textos_selecionados`** : coleção de textos que serão transformados de acordo com as regras de normalização.  
            2. **`dic_palavras_compostas`** : permite substituir palavras compostas por suas formas normalizadas.  
            3. **`dic_siglas`** : tem a finalidade de expandir siglas para suas formas completas.
            """)

        with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
            st.download_button(
                label="📥 Baixar modelo de planilha",
                data=exemplo,
                file_name="gerar_corpus_iramuteq.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        file = st.file_uploader("Envie sua planilha preenchida", type=["xlsx"], key="file_uploader")

        if file:
            try:
                xls = pd.ExcelFile(file)
                required_sheets = ["textos_selecionados", "dic_palavras_compostas", "dic_siglas"]
                
                # Verificar se todas as abas necessárias estão presentes
                missing_sheets = [sheet for sheet in required_sheets if sheet not in xls.sheet_names]
                if missing_sheets:
                    st.error(f"Faltam as seguintes abas na planilha: {', '.join(missing_sheets)}")
                    return
                
                df_textos = xls.parse("textos_selecionados")
                df_compostos = xls.parse("dic_palavras_compostas")
                df_siglas = xls.parse("dic_siglas")
                df_textos.columns = [col.strip().lower() for col in df_textos.columns]

                # Verificar estrutura
                erros = verificar_estrutura(df_textos, df_compostos, df_siglas)
                if erros:
                    for erro in erros:
                        st.error(erro)
                    return

                # Visualização prévia dos dados
                with st.expander("🔍 Visualizar dados carregados"):
                    st.subheader("Textos Selecionados (amostra)")
                    st.dataframe(df_textos.head())
                    
                    st.subheader("Palavras Compostas (amostra)")
                    st.dataframe(df_compostos.head())
                    
                    st.subheader("Siglas (amostra)")
                    st.dataframe(df_siglas.head())

                if st.button("🚀 Gerar Corpus Textual", key="generate_button"):
                    with st.spinner("Processando textos, aguarde..."):
                        corpus, estatisticas, originais, processados = gerar_corpus(df_textos, df_compostos, df_siglas)

                    if corpus.strip():
                        st.success("✅ Corpus gerado com sucesso!")
                        
                        # Exibir estatísticas
                        with st.expander("📊 Estatísticas detalhadas"):
                            st.text(estatisticas)
                        
                        # Criar arquivos ZIP
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                            zip_file.writestr("corpus_IRaMuTeQ.txt", corpus.encode('utf-8'))
                            zip_file.writestr("textos_originais.txt", originais.encode('utf-8'))
                            zip_file.writestr("textos_processados.txt", processados.encode('utf-8'))
                            zip_file.writestr("relatorio_processamento.txt", estatisticas.encode('utf-8'))
                        
                        # Botões de download
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.download_button(
                                label="📄 Baixar Corpus",
                                data=corpus.encode('utf-8'),
                                file_name="corpus_IRaMuTeQ.txt",
                                mime="text/plain"
                            )
                        with col2:
                            st.download_button(
                                label="📦 Baixar Tudo (ZIP)",
                                data=zip_buffer.getvalue(),
                                file_name="corpus_completo.zip",
                                mime="application/zip"
                            )
                        with col3:
                            st.download_button(
                                label="📊 Baixar Relatório",
                                data=estatisticas.encode('utf-8'),
                                file_name="relatorio_processamento.txt",
                                mime="text/plain"
                            )
                        
                        # Visualização do corpus
                        with st.expander("👀 Visualizar Corpus Gerado"):
                            st.text(corpus[:5000] + ("..." if len(corpus) > 5000 else ""))
                    else:
                        st.warning("⚠️ Nenhum texto processado. Verifique os dados da planilha.")

            except Exception as e:
                st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
                st.error("Verifique a estrutura da planilha conforme o modelo fornecido.")

    with tab2:
        st.header("Configurações Avançadas")
        
        st.subheader("Caracteres Especiais")
        st.write("Configure quais caracteres especiais devem ser removidos ou substituídos:")
        
        # Editar lista de caracteres especiais
        caracteres_editaveis = st.text_area(
            "Lista de caracteres especiais (um por linha, formato: caractere=descrição)",
            value="\n".join([f"{k}={v}" for k, v in caracteres_especiais.items()]),
            height=200
        )
        
        st.subheader("Opções de Processamento")
        remover_porcentagem = st.checkbox("Remover símbolo de porcentagem (%)", value=True)
        substituir_hifen = st.checkbox("Substituir hífen por underscore (_)", value=True)
        
        st.subheader("Metadados")
        incluir_data = st.checkbox("Incluir data de processamento nos metadados", value=True)
        prefixo_metadados = st.text_input("Prefixo para metadados", value="****")
    
    with tab3:
        st.header("Sobre o Projeto")
        st.markdown("""
        ### 📚 Gerador de Corpus para IRaMuTeQ
        
        Esta ferramenta foi desenvolvida para auxiliar pesquisadores na preparação de corpora textuais 
        para análise no software IRaMuTeQ, realizando automaticamente:
        
        - Normalização de textos
        - Expansão de siglas
        - Substituição de palavras compostas
        - Remoção de caracteres especiais
        - Geração de metadados
        
        ### 👨‍💻 Autor
        
        **José Wendel dos Santos**  
        Doutorando em Letras - Universidade Federal de Sergipe (UFS)  
        ✉️ eng.wendel@gmail.com  
        🔗 [Lattes](http://lattes.cnpq.br/1234567890123456)
        
        ### 📄 Licença
        
        Este software é distribuído sob a licença MIT.
        """)

if __name__ == "__main__":
    main()
