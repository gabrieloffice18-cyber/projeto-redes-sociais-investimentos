"""
01_tratamento.py - Etapa 1: limpeza, anonimização e preparação da base.
Entrada: dados/Respostas_SIMULADAS_Influencia_redes_sociais_investimentos.xlsx
Saída  : dados/dados_tratados.csv, dados/dicionario_dados.csv, dados/log_tratamento.txt
"""
from pathlib import Path
import pandas as pd
from config import *

RAIZ = Path(__file__).resolve().parent.parent
ARQ = RAIZ / "dados" / "Respostas_SIMULADAS_Influencia_redes_sociais_investimentos.xlsx"
log = []


def registra(msg):
    print(msg)
    log.append(msg)


# 1. Leitura e nomes curtos de coluna (a ordem segue a exportação do Google Forms)
df = pd.read_excel(ARQ, sheet_name="Respostas SIMULADAS")
registra(f"Linhas lidas: {len(df)} | colunas: {df.shape[1]}")
df.columns = ["data_hora", "email", "nome", "genero", "idade", "cidade", "ocupacao", "renda",
              "redes", "tempo_tela", "consumo", "confianca", "produtor", "decisao",
              "influencia", "prejuizo", "lucro", "pressao", "fator_texto", "origem"]

# 2. Duplicidades (mesmo e-mail = mesma pessoa respondendo duas vezes)
n_dup = int(df.duplicated(subset="email").sum())
df = df.drop_duplicates(subset="email")
registra(f"Duplicatas removidas: {n_dup}")

# 3. Valores ausentes: 'produtor' está 100% vazio e será descartado
nulos = df.isna().sum()
registra("Colunas com nulos: " + (", ".join(f"{c}={n}" for c, n in nulos[nulos > 0].items()) or "nenhuma"))

# 4. Anonimização (LGPD): cria id e remove nome, e-mail e produtor
df = df.sort_values("data_hora").reset_index(drop=True)
df.insert(0, "id", [f"P{i + 1:03d}" for i in range(len(df))])
df = df.drop(columns=["email", "nome", "produtor"])
registra("Anonimização: removidos nome e e-mail; coluna 'produtor' descartada (100% vazia)")

# 5. Validação de categorias: qualquer valor fora da lista esperada interrompe o script
for col, ordem in [("genero", GENERO), ("idade", IDADE), ("renda", RENDA), ("ocupacao", OCUP),
                   ("cidade", CIDADE), ("tempo_tela", TEMPO), ("confianca", CONFIA), ("decisao", DECISAO)]:
    fora = set(df[col]) - set(ordem)
    assert not fora, f"Categorias inesperadas em {col}: {fora}"
    df[col] = pd.Categorical(df[col], categories=ordem, ordered=True)
assert df["consumo"].between(1, 5).all(), "consumo fora da escala 1-5"

# 6. Códigos numéricos para as variáveis ordinais
df["tempo_cod"] = df["tempo_tela"].cat.codes + 1      # 1 a 5
df["confianca_cod"] = df["confianca"].cat.codes + 1   # 1 a 4
df["decisao_cod"] = df["decisao"].cat.codes           # 0 a 3
registra("Ordinais codificadas: tempo_cod (1-5), confianca_cod (1-4), decisao_cod (0-3)")

# 7. Binárias Sim/Não -> 1/0
for col in ["influencia", "prejuizo", "lucro", "pressao"]:
    df[col] = df[col].map({"Sim": 1, "Não": 0}).astype(int)

# 8. Multirresposta: 'redes' vira uma coluna 0/1 por rede
for rede in REDES:
    df[f"rede_{rede}"] = df["redes"].str.split(", ").apply(lambda lista: int(rede in lista))
df["n_redes"] = df[[f"rede_{r}" for r in REDES]].sum(axis=1)
df = df.drop(columns="redes")

# 9. Texto livre -> 6 categorias (regras em config.categoriza_fator)
df["fator_categoria"] = df["fator_texto"].apply(categoriza_fator)
registra(f"Fator mais importante: {df['fator_texto'].nunique()} respostas distintas -> {df['fator_categoria'].nunique()} categorias")

# 10. Índice de exposição e checagem de consistência lógica
df["indice_exposicao"] = (df["tempo_cod"] + df["consumo"]) / 2
df["flag_inconsistente"] = ((df["influencia"] == 1) & (df["decisao_cod"] == 0)).astype(int)
registra(f"Respostas inconsistentes (influenciado, mas nunca decidiu): {int(df['flag_inconsistente'].sum())} (mantidas e sinalizadas)")
registra(f"Prejuízo/lucro sem decisão por recomendação: {int(((df.prejuizo + df.lucro > 0) & (df.decisao_cod == 0)).sum())}")

# 11. Saída
df.to_csv(RAIZ / "dados" / "dados_tratados.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(DICIONARIO, columns=["variavel", "tipo", "descricao"]).to_csv(
    RAIZ / "dados" / "dicionario_dados.csv", index=False, encoding="utf-8-sig")
(RAIZ / "dados" / "log_tratamento.txt").write_text("\n".join(log), encoding="utf-8")
registra(f"Base final: {df.shape[0]} linhas x {df.shape[1]} colunas")
