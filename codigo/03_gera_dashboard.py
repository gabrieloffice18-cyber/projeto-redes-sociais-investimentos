"""
03_gera_dashboard.py - Etapa 3: injeta os dados tratados e os resultados estatísticos no
template HTML e gera o dashboard executivo (arquivo único).
Saída: dashboard.html (Chart.js por CDN) e dashboard_offline.html (Chart.js embutido,
gerado só se codigo/vendor/chart.umd.min.js existir).
"""
import json
from pathlib import Path
import pandas as pd
from config import *

RAIZ = Path(__file__).resolve().parent.parent
df = pd.read_csv(RAIZ / "dados" / "dados_tratados.csv")
est = json.loads((RAIZ / "dados" / "estatisticas.json").read_text(encoding="utf-8"))
FATOR_IDX = {c: i for i, c in enumerate(FATOR_CATS)}

# Rótulos de cada dimensão (a ordem define o índice numérico usado nas linhas)
L = dict(g=GENERO, i=IDADE, r=CURTO["r"], o=CURTO["o"], c=CURTO["c"], t=TEMPO,
         k=["1", "2", "3", "4", "5"], f=CURTO["f"], d=CURTO["d"], n=["Não", "Sim"],
         p=["Não", "Sim"], l=["Não", "Sim"], s=["Não", "Sim"], x=FATOR_CATS, m=REDES)
T = dict(g="Gênero", i="Idade", r="Renda", o="Ocupação", c="Cidade", t="Tempo nas redes",
         k="Consumo de conteúdo financeiro", f="Confiança", d="Decisão por recomendação",
         n="Influenciado", p="Prejuízo", l="Lucro", s="Pressão", x="Critério principal",
         m="Rede social")


def idx(col, ordem):
    return df[col].map({v: i for i, v in enumerate(ordem)})


bits = sum(df[f"rede_{r}"] * (1 << b) for b, r in enumerate(REDES))
linhas = pd.DataFrame(dict(
    g=idx("genero", GENERO), i=idx("idade", IDADE), r=idx("renda", RENDA), o=idx("ocupacao", OCUP),
    c=idx("cidade", CIDADE), t=idx("tempo_tela", TEMPO), k=df.consumo - 1, f=idx("confianca", CONFIA),
    d=idx("decisao", DECISAO), n=df.influencia, p=df.prejuizo, l=df.lucro, s=df.pressao,
    x=df.fator_categoria.map(FATOR_IDX), m=bits)).astype(int)

dados = dict(L=L, T=T, R=linhas.values.tolist(), S=est["testes"], dic=[list(d) for d in DICIONARIO])
payload = json.dumps(dados, ensure_ascii=False, separators=(",", ":"))
html = (RAIZ / "codigo" / "dashboard_template.html").read_text(encoding="utf-8").replace("__DATA__", payload)
(RAIZ / "dashboard.html").write_text(html, encoding="utf-8")

vendor = RAIZ / "codigo" / "vendor" / "chart.umd.min.js"
if vendor.exists():
    tag = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>'
    (RAIZ / "dashboard_offline.html").write_text(
        html.replace(tag, "<script>" + vendor.read_text(encoding="utf-8") + "</script>"), encoding="utf-8")
print("Dashboard gerado:", len(html) // 1024, "KB")
