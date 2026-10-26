"""Converte amostras do CETEMPúblico e do CETENFolha em texto corrido, um artigo por bloco.

Entradas (descarregar o início dos ficheiros, não é preciso o corpus inteiro):
  curl -r 0-80000000 -o publico_parcial.txt https://www.linguateca.pt/CETEMPublico/download/CETEMPublico1.7.txt
  curl -r 0-40000000 -o folha_parcial.gz    https://www.linguateca.pt/CETENFolha/download/CETENFolha-1.0.gz

Saídas: pt.txt e br.txt, com os artigos separados por uma linha em branco e uma frase por linha.

Uso: python preparar_corpora.py <pasta>
"""
import gzip
import os
import re
import sys

PONT_ANTES = re.compile(r"\s+([,.;:!?»)])")
PONT_DEPOIS = re.compile(r"([«(])\s+")


def juntar(tokens):
    s = " ".join(tokens)
    s = PONT_ANTES.sub(r"\1", s)
    s = PONT_DEPOIS.sub(r"\1", s)
    return s.replace(" --", " —").replace("-- ", "— ")


def publico(caminho):
    artigos, frases, tokens, dentro = [], [], [], False
    with open(caminho, encoding="latin-1", errors="replace") as f:
        for linha in f:
            l = linha.strip()
            if l.startswith("<ext"):
                frases = []
            elif l == "</ext>":
                if frases:
                    artigos.append(frases)
            elif l == "<s>":
                tokens, dentro = [], True
            elif l == "</s>":
                if tokens:
                    frases.append(juntar(tokens))
                dentro = False
            elif dentro and l and not l.startswith("<"):
                tokens.append(l)
    return artigos


def folha(caminho):
    artigos, frases = [], []
    with gzip.open(caminho, "rt", encoding="latin-1", errors="replace") as f:
        try:
            for linha in f:
                l = linha.strip()
                if l.startswith("<ext"):
                    frases = []
                elif l == "</ext>":
                    if frases:
                        artigos.append(frases)
                elif l.startswith("<s>") and "<t>" not in l and "<a>" not in l:
                    frases.append(juntar(l[3:].replace("</s>", "").split()))
        except (EOFError, OSError):
            pass  # ficheiro truncado de propósito
    return artigos


def gravar(artigos, caminho):
    with open(caminho, "w", encoding="utf-8") as f:
        for a in artigos:
            f.write("\n".join(a) + "\n\n")
    palavras = sum(len(fr.split()) for a in artigos for fr in a)
    print(f"{os.path.basename(caminho)}: {len(artigos)} artigos, {palavras} palavras")


if __name__ == "__main__":
    pasta = sys.argv[1]
    gravar(publico(os.path.join(pasta, "publico_parcial.txt")), os.path.join(pasta, "pt.txt"))
    gravar(folha(os.path.join(pasta, "folha_parcial.gz")), os.path.join(pasta, "br.txt"))
