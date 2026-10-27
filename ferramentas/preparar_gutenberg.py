"""Prepara um corpus literário PT/BR (prosa, 1840-1920) a partir do Project Gutenberg.

Serve para o perfil estilométrico literário (scripts/estilometria.py --perfil literario) e
como referência para descobrir tiques em ficção (ferramentas/descobrir_tiques.py).

Passos:
  1. Lê o catálogo de livros em português (https://www.gutenberg.org/browse/languages/pt),
     já convertido para JSON: [[autor, id, título], ...]
  2. Escolhe livros de prosa de autores portugueses e brasileiros da mesma época,
     no máximo MAX_POR_AUTOR por autor.
  3. Descarrega o texto, retira o cabeçalho e a licença do Gutenberg, e normaliza a
     ortografia anterior a 1911 nas palavras gramaticais (elle -> ele, n'um -> num),
     para que a estilometria compare estilo e não grafia.

Saídas: lit_pt.txt e lit_br.txt (um parágrafo por linha, livros separados por linha em branco)
        e livros.tsv (o que entrou em cada lado).

Uso: python preparar_gutenberg.py <catalogo.json> <pasta_saida>
"""
import json
import os
import re
import sys
import time
import urllib.request

MAX_POR_AUTOR = 4
# Retirados para os dois lados terem o mesmo tipo de prosa (ficção, crónica, memórias):
# poesia e teatro, panfletos económicos, manifestos e obras de história.
EXCLUIR_IDS = {71330, 17591, 24411, 24701, 24853, 28962, 24412, 32872, 29996, 63534, 29394, 34387, 71871}

# Autores de prosa (ficção, crónica, ensaio, memórias). Poetas e cronistas medievais ficam de fora.
PT = ["Castelo Branco, Camilo", "Queirós, Eça de", "Ortigão, Ramalho", "Herculano, Alexandre",
      "Almeida Garrett", "Almeida, Fialho de", "Brandão, Raul", "Coelho, Trindade",
      "Pimentel, Alberto", "Chagas, Manuel Pinheiro", "Oliveira Martins", "Carvalho, Maria Amalia Vaz de",
      "Moraes, Wenceslau de", "Osório, Ana de Castro", "Quental, Antero de", "Lima, Jaime de Magalhães",
      "Queiroz, Teixeira de", "Bastos, Teixeira", "Dinis, Júlio", "Diniz, Júlio", "Botelho, Abel"]
BR = ["Machado de Assis", "Alencar, José Martiniano de", "Almeida, Júlia Lopes de", "Azevedo, Aluísio",
      "Caminha, Adolfo", "Coelho Netto", "Guimarães, Bernardo", "Nabuco, Joaquim", "Pompéia, Raul",
      "Taunay, Alfredo"]
EXCLUIR_TITULOS = re.compile(r"soneto|poesia|poema|versos|cancioneiro|lusíadas|rimas|teatro|comedia|drama|"
                             r"auto |farça|farsa|baladas", re.IGNORECASE)

ANTIGAS = {
    "elle": "ele", "ella": "ela", "elles": "eles", "ellas": "elas", "aquelle": "aquele", "aquella": "aquela",
    "aquelles": "aqueles", "aquellas": "aquelas", "aquillo": "aquilo", "alli": "ali", "emfim": "enfim",
    "comtudo": "contudo", "tambem": "também", "teem": "têm", "sêr": "ser", "vêr": "ver", "nella": "nela",
    "nelle": "nele", "della": "dela", "delle": "dele", "dellas": "delas", "delles": "deles",
}
APOSTROFO = {
    "d'": "d", "n'": "n",
}


def normalizar(t):
    t = t.replace("--", "—")
    # contracções com apóstrofo: d'um -> dum, n'esta -> nesta, d'elle -> dele
    t = re.sub(r"\b([dDnN])['’](?=[a-zà-ÿ])", r"\1", t)
    def troca(m):
        w = m.group(0)
        low = w.lower()
        if low in ANTIGAS:
            n = ANTIGAS[low]
            return n.capitalize() if w[0].isupper() else n
        return w
    t = re.sub(r"[A-Za-zÀ-ÿ]+", troca, t)
    t = re.sub(r"\b([dDnN])(elle|ella|elles|ellas|aquelle|aquella|aquillo)\b",
               lambda m: m.group(1) + ANTIGAS[m.group(2)], t)
    return t


def limpar(bruto):
    ini = re.search(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", bruto)
    fim = re.search(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG", bruto)
    corpo = bruto[ini.end() if ini else 0: fim.start() if fim else len(bruto)]
    paragrafos = []
    for p in re.split(r"\n\s*\n", corpo.replace("\r", "")):
        p = " ".join(p.split())
        letras = re.sub(r"[^A-Za-zÀ-ÿ]", "", p)
        if len(p.split()) < 8 or (letras and letras.isupper()):
            continue  # títulos, notas curtas, índices
        if re.search(r"gutenberg|transcri|produced by|digitaliz", p, re.IGNORECASE):
            continue
        paragrafos.append(normalizar(p))
    return paragrafos


def descarregar(i):
    url = f"https://www.gutenberg.org/cache/epub/{i}/pg{i}.txt"
    req = urllib.request.Request(url, headers={"User-Agent": "portugues-skill (investigação)"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8", errors="replace")


def escolher(livros, autores):
    escolhidos, por_autor = [], {}
    for autor, i, titulo in livros:
        chave = next((a for a in autores if a.lower() in autor.lower()), None)
        if not chave or EXCLUIR_TITULOS.search(titulo) or i in EXCLUIR_IDS:
            continue
        if por_autor.get(chave, 0) >= MAX_POR_AUTOR:
            continue
        por_autor[chave] = por_autor.get(chave, 0) + 1
        escolhidos.append((chave, i, titulo))
    return escolhidos


def main(catalogo, saida):
    os.makedirs(saida, exist_ok=True)
    livros = json.load(open(catalogo, encoding="utf-8"))
    registo = open(os.path.join(saida, "livros.tsv"), "w", encoding="utf-8")
    for lado, autores in (("pt", PT), ("br", BR)):
        palavras = 0
        with open(os.path.join(saida, f"lit_{lado}.txt"), "w", encoding="utf-8") as f:
            for autor, i, titulo in escolher(livros, autores):
                try:
                    ps = limpar(descarregar(i))
                except Exception as e:  # noqa: BLE001
                    print(f"  falhou {i}: {e}")
                    continue
                n = sum(len(p.split()) for p in ps)
                palavras += n
                f.write("\n".join(ps) + "\n\n")
                registo.write(f"{lado}\t{autor}\t{i}\t{titulo}\t{n}\n")
                print(f"{lado} {i} {autor}: {titulo[:40]} ({n} palavras)", flush=True)
                time.sleep(1)  # cortesia para com o servidor do Gutenberg
        print(f"== {lado}: {palavras} palavras")
    registo.close()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1], sys.argv[2])
