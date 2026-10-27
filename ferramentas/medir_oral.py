"""Mede marcadores do registo oral e informal em corpora orais e escritos, PT e BR.

Corpora (listas de frequência da Linguateca, em .cache/corpora/freq/):
  oral PT      museudapessoapt (histórias de vida, entrevistas)
  regional PT  cordial-sin (falares regionais portugueses)
  oral BR      museudapessoabr + coralbrasil
  imprensa PT  cetempublico
  imprensa BR  chavebr945 (Folha de S. Paulo, 1994-1995)

Saídas:
  testes/analises/oral_marcadores.md     tabela por milhão de palavras
  testes/analises/oral_candidatos.md     formas muito mais frequentes na oral PT do que na BR e vice-versa
                                         (mesmo corpus, mesma recolha: Museu da Pessoa), para curadoria
  notas «Oral — <forma>» no cofre        com --cofre

Uso: python medir_oral.py [--cofre]
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cofre  # noqa: E402

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FREQ = os.path.join(REPO, ".cache", "corpora", "freq")
ANALISES = os.path.join(REPO, "testes", "analises")
CORPORA = {"oral PT": ["museudapessoapt"], "regional PT": ["cordial-sin"],
           "oral BR": ["museudapessoabr", "coralbrasil"], "imprensa PT": ["cetempublico"],
           "imprensa BR": ["chavebr945"]}
MARCADORES = ["pá", "pronto", "prontos", "olha", "olhe", "pois", "então", "tou", "tás", "tá", "tô", "cê", "né",
              "bué", "fixe", "giro", "calhar", "tipo", "gente", "você", "vocês", "tu", "estou", "tava", "pra",
              "aí", "daí", "legal", "cara", "rapariga", "miúdo", "moço", "menino", "garoto", "ué", "nossa",
              "caramba", "porra", "pá", "lá", "cá", "ora", "aliás", "portanto"]
PALAVRA = re.compile(r"^[a-zà-ÿ]+(?:-[a-zà-ÿ]+)*$")


def ler(nomes):
    freq, tot = {}, 0
    for n in nomes:
        with open(os.path.join(FREQ, f"formas.{n}.txt"), encoding="latin-1") as f:
            for l in f:
                p = [x.strip() for x in l.rstrip("\n").split("\t")]
                if len(p) == 2 and p[0].isdigit():
                    c = int(p[0])
                    tot += c
                    w = p[1].lower()
                    freq[w] = freq.get(w, 0) + c
    return freq, tot


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    dados = {k: ler(v) for k, v in CORPORA.items()}
    pm = lambda k, w: dados[k][0].get(w, 0) / dados[k][1] * 1e6
    col = list(CORPORA)
    linhas = ["# Marcadores orais por milhão de palavras", "",
              "Fontes: listas de frequência da Linguateca. Tamanhos: " +
              ", ".join(f"{k} {dados[k][1]:,} palavras" for k in col) + ".",
              "Só palavras isoladas: «se calhar» mede-se por «calhar», «a gente» por «gente».", "",
              "| forma | " + " | ".join(col) + " | oral BR ÷ oral PT |", "|---|" + "---|" * (len(col) + 1)]
    medidas = []
    for w in dict.fromkeys(MARCADORES):
        v = [pm(k, w) for k in col]
        razao = (v[2] + 1) / (v[0] + 1)
        medidas.append((w, v, razao))
        linhas.append(f"| {w} | " + " | ".join(f"{x:.0f}" for x in v) + f" | {razao:.1f} |")
    os.makedirs(ANALISES, exist_ok=True)
    open(os.path.join(ANALISES, "oral_marcadores.md"), "w", encoding="utf-8").write("\n".join(linhas) + "\n")
    print("\n".join(linhas))

    # candidatos: Museu da Pessoa PT vs BR (mesma recolha)
    pt, tpt = dados["oral PT"]
    br, tbr = ler(["museudapessoabr"])
    cand = []
    for w in set(pt) | set(br):
        if not PALAVRA.match(w):
            continue
        a, b = pt.get(w, 0), br.get(w, 0)
        if a + b < 15:
            continue
        ppt, pbr = a / tpt * 1e6, b / tbr * 1e6
        r = (pbr + 5) / (ppt + 5)
        if r >= 8 or r <= 1 / 8:
            cand.append((w, a, b, round(ppt), round(pbr), round(r, 2)))
    cand.sort(key=lambda x: -abs(x[4] - x[3]))
    out = ["# Candidatos do registo oral (Museu da Pessoa PT vs BR)", "",
           "Formas pelo menos 8 vezes mais frequentes num dos lados. Para curadoria: há nomes próprios e temas.", "",
           "| forma | ocorr. PT | ocorr. BR | PT/milhão | BR/milhão | BR÷PT |", "|---|---|---|---|---|---|"]
    out += [f"| {c[0]} | {c[1]} | {c[2]} | {c[3]} | {c[4]} | {c[5]} |" for c in cand[:150]]
    open(os.path.join(ANALISES, "oral_candidatos.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"\n{len(cand)} candidatos em testes/analises/oral_candidatos.md")

    if "--cofre" in argv:
        for w, v, razao in medidas:
            t = f"Oral — {w}"
            cofre.escrever("medicao", t, dict(
                fonte=cofre.ligacao("Linguateca — corpora orais"), forma=w,
                por_milhao_pt=round(v[0], 1), por_milhao_br=round(v[2], 1), razao_br_pt=round(razao, 2),
                por_milhao_regional_pt=round(v[1], 1), por_milhao_imprensa_pt=round(v[3], 1),
                por_milhao_imprensa_br=round(v[4], 1),
                metodo="listas de frequência: oral PT = Museu da Pessoa PT; oral BR = Museu da Pessoa BR + C-Oral-Brasil",
                data="2026-10-27"),
                f"# {t}\n\nRegisto oral. Ver [[Fala informal]] e `testes/analises/oral_marcadores.md`.\n")
        print(f"{len(medidas)} medições escritas no cofre")


if __name__ == "__main__":
    main(sys.argv[1:])
