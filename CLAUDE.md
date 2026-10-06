# CLAUDE.md

Desafio 1 do MBA em IA (Full Cycle): ingestão de um PDF e busca semântica com LangChain e PostgreSQL + pgVector, consultada por um chat em linha de comando (CLI).

## Stack obrigatória

- Linguagem: Python
- Framework: LangChain
- Banco de dados: PostgreSQL + pgVector, executado com Docker e Docker Compose
- Embeddings e LLM: Google Gemini, com API Key lida do `.env`

Pacotes recomendados:

- Split: `from langchain_text_splitters import RecursiveCharacterTextSplitter`
- Embeddings: `from langchain_google_genai import GoogleGenerativeAIEmbeddings`
- PDF: `from langchain_community.document_loaders import PyPDFLoader`
- Vector store: `from langchain_postgres import PGVector`

## Comandos

Ambiente virtual (crie e ative antes de instalar dependências):

```bash
python3 -m venv venv && source venv/bin/activate   # Linux/macOS
```

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1   # Windows (PowerShell)
```

Execução e qualidade (iguais nos dois sistemas):

```bash
pip install -r requirements.txt
docker compose up -d       # 1. sobe o banco
python src/ingest.py       # 2. ingestão do PDF
python src/chat.py         # 3. chat no terminal
pytest                     # testes unitários (sem chamadas externas)
ruff check .               # lint
ruff format .              # formatação
```

O ambiente de desenvolvimento é Windows. O README documenta os comandos de Windows e de Linux/macOS.

## Estrutura obrigatória

```text
├── docker-compose.yml
├── requirements.txt
├── .env.example      # template das variáveis de ambiente
├── src/
│   ├── ingest.py     # ingestão do PDF
│   ├── search.py     # busca
│   └── chat.py       # CLI de interação com o usuário
├── document.pdf      # PDF para ingestão
└── README.md         # instruções de execução
```

Não renomeie nem mova esses arquivos. Arquivos e pastas fora dessa estrutura são livres.

## Requisitos funcionais fixos

Os requisitos completos, com IDs rastreáveis (FR, BR, NFR, SEC, DATA), estão em `docs/prd/PRD.md`. Os itens abaixo são os fixos do enunciado.

Ingestão (`src/ingest.py`):

- Dividir o PDF em chunks de 1000 caracteres com overlap de 150.
- Converter cada chunk em embedding.
- Armazenar os vetores no PostgreSQL com pgVector.

Consulta (`src/search.py` e `src/chat.py`), ao receber uma pergunta:

1. Vetorizar a pergunta.
2. Buscar os 10 resultados mais relevantes: `similarity_search_with_score(query, k=10)`.
3. Montar o prompt abaixo e chamar a LLM.
4. Retornar a resposta ao usuário.

O chat abre com `Faça sua pergunta:` e usa os rótulos `PERGUNTA:` e `RESPOSTA:`. As respostas se baseiam apenas no conteúdo do PDF. Para perguntas fora do contexto, a resposta é exatamente:
`Não tenho informações necessárias para responder sua pergunta.`

Use este prompt sem alterar o texto. Os trechos entre chaves são os únicos pontos de substituição. Este é o texto canônico do prompt: specs e documentos referenciam esta seção em vez de copiá-lo.

```text
CONTEXTO:
{resultados concatenados do banco de dados}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta do usuário}

RESPONDA A "PERGUNTA DO USUÁRIO"
```

## Modelos

- O desafio não fixa modelos. Antes de escolher ou trocar um modelo de embeddings ou de LLM, consulte a documentação oficial do Google para ver os modelos disponíveis no momento. Não presuma nomes de modelos de memória.
- Para o volume deste desafio, prefira os modelos mais leves e baratos disponíveis no plano gratuito do Gemini, que é o plano em uso.
- Nomes de modelos e credenciais ficam em variáveis de ambiente (`.env`), com o template mantido em `.env.example`.
- A tabela de vetores é criada na primeira ingestão, com a dimensão do modelo de embeddings escolhido. Trocar o modelo depois disso faz a ingestão falhar por incompatibilidade de dimensão. A correção exige apagar a collection existente (ou o volume do banco) e refazer a ingestão do zero: é uma operação destrutiva, peça confirmação antes.

## Git e commits

- Nunca faça commit nem push automaticamente. Sempre peça permissão antes de cada commit e de cada push (o repositório é público).
- Cada fase de desenvolvimento usa uma nova branch de trabalho, criada a partir da `main`, no padrão `phase-<N>-<nome>` (ex.: `phase-2-ingestion`). As fases estão em `docs/project`.
- Cada fase entra na `main` por Pull Request, aberto com o GitHub CLI (`gh`). O merge é feito pelo dono do projeto.
- Mensagens de commit em português, no formato `<tipo>: <descrição>`.
- Remote `origin`: `https://github.com/fonsecamrs/mba-read-pdf-challenge-1.git`. Branch principal: `main`.

| Tipo | Uso |
| --- | --- |
| `feat` | Nova funcionalidade para o usuário |
| `fix` | Correção de bug ou erro |
| `docs` | Alterações apenas na documentação |
| `style` | Formatação ou estilo, sem afetar o código |
| `refactor` | Alteração que não corrige bug nem adiciona funcionalidade |
| `perf` | Melhoria de desempenho |
| `test` | Adição ou correção de testes |
| `chore` | Build, configuração de ferramentas ou pacotes |

## Restrições

Nunca faça sem pedir confirmação explícita:

- Commitar segredos ou chaves de API. O `.env` é ignorado pelo git; só o `.env.example`, sem valores reais, é versionado.
- Alterar o banco fora do que o `PGVector` gerencia sem um script versionado correspondente em `docs/database`.
- Executar comandos destrutivos no banco (`DROP`, `TRUNCATE`, `DELETE` sem cláusula), apagar a collection ou remover o volume do Docker (`docker compose down -v`).
- Fixar em código nomes de modelos, credenciais, caminhos ou parâmetros que pertencem ao `.env`.
- Adicionar arquitetura ou abstrações além do escopo mínimo definido no ADR-001 (`docs/adr`).

## Specs e documentação

Documentação enxuta: crie apenas o necessário para orientar a implementação.

- `docs/prd/PRD.md`: requisitos do produto com IDs. Fonte da verdade do *o quê*.
- `specs/NNN-<funcionalidade>/spec.md`: especificação detalhada de cada funcionalidade (fluxos, exceções, critérios de aceite, casos de teste), referenciando os IDs do PRD.
- `docs/adr/ADR-NNN-<titulo>.md`: apenas decisões arquiteturais relevantes. Decisão ainda não tomada fica registrada como pendente, não inventada.
- `docs/project/phase-<N>-<nome>.md`: *como* implementar cada fase (escopo, entregas, critérios de aceite).

## Banco de dados

- As tabelas de vetores são criadas e gerenciadas pela integração `PGVector` do LangChain. Não há tabelas próprias nem migrations.
- `docs/database` guarda apenas scripts para o que a biblioteca não gerencia (ex.: a extensão `vector`), numerados no padrão `NNN-<acao>-<objeto>.sql` (ex.: `001-create-vector-extension.sql`).
- Se o projeto passar a ter tabelas próprias, adote migrations versionadas e registre a decisão em um ADR.

## Qualidade

- Lint e formatação com ruff.
- Testes unitários com pytest cobrem as partes previsíveis (normalização da resposta padrão, montagem do contexto e do prompt, comandos do chat) e nunca chamam o Gemini nem o banco.
- Os cenários de aceite do PRD são validados manualmente pelo roteiro documentado ao final de cada fase.

## Idioma

| Item | Idioma |
| --- | --- |
| Specs (`specs/`) | Inglês |
| Documentação técnica (`docs/`) e das fases (`docs/project`) | Inglês |
| Nomes de arquivos, classes, métodos e variáveis | Inglês |
| Comentários no código e mensagens de log | Inglês |
| Códigos de erro | Inglês, em dot-notation (`ingestion.pdf_not_found`) |
| Mensagens de commit | Português |
| Mensagens ao usuário final | Português |
| `README.md` (lido pelo corretor do MBA) | Português |
| Prompts enviados à IA | Português |

## Manutenção deste arquivo

- Este arquivo tem no máximo 200 linhas.
- Se uma alteração fizer o arquivo ultrapassar 200 linhas, não remova informações importantes para caber no limite: extraia as instruções específicas ou detalhadas para arquivos de Rules em `.claude/rules/`.
- Mantenha aqui apenas as instruções gerais, essenciais e de maior abrangência.
- Organize as Rules em um arquivo por assunto, com subdiretórios quando fizer sentido, e use o campo `paths` (globs) no frontmatter para que cada Rule seja aplicada somente aos arquivos ou diretórios relevantes.
- Referencie neste arquivo as Rules criadas e não duplique aqui o que já estiver definido nelas.