# Busca Semântica em PDF com LangChain e pgVector

Aplicação de linha de comando (CLI) que lê um PDF, divide o texto em trechos, gera embeddings com o Google Gemini, armazena tudo no PostgreSQL com pgVector e responde perguntas no terminal **somente com base no conteúdo do PDF**.

Desafio 1 do MBA em IA (Full Cycle).

O `document.pdf` incluído é a base de conhecimento de uma empresa **fictícia**, a SuperTechIABrazil (fundada em 2005, desenvolvimento de software e IA): história, estrutura, clientes, produtos, resultados financeiros de 2021 a 2025 e responsabilidade social. Nenhuma informação se refere a empresas ou pessoas reais.

## Pré-requisitos

- Python 3.12 ou superior (testado com Python 3.14)
- Docker e Docker Compose
- Uma API Key do Google Gemini ([Google AI Studio](https://aistudio.google.com/apikey))

> **Atenção:** o projeto usa o plano gratuito da API do Gemini. Nesse plano, o Google pode usar o conteúdo enviado para melhorar seus produtos. Não faça a ingestão de PDFs com informações sensíveis, confidenciais ou pessoais.

## Configuração

### 1. Ambiente virtual

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Dependências

```bash
pip install -r requirements.txt
```

### 3. Variáveis de ambiente

Copie o arquivo de exemplo e preencha `GOOGLE_API_KEY` no novo arquivo `.env`:

Windows (PowerShell):

```powershell
Copy-Item .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Os demais valores já funcionam para o ambiente local. Variáveis principais:

| Variável | Descrição |
| --- | --- |
| `GOOGLE_API_KEY` | API Key do Gemini (obrigatória) |
| `GOOGLE_EMBEDDING_MODEL` / `GOOGLE_LLM_MODEL` | Modelos do Gemini |
| `PDF_PATH` | PDF para ingestão (padrão: `document.pdf`) |
| `POSTGRES_PORT` | Porta local do banco (padrão: `5432`); altere se ela já estiver em uso |
| `DEBUG` | `true` exibe detalhes técnicos dos erros |

### 4. Banco de dados

```bash
docker compose up -d
```

Aguarde o banco ficar pronto: o comando `docker compose ps` deve mostrar o status `healthy`.

## Execução

```bash
python src/ingest.py   # 1. ingestão do PDF
python src/chat.py     # 2. chat no terminal
```

### Ingestão

A ingestão lê o PDF indicado em `PDF_PATH`, divide o texto em trechos de 1000 caracteres (com sobreposição de 150), gera os embeddings no Gemini e grava tudo no banco. Ao final, exibe um resumo:

```text
Ingestão concluída: 41 trechos gravados a partir de 18 páginas.
```

- **Rodar de novo:** se já houver um documento na base, o sistema pergunta `Deseja substituí-lo? (s/n)`. Com `s`, o conteúdo anterior é substituído (também ao trocar de PDF); com `n`, nada é alterado. Só um PDF fica disponível por vez.
- **Limite de uso do Gemini:** se o plano gratuito recusar a chamada, a ingestão aguarda e tenta de novo automaticamente algumas vezes.
- **Em caso de falha** na geração dos embeddings, o documento já ingerido anteriormente continua disponível.

### Chat

O chat responde **somente com base no conteúdo do PDF**. Quando a resposta não está no documento, ele responde exatamente `Não tenho informações necessárias para responder sua pergunta.`

Exemplo de sessão (com o `document.pdf` incluído):

```text
Faça sua pergunta:

PERGUNTA: Qual foi o lucro líquido e a margem de lucro em 2022?
RESPOSTA: Com base no contexto, em 2022 o lucro líquido foi de R$ 9,8 milhões, com margem de lucro de 8,2%.

Faça sua pergunta:

PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.

Faça sua pergunta:

PERGUNTA: Qual é a capital da França?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.

Faça sua pergunta:

PERGUNTA: sair
Até logo!
```

- Para sair, digite `sair` ou pressione Ctrl+C.
- Se o chat for aberto antes da ingestão, ele avisa que é preciso rodar `python src/ingest.py` primeiro.
- Se o Gemini estiver sobrecarregado, o chat tenta de novo automaticamente; se o limite de uso do plano gratuito for atingido, ele avisa na hora e você pode perguntar de novo depois.

## Solução de problemas

| Situação | O que fazer |
| --- | --- |
| `Não foi possível conectar ao banco de dados` | Inicie o Docker Desktop e rode `docker compose up -d`. Aguarde o status `healthy` em `docker compose ps`. |
| `docker compose up` falha com a porta 5432 em uso | Já existe outro PostgreSQL na máquina. Altere `POSTGRES_PORT` no `.env` (ex.: `5433`) e rode `docker compose up -d` de novo. |
| `A variável ... não está configurada no arquivo .env` | Confira se o `.env` foi criado a partir do `.env.example` e se a variável indicada está preenchida. |
| `A API Key do Gemini é inválida ou não tem permissão de acesso` | Gere uma nova chave no Google AI Studio e atualize `GOOGLE_API_KEY` no `.env`. |
| `O limite de uso da API do Gemini foi atingido` | O plano gratuito limita as requisições por minuto e por dia. Aguarde alguns minutos e tente de novo. |
| `O serviço do Gemini está sobrecarregado no momento` | Instabilidade temporária do Google. Tente novamente em instantes. |
| `Não foi possível extrair texto do PDF` | O PDF é escaneado (imagem). Use um PDF com texto selecionável. |
| `Nenhum documento foi ingerido` | Rode `python src/ingest.py` antes de abrir o chat. |
| Qualquer outro erro | Rode novamente com `DEBUG=true` no `.env` para ver os detalhes técnicos. |

## Documentação do projeto

- Requisitos: [`docs/prd/PRD.md`](docs/prd/PRD.md)
- Especificações: [`specs/`](specs/)
- Decisões de arquitetura (ADRs): [`docs/adr/`](docs/adr/)
- Fases de desenvolvimento e roteiro de aceite: [`docs/project/`](docs/project/)

## Desenvolvimento

Dependências de desenvolvimento (testes e lint):

```bash
pip install -r requirements-dev.txt
pytest
ruff check .
```

O `document.pdf` é gerado pelo script abaixo, que também confere a coerência dos números (por exemplo, receita - custos - despesas = lucro). Para gerá-lo novamente:

```bash
python scripts/generate_document_pdf.py
```
