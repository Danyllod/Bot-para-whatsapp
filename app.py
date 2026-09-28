"""
PRECISO AUTOMATIZAR MINHAS MENSAGENS P/ MEUS CLIENTES GOSTARIA DE SABER VALORES, E GOSTARIA QUE ENTRASSEM EM CONTATO COMIGO P/ EXPLICAR MELHOR, QUERO PODER MANDAR MENSAGENS DE COBRANÇA EM DETERMINADO DIA COM CLIENTES COM VENCIMENTO DIFERENTE

Uso:
    python app.py                     envia para quem vence daqui a DIAS_ANTECEDENCIA dias
    python app.py --dias 0            envia para quem vence hoje
    python app.py --data 01/12/2023   considera essa data como "hoje"
    python app.py --todos             envia para todos os clientes da planilha
    python app.py --simular           só mostra as mensagens, não abre o navegador
"""
import argparse
import csv
import os
from datetime import date, datetime, timedelta
from time import sleep
from urllib.parse import quote
import webbrowser

PLANILHA = 'clientes.xlsx'
ARQUIVO_ERROS = 'erros.csv'
LINK_PAGAMENTO = 'https://www.linkdopagamento.com'

# Quantos dias antes do vencimento a mensagem de cobrança é enviada
DIAS_ANTECEDENCIA = 3

# 'enter' aperta Enter para enviar (mais estável em VM, não depende da resolução da tela)
# 'imagem' procura o botão de enviar na tela usando seta1.png
METODO_ENVIO = 'enter'
IMAGEM_BOTAO_ENVIAR = 'seta1.png'

ESPERA_ABRIR_WHATSAPP = 30  # segundos para o WhatsApp Web carregar (e escanear o QR code, se preciso)
ESPERA_ABRIR_CONVERSA = 15  # segundos para a conversa carregar depois de abrir o link
ESPERA_ENTRE_ACOES = 5


def converter_data(valor):
    """Aceita datetime/date da planilha ou texto dd/mm/aaaa."""
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        for formato in ('%d/%m/%Y', '%Y-%m-%d'):
            try:
                return datetime.strptime(valor.strip(), formato).date()
            except ValueError:
                pass
    raise ValueError(f'data de vencimento inválida: {valor!r}')


def ler_clientes(caminho=PLANILHA):
    import openpyxl

    workbook = openpyxl.load_workbook(caminho)
    pagina_clientes = workbook['Sheet1']
    clientes = []
    for linha in pagina_clientes.iter_rows(min_row=2, values_only=True):
        nome, telefone, vencimento = linha[:3]
        if not nome or not telefone:
            continue
        telefone = ''.join(c for c in str(telefone) if c.isdigit())
        try:
            vencimento = converter_data(vencimento)
        except ValueError as erro:
            registrar_erro(nome, telefone, str(erro))
            continue
        clientes.append({'nome': nome, 'telefone': telefone, 'vencimento': vencimento})
    return clientes


def filtrar_por_vencimento(clientes, data_alvo):
    return [c for c in clientes if c['vencimento'] == data_alvo]


def montar_mensagem(cliente):
    vencimento = cliente['vencimento'].strftime('%d/%m/%Y')
    return (f'Olá {cliente["nome"]} seu boleto vence no dia {vencimento}. '
            f'Favor pagar no link {LINK_PAGAMENTO}')


def registrar_erro(nome, telefone, motivo):
    with open(ARQUIVO_ERROS, 'a', newline='', encoding='utf-8') as arquivo:
        csv.writer(arquivo).writerow(
            [nome, telefone, datetime.now().strftime('%d/%m/%Y %H:%M:%S'), motivo])


def enviar_mensagem(pyautogui, cliente, mensagem):
    link_mensagem_whatsapp = (f'https://web.whatsapp.com/send?phone={cliente["telefone"]}'
                              f'&text={quote(mensagem)}')
    webbrowser.open(link_mensagem_whatsapp)
    sleep(ESPERA_ABRIR_CONVERSA)
    if METODO_ENVIO == 'imagem':
        try:
            seta = pyautogui.locateCenterOnScreen(IMAGEM_BOTAO_ENVIAR)
        except pyautogui.ImageNotFoundException:
            seta = None
        if seta is None:
            raise RuntimeError(f'botão de enviar ({IMAGEM_BOTAO_ENVIAR}) não encontrado na tela')
        pyautogui.click(seta[0], seta[1])
    else:
        pyautogui.press('enter')
    sleep(ESPERA_ENTRE_ACOES)


def main():
    parser = argparse.ArgumentParser(description='Envia mensagens de cobrança pelo WhatsApp Web')
    parser.add_argument('--dias', type=int, default=DIAS_ANTECEDENCIA,
                        help='dias antes do vencimento para enviar a cobrança')
    parser.add_argument('--data', help='data de referência (dd/mm/aaaa); padrão: hoje')
    parser.add_argument('--todos', action='store_true', help='envia para todos os clientes')
    parser.add_argument('--simular', action='store_true', help='não abre o navegador')
    args = parser.parse_args()

    hoje = converter_data(args.data) if args.data else date.today()
    clientes = ler_clientes()
    if args.todos:
        selecionados = clientes
    else:
        data_alvo = hoje + timedelta(days=args.dias)
        selecionados = filtrar_por_vencimento(clientes, data_alvo)
        print(f'Clientes com vencimento em {data_alvo:%d/%m/%Y}: {len(selecionados)}')

    if not selecionados:
        print('Nenhuma mensagem para enviar.')
        return

    if args.simular:
        for cliente in selecionados:
            print(f'[simulação] {cliente["nome"]} ({cliente["telefone"]}): {montar_mensagem(cliente)}')
        return

    import pyautogui

    webbrowser.open('https://web.whatsapp.com/')
    sleep(ESPERA_ABRIR_WHATSAPP)

    enviados = 0
    for cliente in selecionados:
        mensagem = montar_mensagem(cliente)
        try:
            enviar_mensagem(pyautogui, cliente, mensagem)
            enviados += 1
            print(f'Mensagem enviada para {cliente["nome"]}')
        except Exception as erro:
            motivo = f'{type(erro).__name__}: {erro}'
            print(f'Não foi possível enviar mensagem para {cliente["nome"]} - {motivo}')
            registrar_erro(cliente['nome'], cliente['telefone'], motivo)
        finally:
            pyautogui.hotkey('ctrl', 'w')
            sleep(ESPERA_ENTRE_ACOES)

    print(f'Concluído: {enviados} de {len(selecionados)} mensagens enviadas.')
    if enviados < len(selecionados):
        print(f'Veja os detalhes das falhas em {os.path.abspath(ARQUIVO_ERROS)}')


if __name__ == '__main__':
    main()
