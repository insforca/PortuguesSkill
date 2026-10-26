"""Instala os dicionários Hunspell usados por verificar.py (só é preciso uma vez).

Descarrega para dados/dicionarios/:
  - pt_PT-preao  (Projecto Natura, Universidade do Minho — grafia anterior ao AO90)
  - pt_PT        (Projecto Natura — AO90, para reconhecer formas do Acordo)
  - pt_BR        (VERO / LibreOffice — para reconhecer formas brasileiras)

Licenças: os dicionários Natura são GPL/LGPL/MPL; o pt_BR é LGPL/MPL. Não são
redistribuídos com a skill: este script descarrega-os das fontes oficiais.

Requer também a biblioteca spylls:  python -m pip install spylls
"""
import io
import os
import sys
import tarfile
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
DESTINO = os.path.join(AQUI, "..", "dados", "dicionarios")
NATURA = "https://natura.di.uminho.pt/download/sources/Dictionaries/hunspell/LATEST/"
LIBRE = "https://raw.githubusercontent.com/LibreOffice/dictionaries/master/pt_BR/"


def baixar(url):
    print("a descarregar", url)
    req = urllib.request.Request(url, headers={"User-Agent": "portugues-skill"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.read()


def extrair_natura(nome_tar, prefixo):
    with tarfile.open(fileobj=io.BytesIO(baixar(NATURA + nome_tar)), mode="r:gz") as t:
        for m in t.getmembers():
            base = os.path.basename(m.name)
            if base in (prefixo + ".dic", prefixo + ".aff"):
                with open(os.path.join(DESTINO, base), "wb") as f:
                    f.write(t.extractfile(m).read())


def main():
    os.makedirs(DESTINO, exist_ok=True)
    extrair_natura("hunspell-pt_PT-preao-latest.tar.gz", "pt_PT-preao")
    extrair_natura("hunspell-pt_PT-latest.tar.gz", "pt_PT")
    for ext in (".dic", ".aff"):
        with open(os.path.join(DESTINO, "pt_BR" + ext), "wb") as f:
            f.write(baixar(LIBRE + "pt_BR" + ext))
    try:
        import spylls  # noqa: F401
    except ImportError:
        print("\nFalta a biblioteca spylls: python -m pip install spylls")
        return 1
    print("\nDicionários instalados em", os.path.abspath(DESTINO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
