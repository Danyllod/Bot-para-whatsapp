# Descrever os passos manuais e  depois transformar isso em codigo
# Ler planilhas e guardar informações sobre nome, telefone e data de vencimento
# Criar links personalizados do whatapp e enviar mensagens para cada cliente com base nos dados da planilha

import openpyxl


workbook= openpyxl.load_workbook('clientes.xlsx')
pagina_clientes = workbook['Sheet1']

for linha in pagina_clientes.iter_rows(min_row=2):
    #extrair nome, telefone, vencimento
    nome = linha[0].value
    telefone = linha[1].value
    vencimento = linha[2].value
    print(nome, telefone, vencimento)