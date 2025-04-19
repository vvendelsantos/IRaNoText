import streamlit as st
import pandas as pd
import re
import io
import pyperclip
from word2number import w2n

# [Mantenha todas as outras funções existentes...]

# Funções para análise de texto (atualizadas)
def detectar_siglas(texto):
    """Detecta siglas no formato 'AB' ou 'ABC' (2+ letras maiúsculas)"""
    try:
        siglas = re.findall(r'\b[A-Z]{2,}\b', texto)
        return list(set(siglas))
    except Exception as e:
        st.error(f"Erro ao detectar siglas: {e}")
        return []

def sugerir_palavras_compostas(texto):
    """Sugere combinações de palavras com iniciais maiúsculas"""
    try:
        candidatos = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', texto)
        compostos_sugeridos = []
        
        for termo in candidatos:
            if len(termo.split()) >= 2 and len(termo) > 5:
                compostos_sugeridos.append(termo)
        
        return list(set(compostos_sugeridos))
    except Exception as e:
        st.error(f"Erro ao sugerir palavras compostas: {e}")
        return []

# Função para copiar para área de transferência
def copiar_para_clipboard(texto):
    try:
        pyperclip.copy(texto)
        st.success("Copiado para área de transferência!")
    except Exception as e:
        st.error(f"Erro ao copiar: {e}")

# Interface Streamlit (parte atualizada)
with st.expander("🔍 Pré-análise de texto (opcional)", expanded=True):
    texto_usuario = st.text_area(
        "Cole seu texto aqui para detectar siglas e palavras compostas:",
        height=150,
        placeholder="Ex: A UFS oferece cursos em Inteligência Artificial..."
    )
    
    if st.button("Analisar 🔍", key="analisar_texto"):
        if texto_usuario.strip():
            siglas = detectar_siglas(texto_usuario)
            compostos = sugerir_palavras_compostas(texto_usuario)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Palavras compostas detectadas")
                df_compostos = pd.DataFrame({"Palavra composta": compostos})
                
                # Exibe como tabela estilo planilha
                st.dataframe(
                    df_compostos,
                    height=300,
                    hide_index=True,
                    use_container_width=True
                )
                
                # Opções de cópia
                col1_1, col1_2 = st.columns(2)
                with col1_1:
                    if st.button("📋 Copiar Tudo", key="copy_all_compostos"):
                        copiar_para_clipboard("\n".join(compostos))
                with col1_2:
                    selected_composto = st.selectbox(
                        "Selecione para copiar:",
                        compostos,
                        key="select_composto"
                    )
                    if st.button("📋 Copiar Selecionado", key="copy_selected_composto"):
                        copiar_para_clipboard(selected_composto)
            
            with col2:
                st.subheader("Siglas detectadas")
                df_siglas = pd.DataFrame({"Sigla": siglas})
                
                # Exibe como tabela estilo planilha
                st.dataframe(
                    df_siglas,
                    height=300,
                    hide_index=True,
                    use_container_width=True
                )
                
                # Opções de cópia
                col2_1, col2_2 = st.columns(2)
                with col2_1:
                    if st.button("📋 Copiar Tudo", key="copy_all_siglas"):
                        copiar_para_clipboard("\n".join(siglas))
                with col2_2:
                    selected_sigla = st.selectbox(
                        "Selecione para copiar:",
                        siglas,
                        key="select_sigla"
                    )
                    if st.button("📋 Copiar Selecionado", key="copy_selected_sigla"):
                        copiar_para_clipboard(selected_sigla)
            
            st.markdown("---")
            planilha_sugestoes = gerar_planilha_sugestoes(siglas, compostos)
            if planilha_sugestoes:
                st.download_button(
                    label="📥 Baixar planilha com termos detectados",
                    data=planilha_sugestoes,
                    file_name="termos_detectados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("Por favor, insira um texto para análise.")

# [Mantenha o resto do código original...]
