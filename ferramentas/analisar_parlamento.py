"""Analisa o corpus parlamentar (preparado por recolher_parlamento.py) por década e tipo de fala.

Mede: comprimento das frases; «estar + gerúndio» contra «estar a + infinitivo»; ênclise contra
próclise com pronome átono depois do sujeito; formas de tratamento (V. Ex.ª, você, o Sr. Deputado).

Saídas:
  testes/analises/parlamento.md              tabelas por década
  dados/normas_frase.json                    acrescenta as normas «discurso» e «oral» (com --gravar)
  notas no cofre (Medições/Parlamento — …)   com --gravar

Uso: python analisar_parlamento.py [--gravar]
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cofre  # noqa: E402

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CORPORA = os.path.join(REPO, ".cache", "corpora")
SKILL_DADOS = [os.path.join(REPO, "pt-pt", "antesAO90", "dados"),
               os.path.expanduser("~/.claude/skills/portugues-skill/dados")]
PALAVRA = re.compile(r"[A-Za-zÀ-ÿ]+(?:-[A-Za-zÀ-ÿ]+)*")
ESTAR = r"(?:estou|estás|está|estamos|estão|estava|estavam|estávamos|esteve|estiveram|estaria|estará|estarão)"
GERUNDIO = re.compile(r"\b" + ESTAR + r"\s+\w+ndo\b", re.I)
A_INF = re.compile(r"\b" + ESTAR + r"\s+a\s+\w+(?:ar|er|ir|or)\b", re.I)
ENCLISE = re.compile(r"\b\w+(?:ar|er|ir|ou|ei|eu|iu|am|em|a|e)-(?:me|te|se|lhe|lhes|nos|vos|o|a|os|as|lo|la|los|las)\b", re.I)
PROCLISE_SUJ = re.compile(r"\b(?:eu|ele|ela|nós|eles|elas|você|o Governo|a Câmara)\s+(?:me|te|se|lhe|lhes|nos|vos)\s+\w+", re.I)
TRATAMENTO = {"V. Ex.ª": re.compile(r"\bV\.\s?Ex\.?\s?ª|\bVossa Excelência", re.I),
              "você": re.compile(r"\bvocês?\b", re.I),
              "o Sr. Deputado": re.compile(r"\b(?:o|a) Sr\.ª? Deputad[oa]\b")}


def blocos(nome):
    for b in open(os.path.join(CORPORA, nome), encoding="utf-8").read().split("\n\n"):
        if b.startswith("## "):
            cab, _, corpo = b.partition("\n")
            yield int(cab.split()[1]), corpo


def stats(hist):
    tot = sum(hist.values())
    if not tot:
        return None
    m = sum(k * v for k, v in hist.items()) / tot
    d = math.sqrt(sum(v * (k - m) ** 2 for k, v in hist.items()) / tot)
    return {"frases": tot, "media": round(m, 1), "desvio": round(d, 1),
            "pct_35_ou_mais": round(sum(v for k, v in hist.items() if k >= 35) / tot * 100, 1)}


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    res = {}
    for tipo, fich in (("discurso", "parl_discurso.txt"), ("oral", "parl_espontaneo.txt")):
        for ano, corpo in blocos(fich):
            dec = f"{ano // 10 * 10}s"
            for chave in (dec, "total"):
                r = res.setdefault((tipo, chave), {"hist": {}, "palavras": 0, "gerundio": 0, "a_inf": 0,
                                                    "enclise": 0, "proclise": 0,
                                                    **{t: 0 for t in TRATAMENTO}})
                for frase in corpo.split("\n"):
                    n = len(PALAVRA.findall(frase))
                    if n > 2:
                        r["hist"][n] = r["hist"].get(n, 0) + 1
                r["palavras"] += len(PALAVRA.findall(corpo))
                r["gerundio"] += len(GERUNDIO.findall(corpo))
                r["a_inf"] += len(A_INF.findall(corpo))
                r["enclise"] += len(ENCLISE.findall(corpo))
                r["proclise"] += len(PROCLISE_SUJ.findall(corpo))
                for t, p in TRATAMENTO.items():
                    r[t] += len(p.findall(corpo))

    decadas = sorted({k[1] for k in res if k[1] != "total"})
    linhas = ["# Debates parlamentares 1945–2011: análise por década", "",
              "Amostra de 6 sessões por ano (Assembleia Nacional, Constituinte, Assembleia da República, I Série), "
              "texto OCR filtrado por dicionário pré-AO90. «Discurso» = intervenções com 150 ou mais palavras; "
              "«oral» = intervenções com 60 ou menos (réplicas, apartes, presidência).", ""]
    for tipo in ("discurso", "oral"):
        linhas += [f"## {tipo.capitalize()}", "",
                   "| década | palavras | frase média | % frases 35+ | estar+gerúndio | estar a+infinitivo | % gerúndio | ênclise/1000 | V. Ex.ª/1000 | você/1000 |",
                   "|---|---|---|---|---|---|---|---|---|---|"]
        for dec in decadas + ["total"]:
            r = res.get((tipo, dec))
            if not r or not r["palavras"]:
                continue
            s = stats(r["hist"])
            g, a = r["gerundio"], r["a_inf"]
            k = 1000 / r["palavras"]
            linhas.append(f"| {dec} | {r['palavras']:,} | {s['media']} | {s['pct_35_ou_mais']} | {g} | {a} | "
                          f"{(g / (g + a) * 100 if g + a else 0):.0f}% | {r['enclise'] * k:.1f} | "
                          f"{r['V. Ex.ª'] * k:.2f} | {r['você'] * k:.2f} |")
        linhas.append("")
    texto = "\n".join(linhas) + "\n"
    open(os.path.join(REPO, "testes", "analises", "parlamento.md"), "w", encoding="utf-8").write(texto)
    print(texto)

    if "--gravar" in argv:
        for d in SKILL_DADOS:
            p = os.path.join(d, "normas_frase.json")
            if os.path.exists(p):
                n = json.load(open(p, encoding="utf-8"))
                n["discurso"] = stats(res[("discurso", "total")]["hist"])
                n["oral"] = stats(res[("oral", "total")]["hist"])
                n["_fonte_parlamento"] = "Debates parlamentares 1945-2011 (debates.parlamento.pt), amostra de 6 sessões/ano"
                json.dump(n, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        for tipo in ("discurso", "oral"):
            r = res[(tipo, "total")]
            s = stats(r["hist"])
            g, a = r["gerundio"], r["a_inf"]
            t = f"Parlamento — {tipo} 1945-2011"
            cofre.escrever("medicao", t, dict(
                fonte=cofre.ligacao("Debates Parlamentares"), forma=f"fala parlamentar ({tipo})",
                palavras=r["palavras"], media_palavras=s["media"], pct_35_ou_mais=s["pct_35_ou_mais"],
                gerundio=g, estar_a_infinitivo=a, pct_gerundio=round(g / (g + a) * 100, 1) if g + a else None,
                metodo="ferramentas/analisar_parlamento.py", data="2026-10-27"),
                f"# {t}\n\nVer `testes/analises/parlamento.md` (por década), [[Oral formal]], [[Gerúndio]] e [[Tratamento]].\n")
        print("normas e notas gravadas")


if __name__ == "__main__":
    main(sys.argv[1:])
