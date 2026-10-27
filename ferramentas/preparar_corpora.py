"""Converte o CETEMPúblico e o CETENFolha em texto corrido, um extracto por bloco.

Tudo é lido e escrito em fluxo: o CETEMPúblico completo (1,26 GB) não cabe em memória.

Entradas:
  CETEMPublico1.7.txt  https://www.linguateca.pt/CETEMPublico/download/CETEMPublico1.7.txt
                       (ou só o início: curl -r 0-80000000 -o publico_parcial.txt …)
  folha_parcial.gz     curl -r 0-40000000 -o folha_parcial.gz https://www.linguateca.pt/CETENFolha/download/CETENFolha-1.0.gz

Saídas (uma frase por linha, extractos separados por uma linha em branco):
  pt.txt ou pt_completo.txt, br.txt
  normas_frase.json    comprimento das frases por secção do Público (média, desvio, % com 35+ palavras)

Uso:
  python preparar_corpora.py <pasta>               amostras (publico_parcial.txt, folha_parcial.gz)
  python preparar_corpora.py <pasta> --completo    CETEMPublico1.7.txt inteiro -> pt_completo.txt + normas
"""
import gzip
import json
import math
import os
import re
import sys

PONT_ANTES = re.compile(r"\s+([,.;:!?»)])")
PONT_DEPOIS = re.compile(r"([«(])\s+")
PALAVRA = re.compile(r"[A-Za-zÀ-ÿ]+(?:-[A-Za-zÀ-ÿ]+)*")
SECCAO = re.compile(r"\bsec=([a-z-]+)")

# Secções do Público agrupadas por registo
REGISTOS = {"opi": "ensaio", "clt": "cronica", "clt-soc": "cronica",
            "pol": "noticia", "soc": "noticia", "eco": "noticia", "des": "noticia"}


def juntar(tokens):
    s = " ".join(tokens)
    s = PONT_ANTES.sub(r"\1", s)
    s = PONT_DEPOIS.sub(r"\1", s)
    return s.replace(" --", " —").replace("-- ", "— ")


def publico(caminho, saida, normas=None):
    """Lê o formato do CETEMPúblico (um token por linha) e escreve em fluxo."""
    hist = {}  # registo -> {comprimento: contagem}
    extractos = palavras = 0
    frases, tokens, dentro, sec = [], [], False, "nd"
    with open(caminho, encoding="latin-1", errors="replace") as f, \
            open(saida, "w", encoding="utf-8", newline="\n") as out:
        for linha in f:
            l = linha.strip()
            if l.startswith("<ext"):
                frases = []
                m = SECCAO.search(l)
                sec = m.group(1) if m else "nd"
            elif l == "</ext>":
                if frases:
                    out.write("\n".join(frases) + "\n\n")
                    extractos += 1
            elif l == "<s>":
                tokens, dentro = [], True
            elif l == "</s>":
                if tokens:
                    frase = juntar(tokens)
                    frases.append(frase)
                    n = len(PALAVRA.findall(frase))
                    palavras += n
                    if normas is not None and n > 2:
                        for reg in ("geral", REGISTOS.get(sec)):
                            if reg:
                                h = hist.setdefault(reg, {})
                                h[n] = h.get(n, 0) + 1
                dentro = False
            elif dentro and l and not l.startswith("<"):
                tokens.append(l)
    print(f"{os.path.basename(saida)}: {extractos} extractos, {palavras} palavras")
    if normas is not None:
        res = {}
        for reg, h in hist.items():
            tot = sum(h.values())
            media = sum(k * v for k, v in h.items()) / tot
            desvio = math.sqrt(sum(v * (k - media) ** 2 for k, v in h.items()) / tot)
            longas = sum(v for k, v in h.items() if k >= 35) / tot * 100
            res[reg] = {"frases": tot, "media": round(media, 1), "desvio": round(desvio, 1),
                        "pct_35_ou_mais": round(longas, 1)}
        res["_fonte"] = "CETEMPúblico 1.7 (Linguateca), Público 1991-1998, frases com mais de 2 palavras"
        res["_seccoes"] = REGISTOS
        with open(normas, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        print(json.dumps(res, ensure_ascii=False, indent=1))


def folha(caminho, saida):
    extractos = palavras = 0
    frases = []
    with gzip.open(caminho, "rt", encoding="latin-1", errors="replace") as f, \
            open(saida, "w", encoding="utf-8", newline="\n") as out:
        try:
            for linha in f:
                l = linha.strip()
                if l.startswith("<ext"):
                    frases = []
                elif l == "</ext>":
                    if frases:
                        out.write("\n".join(frases) + "\n\n")
                        extractos += 1
                        palavras += sum(len(x.split()) for x in frases)
                elif l.startswith("<s>") and "<t>" not in l and "<a>" not in l:
                    frases.append(juntar(l[3:].replace("</s>", "").split()))
        except (EOFError, OSError):
            pass  # ficheiro truncado de propósito
    print(f"{os.path.basename(saida)}: {extractos} extractos, {palavras} palavras")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    pasta = sys.argv[1]
    if "--completo" in sys.argv:
        publico(os.path.join(pasta, "CETEMPublico1.7.txt"), os.path.join(pasta, "pt_completo.txt"),
                os.path.join(pasta, "normas_frase.json"))
    else:
        publico(os.path.join(pasta, "publico_parcial.txt"), os.path.join(pasta, "pt.txt"))
        folha(os.path.join(pasta, "folha_parcial.gz"), os.path.join(pasta, "br.txt"))
