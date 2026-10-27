"""Recolhe e prepara uma amostra dos debates parlamentares portugueses anteriores ao AO90.

Fonte: https://debates.parlamento.pt/ (texto integral obtido por OCR). Respeita o robots.txt:
2 segundos entre pedidos (Crawl-delay), só páginas de catálogo e a vista «?sft=true», nunca
/pesquisa. Os textos ficam em .cache/parlamento/ e a recolha retoma onde parou.

Séries usadas:
  r2/dan  Assembleia Nacional (1935-1974)
  r3/dac  Assembleia Constituinte (1975-1976)
  r3/dar  Assembleia da República, I Série (1976-), só até 2011 (antes da aplicação do AO90)

Uso:
  python recolher_parlamento.py recolher [--por-ano 6] [--de 1945] [--ate 2011]
  python recolher_parlamento.py preparar        limpa, filtra o OCR e separa os registos

Saídas de «preparar» (em .cache/corpora/):
  parl_discurso.txt     intervenções longas (discurso preparado), uma por bloco
  parl_espontaneo.txt   intervenções curtas, apartes e réplicas (fala espontânea)
  parl_resumo.json      contagens por década e tipo
Cada bloco começa por uma linha «## AAAA série» com o ano e a série.
"""
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE = "https://debates.parlamento.pt"
REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CACHE = os.path.join(REPO, ".cache", "parlamento")
SAIDA = os.path.join(REPO, ".cache", "corpora")
DIC = os.path.expanduser("~/.claude/skills/portugues-skill/dados/dicionarios/pt_PT-preao")
SERIES = [("r2/dan", 1935, 1974), ("r3/dac", 1975, 1976), ("r3/dar/01", 1976, 2011)]
PAUSA = 2.0
_ultimo = [0.0]


def pedir(caminho):
    for tentativa in range(5):
        espera = PAUSA - (time.time() - _ultimo[0])
        if espera > 0:
            time.sleep(espera)
        _ultimo[0] = time.time()
        try:
            req = urllib.request.Request(BASE + caminho, headers={
                "User-Agent": "portugues-skill/1.8 (investigação linguística; github.com/insforca/PortuguesSkill)"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            print(f"   falha ({e}); nova tentativa dentro de {10 * (tentativa + 1)} s", flush=True)
            time.sleep(10 * (tentativa + 1))
    raise RuntimeError(f"desisti de {caminho}")


def sublinks(caminho):
    s = pedir(caminho)
    return sorted({l for l in re.findall(r'href="(/catalogo/[^"#?]+)"', s) if l.startswith(caminho + "/")})


def sessoes(serie, de, ate):
    """Percorre o catálogo até às sessões datadas (…/NNN/AAAA-MM-DD)."""
    res, pilha, vistos = [], [f"/catalogo/{serie}"], set()
    while pilha:
        c = pilha.pop()
        if c in vistos:
            continue
        vistos.add(c)
        for l in sublinks(c):
            m = re.search(r"/(\d{3}[A-Z0-9]*)/(\d{4})-\d{2}-\d{2}$", l)
            if m:
                if "S" not in m.group(1) and de <= int(m.group(2)) <= ate:
                    res.append(l)
            elif not re.search(r"/\d{4}-\d{2}-\d{2}/", l):  # não descer às páginas de uma sessão
                pilha.append(l)
    return sorted(res)


def texto_integral(caminho):
    s = pedir(caminho + "?sft=true")
    s = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", s)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", s))
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    i = t.find("SESSÃO")
    return t[i if i > 0 else 0:]


def recolher(por_ano=6, de=1945, ate=2011):
    os.makedirs(CACHE, exist_ok=True)
    for serie, s_de, s_ate in SERIES:
        a, b = max(de, s_de), min(ate, s_ate)
        if a > b:
            continue
        indice = os.path.join(CACHE, serie.replace("/", "_") + "_indice.txt")
        if os.path.exists(indice):
            todas = open(indice, encoding="utf-8").read().split()
        else:
            print(f"a listar {serie}…", flush=True)
            todas = sessoes(serie, s_de, s_ate)
            open(indice, "w", encoding="utf-8").write("\n".join(todas))
        por = {}
        for s in todas:
            ano = int(s[-10:-6])
            if a <= ano <= b:
                por.setdefault(ano, []).append(s)
        for ano, lista in sorted(por.items()):
            passo = max(1, len(lista) // por_ano)
            for s in lista[::passo][:por_ano]:
                destino = os.path.join(CACHE, serie.replace("/", "_") + "_" + s.split("/")[-1] + "_"
                                       + s.split("/")[-2] + ".txt")
                if os.path.exists(destino):
                    continue
                print(f"{serie} {s.split('/')[-1]}", flush=True)
                open(destino, "w", encoding="utf-8").write(texto_integral(s))


# --- preparação -------------------------------------------------------------------------
ORADOR = re.compile(r"^(?:O|A) (?:Sr\.ª?|Sra\.|Orador|Oradora|Presidente)[^:\n]{0,80}:\s*[—–-]?\s*", re.M)
RUIDO = re.compile(r"^(Página \d+|DIÁRIO D[AE] .*|\d+ DIÁRIO .*|.*SÉRIE.*NÚMERO.*|Aplausos.*|Risos\.?|"
                   r"Vozes.*|Protestos.*|Pausa\.?)$", re.M)


def intervencoes(texto):
    texto = RUIDO.sub("", texto)
    partes = ORADOR.split(texto)
    for p in partes[1:]:
        p = re.sub(r"\(O orador não reviu\.?\)|\(A oradora não reviu\.?\)", "", p)
        p = re.sub(r"-\n(\w)", r"\1", p)          # palavras cortadas no fim da linha
        p = " ".join(p.split())
        if len(p.split()) >= 5:
            yield p


def preparar():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from spylls.hunspell import Dictionary
    dic = Dictionary.from_files(DIC)
    cache = {}

    def conhecida(w):
        if w not in cache:
            cache[w] = bool(dic.lookup(w))
        return cache[w]

    os.makedirs(SAIDA, exist_ok=True)
    resumo, rejeitadas = {}, 0
    with open(os.path.join(SAIDA, "parl_discurso.txt"), "w", encoding="utf-8", newline="\n") as fd, \
            open(os.path.join(SAIDA, "parl_espontaneo.txt"), "w", encoding="utf-8", newline="\n") as fe:
        for f in sorted(os.listdir(CACHE)):
            if not f.endswith(".txt") or "_indice" in f:
                continue
            m = re.search(r"(\d{4})-\d{2}-\d{2}", f)
            ano, serie = m.group(1), f.split("_")[1]
            for p in intervencoes(open(os.path.join(CACHE, f), encoding="utf-8").read()):
                palavras = re.findall(r"[a-zà-ÿ]+", p)
                if not palavras:
                    continue
                desconhecidas = sum(1 for w in palavras if len(w) > 2 and not conhecida(w))
                if desconhecidas / len(palavras) > 0.12:  # OCR demasiado estragado
                    rejeitadas += 1
                    continue
                tipo = "discurso" if len(palavras) >= 150 else "espontaneo" if len(palavras) <= 60 else None
                if not tipo:
                    continue
                frases = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý«—])", p)
                (fd if tipo == "discurso" else fe).write(f"## {ano} {serie}\n" + "\n".join(frases) + "\n\n")
                dec = ano[:3] + "0"
                resumo.setdefault(dec, {"discurso": 0, "espontaneo": 0})[tipo] += 1
    resumo["_rejeitadas_ocr"] = rejeitadas
    json.dump(resumo, open(os.path.join(SAIDA, "parl_resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(resumo, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    opc = lambda k, d: int(a[a.index(k) + 1]) if k in a else d
    if a and a[0] == "recolher":
        recolher(opc("--por-ano", 6), opc("--de", 1945), opc("--ate", 2011))
    elif a and a[0] == "preparar":
        preparar()
    else:
        print(__doc__)
