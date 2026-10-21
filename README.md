# Bot para WhatsApp

## Confirmação de consultas do CRESM (`extrair_relatorio.py`)

Lê o relatório **"Controle de Consultas"** em PDF e gera a planilha para importar na plataforma
de campanhas (que envia a mensagem com os botões SIM/NÃO).

```
pip install pdfplumber openpyxl
python extrair_relatorio.py Relatorio.pdf --saida pasta_de_saida
```

Gera `campanha_AAAA-MM-DD.xlsx` (abas **Campanha** e **Pendências**) e `campanha_AAAA-MM-DD.csv`.

- Uma linha por paciente/dia; a coluna `consultas` traz uma linha por consulta
  (`• Psicologia – Ludmila de Souza Ribeiro`) quando o paciente tem mais de uma no mesmo dia.
- `periodo`: pelo primeiro horário do dia, "a partir das 07h00 (matutino)" ou
  "a partir das 13h00 (vespertino)".
- `telefone`: primeiro número válido, já no formato `55DDD9XXXXXXXX` (celulares antigos com
  8 dígitos ganham o 9); os outros ficam em `telefones_reserva`.
- Pacientes sem telefone válido vão para a aba **Pendências**.
- Um mesmo telefone não é usado para dois pacientes (ex.: irmãos). O segundo usa outro número dele;
  se não tiver, vai para **Pendências** para a recepção entrar em contato.

### Verificação no WhatsApp (evita conversa duplicada pelo 9º dígito)

Muitas contas de WhatsApp no Brasil ainda são identificadas **sem o 9** (ex.: `556285284919`).
Se a campanha sai para o número com o 9 e a resposta chega pelo número sem o 9, o atendimento abre
uma segunda conversa. Com a Evolution API configurada, o script consulta cada número e grava na
coluna `telefone` exatamente como o WhatsApp o identifica:

```
export EVOLUTION_URL=http://localhost:8080
export EVOLUTION_INSTANCIA=nome-da-instancia
export EVOLUTION_APIKEY=chave-da-api
python extrair_relatorio.py Relatorio.pdf
```

A coluna `whatsapp_verificado` indica se a verificação foi feita. Números sem WhatsApp são trocados
pelo reserva; se nenhum tiver WhatsApp, o paciente vai para **Pendências**. Se a Evolution não
responder, a planilha não é gerada (para não sair uma campanha sem verificação por engano).
- O script confere o total de pacientes e de agendamentos com o rodapé do relatório e avisa se
  não baterem.

## Cobrança (`app.py`)

Envia mensagens de cobrança pelo WhatsApp Web a partir de `clientes.xlsx`.
Veja `python app.py --help`.
