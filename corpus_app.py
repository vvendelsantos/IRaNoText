
import streamlit as st

def gerar_corpus(textos_selecionados, dic_palavras_compostas, dic_siglas):
    # dicionários para armazenar as palavras compostas e siglas
    dict_compostos = {}
    dict_siglas = {}

    # Adicionar palavras compostas ao dicionário
    for i in range(len(dic_palavras_compostas)):
        if dic_palavras_compostas[i][0] and dic_palavras_compostas[i][1]:
            dict_compostos[dic_palavras_compostas[i][0].lower()] = dic_palavras_compostas[i][1].lower()

    # Adicionar siglas ao dicionário
    for i in range(len(dic_siglas)):
        if dic_siglas[i][0] and dic_siglas[i][1]:
            dict_siglas[dic_siglas[i][0].lower()] = dic_siglas[i][1].lower()

    # Variáveis de controle para o número de alterações
    total_textos = 0
    total_siglas_removidas = 0
    total_substituicoes_compostas = 0
    total_caracteres_removidos = 0

    corpus_final = ""

    for texto in textos_selecionados:
        texto_original = texto
        texto_corrigido = texto.lower()
        total_textos += 1

        # Remover siglas entre parênteses
        for sigla, descricao in dict_siglas.items():
            texto_corrigido = texto_corrigido.replace(f"({sigla})", "")
            total_siglas_removidas += 1

        # Substituir siglas isoladas
        for sigla, descricao in dict_siglas.items():
            texto_corrigido = texto_corrigido.replace(f" {sigla} ", f" {descricao} ")
            total_siglas_removidas += 1

        # Substituir palavras compostas
        for termo, substituto in dict_compostos.items():
            if termo in texto_corrigido:
                texto_corrigido = texto_corrigido.replace(termo, substituto)
                total_substituicoes_compostas += 1

        # Remover caracteres especiais
        caracteres = {"-": "Hífen", ";": "Ponto e vírgula", '"': "Aspas duplas", "'": "Aspas simples",
                      "…": "Reticências", "–": "Travessão", "(": "Parêntese esquerdo", ")": "Parêntese direito", "/": "Barra"}

        for caractere, nome in caracteres.items():
            while caractere in texto_corrigido:
                texto_corrigido = texto_corrigido.replace(caractere, "_")
                total_caracteres_removidos += 1

        # Remover quebras de linha
        texto_corrigido = texto_corrigido.replace("
", " ")

        # Montar a linha final do corpus
        corpus_linha = "**** *ID_" + str(textos_selecionados.index(texto) + 1)
        corpus_linha += " " + texto_corrigido + "
"

        corpus_final += corpus_linha

    # Estatísticas
    detalhes_caracteres = "
"
    for caractere, nome in caracteres.items():
        if texto_corrigido.count(caractere) > 0:
            detalhes_caracteres += f" - {nome} ({caractere}) : {texto_corrigido.count(caractere)}"

    resultado = f"""
    Corpus textual gerado com sucesso.

    Estatísticas do processamento:
    • Textos processados: {total_textos}
    • Siglas removidas/substituídas: {total_siglas_removidas}
    • Palavras compostas substituídas: {total_substituicoes_compostas}
    • Caracteres especiais removidos: {total_caracteres_removidos}
    {detalhes_caracteres}
    """

    return corpus_final, resultado


def main():
    st.title("Gerador de Corpus IRaMuTeQ")

    st.write("Insira os textos selecionados, dic_palavras_compostas e dic_siglas para gerar o corpus.")

    # Exemplo de entrada de dados
    textos_selecionados = [
        "O exemplo de sigla é (ABC) e a palavra composta é testando-completo.",
        "Outra sigla pode ser (DEF) e outra palavra composta como exemplo-composto."
    ]
    dic_palavras_compostas = [
        ("testando-completo", "teste completo"),
        ("exemplo-composto", "exemplo composto")
    ]
    dic_siglas = [
        ("ABC", "ABC Significado"),
        ("DEF", "DEF Significado")
    ]

    corpus, resultado = gerar_corpus(textos_selecionados, dic_palavras_compostas, dic_siglas)

    st.subheader("Corpus gerado:")
    st.text(corpus)

    st.subheader("Resultado do processamento:")
    st.text(resultado)


if __name__ == "__main__":
    main()
