"""config.py - categorias, ordens e dicionário de dados compartilhados pelos scripts."""

# Ordem das categorias (ordinais seguem a ordem lógica)
GENERO = ["Feminino", "Masculino", "Prefiro não dizer"]
IDADE = ["18-20", "21-23", "24-26", "27-29", "30+"]
RENDA = ["Até R$ 1.500", "R$ 1.501–3.000", "R$ 3.001–5.000", "R$ 5.001–10.000", "Acima de R$ 10.000"]
OCUP = ["Estudante", "Estudante e empregado", "Empregado", "Autônomo", "Desempregado"]
CIDADE = ["Cidade de São Paulo", "Região Metropolitana de São Paulo",
          "Outra cidade no estado de São Paulo", "Não moro no estado de São Paulo"]
TEMPO = ["0 - 2 Horas", "2 - 4 Horas", "4 - 6 Horas", "6 - 8 Horas", "+ 8 Horas"]
CONFIA = ["Não considero confiável", "Considero pouco confiável",
          "Depende do influenciador/produtor de conteúdo", "Considero muito confiável"]
DECISAO = ["Nunca tomei decisão por recomendação", "Sim, mas não faria novamente",
           "Sim, poucas vezes", "Sim, muitas vezes"]
REDES = ["Instagram", "Youtube", "Linkedin", "Tiktok", "X (Twitter)", "Threads", "Facebook"]
FATOR_CATS = ["Segurança e baixo risco", "Retorno e rentabilidade", "Risco x retorno e objetivos",
              "Conhecimento e pesquisa", "Liquidez", "Ainda não investe"]

# Rótulos curtos usados nos gráficos do dashboard
CURTO = {
    "r": ["Até 1,5 mil", "1,5–3 mil", "3–5 mil", "5–10 mil", "Acima de 10 mil"],
    "c": ["Capital SP", "Grande SP", "Interior SP", "Fora de SP"],
    "o": ["Estudante", "Estuda e trabalha", "Empregado", "Autônomo", "Desempregado"],
    "f": ["Não confia", "Confia pouco", "Depende", "Confia muito"],
    "d": ["Nunca decidiu", "Decidiu, não repetiria", "Decidiu poucas vezes", "Decidiu muitas vezes"],
}


def categoriza_fator(texto: str) -> str:
    """Agrupa as 29 respostas livres em 6 categorias. As regras são avaliadas em ordem de
    prioridade (frases mistas, como 'Liquidez e segurança', ficam na primeira regra que casar)."""
    t = texto.lower()
    if "não invisto" in t:
        return FATOR_CATS[5]
    if any(p in t for p in ("fundamentos", "cenário", "pesquisa", "certeza", "conhecimento")):
        return FATOR_CATS[3]
    if ("risco" in t and any(p in t for p in ("retorno", "diversifica", "perfil"))) or "objetivos" in t:
        return FATOR_CATS[2]
    if any(p in t for p in ("seguran", "risco baixo", "estabil", "confiabil", "perda", "garantido")):
        return FATOR_CATS[0]
    if "liquidez" in t:
        return FATOR_CATS[4]
    if any(p in t for p in ("retorno", "rentabil", "ganho")):
        return FATOR_CATS[1]
    raise ValueError(f"Fator sem categoria: {texto!r}")


DICIONARIO = [
    ("id", "texto", "Identificador anônimo (P001...) criado na limpeza; substitui nome e e-mail"),
    ("data_hora", "data/hora", "Carimbo de resposta do formulário"),
    ("genero", "nominal", "Gênero autodeclarado"),
    ("idade", "ordinal", "Faixa etária (18-20, 21-23, 24-26, 27-29, 30+)"),
    ("cidade", "nominal", "Localização agrupada em 4 categorias"),
    ("ocupacao", "nominal", "Ocupação principal"),
    ("renda", "ordinal", "Faixa de renda mensal (5 faixas)"),
    ("tempo_tela", "ordinal", "Tempo diário em redes sociais (5 faixas); tempo_cod = 1 a 5"),
    ("consumo", "ordinal 1-5", "Frequência de consumo de conteúdo sobre dinheiro e investimentos"),
    ("confianca", "ordinal", "Confiança em influenciadores para decisões financeiras; confianca_cod = 1 a 4"),
    ("decisao", "ordinal", "Já decidiu investir por recomendação nas redes; decisao_cod = 0 a 3"),
    ("influencia", "binária 0/1", "Redes sociais influenciam suas decisões (1 = sim)"),
    ("prejuizo", "binária 0/1", "Já teve prejuízo ligado a conteúdo de redes (1 = sim)"),
    ("lucro", "binária 0/1", "Já teve lucro ligado a conteúdo de redes (1 = sim)"),
    ("pressao", "binária 0/1", "Sentiu pressão para investir ao ver ganhos de outros (1 = sim)"),
    ("fator_categoria", "nominal", "Fator mais importante na decisão, agrupado em 6 categorias (original em fator_texto)"),
    ("rede_*", "binária 0/1", "Uma coluna por rede social usada (multirresposta em dummies); n_redes = soma"),
    ("indice_exposicao", "numérico 1-5", "Média de tempo_cod e consumo (resume a exposição a conteúdo financeiro)"),
    ("flag_inconsistente", "binária 0/1", "1 = diz ser influenciado pelas redes, mas nunca decidiu por recomendação"),
    ("origem", "texto", "SIMULADO nesta versão; trocar por REAL quando a coleta for feita"),
]
