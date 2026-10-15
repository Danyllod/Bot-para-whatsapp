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
- O script confere o total de pacientes e de agendamentos com o rodapé do relatório e avisa se
  não baterem.

## Cobrança (`app.py`)

Envia mensagens de cobrança pelo WhatsApp Web a partir de `clientes.xlsx`.
Veja `python app.py --help`.
