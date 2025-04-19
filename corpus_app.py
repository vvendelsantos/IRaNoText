import streamlit as st
import pandas as pd
import re
import io

# Função para detectar palavras compostas
def detectar_palavras_compostas(texto):
    # Exemplo de palavras compostas (isso deve ser carregado de um dicionário real)
    palavras_compostas = ["inteligência artificial", "instituto federal de sergipe"]
    palavras_detectadas = []
    
    for palavra in palavras_compostas:
        if palavra.lower() in texto.lower():
            palavras_detectadas.append(palavra)
    
    return palavras_detectadas

# Função para detectar siglas
def detectar_siglas(texto):
    # Exemplo de siglas (isso deve ser carregado de um dicionário real)
    siglas = ["ifs", "ia", "ufsc"]
    siglas_detectadas = []

    for sigla in siglas:
        if sigla.lower() in texto.lower():
            siglas_detectadas.append(sigla)
    
    return siglas_detectadas

# Função para processar o arquivo e gerar o corpus
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
                # Se o caractere for '%' não substituímos por "_", apenas removemos
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

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de Corpus Textual para IRaMuTeQ")

# Campo para o usuário inserir o texto
texto_usuario = st.text_area("🔤 Insira o seu texto aqui", height=200)

# Botão "Analisar"
if st.button("🔍 Analisar"):
    # Detectando palavras compostas e siglas
    palavras_compostas = detectar_palavras_compostas(texto_usuario)
    siglas_detectadas = detectar_siglas(texto_usuario)
    
    # Mostrar os resultados
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔤 Sugestões de Palavras Compostas")
        if palavras_compostas:
            st.write("\n".join(palavras_compostas))
        else:
            st.write("Nenhuma palavra composta detectada.")
    
    with col2:
        st.subheader("🔤 Siglas Detectadas")
        if siglas_detectadas:
            st.write("\n".join(siglas_detectadas))
        else:
            st.write("Nenhuma sigla detectada.")
    
    # Mostrar botão para upload da planilha após análise
    st.markdown("### 📤 Agora, faça o upload da sua planilha:")
    file = st.file_uploader("Envie sua planilha preenchida", type=["xlsx"])
    
    if file:
        try:
            xls = pd.ExcelFile(file)
            df_textos = xls.parse("textos_selecionados")
            df_compostos = xls.parse("dic_palavras_compostas")
            df_siglas = xls.parse("dic_siglas")
            df_textos.columns = [col.strip().lower() for col in df_textos.columns]

            st.success("Planilha carregada com sucesso!")

            # Processo de geração do corpus
            if st.button("🚀 GERAR CORPUS TEXTUAL"):
                corpus, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas)

                if corpus.strip():
                    st.success("Corpus gerado com sucesso!")
                    st.text_area("📊 Estatísticas do processamento", estatisticas, height=250)

                    buf = io.BytesIO()
                    buf.write(corpus.encode("utf-8"))
                    st.download_button("📄 BAIXAR CORPUS TEXTUAL", data=buf.getvalue(), file_name="corpus_IRaMuTeQ.txt", mime="text/plain")
                else:
                    st.warning("Nenhum texto processado. Verifique os dados da planilha.")

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
