import os
from pathlib import Path

# Pergunta ao usuário o nome da pasta principal
nome_pasta_principal = input("Digite o nome da pasta principal: ")

# Obtém o diretório atual (a pasta onde o script está sendo executado)
diretorio_atual = Path.cwd()

# Cria a pasta principal com o nome fornecido pelo usuário
pasta_principal = diretorio_atual / nome_pasta_principal
pasta_principal.mkdir(exist_ok=True)

# Lista de subpastas que serão criadas em cada pasta diária
subpastas = ['Audio', 'Roteiro', 'Imagens', 'Postar']

# Cria as 30 pastas numeradas e suas subpastas
for dia in range(1, 31):
    # Cria a pasta do dia
    pasta_dia = pasta_principal / f'{dia}'
    pasta_dia.mkdir(exist_ok=True)

    # Cria as subpastas dentro da pasta do dia
    for subpasta in subpastas:
        caminho_subpasta = pasta_dia / subpasta
        caminho_subpasta.mkdir(exist_ok=True)

        # Cria arquivo .docx na pasta Roteiro (como arquivo vazio)
        if subpasta == 'Roteiro':
            arquivo_docx = caminho_subpasta / f'{dia}.docx'
            arquivo_docx.touch()

        # Cria arquivo .txt na pasta Postar
        elif subpasta == 'Postar':
            arquivo_txt = caminho_subpasta / f'{dia}.txt'
            arquivo_txt.touch()

print("Estrutura de pastas e arquivos criada com sucesso!")
