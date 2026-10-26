"""Verificador de português europeu pré-AO90 e de marcas de texto gerado por IA.

Uso:
  python verificar.py texto.md [outro.md ...]
  python verificar.py -            (lê da entrada padrão)
  python verificar.py --json texto.md
  python verificar.py --rapido texto.md   (não carrega os dicionários Hunspell)

Níveis:
  ERRO   grafia AO90 ou brasileira, brasileirismo lexical, gerúndio com «estar», próclise inicial
  AVISO  provável problema de estilo ou de registo; decidir caso a caso
  NOTA   palavra desconhecida dos dicionários (nome próprio, neologismo ou gralha)

Código de saída: 0 sem erros, 1 com erros, 2 erro de utilização.

Os dicionários Hunspell são opcionais (ver instalar_dicionarios.py). Sem eles, a verificação
ortográfica usa só dados/ao90_preao.tsv, que cobre as cerca de 1400 formas AO90 mais
frequentes na imprensa portuguesa.
"""
import json
import os
import re
import statistics
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "..", "dados")
DIC = os.path.join(DADOS, "dicionarios")

PALAVRA = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:[-'’][A-Za-zÀ-ÖØ-öø-ÿ]+)*")
MESES = r"janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro"
# Sinais gráficos inequivocamente brasileiros: circunflexo antes de m/n (econômico, gênero),
# acento em ditongo aberto antes de 1990 (idéia, apóia), trema (freqüente).
# Palavras raras sem estes sinais e ausentes do dicionário pré-AO90 ficam como NOTA.
MARCA_BR = re.compile(r"[êô](?=[mn])|[éó]i(?=a|as|o|os)\b|ü")
ESTAR = (r"estar|estou|estás|está|estamos|estais|estão|estava|estavas|estávamos|estavam|"
         r"esteve|estive|estivemos|estiveram|estaria|estariam|estará|estarão|estivesse|estivessem|"
         r"esteja|estejam|estive|estiveste")


def ler_tsv(nome):
    linhas = []
    with open(os.path.join(DADOS, nome), encoding="utf-8") as f:
        for l in f:
            if l.startswith("#") or not l.strip():
                continue
            linhas.append(l.rstrip("\n").split("\t"))
    return linhas


def carregar_dicionarios():
    try:
        from spylls.hunspell import Dictionary
    except ImportError:
        return None
    caminhos = {k: os.path.join(DIC, k) for k in ("pt_PT-preao", "pt_PT", "pt_BR")}
    if not all(os.path.exists(c + ".dic") for c in caminhos.values()):
        return None
    return {k: Dictionary.from_files(c) for k, c in caminhos.items()}


class Verificador:
    def __init__(self, usar_dicionarios=True):
        self.ao90 = {a: p for a, p, *_ in ler_tsv("ao90_preao.tsv")}
        self.bras = []
        for linha in ler_tsv("brasileirismos.tsv"):
            formas, alt, nivel = linha[0], linha[1], linha[2]
            nota = linha[3] if len(linha) > 3 else ""
            padrao = re.compile(r"(?<![\w-])(" + formas + r")(?![\w-])", re.IGNORECASE)
            self.bras.append((padrao, alt, nivel.upper(), nota))
        self.ia = [(re.compile(p, re.IGNORECASE), int(lim), sug) for p, lim, sug in ler_tsv("vocabulario_ia.tsv")]
        self.dic = carregar_dicionarios() if usar_dicionarios else None
        self._cache = {}

    # --- utilitários -------------------------------------------------------
    @staticmethod
    def _pos(texto, i):
        linha = texto.count("\n", 0, i) + 1
        col = i - (texto.rfind("\n", 0, i) + 1) + 1
        return linha, col

    @staticmethod
    def _excerto(texto, i, j, margem=30):
        a, b = max(0, i - margem), min(len(texto), j + margem)
        return ("…" if a else "") + texto[a:b].replace("\n", " ") + ("…" if b < len(texto) else "")

    def _add(self, res, texto, nivel, categoria, i, j, msg):
        l, c = self._pos(texto, i)
        res.append({"nivel": nivel, "categoria": categoria, "linha": l, "coluna": c,
                    "texto": texto[i:j], "mensagem": msg, "contexto": self._excerto(texto, i, j)})

    def _classificar(self, palavra):
        """Devolve 'ok', 'ao90', 'br' ou 'desconhecida' segundo os dicionários."""
        if palavra in self._cache:
            return self._cache[palavra]
        pre, ao, br = self.dic["pt_PT-preao"], self.dic["pt_PT"], self.dic["pt_BR"]
        partes = [palavra] + (re.split(r"[-'’]", palavra) if re.search(r"[-'’]", palavra) else [])
        if pre.lookup(palavra) or (len(partes) > 1 and all(pre.lookup(p) for p in partes[1:] if p)):
            r = "ok"
        elif ao.lookup(palavra):
            r = "ao90"
        elif br.lookup(palavra):
            r = "br"
        else:
            r = "desconhecida"
        self._cache[palavra] = r
        return r

    # --- verificações ----------------------------------------------------------
    def ortografia(self, texto, res):
        inicio_frase = True
        for m in PALAVRA.finditer(texto):
            w = m.group(0)
            antes = texto[max(0, m.start() - 3):m.start()]
            inicio = m.start() == 0 or bool(re.search(r"[.!?:\n»]\s*$|^\s*[-—>*#]\s*$", antes))
            baixa = w.lower()
            if baixa in self.ao90:
                sug = self.ao90[baixa]
                sug = sug[0].upper() + sug[1:] if w[0].isupper() else sug
                self._add(res, texto, "ERRO", "grafia AO90", m.start(), m.end(), f"escrever «{sug}»")
                continue
            if self.dic is None or any(ch.isdigit() for ch in w) or len(w) < 2:
                continue
            if w[0].isupper() and not inicio:
                continue  # provável nome próprio
            r = self._classificar(w) if not w.isupper() else "ok"
            if r == "ok" and w[0].isupper():
                continue
            if r != "ok" and w[0].isupper():
                r = self._classificar(baixa)
            if r == "ao90":
                self._add(res, texto, "ERRO", "grafia AO90", m.start(), m.end(), "forma do AO90: usar a grafia anterior")
            elif r == "br" and MARCA_BR.search(baixa):
                self._add(res, texto, "ERRO", "grafia brasileira", m.start(), m.end(), "forma brasileira: usar a grafia portuguesa")
            elif r in ("br", "desconhecida") and w.islower():
                self._add(res, texto, "NOTA", "palavra desconhecida", m.start(), m.end(), "confirmar (gralha, neologismo ou estrangeirismo)")

        for m in re.finditer(r"(?<![\w-])(" + MESES + r")(?![\w-])", texto):
            if texto[m.start()] .islower():
                self._add(res, texto, "ERRO", "maiúsculas", m.start(), m.end(), "na grafia pré-AO90 os meses escrevem-se com maiúscula")
        for m in re.finditer(r"\b(primavera|verão|outono|inverno)\b", texto):
            self._add(res, texto, "AVISO", "maiúsculas", m.start(), m.end(), "estação do ano: com maiúscula (Primavera, Verão…) na grafia pré-AO90")
        hifens = {r"fim de semana": "fim-de-semana", r"fins de semana": "fins-de-semana",
                  r"(hei|hás|há|havemos|heis|hão) de": None, r"cor de rosa": "cor-de-rosa",
                  r"para-quedas": "pára-quedas", r"paraquedas": "pára-quedas"}
        for pad, sug in hifens.items():
            for m in re.finditer(r"(?<![\w-])" + pad + r"(?![\w-])", texto, re.IGNORECASE):
                s = sug or m.group(0).replace(" ", "-")
                self._add(res, texto, "ERRO", "hífen", m.start(), m.end(), f"escrever «{s}»")

    def lexico(self, texto, res):
        for padrao, alt, nivel, nota in self.bras:
            for m in padrao.finditer(texto):
                msg = f"brasileirismo: em PT-PT, {alt}" + (f" ({nota})" if nota else "")
                self._add(res, texto, nivel, "brasileirismo", m.start(), m.end(), msg)

    def sintaxe(self, texto, res):
        for m in re.finditer(r"\b(" + ESTAR + r")\s+(\w+ndo)\b", texto, re.IGNORECASE):
            self._add(res, texto, "ERRO", "gerúndio", m.start(), m.end(),
                      "estar + gerúndio: em PT-PT, «estar a + infinitivo»")
        for m in re.finditer(r"\b(continua|continuam|continuou|continuava|fica|ficou|ficava|fiquei|ficaram)\s+(\w+ndo)\b", texto, re.IGNORECASE):
            self._add(res, texto, "AVISO", "gerúndio", m.start(), m.end(),
                      "em PT-PT, «continuar a / ficar a + infinitivo» ou «ficar à espera»")
        for m in re.finditer(r"(?:^|(?<=[.!?»]\s)|(?<=\n))\s*(Me|Te|Lhe|Lhes|Vos)\s+[a-zà-ÿ]+", texto):
            self._add(res, texto, "ERRO", "colocação pronominal", m.start(1), m.end(),
                      "próclise em início de frase: em PT-PT, ênclise («Disse-me», «Parece-me»)")
        for m in re.finditer(r"(?:^|(?<=[.!?]\s)|(?<=\n))(Meu|Minha|Meus|Minhas|Seu|Sua|Seus|Suas|Nosso|Nossa)\s+(?!caro|cara|querid|Deus|senhor|senhora|amig)[a-zà-ÿ]+", texto):
            self._add(res, texto, "AVISO", "artigo", m.start(), m.end(),
                      "possessivo sem artigo: em PT-PT, «O meu…», «A minha…»")
        for m in re.finditer(r"\b(tem|tens|temos|têm|tinha|tinham|tive|teve|terá|terão|ter)\s+que\s+[a-zà-ÿ]+(r|r-se)\b", texto, re.IGNORECASE):
            self._add(res, texto, "AVISO", "regência", m.start(), m.end(), "preferir «ter de»")

    def estilo(self, texto, res):
        for padrao, limite, sug in self.ia:
            ocorr = list(padrao.finditer(texto))
            if len(ocorr) > limite:
                for m in ocorr[limite:]:
                    self._add(res, texto, "AVISO", "marca de IA", m.start(), m.end(),
                              f"{sug} (limite: {limite} por texto)")
        palavras = len(PALAVRA.findall(texto))
        paragrafos = [p for p in re.split(r"\n\s*\n", texto) if len(PALAVRA.findall(p)) > 15
                      and not p.lstrip().startswith(("#", "-", "*", "|", ">"))]
        for p in paragrafos:
            n = p.count("—") + len(re.findall(r"\s–\s", p))
            if n > 2 and not p.lstrip().startswith("—"):
                i = texto.find(p)
                self._add(res, texto, "AVISO", "travessões", i, i + min(40, len(p)),
                          f"{n} travessões num parágrafo: usar vírgulas, parênteses ou dois-pontos")
        perguntas = texto.count("?")
        if perguntas > max(2, palavras // 250):
            self._add(res, texto, "AVISO", "perguntas retóricas", 0, 0, f"{perguntas} perguntas em {palavras} palavras")
        exclam = len(re.findall(r"!(?!\[)", texto))
        if exclam > max(1, palavras // 400):
            self._add(res, texto, "AVISO", "exclamações", 0, 0, f"{exclam} pontos de exclamação")
        for m in re.finditer(r"[“”]", texto):
            self._add(res, texto, "AVISO", "aspas", m.start(), m.end(), "em PT-PT, preferir aspas angulares « »")
            break
        if len(re.findall(r"\*\*[^*]+\*\*", texto)) > 3 and len(paragrafos) >= 3:
            self._add(res, texto, "AVISO", "formatação", 0, 0, "muitos negritos em prosa corrida")
        if len(paragrafos) >= 5:
            tam = [len(PALAVRA.findall(p)) for p in paragrafos]
            cv = statistics.pstdev(tam) / statistics.mean(tam)
            if cv < 0.25:
                self._add(res, texto, "AVISO", "ritmo", 0, 0,
                          f"parágrafos de tamanho quase igual (variação {cv:.2f}); variar")
        frases = [f for f in re.split(r"(?<=[.!?])\s+", texto) if len(PALAVRA.findall(f)) > 3]
        if len(frases) >= 8:
            tam = [len(PALAVRA.findall(f)) for f in frases]
            cv = statistics.pstdev(tam) / statistics.mean(tam)
            if cv < 0.35:
                self._add(res, texto, "AVISO", "ritmo", 0, 0,
                          f"frases de tamanho uniforme (variação {cv:.2f}); alternar longas e curtas")
        triades = re.findall(r"\b\w+, \w+ e \w+\b", texto)
        if len(triades) > max(2, palavras // 200):
            self._add(res, texto, "AVISO", "tríades", 0, 0, f"{len(triades)} enumerações de três elementos")

    def verificar(self, texto):
        res = []
        # ignora blocos de código
        limpo = re.sub(r"```.*?```", lambda m: " " * len(m.group(0)), texto, flags=re.S)
        self.ortografia(limpo, res)
        self.lexico(limpo, res)
        self.sintaxe(limpo, res)
        self.estilo(limpo, res)
        ordem = {"ERRO": 0, "AVISO": 1, "NOTA": 2}
        res.sort(key=lambda r: (ordem[r["nivel"]], r["linha"], r["coluna"]))
        return res


def resumo(res):
    return {n: sum(1 for r in res if r["nivel"] == n) for n in ("ERRO", "AVISO", "NOTA")}


def imprimir(nome, res, palavras):
    c = resumo(res)
    print(f"== {nome}: {palavras} palavras · {c['ERRO']} erros · {c['AVISO']} avisos · {c['NOTA']} notas")
    for r in res:
        onde = f"{r['linha']}:{r['coluna']}" if r["linha"] else "-"
        alvo = f"«{r['texto']}» " if r["texto"] else ""
        print(f"  {r['nivel']:5} {onde:>7}  [{r['categoria']}] {alvo}— {r['mensagem']}")


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    sys.stdout.reconfigure(encoding="utf-8")
    v = Verificador(usar_dicionarios="--rapido" not in argv)
    if v.dic is None and "--rapido" not in argv:
        print("(dicionários Hunspell não disponíveis: verificação ortográfica limitada à lista AO90; "
              "ver scripts/instalar_dicionarios.py)", file=sys.stderr)
    saida, erros = {}, 0
    for nome in args:
        texto = sys.stdin.read() if nome == "-" else open(nome, encoding="utf-8").read()
        res = v.verificar(texto)
        erros += resumo(res)["ERRO"]
        if "--json" in argv:
            saida[nome] = {"palavras": len(PALAVRA.findall(texto)), "resumo": resumo(res), "ocorrencias": res}
        else:
            imprimir(nome, res, len(PALAVRA.findall(texto)))
    if "--json" in argv:
        print(json.dumps(saida, ensure_ascii=False, indent=1))
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
