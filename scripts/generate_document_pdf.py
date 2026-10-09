"""Generates document.pdf: the fictitious knowledge base of SuperTechIABrazil (Portuguese).

Every company, person, client, product, certification, award, address, event and number in
this document is fictitious and was created exclusively for this project.

Usage: python scripts/generate_document_pdf.py [output.pdf]   (default: document.pdf)
Requires the development dependencies (requirements-dev.txt).
"""

import sys

from fpdf import FPDF
from fpdf.fonts import FontFace

DEFAULT_OUTPUT = "document.pdf"
REFERENCE_DATE = "outubro de 2026"

# Core PDF fonts only support Latin-1: replace typographic characters outside it
LATIN1_REPLACEMENTS = {"–": "-", "—": "-", "“": '"', "”": '"', "‘": "'", "’": "'", "•": "-"}

# ---------------------------------------------------------------------------------------------
# Data shared by several sections (consistency is checked in check_consistency)
# ---------------------------------------------------------------------------------------------

# Year: (revenue, operating costs, expenses, investments), in R$ millions
FINANCIALS = {
    2021: (102.5, 58.4, 33.1, 14.2),
    2022: (118.9, 67.3, 41.8, 21.6),
    2023: (141.3, 77.0, 49.5, 24.8),
    2024: (164.7, 86.6, 55.2, 22.5),
    2025: (192.4, 98.1, 62.6, 26.3),
}
REVENUE_2020 = 88.0

# Department, board area, employees, managers (end of 2025)
DEPARTMENTS = [
    ("Engenharia de Software", "Tecnologia", 241, 8),
    ("Infraestrutura, Nuvem e DevOps", "Tecnologia", 48, 2),
    ("Segurança da Informação", "Tecnologia", 18, 1),
    ("Produtos e Experiência do Usuário (UX)", "Tecnologia", 42, 1),
    ("Centro de Excelência em IA e Dados (CEIA)", "IA e Dados", 96, 7),
    ("Serviços Profissionais e Implantação", "Operações e Serviços", 64, 5),
    ("Suporte e Sucesso do Cliente", "Operações e Serviços", 52, 3),
    ("Comercial e Marketing", "Comercial e Marketing", 34, 5),
    ("Pessoas e Cultura", "Pessoas e Cultura", 14, 2),
    ("Financeiro, Jurídico e Administrativo", "Financeira", 24, 4),
]
EXECUTIVE_BOARD = 7  # CEO + 6 directors
TOTAL_EMPLOYEES = 640
TOTAL_MANAGERS = 38

# Unit, city, opening year, employees (end of 2025), focus
UNITS = [
    ("Sede", "Campinas (SP)", 2005, 352, "Engenharia, CEIA, produtos e áreas corporativas"),
    ("Filial", "São Paulo (SP)", 2011, 128, "Comercial, serviços financeiros e consultoria"),
    ("Filial", "Belo Horizonte (MG)", 2015, 84, "Indústria, agronegócio e implantação"),
    ("Filial", "Recife (PE)", 2022, 46, "Hub de engenharia e suporte do Nordeste"),
    ("Filial", "Porto Alegre (RS)", 2024, 30, "Centro de agentes de IA e clientes do Sul"),
]

# Business line, revenue in 2025 (R$ millions)
REVENUE_BY_LINE_2025 = [
    ("GestPro Cloud (ERP em nuvem, assinatura)", 54.2),
    ("AgentFlow (agentes de IA e automação, assinatura)", 31.5),
    ("AtendIA (atendimento com IA generativa, assinatura)", 24.8),
    ("InsightHub e PrevisIA (dados, analytics e IA preditiva, assinatura)", 22.6),
    ("ConectaAPI (integração e APIs, assinatura)", 12.1),
    ("Serviços profissionais (projetos sob medida, consultoria e implantação)", 47.2),
]

# Segment, share of 2025 revenue (%)
SEGMENTS = [
    ("Varejo", 24),
    ("Indústria", 21),
    ("Serviços financeiros e cooperativas de crédito", 17),
    ("Saúde", 12),
    ("Logística e transporte", 10),
    ("Agronegócio", 8),
    ("Educação", 5),
    ("Energia e saneamento", 3),
]

# Year, social donations and investments (R$ millions)
DONATIONS = {2021: 0.60, 2022: 0.70, 2023: 0.85, 2024: 0.95, 2025: 1.10}


def brl(value: float) -> str:
    """Format R$ millions in Brazilian style: 192.4 -> 'R$ 192,4 milhões', 0.85 -> 'R$ 850 mil'."""
    if value < 1:
        return f"R$ {round(value * 1000)} mil"
    unit = "milhão" if value < 2 else "milhões"
    return f"R$ {value:.1f} {unit}".replace(".", ",")


def pct(value: float) -> str:
    return f"{value:.1f}%".replace(".", ",")


def check_consistency() -> None:
    for year, (revenue, costs, expenses, _investments) in FINANCIALS.items():
        assert round(revenue - costs - expenses, 1) > 0, year
    assert sum(d[2] for d in DEPARTMENTS) + EXECUTIVE_BOARD == TOTAL_EMPLOYEES
    assert sum(d[3] for d in DEPARTMENTS) == TOTAL_MANAGERS
    assert sum(u[3] for u in UNITS) == TOTAL_EMPLOYEES
    assert round(sum(v for _, v in REVENUE_BY_LINE_2025), 1) == FINANCIALS[2025][0]
    assert sum(s for _, s in SEGMENTS) == 100


def number(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")


def financial_rows() -> list[list[str]]:
    """One line per year, values in R$ millions (the unit goes in the table headings)."""
    rows = []
    previous = REVENUE_2020
    for year, (revenue, costs, expenses, investments) in FINANCIALS.items():
        profit = round(revenue - costs - expenses, 1)
        rows.append(
            [
                str(year),
                number(revenue),
                number(costs),
                number(expenses),
                number(profit),
                pct(profit / revenue * 100),
                number(investments),
                pct((revenue / previous - 1) * 100),
            ]
        )
        previous = revenue
    return rows


def financial_paragraphs() -> list[tuple]:
    notes = {
        2021: "Primeiro ano do Programa IA em Tudo e da gestão do CEO Rafael Ishikawa Duarte. "
        "A receita cresceu impulsionada pela migração de clientes para o GestPro Cloud.",
        2022: "Ano de maior investimento da transformação para a IA: a expansão do CEIA e a "
        "abertura da filial de Recife elevaram as despesas e reduziram a margem.",
        2023: "Lançamento do AtendIA, primeiro produto de IA generativa, que atingiu 61 clientes "
        "contratantes ao final do ano. A margem voltou a crescer.",
        2024: "Lançamento do AgentFlow e abertura da filial de Porto Alegre. Os ganhos de "
        "produtividade com IA nos processos internos reduziram o peso dos custos.",
        2025: "Melhor resultado da história da empresa, no ano em que completou 20 anos. "
        "AgentFlow e AtendIA somaram R$ 56,3 milhões, ou 29,3% da receita.",
    }
    blocks = []
    previous = REVENUE_2020
    for year, (revenue, costs, expenses, investments) in FINANCIALS.items():
        profit = round(revenue - costs - expenses, 1)
        blocks.append(
            (
                "p",
                f"Resultado de {year}: a receita anual da SuperTechIABrazil em {year} foi de "
                f"{brl(revenue)}, com crescimento de {pct((revenue / previous - 1) * 100)} em "
                f"relação ao ano anterior. Os custos operacionais foram de {brl(costs)} e as "
                f"despesas, de {brl(expenses)}. O lucro líquido foi de {brl(profit)}, com margem "
                f"de lucro de {pct(profit / revenue * 100)}. Os investimentos somaram "
                f"{brl(investments)}. {notes[year]}",
            )
        )
        previous = revenue
    return blocks


# ---------------------------------------------------------------------------------------------
# Content: list of blocks (kind, ...) rendered in order
# ---------------------------------------------------------------------------------------------


def content() -> list[tuple]:
    return [
        ("title", "SuperTechIABrazil"),
        ("subtitle", "Base de Conhecimento Empresarial"),
        (
            "p",
            "AVISO: este documento é inteiramente fictício. A SuperTechIABrazil não existe. "
            "Todos os nomes de pessoas, clientes, produtos, certificações, prêmios, endereços, "
            "eventos e valores foram inventados exclusivamente para o projeto de busca semântica "
            "do MBA em IA e não representam nenhuma organização real.",
        ),
        ("p", f"Data de referência das informações: {REFERENCE_DATE}."),
        # 1 -------------------------------------------------------------------------------------
        ("h1", "1. Informações institucionais"),
        (
            "table",
            ["Item", "Informação"],
            [
                ["Nome da empresa", "SuperTechIABrazil"],
                ["Razão social", "SuperTechIABrazil Tecnologia S.A. (capital fechado)"],
                ["Ramo de atividade", "Desenvolvimento de software e soluções de tecnologia"],
                ["Ano de fundação", "2005"],
                ["Anos de atuação", "21 anos (2005 a 2026)"],
                [
                    "Sede",
                    "Rua dos Algoritmos, 2005, Polo Tecnológico Alvorada, Campinas (SP)",
                ],
                [
                    "Unidades",
                    "Sede em Campinas e filiais em São Paulo, Belo Horizonte, "
                    "Recife e Porto Alegre",
                ],
                ["Fundadores", "Henrique Valadares Moura e Lúcia Carvalho Prado"],
                ["CEO atual", "Rafael Ishikawa Duarte (desde 2021)"],
                ["Funcionários (final de 2025)", str(TOTAL_EMPLOYEES)],
                ["Clientes ativos (final de 2025)", "412 clientes em 19 estados"],
                ["Receita anual de 2025", brl(FINANCIALS[2025][0])],
            ],
        ),
        # Own page: PDF pages are loaded separately, so this section becomes a focused chunk
        ("pagebreak",),
        ("h2", "1.1 Missão, visão e valores da SuperTechIABrazil"),
        (
            "p",
            "A missão da SuperTechIABrazil é simplificar a gestão e acelerar a transformação "
            "digital das empresas brasileiras com software confiável e Inteligência Artificial "
            "responsável.",
        ),
        (
            "p",
            "A visão da SuperTechIABrazil é ser, até 2030, a principal referência brasileira em "
            "agentes de IA e automação inteligente para empresas de médio porte.",
        ),
        ("p", "Os valores da SuperTechIABrazil são:"),
        (
            "bullets",
            [
                "Cliente no centro: cada decisão começa pelo impacto no negócio do cliente.",
                "Ética e transparência: IA explicável, uso responsável de dados e respeito à "
                "privacidade.",
                "Aprendizado contínuo: todos ensinam e todos aprendem.",
                "Excelência técnica: qualidade, segurança e simplicidade em cada entrega.",
                "Colaboração: times multidisciplinares e decisões compartilhadas.",
                "Impacto positivo: compromisso com a sociedade e com o meio ambiente.",
            ],
        ),
        ("pagebreak",),
        ("h2", "1.2 Objetivos básicos da empresa"),
        (
            "p",
            "Sobrevivência: manter a empresa financeiramente saudável e relevante no longo prazo, "
            "com receita recorrente predominante (75,5% da receita de 2025 veio de assinaturas), "
            "reserva de caixa equivalente a seis meses de despesas e nenhum cliente "
            "representando mais de 5% da receita.",
        ),
        (
            "p",
            "Lucratividade: gerar lucro sustentável para reinvestir em inovação. A meta "
            "corporativa é manter a margem de lucro líquido acima de 15%, alcançada em 2025 "
            "(16,5%).",
        ),
        (
            "p",
            "Crescimento: crescer acima de 15% ao ano em receita, ampliando a base de clientes, "
            "a presença regional e o portfólio de produtos de Inteligência Artificial. A meta "
            "para 2030 é atingir receita anual de R$ 400 milhões.",
        ),
        ("h2", "1.3 Especialidades e principais áreas de atuação"),
        (
            "bullets",
            [
                "Software de gestão empresarial (ERP) em nuvem para médias empresas.",
                "Agentes de IA e automação inteligente de processos.",
                "IA generativa aplicada ao atendimento ao cliente.",
                "Dados, analytics e IA preditiva (previsão de demanda, estoque e safra).",
                "Integração de sistemas, APIs e microsserviços.",
                "Desenvolvimento de software sob medida, aplicativos web e móveis.",
                "Consultoria em nuvem, DevOps e segurança da informação.",
            ],
        ),
        ("h2", "1.4 Localização e unidades"),
        (
            "table",
            ["Unidade", "Cidade", "Inauguração", "Funcionários (2025)", "Foco"],
            [[u[0], u[1], str(u[2]), str(u[3]), u[4]] for u in UNITS],
        ),
        # 2 -------------------------------------------------------------------------------------
        ("h1", "2. História e evolução"),
        ("h2", "2.1 Fundação"),
        (
            "p",
            "A SuperTechIABrazil foi fundada em março de 2005, em Campinas (SP), pelo engenheiro "
            "de computação Henrique Valadares Moura e pela analista de sistemas Lúcia Carvalho "
            "Prado. A empresa começou com cinco pessoas, capital inicial de R$ 80 mil e uma sala "
            "de 60 m² na Incubadora de Empresas Semente Digital. O primeiro projeto foi um "
            "sistema de controle de estoque desenvolvido em 2006 para os Supermercados Vale "
            "Verde, que na época tinham 12 lojas.",
        ),
        ("h2", "2.2 Principais fases de crescimento"),
        (
            "table",
            ["Fase", "Período", "Foco", "Funcionários ao final"],
            [
                [
                    "1. Fundação e software sob medida",
                    "2005-2008",
                    "Sistemas desktop cliente-servidor para o varejo e a indústria regional",
                    "22",
                ],
                [
                    "2. Web e primeiros produtos",
                    "2009-2011",
                    "Aplicações web, lançamento do GestPro Web, filial de São Paulo",
                    "85",
                ],
                [
                    "3. Nuvem e mobilidade",
                    "2012-2015",
                    "GestPro Cloud (SaaS), aplicativos móveis, filial de Belo Horizonte",
                    "190",
                ],
                [
                    "4. Plataformas, APIs e DevOps",
                    "2016-2017",
                    "Microsserviços, ConectaAPI, cultura DevOps, transformação em S.A.",
                    "260",
                ],
                [
                    "5. Dados e IA aplicada",
                    "2018-2020",
                    "InsightHub, primeira equipe de ciência de dados, PrevisIA",
                    "360",
                ],
                [
                    "6. Transformação para a IA",
                    "2021-2023",
                    "Programa IA em Tudo, CEIA, IA generativa e AtendIA",
                    "510",
                ],
                [
                    "7. Agentes e automação inteligente",
                    "2024-2026",
                    "AgentFlow, agentes de IA, filial de Porto Alegre",
                    "640 (2025)",
                ],
            ],
        ),
        ("h2", "2.3 Linha do tempo dos principais marcos"),
        (
            "table",
            ["Ano", "Marco"],
            [
                ["2005", "Fundação em Campinas, com 5 pessoas."],
                ["2006", "Primeiro cliente: Supermercados Vale Verde."],
                ["2007", "Lançamento do SuperGestão Desktop, primeiro produto próprio."],
                ["2009", "Lançamento do GestPro Web, primeira versão web do sistema de gestão."],
                ["2010", "Receita anual de R$ 9,8 milhões e 58 funcionários."],
                ["2011", "Inauguração da filial de São Paulo."],
                ["2012", "Lançamento do GestPro Cloud, versão em nuvem por assinatura."],
                ["2013", "Lançamento do aplicativo Campo Móvel para equipes externas."],
                ["2014", "Lúcia Carvalho Prado assume como CEO."],
                [
                    "2015",
                    "Filial de Belo Horizonte; descontinuação do SuperGestão Desktop; "
                    "receita de R$ 38,5 milhões.",
                ],
                [
                    "2016",
                    "Transformação em sociedade anônima, criação do Conselho de "
                    "Administração, lançamento da ConectaAPI e criação do Instituto SuperTech.",
                ],
                ["2017", "Adoção da cultura DevOps e entrega contínua em todos os produtos."],
                ["2018", "Lançamento do InsightHub e criação da equipe de ciência de dados."],
                ["2019", "Lançamento do PrevisIA, primeiro produto com aprendizado de máquina."],
                [
                    "2020",
                    "Trabalho remoto durante a pandemia e adoção do modelo híbrido; "
                    "receita de R$ 88,0 milhões.",
                ],
                [
                    "2021",
                    "Rafael Ishikawa Duarte assume como CEO; início do Programa IA em "
                    "Tudo e criação do CEIA.",
                ],
                ["2022", "Filial de Recife e criação do Comitê de Ética e IA Responsável."],
                ["2023", "Lançamento do AtendIA, primeiro produto de IA generativa."],
                ["2024", "Lançamento do AgentFlow e inauguração da filial de Porto Alegre."],
                ["2025", "20 anos da empresa, 640 funcionários e receita de R$ 192,4 milhões."],
                [
                    "2026",
                    "Lançamento do AgentFlow 2.0 com agentes colaborativos entre "
                    "sistemas (abril de 2026).",
                ],
            ],
        ),
        ("h2", "2.4 Expansão da empresa"),
        (
            "p",
            "A expansão geográfica acompanhou a demanda dos clientes. A filial de São Paulo "
            "(2011) aproximou a empresa dos clientes de serviços financeiros e de grandes redes "
            "varejistas. Belo Horizonte (2015) atendeu à indústria e ao agronegócio do Sudeste e "
            "do Centro-Oeste. Recife (2022) tornou-se o hub de engenharia e suporte do "
            "Nordeste, contratando talentos formados pelo programa Código do Futuro. Porto "
            "Alegre (2024) concentra o centro de agentes de IA e os clientes da região Sul. Em "
            "2025, a empresa atendia clientes em 19 estados brasileiros.",
        ),
        ("h2", "2.5 Mudanças internas e organizacionais"),
        (
            "bullets",
            [
                "2010: adoção de processos formais de desenvolvimento e gestão de projetos, "
                "necessária para a primeira certificação de maturidade.",
                "2014: primeira sucessão de CEO; Henrique Valadares Moura passa a se dedicar à "
                "estratégia de produtos e, em 2016, à presidência do Conselho de Administração.",
                "2016: transformação em sociedade anônima de capital fechado, com Conselho de "
                "Administração de 5 membros (2 independentes), e reorganização da engenharia "
                "em squads ágeis por produto.",
                "2017: criação da área de Infraestrutura, Nuvem e DevOps e adoção de entrega "
                "contínua.",
                "2020: modelo de trabalho híbrido, com presença no escritório 2 dias por semana.",
                "2021: criação da Diretoria de IA e Dados e do Centro de Excelência em IA e "
                "Dados (CEIA).",
                "2022: criação do Comitê de Ética e IA Responsável.",
                "2023: adoção do modelo de trabalho 'IA primeiro', em que todo processo interno "
                "é avaliado quanto ao uso de IA antes de ser redesenhado.",
                "2024: criação da Academia SuperTech também para clientes e parceiros.",
            ],
        ),
        ("h2", "2.6 Evolução tecnológica ao longo dos anos"),
        (
            "table",
            ["Período", "Tecnologia", "Impacto na empresa"],
            [
                [
                    "2005-2008",
                    "Software tradicional desktop (cliente-servidor)",
                    "Projetos sob medida e o SuperGestão Desktop",
                ],
                ["2009-2011", "Aplicações web", "GestPro Web e acesso pelo navegador"],
                [
                    "2012-2015",
                    "Computação em nuvem (SaaS)",
                    "GestPro Cloud e modelo de receita por assinatura",
                ],
                ["2013-2016", "Aplicativos móveis", "Campo Móvel e apps sob medida para clientes"],
                [
                    "2016-2017",
                    "Microsserviços e APIs",
                    "Reescrita da plataforma em microsserviços e lançamento da ConectaAPI",
                ],
                [
                    "2017",
                    "DevOps",
                    "Entrega contínua: de 1 versão por mês para mais de 40 implantações por dia",
                ],
                ["2018-2020", "Dados e analytics; aprendizado de máquina", "InsightHub e PrevisIA"],
                ["2021-2022", "Inteligência Artificial em escala", "Programa IA em Tudo e CEIA"],
                ["2023", "IA generativa", "AtendIA e assistente de código interno CodeAssist"],
                [
                    "2024-2026",
                    "Agentes de IA e automação de processos",
                    "AgentFlow e automação de 58 processos internos",
                ],
            ],
        ),
        ("h2", "2.7 Transformação para a era da Inteligência Artificial"),
        (
            "p",
            "A entrada na Inteligência Artificial foi a maior transformação interna da história "
            "da empresa. Os primeiros passos vieram em 2018, com a equipe de ciência de dados, e "
            "em 2019, com o PrevisIA. Em 2021, o novo CEO Rafael Ishikawa Duarte lançou o "
            "Programa IA em Tudo, com três pilares: produtos, processos e pessoas.",
        ),
        (
            "bullets",
            [
                "Investimento: R$ 25,0 milhões entre 2021 e 2023 (R$ 6,0 milhões em 2021, "
                "R$ 9,5 milhões em 2022 e R$ 9,5 milhões em 2023), parte dos investimentos "
                "totais da empresa no período.",
                "Equipes: criação do CEIA em 2021 com 18 profissionais; o centro chegou a 96 "
                "profissionais em 2025.",
                "Capacitação: até 2023, 100% dos funcionários concluíram a trilha básica de IA "
                "da Academia SuperTech (40 horas); até 2025, 186 profissionais concluíram a "
                "trilha avançada.",
                "Produtos: todos os produtos passaram a ter recursos de IA; lançamento do "
                "AtendIA (2023) e do AgentFlow (2024).",
                "Processos: o assistente de código CodeAssist aumentou em 27% a produtividade "
                "das equipes de engenharia em 2023; em 2025, 58 processos internos eram "
                "executados com apoio de agentes de IA.",
                "Governança: Comitê de Ética e IA Responsável (2022) e Certificação em IA "
                "Responsável (2025).",
                "Estratégia: a meta de que produtos de IA representem metade da receita até 2028.",
            ],
        ),
        ("h2", "2.8 Principais acontecimentos e conquistas"),
        (
            "bullets",
            [
                "Crescimento contínuo de receita desde a fundação, sem nenhum ano de prejuízo "
                "desde 2008.",
                "Mais de 20 anos de relacionamento com o primeiro cliente, os Supermercados "
                "Vale Verde.",
                "Prêmio Inovação Digital Brasil 2019 com o PrevisIA.",
                "Prêmio Transformação com IA 2024, categoria Agentes, com o AgentFlow.",
                "3.200 jovens formados pelo programa social Código do Futuro entre 2016 e 2025.",
            ],
        ),
        # 3 -------------------------------------------------------------------------------------
        ("h1", "3. Estrutura organizacional"),
        ("h2", "3.1 Números da estrutura (final de 2025)"),
        (
            "table",
            ["Indicador", "Quantidade"],
            [
                ["Número total de funcionários", str(TOTAL_EMPLOYEES)],
                ["Número de diretores (sem contar o CEO)", "6"],
                ["Diretoria executiva (CEO e diretores)", str(EXECUTIVE_BOARD)],
                ["Número de gerentes", str(TOTAL_MANAGERS)],
                ["Coordenadores e líderes técnicos", "64"],
                ["Membros do Conselho de Administração", "5 (2 independentes)"],
                ["Número de CEOs ao longo da história", "3"],
                ["Departamentos", str(len(DEPARTMENTS))],
            ],
        ),
        ("h2", "3.2 CEOs ao longo da história"),
        (
            "table",
            ["CEO", "Período", "Destaques da gestão"],
            [
                [
                    "Henrique Valadares Moura (cofundador)",
                    "2005-2014",
                    "Fundação, primeiros produtos, entrada na web e na nuvem",
                ],
                [
                    "Lúcia Carvalho Prado (cofundadora)",
                    "2014-2021",
                    "Expansão nacional, transformação em S.A., APIs, DevOps e dados",
                ],
                [
                    "Rafael Ishikawa Duarte",
                    "2021-atual",
                    "Programa IA em Tudo, IA generativa e agentes de IA",
                ],
            ],
        ),
        (
            "p",
            "Rafael Ishikawa Duarte entrou na empresa em 2009 como desenvolvedor e foi diretor "
            "de tecnologia entre 2016 e 2021, antes de assumir como CEO. Lúcia Carvalho Prado é "
            "membro do Conselho de Administração desde 2021.",
        ),
        ("h2", "3.3 Estrutura hierárquica"),
        (
            "bullets",
            [
                "Nível 1: Conselho de Administração (5 membros), presidido pelo cofundador "
                "Henrique Valadares Moura.",
                "Nível 2: CEO (Rafael Ishikawa Duarte).",
                "Nível 3: Diretoria executiva com 6 diretorias.",
                "Nível 4: 38 gerências.",
                "Nível 5: 64 coordenações e lideranças técnicas de squads.",
                "Nível 6: equipes e squads multidisciplinares.",
            ],
        ),
        ("h2", "3.4 Diretoria executiva"),
        (
            "table",
            ["Diretoria", "Diretor(a)", "Responsabilidades"],
            [
                [
                    "Tecnologia (CTO)",
                    "Mariana Teles Bastos",
                    "Engenharia, nuvem, DevOps, segurança e produtos",
                ],
                ["IA e Dados", "Diego Matsuda Ferraz", "CEIA, ciência de dados e IA responsável"],
                [
                    "Financeira (CFO)",
                    "Paulo Henrique Rezende Lago",
                    "Finanças, jurídico, compras e administração",
                ],
                [
                    "Operações e Serviços (COO)",
                    "Beatriz Nogueira Sales",
                    "Implantação, serviços profissionais, suporte e sucesso do cliente",
                ],
                [
                    "Comercial e Marketing",
                    "André Lacerda Pimentel",
                    "Vendas, parcerias, marketing e relacionamento",
                ],
                [
                    "Pessoas e Cultura",
                    "Carla Menezes Rocha",
                    "Recrutamento, Academia SuperTech, cultura e benefícios",
                ],
            ],
        ),
        ("h2", "3.5 Principais departamentos e áreas internas (final de 2025)"),
        (
            "table",
            ["Departamento", "Diretoria", "Funcionários", "Gerentes"],
            [[d[0], d[1], str(d[2]), str(d[3])] for d in DEPARTMENTS]
            + [["Diretoria executiva (CEO e diretores)", "-", str(EXECUTIVE_BOARD), "-"]]
            + [["Total", "-", str(TOTAL_EMPLOYEES), str(TOTAL_MANAGERS)]],
        ),
        ("h2", "3.6 Evolução do número de funcionários"),
        (
            "table",
            ["Ano", "Funcionários"],
            [
                [str(y), str(n)]
                for y, n in [
                    (2005, 5),
                    (2007, 15),
                    (2008, 22),
                    (2010, 58),
                    (2011, 85),
                    (2013, 140),
                    (2015, 190),
                    (2017, 260),
                    (2018, 290),
                    (2020, 360),
                    (2021, 395),
                    (2022, 450),
                    (2023, 510),
                    (2024, 575),
                    (2025, 640),
                ]
            ],
        ),
        # 4 -------------------------------------------------------------------------------------
        ("h1", "4. Mercado e certificações"),
        ("h2", "4.1 Segmentos de mercado atendidos (participação na receita de 2025)"),
        ("table", ["Segmento", "Participação"], [[s, f"{p}%"] for s, p in SEGMENTS]),
        ("h2", "4.2 Posicionamento no mercado"),
        (
            "p",
            "A SuperTechIABrazil é especializada em empresas de médio porte, com faturamento "
            "entre R$ 50 milhões e R$ 2 bilhões, segmento em que combina sistemas de gestão em "
            "nuvem com agentes de IA. Segundo o estudo fictício Panorama Software Brasil 2025, a "
            "empresa ocupa a 4ª posição entre os fornecedores nacionais de ERP em nuvem para "
            "médias empresas e a 1ª posição em agentes de IA para esse segmento. Seus "
            "diferenciais são o suporte em português 24 horas por dia, a implantação em até 90 "
            "dias e a integração nativa entre ERP, dados e IA.",
        ),
        ("h2", "4.3 Certificações"),
        (
            "table",
            ["Ano", "Certificação (fictícia)", "Entidade emissora (fictícia)", "Situação"],
            [
                [
                    "2010",
                    "Selo Brasileiro de Maturidade em Processos de Software (SBMPS), Nível C",
                    "Associação Brasileira de Qualidade de Software (ABQS)",
                    "Substituída pelo Nível A",
                ],
                ["2016", "SBMPS Nível A", "ABQS", "Vigente, renovada em 2025"],
                [
                    "2014",
                    "Certificação Nacional de Qualidade em Serviços de TI (CNQ-TI)",
                    "Instituto Nacional de Serviços Digitais (INSD)",
                    "Vigente",
                ],
                [
                    "2017",
                    "Certificação Brasileira de Segurança da Informação (CBSI)",
                    "Conselho Brasileiro de Segurança Digital (CBSD)",
                    "Vigente, renovada em 2020 e 2023",
                ],
                [
                    "2019",
                    "Selo Nuvem Confiável",
                    "Associação Brasileira de Serviços em Nuvem (ABSN)",
                    "Vigente",
                ],
                [
                    "2022",
                    "Selo de Privacidade e Proteção de Dados (SPPD)",
                    "Instituto Brasileiro de Privacidade Digital (IBPD)",
                    "Vigente",
                ],
                [
                    "2025",
                    "Certificação em IA Responsável (CIAR), nível Avançado",
                    "Instituto Brasileiro de Ética em IA (IBEIA)",
                    "Vigente",
                ],
                ["2025", "Selo Carbono Consciente", "Rede Empresarial pelo Clima (REC)", "Vigente"],
            ],
        ),
        ("h2", "4.4 Reconhecimentos do mercado"),
        (
            "table",
            ["Ano", "Reconhecimento (fictício)"],
            [
                ["2012", "Prêmio Inova Interior, categoria Startup de Software"],
                ["2019", "Prêmio Inovação Digital Brasil, categoria IA Aplicada, com o PrevisIA"],
                ["2021", "Selo Empresa que Mais Capacita em Tecnologia, Guia Carreira Tech"],
                [
                    "2023, 2024 e 2025",
                    "Ranking Melhores Lugares para Trabalhar em Tecnologia, "
                    "Guia Carreira Tech (entre as 10 primeiras de médio porte)",
                ],
                ["2024", "Prêmio Transformação com IA, categoria Agentes, com o AgentFlow"],
                ["2025", "Prêmio Empresa Cidadã Digital, pelo programa Código do Futuro"],
            ],
        ),
        # 5 -------------------------------------------------------------------------------------
        ("h1", "5. Clientes"),
        ("h2", "5.1 Visão geral"),
        (
            "p",
            "Ao final de 2025, a SuperTechIABrazil tinha 412 clientes ativos em 19 estados. Os "
            "10 maiores clientes representaram 31% da receita de 2025, e nenhum cliente "
            "isolado ultrapassou 5% da receita. A taxa de renovação anual dos contratos de "
            "assinatura foi de 94% em 2025.",
        ),
        ("h2", "5.2 Principais clientes (fictícios)"),
        (
            "table",
            ["Cliente", "Segmento", "Cliente desde", "Principais soluções"],
            [
                [
                    "Supermercados Vale Verde",
                    "Varejo alimentar",
                    "2006",
                    "GestPro Cloud, PrevisIA, AgentFlow",
                ],
                [
                    "MetalForte Autopeças",
                    "Indústria",
                    "2010",
                    "GestPro Cloud, ConectaAPI, AgentFlow",
                ],
                [
                    "TransLog Expresso",
                    "Logística e transporte",
                    "2014",
                    "Campo Móvel, InsightHub, roteirização com IA",
                ],
                [
                    "Banco Cooperativo Horizonte",
                    "Serviços financeiros",
                    "2016",
                    "ConectaAPI, AtendIA",
                ],
                ["Hospital Santa Aurora", "Saúde", "2018", "InsightHub, AgentFlow"],
                [
                    "Cooperativa Agro Cerrado Unido",
                    "Agronegócio",
                    "2019",
                    "PrevisIA, GestPro Cloud",
                ],
                ["Universidade Nova Fronteira", "Educação", "2021", "AtendIA, InsightHub"],
                ["Energia Planalto Distribuidora", "Energia", "2022", "AgentFlow, ConectaAPI"],
            ],
        ),
        ("h2", "5.3 Relacionamento e projetos realizados"),
        (
            "p",
            "Supermercados Vale Verde (varejo alimentar, 86 lojas em 2025): primeiro cliente da "
            "empresa, desde 2006. Em 2007 adotou o SuperGestão Desktop e, em 2012, foi um dos "
            "primeiros a migrar para o GestPro Cloud. Em 2019, o PrevisIA reduziu em 23% a falta "
            "de produtos nas prateleiras. Em 2024, agentes do AgentFlow passaram a gerar "
            "automaticamente os pedidos de reposição das lojas.",
        ),
        (
            "p",
            "MetalForte Autopeças (indústria): cliente desde 2010. Em 2017, a ConectaAPI "
            "integrou a empresa a 140 fornecedores, reduzindo de 5 dias para 6 horas o ciclo "
            "de compras. Em 2025, agentes de IA passaram a apoiar o planejamento da produção, "
            "com redução de 18% nos estoques parados.",
        ),
        (
            "p",
            "TransLog Expresso (logística e transporte): cliente desde 2014, quando adotou o "
            "aplicativo Campo Móvel para 1.300 motoristas. Em 2022, um projeto de roteirização "
            "com IA reduziu em 14% o consumo de combustível da frota.",
        ),
        (
            "p",
            "Banco Cooperativo Horizonte (serviços financeiros): cliente desde 2016, com a "
            "integração de canais digitais pela ConectaAPI. Em 2023, implantou o AtendIA, que "
            "passou a atender 1,2 milhão de conversas por mês, resolvendo 68% delas sem "
            "atendente humano.",
        ),
        (
            "p",
            "Hospital Santa Aurora (saúde, 420 leitos): cliente desde 2018, com painéis do "
            "InsightHub para gestão de ocupação de leitos. Em 2024, agentes do AgentFlow "
            "passaram a confirmar e remarcar consultas, reduzindo em 31% as faltas de "
            "pacientes.",
        ),
        (
            "p",
            "Cooperativa Agro Cerrado Unido (agronegócio, 5.400 cooperados): cliente desde 2019. "
            "O PrevisIA passou a estimar a produção das safras com erro médio de 4%, apoiando o "
            "planejamento de armazenagem e de vendas.",
        ),
        (
            "p",
            "Universidade Nova Fronteira (educação, 38 mil alunos): cliente desde 2021. Em 2023, "
            "o AtendIA assumiu o atendimento a estudantes sobre matrículas, bolsas e "
            "documentos, com tempo médio de resposta de 20 segundos.",
        ),
        (
            "p",
            "Energia Planalto Distribuidora (energia): cliente desde 2022. Em 2025, o AgentFlow "
            "automatizou a abertura e a priorização de ordens de serviço de manutenção, "
            "reduzindo em 26% o tempo médio de atendimento das ocorrências.",
        ),
        # 6 -------------------------------------------------------------------------------------
        ("h1", "6. Produtos e soluções"),
        ("h2", "6.1 Portfólio atual"),
        (
            "table",
            ["Produto", "Lançamento", "Categoria", "Descrição"],
            [
                [
                    "GestPro Cloud",
                    "2012",
                    "Sistema de gestão (ERP) em nuvem",
                    "Finanças, estoque, compras, vendas, fiscal e produção para médias empresas",
                ],
                [
                    "ConectaAPI",
                    "2016",
                    "Plataforma de integração",
                    "Integração de sistemas por APIs, com mais de 300 conectores prontos",
                ],
                [
                    "InsightHub",
                    "2018",
                    "Dados e analytics",
                    "Painéis, indicadores e consultas em linguagem natural",
                ],
                [
                    "PrevisIA",
                    "2019",
                    "IA preditiva",
                    "Previsão de demanda, estoque e safra com aprendizado de máquina",
                ],
                [
                    "AtendIA",
                    "2023",
                    "IA generativa",
                    "Assistente virtual de atendimento em canais de mensagem e na web",
                ],
                [
                    "AgentFlow",
                    "2024",
                    "Agentes de IA e automação",
                    "Criação e operação de agentes de IA que executam processos de ponta a ponta",
                ],
            ],
        ),
        ("h2", "6.2 Produtos de Inteligência Artificial"),
        (
            "p",
            "PrevisIA (2019): primeiro produto de IA da empresa, usa aprendizado de máquina para "
            "prever demanda, estoque e safras. Desde 2022 faz parte do InsightHub.",
        ),
        (
            "p",
            "AtendIA (2023): assistente de atendimento com IA generativa, treinado com as bases "
            "de conhecimento de cada cliente e com regras de segurança que impedem respostas "
            "fora do contexto autorizado. Ao final de 2023 tinha 61 clientes contratantes.",
        ),
        (
            "p",
            "AgentFlow (2024): plataforma para criar agentes de IA que executam processos de "
            "negócio de ponta a ponta, como reposição de estoque, cobrança, agendamento e "
            "abertura de ordens de serviço, com aprovação humana nos pontos críticos. Em abril "
            "de 2026 foi lançado o AgentFlow 2.0, com agentes que colaboram entre sistemas "
            "diferentes.",
        ),
        (
            "p",
            "CodeAssist (2023, uso interno): assistente de código com IA generativa usado pelas "
            "equipes de engenharia, responsável por um aumento de 27% na produtividade.",
        ),
        ("h2", "6.3 Serviços de tecnologia"),
        (
            "bullets",
            [
                "Desenvolvimento de software sob medida: sistemas web, aplicativos móveis e "
                "integrações.",
                "Consultoria em nuvem e DevOps: migração para a nuvem, automação de "
                "infraestrutura e entrega contínua.",
                "Engenharia de dados e analytics: estruturação de dados e painéis de gestão.",
                "Implantação de IA: diagnóstico, prova de conceito e implantação de agentes de IA.",
                "Suporte e sucesso do cliente: atendimento em português 24 horas por dia, 7 dias "
                "por semana.",
                "Academia SuperTech: cursos de IA e de produtos para clientes e parceiros "
                "(desde 2024).",
            ],
        ),
        ("h2", "6.4 Evolução dos produtos ao longo dos anos"),
        (
            "table",
            ["Produto", "Lançamento", "Situação em 2026"],
            [
                [
                    "SuperGestão Desktop",
                    "2007",
                    "Descontinuado em 2015 (substituído pelo GestPro Cloud)",
                ],
                ["GestPro Web", "2009", "Evoluiu para o GestPro Cloud em 2012"],
                ["GestPro Cloud", "2012", "Ativo, com recursos de IA desde 2022"],
                ["Campo Móvel", "2013", "Incorporado ao GestPro Cloud em 2019"],
                ["ConectaAPI", "2016", "Ativo"],
                ["InsightHub", "2018", "Ativo, com consultas em linguagem natural desde 2023"],
                ["PrevisIA", "2019", "Ativo, integrado ao InsightHub desde 2022"],
                ["AtendIA", "2023", "Ativo"],
                ["CodeAssist", "2023", "Ativo, uso interno"],
                ["AgentFlow", "2024", "Ativo; versão 2.0 lançada em abril de 2026"],
            ],
        ),
        # 7 -------------------------------------------------------------------------------------
        ("h1", "7. Resultados financeiros (2021 a 2025)"),
        (
            "p",
            "Valores em reais (R$). As despesas incluem despesas comerciais, administrativas, de "
            "pesquisa e desenvolvimento e os tributos sobre o lucro. Lucro líquido = receita - "
            "custos operacionais - despesas. Margem de lucro = lucro líquido / receita. A receita "
            f"de 2020, base para o crescimento de 2021, foi de {brl(REVENUE_2020)}.",
        ),
        ("h2", "7.1 Resumo dos últimos 5 anos (valores em R$ milhões)"),
        (
            "table",
            [
                "Ano",
                "Receita (R$ milhões)",
                "Custos operacionais (R$ milhões)",
                "Despesas (R$ milhões)",
                "Lucro líquido (R$ milhões)",
                "Margem de lucro",
                "Investimentos (R$ milhões)",
                "Crescimento da receita",
            ],
            financial_rows(),
        ),
        ("h2", "7.2 Resultados ano a ano"),
        *financial_paragraphs(),
        ("h2", "7.3 Receita por linha de negócio em 2025"),
        (
            "table",
            ["Linha de negócio", "Receita 2025", "Participação"],
            [
                [line, brl(value), pct(value / FINANCIALS[2025][0] * 100)]
                for line, value in REVENUE_BY_LINE_2025
            ],
        ),
        (
            "p",
            "Em 2025, a receita recorrente de assinaturas somou R$ 145,2 milhões (75,5% da "
            "receita) e os serviços profissionais, R$ 47,2 milhões (24,5%).",
        ),
        ("h2", "7.4 Destinação dos investimentos"),
        (
            "p",
            "Os investimentos foram destinados principalmente a pesquisa e desenvolvimento de "
            "produtos de IA, infraestrutura de nuvem, capacitação dos funcionários e abertura de "
            "filiais. Entre 2021 e 2025, a empresa investiu R$ 109,4 milhões no total, dos "
            "quais R$ 25,0 milhões no Programa IA em Tudo (2021 a 2023).",
        ),
        # 8 -------------------------------------------------------------------------------------
        ("h1", "8. Responsabilidade social e sustentabilidade"),
        ("h2", "8.1 Política de sustentabilidade"),
        (
            "p",
            "A Política de Sustentabilidade foi criada em 2015 e revisada em 2022. Ela define "
            "três compromissos: reduzir o impacto ambiental das operações, usar a tecnologia "
            "para inclusão social e manter práticas éticas e transparentes. A meta é atingir a "
            "neutralidade de carbono em 2030. Os resultados são publicados anualmente no "
            "Relatório de Sustentabilidade da empresa.",
        ),
        ("h2", "8.2 Iniciativas ambientais e projetos de redução de impacto"),
        (
            "table",
            ["Iniciativa", "Início", "Resultado"],
            [
                [
                    "Usina solar na sede de Campinas (420 kWp)",
                    "2021",
                    "100% da energia da sede de fonte renovável",
                ],
                [
                    "Migração dos servidores próprios para a nuvem",
                    "2019",
                    "Redução de 35% no consumo de energia com infraestrutura",
                ],
                [
                    "Programa Lixo Eletrônico Zero",
                    "2019",
                    "12 toneladas de equipamentos reciclados até 2025",
                ],
                [
                    "Projeto Raízes Digitais (reflorestamento)",
                    "2020",
                    "18.000 mudas nativas plantadas até 2025",
                ],
                [
                    "Escritórios sem copos descartáveis e com coleta seletiva",
                    "2018",
                    "Redução de 70% dos resíduos não recicláveis",
                ],
                [
                    "Inventário anual de emissões de carbono",
                    "2022",
                    "Redução de 28% das emissões por funcionário entre 2022 e 2025",
                ],
            ],
        ),
        ("h2", "8.3 Programas de responsabilidade social"),
        (
            "p",
            "O Instituto SuperTech, criado em 2016, coordena os programas sociais da empresa. O "
            "principal é o Código do Futuro, que oferece cursos gratuitos de programação e de IA "
            "para jovens de 16 a 24 anos de famílias de baixa renda. Entre 2016 e 2025, o "
            "programa formou 3.200 jovens; 410 foram contratados por empresas de tecnologia, "
            "sendo 96 pela própria SuperTechIABrazil. Desde 2022, o programa também é oferecido "
            "em Recife.",
        ),
        (
            "p",
            "O programa Inclusão Digital Sênior, criado em 2019, ensina pessoas idosas a usar "
            "serviços digitais com segurança e já atendeu 1.850 participantes. Entre 2017 e "
            "2025, a empresa doou 1.450 computadores recondicionados a escolas e entidades.",
        ),
        ("h2", "8.4 Apoio a entidades carentes e doações"),
        (
            "p",
            "A empresa apoia de forma contínua as entidades fictícias Lar Esperança Viva "
            "(acolhimento de crianças), Associação Mãos que Acolhem (cuidado de idosos) e Casa "
            "do Caminho Solidário (alimentação de pessoas em situação de rua), com doações em "
            "dinheiro, alimentos, equipamentos e serviços de tecnologia.",
        ),
        (
            "table",
            ["Ano", "Doações e investimento social"],
            [[str(year), brl(value)] for year, value in DONATIONS.items()]
            + [["Total 2021-2025", brl(sum(DONATIONS.values()))]],
        ),
        ("h2", "8.5 Obras e projetos sociais realizados"),
        (
            "table",
            ["Ano", "Obra ou projeto", "Beneficiados"],
            [
                [
                    "2018",
                    "Construção de laboratório de informática na Escola Comunitária "
                    "Jardim Esperança",
                    "600 alunos por ano",
                ],
                [
                    "2020",
                    "Doação de 300 notebooks para ensino a distância durante a pandemia",
                    "300 estudantes",
                ],
                ["2022", "Reforma completa da sede do Lar Esperança Viva", "45 crianças"],
                [
                    "2024",
                    "Construção do Centro Comunitário Digital Vila Aurora, em Campinas",
                    "1.200 atendimentos por ano",
                ],
                [
                    "2025",
                    "Cozinha industrial da Casa do Caminho Solidário",
                    "500 refeições por dia",
                ],
            ],
        ),
        ("h2", "8.6 Programa de voluntariado dos funcionários"),
        (
            "p",
            "O programa Voluntários Super, criado em 2016, oferece a cada funcionário 8 horas "
            "remuneradas por ano para atividades voluntárias. Em 2025, 312 funcionários "
            "participaram, somando 4.100 horas de voluntariado em mentorias do Código do "
            "Futuro, aulas de inclusão digital, mutirões nas entidades apoiadas e plantio de "
            "mudas do Projeto Raízes Digitais.",
        ),
    ]


# ---------------------------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------------------------


def latin1(text: str) -> str:
    for original, replacement in LATIN1_REPLACEMENTS.items():
        text = text.replace(original, replacement)
    return text


class KnowledgeBasePdf(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", size=8)
        self.cell(0, 6, f"Página {self.page_no()}", align="C")


def render(blocks: list[tuple], output: str) -> None:
    pdf = KnowledgeBasePdf()
    # Every block starts at the left margin of the next line
    line = {"new_x": "LMARGIN", "new_y": "NEXT"}
    pdf.set_margins(18, 18, 18)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    for kind, *args in blocks:
        if kind == "title":
            pdf.set_font("Helvetica", "B", 22)
            pdf.multi_cell(0, 12, latin1(args[0]), align="C", **line)
        elif kind == "subtitle":
            pdf.set_font("Helvetica", "B", 15)
            pdf.multi_cell(0, 9, latin1(args[0]), align="C", **line)
            pdf.ln(4)
        elif kind == "pagebreak":
            pdf.add_page()
        elif kind == "h1":
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 15)
            pdf.multi_cell(0, 9, latin1(args[0]), **line)
            pdf.ln(2)
        elif kind == "h2":
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 12)
            pdf.multi_cell(0, 7, latin1(args[0]), **line)
            pdf.ln(1)
        elif kind == "p":
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(0, 5.5, latin1(args[0]), **line)
            pdf.ln(2)
        elif kind == "bullets":
            pdf.set_font("Helvetica", size=10)
            for item in args[0]:
                pdf.multi_cell(0, 5.5, latin1(f"- {item}"), **line)
            pdf.ln(2)
        elif kind == "table":
            headers, rows = args
            pdf.set_font("Helvetica", size=8.5)
            with pdf.table(
                text_align="LEFT",
                line_height=4.5,
                headings_style=FontFace(emphasis="BOLD"),
            ) as table:
                for row in [headers, *rows]:
                    table_row = table.row()
                    for value in row:
                        table_row.cell(latin1(value))
            pdf.ln(3)
        else:
            raise ValueError(f"unknown block kind: {kind}")
    pdf.output(output)


def main(output: str) -> None:
    check_consistency()
    render(content(), output)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUTPUT)
