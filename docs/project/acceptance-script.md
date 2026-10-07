# Manual Acceptance Script

Run at the end of each phase and before delivery, with the `document.pdf` included in the repository (fictitious SuperTechIABrazil knowledge base). Questions and expected answers are in Portuguese, as the user sees them.

**Pre-conditions:** database `healthy` (`docker compose ps`), `.env` filled from `.env.example`, ingestion completed (`Ingestão concluída: 41 trechos gravados a partir de 18 páginas.`).

The free tier allows 15 LLM requests per minute: keep the session below that, or wait a minute between blocks.

## 1. Ingestion (spec 001)

| ID | Action | Expected result |
| --- | --- | --- |
| ING-1 | `python src/ingest.py` with an empty database | Summary message; no confirmation question |
| ING-2 | Run again and answer `n` | `Ingestão cancelada. Nenhum dado foi alterado.` |
| ING-3 | Run again, answer `x`, then `s` | Question repeated, then content replaced (same chunk count, no duplicates) |
| ING-4 | `PDF_PATH=nao-existe.pdf` | `Arquivo PDF não encontrado: nao-existe.pdf` |
| ING-5 | Database stopped (`docker compose stop`) | `Não foi possível conectar ao banco de dados...` |

## 2. Questions within the PDF (Scenario A)

| ID | Question | Expected content (wording may vary) |
| --- | --- | --- |
| Q-01 | Qual o faturamento da Empresa SuperTechIABrazil em 2025? | R$ 192,4 milhões |
| Q-02 | Qual foi o lucro líquido e a margem de lucro em 2022? | R$ 9,8 milhões; 8,2% |
| Q-03 | Quantos funcionários e quantos gerentes a empresa tem? | 640 funcionários; 38 gerentes (final de 2025) |
| Q-04 | Quem foram os CEOs da empresa ao longo da história? | Henrique Valadares Moura (2005-2014), Lúcia Carvalho Prado (2014-2021), Rafael Ishikawa Duarte (2021-atual) |
| Q-05 | Em que ano a empresa foi fundada e onde fica a sede? | 2005; Rua dos Algoritmos, 2005, Polo Tecnológico Alvorada, Campinas (SP) |
| Q-06 | O que é o AgentFlow e quando foi lançado? | Plataforma de agentes de IA; 2024 (versão 2.0 em abril de 2026) |
| Q-07 | Quanto foi investido no Programa IA em Tudo? | R$ 25,0 milhões entre 2021 e 2023 |
| Q-08 | Qual projeto foi feito para o Hospital Santa Aurora? | InsightHub (ocupação de leitos) e AgentFlow (consultas, 31% menos faltas) |
| Q-09 | Quantos jovens o programa Código do Futuro formou? | 3.200 jovens (2016 a 2025) |

## 3. Questions outside the PDF (Scenarios B, C and D)

The answer must be exactly `Não tenho informações necessárias para responder sua pergunta.`

| ID | Question |
| --- | --- |
| Q-10 | Quantos clientes temos em 2024? |
| Q-11 | Qual é a capital da França? |
| Q-12 | Você acha isso bom ou ruim? |

## 4. Chat controls (Scenarios F and G)

| ID | Action | Expected result |
| --- | --- | --- |
| CTL-1 | Press Enter without typing | `PERGUNTA:` shown again, no API call |
| CTL-2 | Type `sair` (or `SAIR`) | `Até logo!` |
| CTL-3 | Press Ctrl+C | `Até logo!`, no stack trace |
| CTL-4 | Start the chat with an empty collection | `Nenhum documento foi ingerido. Execute primeiro: python src/ingest.py` |
| CTL-5 | Start the chat with the database stopped | `Não foi possível conectar ao banco de dados...` |
