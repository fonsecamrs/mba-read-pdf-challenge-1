"""Generates document.pdf: a fictitious company report (Portuguese) used to test the ingestion.

Usage: python scripts/generate_document_pdf.py [output.pdf]   (default: document.pdf)
Requires the development dependencies (requirements-dev.txt).
"""

import sys

from fpdf import FPDF

DEFAULT_OUTPUT = "document.pdf"

SECTIONS = [
    (
        "Relatório Institucional 2023 - SuperTechIABrazil",
        [
            "Documento fictício criado exclusivamente para testes do desafio de ingestão e busca "
            "semântica. Nenhuma informação deste relatório se refere a empresas ou pessoas reais.",
            "A SuperTechIABrazil é uma empresa brasileira de tecnologia especializada em soluções "
            "de inteligência artificial para o varejo e para a indústria. A empresa foi fundada em "
            "2015, na cidade de Campinas, no estado de São Paulo, pelos engenheiros Ana Ribeiro e "
            "Carlos Mendes, que se conheceram durante o mestrado em ciência da computação.",
            "A missão da empresa é tornar a inteligência artificial acessível para pequenas e "
            "médias empresas, oferecendo produtos simples de implantar e com custo previsível. A "
            "visão para os próximos anos é ser referência nacional em automação inteligente de "
            "processos comerciais.",
        ],
    ),
    (
        "Histórico",
        [
            "Em 2016, a empresa lançou seu primeiro produto, o PrevIA, uma ferramenta de previsão "
            "de demanda para supermercados. Em 2018, recebeu um aporte de 5 milhões de reais de um "
            "fundo de investimento de Belo Horizonte, o que permitiu ampliar a equipe técnica.",
            "Em 2020, a SuperTechIABrazil abriu uma filial em Recife, voltada ao atendimento de "
            "clientes da região Nordeste. Em 2022, a empresa passou a oferecer seus produtos em "
            "modelo de assinatura mensal, abandonando a venda de licenças perpétuas.",
        ],
    ),
    (
        "Produtos",
        [
            "PrevIA: previsão de demanda baseada em histórico de vendas, sazonalidade e feriados "
            "regionais. É o produto mais antigo e o de maior receita da empresa.",
            "AtendIA: assistente virtual para atendimento ao cliente em canais de mensagem, com "
            "integração a sistemas de gestão de pedidos.",
            "InspecIA: sistema de visão computacional para inspeção de qualidade em linhas de "
            "produção industrial, lançado em 2023 em parceria com uma fabricante de embalagens.",
        ],
    ),
    (
        "Resultados financeiros de 2023",
        [
            "O faturamento foi de 10 milhões de reais no ano de 2023, um crescimento de 25% em "
            "relação ao ano anterior. O lucro líquido do período foi de 1,2 milhão de reais.",
            "O produto PrevIA respondeu por 60% do faturamento, o AtendIA por 30% e o InspecIA por "
            "10%. A empresa investiu 2 milhões de reais em pesquisa e desenvolvimento ao longo do "
            "ano, principalmente em modelos de linguagem para o AtendIA.",
        ],
    ),
    (
        "Pessoas e estrutura",
        [
            "Ao final de 2023, a SuperTechIABrazil contava com 85 funcionários, sendo 50 na sede "
            "em Campinas e 35 na filial de Recife. Cerca de 60% da equipe atua nas áreas de "
            "engenharia e ciência de dados.",
            "A empresa adota o modelo de trabalho híbrido, com presença no escritório três dias "
            "por semana. O programa de capacitação interna oferece 40 horas anuais de treinamento "
            "por funcionário.",
        ],
    ),
    (
        "Perspectivas",
        [
            "Para os próximos anos, a empresa planeja expandir o InspecIA para o setor de "
            "alimentos e abrir um escritório comercial em Porto Alegre. A diretoria também avalia "
            "a internacionalização para países da América do Sul.",
        ],
    ),
]


def main(output: str) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    for index, (title, paragraphs) in enumerate(SECTIONS):
        if index in (0, 2, 4):
            pdf.add_page()
        pdf.set_font("Helvetica", "B", 15 if index == 0 else 13)
        pdf.multi_cell(0, 8, title)
        pdf.ln(2)
        pdf.set_font("Helvetica", size=11)
        for paragraph in paragraphs:
            pdf.multi_cell(0, 6, paragraph)
            pdf.ln(3)
    pdf.output(output)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUTPUT)
