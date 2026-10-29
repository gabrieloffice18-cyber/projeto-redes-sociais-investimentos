# Redes sociais e decisões de investimento

Projeto de **Ciência de Dados e Programação** (Strong Business School, Prof. Dr. Bruno Henrique Oliveira Mulina).

Pergunta central: em que medida o consumo de conteúdo financeiro nas redes sociais está associado a decisões de investimento, confiança em influenciadores e pressão para investir?

> **Aviso:** a base atual é **100% simulada** (gerada por computador) e serve para validar o pipeline. Os resultados não representam pessoas reais. Será substituída pela coleta real.

## Estrutura

```
projeto/
├── dashboard.html            # painel executivo interativo (usa Chart.js por CDN)
├── dashboard_offline.html    # mesma coisa, com Chart.js embutido (funciona sem internet)
├── codigo/
│   ├── config.py             # categorias, ordens e dicionário de dados
│   ├── 01_tratamento.py      # limpeza, anonimização e codificação
│   ├── 02_analise.py         # estatística descritiva e testes de hipótese
│   ├── 03_gera_dashboard.py  # injeta dados e resultados no HTML
│   └── dashboard_template.html
├── dados/
│   ├── Respostas_SIMULADAS_*.xlsx   # base original (simulada)
│   ├── dados_tratados.csv
│   ├── dicionario_dados.csv
│   ├── estatisticas.json
│   ├── tabelas_descritivas.csv
│   └── log_tratamento.txt
└── requirements.txt
```

## Como rodar

```bash
pip install -r requirements.txt
cd codigo
python 01_tratamento.py
python 02_analise.py
python 03_gera_dashboard.py
```

Abra `dashboard.html` no navegador. Para gerar também o `dashboard_offline.html`, coloque o arquivo `chart.umd.min.js` (Chart.js 4.4.1) em `codigo/vendor/` antes do passo 3.

## Método

- **Tratamento:** anonimização (remoção de nome e e-mail), validação de categorias, codificação de ordinais, dummies para multirresposta, agrupamento do texto livre em 6 categorias e sinalização de respostas inconsistentes.
- **Estatística:** testes não paramétricos (Spearman, Mann-Whitney, Kruskal-Wallis, qui-quadrado) com tamanho de efeito e correção de Bonferroni.
- **Dashboard:** HTML único e interativo, com filtros, filtro cruzado por clique, correlações recalculadas e leitura automática do recorte.

## Trocar pela base real

1. Exporte as respostas do Google Forms para `.xlsx` com as mesmas colunas.
2. Guarde o arquivo original em `dados/reais/` (essa pasta **não vai para o GitHub**).
3. Ajuste o nome do arquivo em `01_tratamento.py` e rode os três scripts.
4. Remova o selo "Dados simulados" do `dashboard_template.html`.

## Limitações

Amostra pequena, maioria com 18 a 29 anos, respostas autodeclaradas e correlação não implica causa.
