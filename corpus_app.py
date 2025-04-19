import pandas as pd
import re
import spacy
from spacy.matcher import Matcher
import streamlit as st

# Carregar o modelo de linguagem spaCy para o português
nlp = spacy.load("pt_core_news_sm")

# Função para detectar palavras compostas automaticamente (sem precisar ser manual)
def detectar_palavras_compostas(texto):
    # Processar o texto com o modelo spaCy
    doc = nlp(texto)
    
    # Criar o matcher para procurar bigramas/trigramas
    matcher = Matcher(nlp.vocab)
    
    # Definir padrões para bigramas e trigramas (duas ou três palavras consecutivas)
    bigramas = [[{"is_stop": False}, {"is_stop": False}]]  # Exclui stopwords
    trigramas = [[{"is_stop": False}, {"is_stop": False}, {"is_stop": False}]]  # Exclui stopwords

    matcher.add("BIGRAMAS", [bigramas])
    matcher.add("TRIGRAMAS", [trigramas])
    
    # Encontrar os padrões no texto
    matches = matcher(doc)
    palavras_compostas = []

    # Processar os matches e coletar as palavras compostas
    for match_id, start, end in matches:
        span = doc[start:end]
        if len(span) > 1:  # Ignora palavras únicas
            palavras_compostas.append(" ".join([token.text for token in span]))

    return palavras_compostas

# Função para detectar siglas automaticamente
def detectar_siglas(texto):
    # Expressão regular para identificar siglas (palavras com letras maiúsculas, como IA, INPI, etc.)
    siglas = re.findall(r'\b[A-Z]{2,}\b', texto)
    return siglas

# Função para gerar o corpus a partir do DataFrame
def gerar_corpus(df):
    textos = df['Textos selecionados']  # Coluna 'Textos selecionados' com o texto do usuário
    corpus = []
    
    for texto in textos:
        # Detecta palavras compostas e siglas
        palavras_compostas = detectar_palavras_compostas(texto)
        siglas = detectar_siglas(texto)

        # Remover as palavras compostas e siglas do texto original
        for pc in palavras_compostas + siglas:
            texto = texto.replace(pc, '')
        
        # Adicionar as palavras compostas e siglas ao corpus (se não estiverem vazias)
        corpus.append({
            'texto_original': texto,
            'palavras_compostas': ", ".join(palavras_compostas),
            'siglas': ", ".join(siglas)
        })
    
    # Criar um DataFrame do corpus
    corpus_df = pd.DataFrame(corpus)
    return corpus_df

# Função para gerar metadados automaticamente
def gerar_metadados(df):
    # Gerar metadados (exemplo: número de palavras, número de siglas, etc.)
    df['num_palavras'] = df['Textos selecionados'].apply(lambda x: len(x.split()))
    df['num_siglas'] = df['siglas'].apply(lambda x: len(x.split(',')) if x else 0)
    return df

# Função para remover caracteres especiais e normalizar o texto
def normalizar_texto(df):
    # Remover caracteres especiais e normalizar o texto (exemplo: substituir acentos, etc.)
    df['Textos selecionados'] = df['Textos selecionados'].apply(lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', x))
    return df

# Função para sugerir palavras compostas manualmente
def sugerir_palavras_compostas(df):
    # Analisar os textos e sugerir palavras compostas
    sugestoes = []
    
    for texto in df['Textos selecionados']:
        palavras_compostas = detectar_palavras_compostas(texto)
        sugestoes.append(palavras_compostas)
    
    return sugestoes

# Função para atualizar o dataframe com as palavras compostas detectadas
def atualizar_dataframe(df, sugestoes_palavras_compostas):
    for i, sugestao in enumerate(sugestoes_palavras_compostas):
        df.at[i, 'Palavras compostas sugeridas'] = ', '.join(sugestao)

# Função principal que integra tudo no Streamlit
def app():
    st.title("Gerador de Corpus e Análise de Palavras Compostas")

    # Upload de arquivo (planilha)
    uploaded_file = st.file_uploader("Faça o upload da planilha de textos (CSV ou Excel)", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        # Carregar o arquivo
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Verificar se a coluna 'Textos selecionados' existe
        if 'Textos selecionados' not in df.columns:
            st.error("A coluna 'Textos selecionados' não foi encontrada na planilha.")
            return
        
        # Exibir os dados da planilha
        st.write("Dados carregados:")
        st.write(df.head())

        # Mostrar uma área de texto para o usuário adicionar um novo texto
        novo_texto = st.text_area("Cole um texto para análise", "")
        
        if novo_texto:
            # Detectar palavras compostas e siglas no novo texto
            palavras_compostas = detectar_palavras_compostas(novo_texto)
            siglas = detectar_siglas(novo_texto)

            # Exibir sugestões de palavras compostas e siglas detectadas
            st.write(f"**Palavras compostas detectadas**: {', '.join(palavras_compostas)}")
            st.write(f"**Siglas detectadas**: {', '.join(siglas)}")
        
        # Detecção de palavras compostas e siglas para todos os textos
        sugestoes_palavras_compostas = sugerir_palavras_compostas(df)

        # Gerar o corpus final com os textos processados
        corpus_df = gerar_corpus(df)

        # Gerar metadados
        corpus_df = gerar_metadados(corpus_df)

        # Normalizar o texto (remover caracteres especiais)
        corpus_df = normalizar_texto(corpus_df)

        # Atualizar o dataframe com as sugestões de palavras compostas
        atualizar_dataframe(corpus_df, sugestoes_palavras_compostas)

        # Exibir o corpus gerado com as sugestões de palavras compostas
        st.write("**Corpus Gerado**:")
        st.write(corpus_df)

        # Opção de exportar o resultado para CSV
        exportar = st.button("Exportar Corpus para CSV")
        
        if exportar:
            corpus_df.to_csv("corpus_gerado.csv", index=False)
            st.success("Corpus exportado com sucesso para 'corpus_gerado.csv'!")

# Rodar a aplicação Streamlit
if __name__ == "__main__":
    app()
