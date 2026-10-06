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

```bash
python3 -m venv venv && source venv/bin/activate   # antes de instalar dependências
pip install -r requirements.txt
docker compose up -d       # 1. sobe o banco
python src/ingest.py       # 2. ingestão do PDF
python src/chat.py         # 3. chat no terminal
```

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

Use este prompt sem alterar o texto. Os trechos entre chaves são os únicos pontos de substituição:

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
- Para o volume deste desafio, prefira os modelos mais leves e baratos.
- Nomes de modelos e credenciais ficam em variáveis de ambiente (`.env`), com o template mantido em `.env.example`.
- A tabela de vetores é criada na primeira ingestão, com a dimensão do modelo de embeddings escolhido. Trocar o modelo depois disso faz a ingestão falhar por incompatibilidade de dimensão. A correção exige apagar a collection existente (ou o volume do banco) e refazer a ingestão do zero: é uma operação destrutiva, peça confirmação antes.

## Git e commits

- Nunca faça commit automaticamente. Sempre peça permissão antes de cada commit.
- Se o projeto estiver organizado em fases de desenvolvimento, cada fase usa uma nova branch de trabalho.
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

- Editar arquivos de configuração de ambientes não locais.
- Commitar segredos, chaves de API ou a chave-mestra de criptografia.
- Alterar o schema do banco sem script versionado correspondente em `docs/database`.
- Executar comandos destrutivos no banco (`DROP`, `TRUNCATE`, `DELETE` sem cláusula) fora de ambiente efêmero de teste.
- Fixar em código o provedor de LLM, o broker ou o storage, contornando as portas.
- Introduzir dependência do domínio para qualquer outro projeto.

## Specs e documentação

- `specs/` é a fonte da verdade das regras de negócio: em inglês, focadas no *o quê*.
- `docs/project` detalha *como* implementar cada fase. Documente o desenho do projeto fase a fase, com a especificação de implementação de cada fase.

## Banco de dados

- Scripts de bootstrap em `docs/database`, numerados e prefixados por domínio, no padrão `NNN-create-<dominio>-<tabela>.sql`.
- Migrations versionadas.
- Convenções detalhadas em `specs/`.

## Idioma

| Item | Idioma |
| --- | --- |
| Specs (`specs/`) | Inglês |
| Documentação técnica (`docs/`) e das fases (`docs/project`) | Inglês |
| Nomes de arquivos, classes, métodos e variáveis | Inglês |
| Comentários no código e mensagens de log | Inglês |
| Códigos de erro | Inglês, em dot-notation (`receipt.not_found`) |
| Mensagens de commit | Português |
| Mensagens ao usuário final | Português |
| Prompts enviados à IA | Português |

## Manutenção deste arquivo

- Este arquivo tem no máximo 200 linhas.
- Se uma alteração fizer o arquivo ultrapassar 200 linhas, não remova informações importantes para caber no limite: extraia as instruções específicas ou detalhadas para arquivos de Rules em `.claude/rules/`.
- Mantenha aqui apenas as instruções gerais, essenciais e de maior abrangência.
- Organize as Rules em um arquivo por assunto, com subdiretórios quando fizer sentido, e use o campo `paths` (globs) no frontmatter para que cada Rule seja aplicada somente aos arquivos ou diretórios relevantes.
- Referencie neste arquivo as Rules criadas e não duplique aqui o que já estiver definido nelas.