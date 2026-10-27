"""Descobre tiques de escrita: palavras e sequências que os textos gerados usam muito mais
(ou muito menos) do que a imprensa portuguesa real.

Compara os textos gerados com o texto corrido do CETEMPúblico (ver preparar_corpora.py)
usando a log-verosimilhança de Dunning (G²). Para não contar como tique o que é só o
assunto de um pedido, cada candidato tem de aparecer em vários textos diferentes.

O resultado é uma lista de CANDIDATOS para curadoria humana: o corpus de referência é
jornalístico, por isso marcas de género (cartas, diálogos, ficção) também aparecem.

Uso:
  python descobrir_tiques.py <referencia_pt.txt> <pasta_textos> [<pasta_textos> ...]
         [--min-textos 3] [--top 60] [--saida relatorio.md] [--dobrar]

Referências: pt.txt (CETEMPúblico, imprensa) para textos não ficcionais; lit_pt.txt (prosa
literária portuguesa 1840-1920, Project Gutenberg) para ficção, com --dobrar, porque essa
referência tem a grafia anterior a 1911 nas palavras comuns. Os nomes dos ficheiros
«17_v1.5.md» contam como o mesmo pedido «17».
"""
import math
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

PALAVRA = re.compile(r"[a-zà-öø-ÿ]+(?:-[a-zà-öø-ÿ]+)*")
SEPARA = re.compile(r"[.!?;:,()«»\"“”—–\n]+")


DOBRAR = False  # activado com --dobrar (referências com ortografia anterior a 1911)


def dobrar(w):
    """Chave neutra à grafia: sem acentos, sem consoantes dobradas, ph->f, th->t, y->i.
    Faz coincidir «ninguém»/«ninguem», «anos»/«annos», «à»/«á», «farmácia»/«pharmacia»."""
    w = unicodedata.normalize("NFD", w)
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    w = w.replace("ph", "f").replace("th", "t").replace("y", "i")
    return re.sub(r"([bcdfglmnpt])\1", r"\1", w)


def segmentos(texto):
    """Troços de texto entre sinais de pontuação, em minúsculas e já tokenizados."""
    for s in SEPARA.split(texto.lower()):
        toks = PALAVRA.findall(s)
        if toks:
            yield [dobrar(t) for t in toks] if DOBRAR else toks


def ngramas(toks, n):
    return (" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1))


def g2(a, b, c, d):
    """a: ocorrências no alvo, b: na referência, c/d: totais."""
    e1 = c * (a + b) / (c + d)
    e2 = d * (a + b) / (c + d)
    t = 0.0
    if a:
        t += a * math.log(a / e1)
    if b:
        t += b * math.log(b / e2)
    return 2 * t


def ler_textos(pastas):
    textos = {}
    for p in pastas:
        for f in sorted(os.listdir(p)):
            if f.endswith(".md") and f != "avaliacao.md":
                textos[f"{os.path.basename(p.rstrip('/\\'))}/{f}"] = open(os.path.join(p, f), encoding="utf-8").read()
    return textos


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    global DOBRAR
    if "--dobrar" in argv:
        DOBRAR = True
        argv = [a for a in argv if a != "--dobrar"]
    opc = {"--min-textos": 3, "--top": 60, "--saida": None}
    pos = []
    i = 0
    while i < len(argv):
        if argv[i] in opc:
            opc[argv[i]] = argv[i + 1]
            i += 2
        else:
            pos.append(argv[i])
            i += 1
    ref, pastas = pos[0], pos[1:]
    min_textos, top = int(opc["--min-textos"]), int(opc["--top"])

    textos = ler_textos(pastas)
    # pedido de origem (os dois primeiros caracteres do ficheiro): um tique tem de atravessar pedidos
    alvo = {n: Counter() for n in (1, 2, 3)}
    pedidos = {n: defaultdict(set) for n in (1, 2, 3)}
    tot_alvo = 0
    for nome, t in textos.items():
        pid = os.path.splitext(os.path.basename(nome))[0].split("_")[0]
        for toks in segmentos(t):
            tot_alvo += len(toks)
            for n in (1, 2, 3):
                for g in ngramas(toks, n):
                    alvo[n][g] += 1
                    pedidos[n][g].add(pid)

    candidatos = {n: {g for g, c in alvo[n].items() if len(pedidos[n][g]) >= min_textos} for n in (1, 2, 3)}
    refc = {n: Counter() for n in (1, 2, 3)}
    uni_ref = Counter()
    tot_ref = 0
    with open(ref, encoding="utf-8") as f:
        for linha in f:
            for toks in segmentos(linha):
                tot_ref += len(toks)
                uni_ref.update(toks)
                for n in (2, 3):
                    if len(toks) >= n:
                        for g in ngramas(toks, n):
                            if g in candidatos[n]:
                                refc[n][g] += 1
    refc[1] = uni_ref

    linhas = [f"# Tiques candidatos", "",
              f"{len(textos)} textos ({tot_alvo} palavras) comparados com {tot_ref:,} palavras de {os.path.basename(ref)}"
              f"{' (comparação neutra à grafia)' if DOBRAR else ''}. "
              f"Só entram sequências presentes em pelo menos {min_textos} pedidos diferentes.", ""]
    for n in (1, 2, 3):
        res = []
        for g in candidatos[n]:
            a, b = alvo[n][g], refc[n][g]
            pm_a, pm_b = a / tot_alvo * 1e6, b / tot_ref * 1e6
            if pm_a <= pm_b * 3:
                continue
            res.append((g, a, len(pedidos[n][g]), round(pm_a), round(pm_b, 1),
                        round((pm_a + 1) / (pm_b + 1), 1), round(g2(a, b, tot_alvo, tot_ref), 1)))
        res.sort(key=lambda x: -x[6])
        nome = {1: "Palavras", 2: "Sequências de 2 palavras", 3: "Sequências de 3 palavras"}[n]
        linhas += [f"## {nome} usadas a mais", "",
                   "| sequência | ocorrências | pedidos | por milhão (gerado) | por milhão (referência) | razão | G² |",
                   "|---|---|---|---|---|---|---|"]
        linhas += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} |" for r in res[:top]]
        linhas.append("")

    # sub-uso: palavras gramaticais frequentes no Público que os textos gerados quase não usam
    sub = []
    for g, b in uni_ref.most_common(400):
        pm_b = b / tot_ref * 1e6
        a = alvo[1].get(g, 0)
        pm_a = a / tot_alvo * 1e6
        esperado = pm_b * tot_alvo / 1e6
        if esperado >= 4 and pm_a < pm_b / 3:
            sub.append((g, a, round(esperado, 1), round(pm_a), round(pm_b)))
    linhas += ["## Palavras frequentes na referência que os textos gerados evitam", "",
               "| palavra | ocorrências | esperado | por milhão (gerado) | por milhão (referência) |",
               "|---|---|---|---|---|"]
    linhas += [f"| {s[0]} | {s[1]} | {s[2]} | {s[3]} | {s[4]} |" for s in sub[:top]]
    rel = "\n".join(linhas) + "\n"
    if opc["--saida"]:
        open(opc["--saida"], "w", encoding="utf-8").write(rel)
    print(rel)


if __name__ == "__main__":
    main(sys.argv[1:])
