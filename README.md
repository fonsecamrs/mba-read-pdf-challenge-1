# Busca Semântica em PDF com LangChain e pgVector

Aplicação de linha de comando (CLI) que lê um PDF, divide o texto em trechos, gera embeddings com o Google Gemini, armazena tudo no PostgreSQL com pgVector e responde perguntas no terminal **somente com base no conteúdo do PDF**.

Desafio 1 do MBA em IA (Full Cycle).

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

## Desenvolvimento

Dependências de desenvolvimento (testes e lint):

```bash
pip install -r requirements-dev.txt
pytest
ruff check .
```
