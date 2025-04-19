import streamlit as st
import pandas as pd
import re
import io
from word2number import w2n
from collections import Counter
import spacy

# Carregar o modelo spaCy para português
try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    st.error("Modelo spaCy 'pt_core_news_sm' não encontrado. Por favor instale com:")
    st.code("python -m spacy download pt_core_news_sm")
    st.stop()

# [Mantenha todas as funções existentes: converter_numeros_por_extenso, 
# processar_palavras_com_se, processar_pronomes_pospostos, gerar_corpus...]

# Dicionários para filtros
PALAVRAS_COMUNS = {
    'de', 'da', 'do', 'das', 'dos', 'e', 'com', 'para', 'por', 'em', 
    'no', 'na', 'nos', 'nas', 'o', 'a', 'os', 'as', 'um', 'uma', 
    'uns', 'umas', 'que', 'se', 'ao', 'à'
}

SUFIXOS_COMPOSTOS = {
    'ação', 'dade', 'mento', 'ção', 'ismo', 'ista', 'agem', 'ário',
    'ório', 'ência', 'eiro', 'eira', 'ez', 'eza', 'ivo', 'iva'
}

# Função para detectar siglas
def detectar_siglas(texto):
    """Detecta siglas (2+ letras maiúsculas) com filtro de contexto"""
    try:
        # Padrão básico para siglas
        siglas = re.findall(r'\b[A-Z]{2,}\b', texto)
        
        # Filtra palavras comuns
        palavras_comuns = {'EU', 'OS', 'AOS', 'COM', 'PARA', 'PELA', 'PELO', 
                          'UMA', 'ESTE', 'QUE', 'SEM', 'SOB', 'SOBRE'}
        siglas_filtradas = [s for s in set(siglas) if s not in palavras_comuns]
        
        return sorted(siglas_filtradas)
    except Exception as e:
        st.error(f"Erro ao detectar siglas: {e}")
        return []

# Função para detectar palavras compostas com spaCy + regras
def detectar_palavras_compostas(texto):
    """Detecção robusta usando spaCy NER + regras complementares"""
    try:
        compostas = set()
        
        # 1. Análise com spaCy NER
        doc = nlp(texto)
        for ent in doc.ents:
            if len(ent.text.split()) > 1:  # Pega apenas entidades com múltiplas palavras
                compostas.add(ent.text)
        
        # 2. Padrão regex para sequências capitalizadas (complementar)
        padrao_regex = re.findall(r'\b(?:[A-Z][a-záéíóúâêôãõç]+\s?){2,}\b', texto)
        for termo in padrao_regex:
            palavras = termo.split()
            if (len(palavras) >= 2 and
                not any(p.lower() in PALAVRAS_COMUNS for p in palavras)):
                compostas.add(termo)
        
        # 3. Padrão para termos com hífen
        padrao_hifen = re.findall(r'\b[A-Z][a-záéíóúâêôãõç]+-[A-Z][a-záéíóúâêôãõç]+\b', texto)
        compostas.update(padrao_hifen)
        
        # Filtro final para termos válidos
        compostas_validas = []
        for termo in compostas:
            palavras = termo.split()
            if (len(palavras) >= 2 and
                not any(p.lower() in PALAVRAS_COMUNS for p in palavras)):
                compostas_validas.append(termo)
        
        return sorted(compostas_validas)
    
    except Exception as e:
        st.error(f"Erro ao detectar palavras compostas: {e}")
        return []

# Interface Streamlit
st.set_page_config(layout="wide")
st.title("Gerador de corpus textual para IRaMuTeQ")

# Seção de pré-análise
st.markdown("## 🔍 Pré-análise de texto (opcional)")
with st.container():
    texto_usuario = st.text_area(
        "Cole seu texto aqui para detectar siglas e palavras compostas:",
        height=200,
        placeholder="Ex: A Universidade Federal de Sergipe oferece cursos em Inteligência Artificial e Machine Learning...",
        label_visibility="collapsed"
    )
    
    if st.button("Analisar 🔍", key="analisar_texto"):
        if texto_usuario.strip():
            siglas = detectar_siglas(texto_usuario)
            compostas = detectar_palavras_compostas(texto_usuario)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Palavras compostas detectadas**")
                if compostas:
                    for composto in compostas:
                        st.write(f"▪ {composto}")
                    st.info(f"Total detectado: {len(compostas)}")
                else:
                    st.warning("Nenhuma palavra composta detectada")
            
            with col2:
                st.markdown("**Siglas detectadas**")
                if siglas:
                    for sigla in siglas:
                        st.write(f"▪ {sigla}")
                    st.info(f"Total detectado: {len(siglas)}")
                else:
                    st.warning("Nenhuma sigla detectada")

# [Mantenha as seções de upload e processamento do corpus...]

# Seção principal de upload
st.markdown("## 📌 Envie sua planilha completa para gerar o corpus")
with st.container():
    with open("gerar_corpus_iramuteq.xlsx", "rb") as exemplo:
        st.download_button(
            label="📅 Baixar modelo de planilha",
            data=exemplo,
            file_name="gerar_corpus_iramuteq.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    file = st.file_uploader("Envie sua planilha preenchida", type=["xlsx"], label_visibility="collapsed")

    if file:
        try:
            xls = pd.ExcelFile(file)
            df_textos = xls.parse("textos_selecionados")
            df_compostos = xls.parse("dic_palavras_compostas")
            df_siglas = xls.parse("dic_siglas")
            df_textos.columns = [col.strip().lower() for col in df_textos.columns]

            if st.button("🚀 GERAR CORPUS TEXTUAL"):
                corpus, estatisticas = gerar_corpus(df_textos, df_compostos, df_siglas)

                if corpus.strip():
                    st.success("Corpus gerado com sucesso!")
                    st.text_area("📊 Estatísticas do processamento", estatisticas, height=250)

                    buf = io.BytesIO()
                    buf.write(corpus.encode("utf-8"))
                    st.download_button(
                        "📄 BAIXAR CORPUS TEXTUAL", 
                        data=buf.getvalue(), 
                        file_name="corpus_IRaMuTeQ.txt", 
                        mime="text/plain"
                    )
                else:
                    st.warning("Nenhum texto processado. Verifique os dados da planilha.")

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")

# Rodapé
st.markdown("""
---
👨‍🏫 **Sobre o autor**

**Autor:** José Wendel dos Santos  
**Instituição:** Universidade Federal de Sergipe (UFS)  
**Contato:** eng.wendel@gmail.com
""")
