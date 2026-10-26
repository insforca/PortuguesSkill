"""Gera as listas de dados da skill a partir de corpora e dicionários.

Este script é para quem mantém a skill; quem só a usa não precisa dele.

Entradas (descarregar antes):
  - Listas de frequência da Linguateca (https://www.linguateca.pt/acesso/ordenador.php):
      formas.cetempublico.txt   (Público, 1991-1998)
      formas.chavept945.txt     (Público, 1994-1995)
      formas.chavebr945.txt     (Folha de S. Paulo, 1994-1995)
  - Dicionários Hunspell (pt_PT pré-AO, pt_PT AO90, pt_BR), ver scripts/instalar_dicionarios.py

Saídas (em dados/):
  - ao90_preao.tsv              forma AO90 -> forma pré-AO90, com frequência no CETEMPúblico
  - candidatos_brasileirismos.tsv  formas muito mais frequentes na Folha do que no Público
                                   (lista bruta, para curadoria manual em brasileirismos.tsv)

Uso:
  python gerar_listas.py <pasta_frequencias> <pasta_dicionarios> <pasta_saida>
"""
import itertools
import math
import os
import re
import sys

from spylls.hunspell import Dictionary

CLUSTER = re.compile(r"[cp](?=[cçt])")
PALAVRA = re.compile(r"^[a-zàáâãçéêíóôõúü]+(?:-[a-zàáâãçéêíóôõúü]+)*$")


def ler_freq(caminho, minimo=1):
    freq = {}
    with open(caminho, encoding="latin-1") as f:
        for linha in f:
            partes = linha.rstrip("\n").split("\t")
            if len(partes) != 2:
                continue
            n, forma = partes
            try:
                n = int(n)
            except ValueError:
                continue
            if n >= minimo:
                freq[forma] = freq.get(forma, 0) + n
    return freq


def candidatos_ao90(palavra):
    """Formas obtidas apagando consoantes mudas (c/p antes de c, ç, t)."""
    posicoes = [m.start() for m in CLUSTER.finditer(palavra)]
    for k in range(1, len(posicoes) + 1):
        for combo in itertools.combinations(posicoes, k):
            yield "".join(ch for i, ch in enumerate(palavra) if i not in combo)
    if "-" in palavra:
        # auto-estrada -> autoestrada, anti-semita -> antissemita
        a, _, b = palavra.partition("-")
        if b[:1] in ("r", "s") and a[-1:] in "aeiou":
            yield a + b[0] + b
        yield a + b


def main(pasta_freq, pasta_dic, saida):
    os.makedirs(saida, exist_ok=True)
    pre = Dictionary.from_files(os.path.join(pasta_dic, "pt_PT-preao"))
    ao = Dictionary.from_files(os.path.join(pasta_dic, "pt_PT"))

    # 1. Mapa AO90 -> pré-AO90, a partir das formas reais do CETEMPúblico
    cetem = ler_freq(os.path.join(pasta_freq, "formas.cetempublico.txt"), minimo=10)
    pares = {}
    for forma, n in cetem.items():
        if not PALAVRA.match(forma):
            continue
        if not (CLUSTER.search(forma) or "-" in forma):
            continue
        if not pre.lookup(forma) or ao.lookup(forma):
            continue
        for cand in candidatos_ao90(forma):
            if cand != forma and ao.lookup(cand) and not pre.lookup(cand):
                if cand not in pares or pares[cand][1] < n:
                    pares[cand] = (forma, n)
    with open(os.path.join(saida, "ao90_preao.tsv"), "w", encoding="utf-8") as f:
        f.write("# forma_ao90\tforma_pre_ao90\tfreq_cetempublico\n")
        for cand, (forma, n) in sorted(pares.items(), key=lambda x: -x[1][1]):
            f.write(f"{cand}\t{forma}\t{n}\n")
    print("ao90_preao.tsv:", len(pares))

    # 2. Candidatos a brasileirismo: CHAVE (Público vs Folha, 1994-1995)
    pt = ler_freq(os.path.join(pasta_freq, "formas.chavept945.txt"))
    br = ler_freq(os.path.join(pasta_freq, "formas.chavebr945.txt"))
    tot_pt, tot_br = sum(pt.values()), sum(br.values())
    linhas = []
    for forma, nb in br.items():
        if nb < 40 or not PALAVRA.match(forma):
            continue
        np_ = pt.get(forma, 0)
        pm_br = nb / tot_br * 1e6
        pm_pt = np_ / tot_pt * 1e6
        razao = (pm_br + 0.5) / (pm_pt + 0.5)
        if razao >= 8:
            linhas.append((forma, nb, np_, round(razao, 1), round(nb * math.log(razao))))
    linhas.sort(key=lambda x: -x[4])
    with open(os.path.join(saida, "candidatos_brasileirismos.tsv"), "w", encoding="utf-8") as f:
        f.write("# forma\tocorr_folha\tocorr_publico\trazao_por_milhao\tpeso\n")
        for l in linhas:
            f.write("\t".join(map(str, l)) + "\n")
    print("candidatos_brasileirismos.tsv:", len(linhas))


if __name__ == "__main__":
    main(*sys.argv[1:4])
