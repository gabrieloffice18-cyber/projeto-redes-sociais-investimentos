"""
02_analise.py - Etapa 2: estatística descritiva e inferencial.
Entrada: dados/dados_tratados.csv
Saída  : dados/tabelas_descritivas.csv, dados/estatisticas.json (consumido pelo dashboard)
Escolha dos testes: variáveis ordinais/categóricas e amostra pequena (n=100), portanto
testes não paramétricos (Spearman, Mann-Whitney, Kruskal-Wallis, qui-quadrado).
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parent.parent
df = pd.read_csv(RAIZ / "dados" / "dados_tratados.csv")
df["decidiu"] = (df["decisao_cod"] > 0).astype(int)
n = len(df)
testes = []


def virg(x):  # formato brasileiro
    return str(x).replace(".", ",")


def forca(v, limites=(0.1, 0.3, 0.5), nomes=("desprezível", "fraco", "moderado", "forte")):
    return nomes[sum(abs(v) >= l for l in limites)]


def add(titulo, estat, p, efeito):
    testes.append(dict(t=titulo, e=virg(estat), p=float(p), ef=efeito))


def spearman(a, b, titulo):
    r, p = stats.spearmanr(df[a], df[b])
    z, se = np.arctanh(r), 1.06 / np.sqrt(n - 3)  # IC por transformação de Fisher (Bonett-Wright)
    lo, hi = np.tanh([z - 1.96 * se, z + 1.96 * se])
    add(titulo, f"ρ de Spearman = {r:.2f} (IC95% {lo:.2f} a {hi:.2f})", p, f"correlação {forca(r)}")


def qui(a, b, titulo, base=None):
    d = df if base is None else base
    tab = pd.crosstab(d[a], d[b])
    chi2, p, _, esp = stats.chi2_contingency(tab)
    v = np.sqrt(chi2 / (tab.values.sum() * (min(tab.shape) - 1)))
    aviso = " (atenção: frequência esperada < 5 em alguma célula)" if esp.min() < 5 else ""
    add(titulo, f"χ² = {chi2:.2f}; V de Cramér = {v:.2f}", p,
        f"associação {forca(v, (0.1, 0.3, 0.5), ('desprezível', 'pequena', 'média', 'grande'))}{aviso}")


def mann(col, grupo, titulo):
    a, b = df.loc[df[grupo] == 1, col], df.loc[df[grupo] == 0, col]
    u, p = stats.mannwhitneyu(a, b)
    r = 2 * u / (len(a) * len(b)) - 1  # correlação bisserial por postos
    add(titulo, f"U = {u:.0f}; r = {r:.2f}; mediana {a.median():.0f} vs {b.median():.0f}", p, f"efeito {forca(r)}")


def kruskal(col, grupo, titulo):
    g = [x[col].values for _, x in df.groupby(grupo)]
    h, p = stats.kruskal(*g)
    eps = (h - len(g) + 1) / (n - len(g))  # epsilon quadrado
    add(titulo, f"H = {h:.2f}; ε² = {eps:.3f}", p,
        f"efeito {forca(eps, (0.01, 0.08, 0.26), ('desprezível', 'pequeno', 'moderado', 'forte'))}")


# --- Testes (hipóteses H1 a H5 do relatório) ---
spearman("consumo", "decisao_cod", "H1: Quem consome mais conteúdo financeiro decide mais por recomendação?")
spearman("consumo", "confianca_cod", "H2: Quem consome mais confia mais em influenciadores?")
spearman("consumo", "tempo_cod", "Consumo de conteúdo financeiro × tempo diário nas redes")
spearman("consumo", "n_redes", "Consumo de conteúdo financeiro × número de redes usadas")
spearman("confianca_cod", "decisao_cod", "Confiança em influenciadores × decisões tomadas por recomendação")
qui("pressao", "influencia", "H3: Sentir pressão está associado a dizer que é influenciado?")
qui("pressao", "decidiu", "Sentir pressão × já ter decidido por recomendação")
mann("consumo", "pressao", "H4: Quem sente pressão consome mais conteúdo financeiro?")
qui("genero", "pressao", "Gênero × sentir pressão (apenas Feminino e Masculino)",
    base=df[df["genero"].isin(["Feminino", "Masculino"])])
kruskal("consumo", "renda", "H5: O consumo de conteúdo difere entre faixas de renda?")
kruskal("consumo", "idade", "Consumo de conteúdo difere entre faixas de idade?")
kruskal("consumo", "ocupacao", "Consumo de conteúdo difere entre ocupações?")

# Correção de Bonferroni para múltiplos testes
m = len(testes)
for t in testes:
    t["pa"] = min(1.0, t["p"] * m)
    if t["pa"] < 0.05:
        t["r"] = f"Significativo a 5% mesmo após a correção de Bonferroni para {m} testes."
    elif t["p"] < 0.05:
        t["r"] = f"Significativo a 5% isoladamente, mas não resiste à correção para {m} testes: trate como indício."
    else:
        t["r"] = "Sem evidência de associação nesta amostra. Isso não prova que a relação não exista."

# --- Descritivas ---
cats = ["genero", "idade", "cidade", "ocupacao", "renda", "tempo_tela", "consumo", "confianca",
        "decisao", "influencia", "prejuizo", "lucro", "pressao", "fator_categoria"]
tabs = []
for c in cats:
    f = df[c].value_counts().rename("n").to_frame()
    f["pct"] = (100 * f["n"] / n).round(1)
    f.insert(0, "variavel", c)
    tabs.append(f.reset_index(names="categoria"))
pd.concat(tabs).to_csv(RAIZ / "dados" / "tabelas_descritivas.csv", index=False, encoding="utf-8-sig")

dec = df[df["decidiu"] == 1]
resumo = dict(n=n, consumo_media=round(df.consumo.mean(), 2), consumo_dp=round(df.consumo.std(), 2),
              pct_decidiu=round(100 * df.decidiu.mean(), 1), pct_pressao=round(100 * df.pressao.mean(), 1),
              pct_prejuizo_decididos=round(100 * dec.prejuizo.mean(), 1),
              pct_lucro_decididos=round(100 * dec.lucro.mean(), 1), n_testes=m)
(RAIZ / "dados" / "estatisticas.json").write_text(
    json.dumps(dict(resumo=resumo, testes=testes), ensure_ascii=False, indent=1), encoding="utf-8")
for t in testes:
    print(f"{t['t'][:62]:62} p={t['p']:.4f} p_adj={t['pa']:.4f}")
print(resumo)
