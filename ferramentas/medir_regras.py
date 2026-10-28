"""Mede as regras do cofre em corpora reais e em texto gerado, e classifica a evidência.

Corpora (todos pré-AO90 do lado português):
  Público      .cache/corpora/pt_completo.txt   (CETEMPúblico completo, 1991-1998)
  Folha        .cache/corpora/br.txt            (CETENFolha, amostra)
  Parlamento   .cache/corpora/parl_discurso.txt + parl_espontaneo.txt (1945-2011)
  IA           testes/resultados/sem-skill + dificeis-sem-skill (Claude sem a skill)

Para cada regra (por omissão, só as presumidas) conta as ocorrências do padrão, com as mesmas
opções de maiúsculas que o verificador usa, e calcula a frequência por milhão de palavras.

Leitura:
  brasileirismo, grafia, sintaxe  medida se Folha ÷ Público ≥ 3; contestada se < 1,5
  marca de IA                     medida se IA ÷ (Público e Parlamento) ≥ 3, ou se o padrão é raro
                                  na prosa portuguesa (< 2 por milhão) e o limite é baixo;
                                  contestada se o uso normal num texto de 1000 palavras
                                  ultrapassa o limite (a regra estaria a punir português normal)

Uso:
  python medir_regras.py [--todas] [--gravar]
  --gravar escreve as notas de medição no cofre, liga-as às regras e actualiza o estado.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cofre  # noqa: E402

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
C = os.path.join(REPO, ".cache", "corpora")
FONTES = {"Público": [os.path.join(C, "pt_completo.txt")],
          "Folha": [os.path.join(C, "br.txt")],
          "Parlamento": [os.path.join(C, "parl_discurso.txt"), os.path.join(C, "parl_espontaneo.txt")],
          "IA": [os.path.join(REPO, "testes", "resultados", d, f)
                 for d in ("sem-skill", "dificeis-sem-skill", "base-extra")
                 if os.path.isdir(os.path.join(REPO, "testes", "resultados", d))
                 for f in sorted(os.listdir(os.path.join(REPO, "testes", "resultados", d)))
                 if f.endswith(".md") and f != "avaliacao.md"]}
PALAVRA = re.compile(r"[A-Za-zÀ-ÿ]+")
# O Público completo (168 M palavras) é amostrado: 1 bloco de 20 000 frases em cada 5 (~34 M palavras)
AMOSTRA = {"Público": 5}
# regras que o verificador aplica com distinção de maiúsculas
SENSIVEIS = ("OR — meses com minúscula", "SX — próclise em início de frase", "SX — possessivo sem artigo")


def padrao_de(r):
    p = r.get("padrao") or ""
    if not p:
        return None
    if r.get("categoria") == "brasileirismo":
        p = r"(?<![\w-])(?:" + p + r")(?![\w-])"
    # atenção: «(?-im:…)» desligaria também o modo multilinha; o certo é «(?m-i:…)»
    return f"(?m-i:{p})" if r["_titulo"] in SENSIVEIS else f"(?im:{p})"


def contar(regras):
    pads = {r["_titulo"]: re.compile(padrao_de(r)) for r in regras if padrao_de(r)}
    res = {t: {} for t in pads}
    totais = {}
    for fonte, ficheiros in FONTES.items():
        tot, cont, n_bloco = 0, {t: 0 for t in pads}, 0
        passo = AMOSTRA.get(fonte, 1)
        for f in ficheiros:
            with open(f, encoding="utf-8", errors="replace") as fh:
                bloco = []
                for linha in fh:
                    if linha.startswith("## "):
                        continue
                    bloco.append(linha)
                    if len(bloco) >= 20000:
                        n_bloco += 1
                        if n_bloco % passo == 0:  # amostra sistemática: 1 bloco em cada «passo»
                            texto = "".join(bloco)
                            tot += len(PALAVRA.findall(texto))
                            for t, p in pads.items():
                                cont[t] += len(p.findall(texto))
                        bloco = []
                if bloco:
                    texto = "".join(bloco)
                    tot += len(PALAVRA.findall(texto))
                    for t, p in pads.items():
                        cont[t] += len(p.findall(texto))
        totais[fonte] = tot
        for t in pads:
            res[t][fonte] = cont[t]
        print(f"{fonte}: {tot:,} palavras", flush=True)
    return res, totais


def classificar(r, c, tot):
    pm = {f: c[f] / tot[f] * 1e6 for f in c}
    cat = r.get("categoria")
    if cat in ("brasileirismo", "grafia", "sintaxe"):
        # com poucos casos a razão não diz nada (ex.: léxico informático nos jornais de 1991-1998)
        if c["Público"] + c["Folha"] < 20:
            return "presumida", (f"só {c['Público'] + c['Folha']} casos no Público e na Folha: "
                                 "faltam dados (consultar o NOW no Corpus do Português)")
        razao = (pm["Folha"] + 0.5) / (pm["Público"] + 0.5)
        if razao >= 3:
            return "medida", f"Folha ÷ Público = {razao:.1f}"
        if razao < 1.5:
            return "contestada", f"Folha ÷ Público = {razao:.1f}: não distingue as variedades"
        return "presumida", f"Folha ÷ Público = {razao:.1f}: sinal fraco"
    # marcas de IA
    ref = (c["Público"] + c["Parlamento"]) / (tot["Público"] + tot["Parlamento"]) * 1e6
    sobre = (pm["IA"] + 1) / (ref + 1)
    limite = r.get("limite") or 0
    normal_1000 = ref * 1000 / 1e6
    if normal_1000 > limite + 0.5:
        return "contestada", (f"uso normal em prosa portuguesa: {ref:.0f} por milhão "
                              f"(≈ {normal_1000:.1f} por 1000 palavras), acima do limite {limite}")
    if c["IA"] >= 2 and sobre >= 3:
        return "medida", f"o Claude sem a skill usa-o {sobre:.0f} vezes mais do que a prosa portuguesa"
    if ref < 2:
        return "medida", f"raro na prosa portuguesa ({ref:.2f} por milhão): um uso já destoa"
    return "presumida", f"prosa portuguesa {ref:.1f} por milhão; IA {pm['IA']:.0f} por milhão ({c['IA']} ocorr.)"


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    regras = [r for r in cofre.todas("regra") if "--todas" in argv or r.get("estado") == "presumida"]
    res, tot = contar(regras)
    linhas = ["# Medição das regras presumidas", "",
              "Frequência por milhão de palavras. " + ", ".join(f"{f}: {n:,} palavras" for f, n in tot.items()) + ".", "",
              "| regra | Público | Folha | Parlamento | IA | estado | razão |", "|---|---|---|---|---|---|---|"]
    novos = {}
    for r in regras:
        t = r["_titulo"]
        if t not in res:
            continue
        c = res[t]
        estado, porque = classificar(r, c, tot)
        novos[t] = (estado, porque, c)
        pm = lambda f: c[f] / tot[f] * 1e6
        linhas.append(f"| {t} | {pm('Público'):.1f} | {pm('Folha'):.1f} | {pm('Parlamento'):.1f} | {pm('IA'):.0f} | "
                      f"{estado} | {porque} |")
    rel = "\n".join(linhas) + "\n"
    open(os.path.join(REPO, "testes", "analises", "regras_medidas.md"), "w", encoding="utf-8").write(rel)
    print(rel)
    if "--gravar" in argv:
        for r in regras:
            t = r["_titulo"]
            if t not in novos:
                continue
            estado, porque, c = novos[t]
            titulo_m = f"Corpora — {t}"
            cofre.escrever("medicao", titulo_m, dict(
                fonte=[cofre.ligacao("CETEMPúblico"), cofre.ligacao("Debates Parlamentares"), cofre.ligacao("Testes da skill")],
                forma=r.get("padrao"),
                **{f"ocorr_{f.lower()}": c[f] for f in c},
                **{f"por_milhao_{f.lower()}": round(c[f] / tot[f] * 1e6, 2) for f in c},
                por_milhao_pt=round(c["Público"] / tot["Público"] * 1e6, 2),
                por_milhao_br=round(c["Folha"] / tot["Folha"] * 1e6, 2),
                razao_br_pt=round((c["Folha"] / tot["Folha"] * 1e6 + 0.5) / (c["Público"] / tot["Público"] * 1e6 + 0.5), 2),
                leitura=porque, metodo="ferramentas/medir_regras.py", data="2026-10-27"),
                f"# {titulo_m}\n\n{porque}.\n\nRegra: [[{cofre.nome_ficheiro(t)}]].\n")
            p = os.path.join(cofre.RAIZ, "Regras", cofre.nome_ficheiro(t) + ".md")
            s = open(p, encoding="utf-8").read()
            ev = cofre.ler(p).get("evidencia") or []
            lig = cofre.ligacao(titulo_m)
            if lig not in ev:
                ev.append(lig)
            s = re.sub(r"^evidencia: .*$", lambda m: "evidencia: " + cofre._valor_yaml(ev), s, count=1, flags=re.M)
            if not re.search(r"^evidencia:", s, re.M):
                s = s.replace("\n---\n", f"\nevidencia: {cofre._valor_yaml(ev)}\n---\n", 1)
            s = re.sub(r"^estado: .*$", f"estado: '{estado}'", s, count=1, flags=re.M)
            open(p, "w", encoding="utf-8", newline="\n").write(s)
        print("cofre actualizado")


if __name__ == "__main__":
    main(sys.argv[1:])
