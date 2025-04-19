# NOVAS FUNÇÕES PARA ANÁLISE DE TEXTO (VERSÃO SIMPLIFICADA)
def detectar_siglas(texto):
    """Detecta siglas no formato 'AB' ou 'ABC' (2+ letras maiúsculas)"""
    try:
        siglas = re.findall(r'\b[A-Z]{2,}\b', texto)
        return list(set(siglas))  # Remove duplicatas
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

def gerar_planilha_sugestoes(siglas, compostos):
    """Cria um DataFrame com as sugestões para download (versão simplificada)"""
    try:
        # Criar DataFrames sem colunas extras
        df_siglas = pd.DataFrame({"Sigla": siglas})
        df_compostos = pd.DataFrame({"Palavra composta": compostos})
        
        # Criar arquivo Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_siglas.to_excel(writer, sheet_name="dic_siglas", index=False)
            df_compostos.to_excel(writer, sheet_name="dic_palavras_compostas", index=False)
        
        return output.getvalue()
    except Exception as e:
        st.error(f"Erro ao gerar planilha: {e}")
        return None

# PARTE DA INTERFACE STREAMLIT (MODIFICADA)
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
                st.dataframe(
                    pd.DataFrame({"Palavra composta": compostos}),
                    height=300,
                    hide_index=True
                )
            
            with col2:
                st.subheader("Siglas detectadas")
                st.dataframe(
                    pd.DataFrame({"Sigla": siglas}),
                    height=300,
                    hide_index=True
                )
            
            # Botão para baixar planilha simplificada
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
