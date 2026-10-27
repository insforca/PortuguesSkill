"""Cria o cofre Obsidian (Portuguese Skill/) a partir dos dados actuais da skill. Corre-se uma vez.

Fontes: pt-pt/antesAO90/dados/{brasileirismos,vocabulario_ia,now_medicoes}.tsv, listas de
frequência do CHAVE em .cache/corpora/freq/ e os resultados conhecidos dos testes.
Depois disto, as regras editam-se no cofre e os TSV geram-se com gerar_dados.py.

Uso: python migrar_para_cofre.py [--forcar]   (--forcar apaga o cofre existente)
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cofre  # noqa: E402

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DADOS = os.path.join(REPO, "pt-pt", "antesAO90", "dados")
FREQ = os.path.join(REPO, ".cache", "corpora", "freq")
HOJE = "2026-10-27"


def ler_tsv(nome):
    """Devolve [(grupo, campos)] mantendo os cabeçalhos de grupo («# --- … ---»)."""
    grupo, linhas = "base", []
    for l in open(os.path.join(DADOS, nome), encoding="utf-8"):
        l = l.rstrip("\r\n")
        m = re.match(r"#\s*---\s*(.*?)\s*---\s*$", l)
        if m:
            grupo = m.group(1)
            continue
        if l.startswith("#") or not l.strip():
            continue
        linhas.append((grupo, l.split("\t")))
    return linhas


def ler_freq(nome):
    freq, tot = {}, 0
    with open(os.path.join(FREQ, nome), encoding="latin-1") as f:
        for l in f:
            p = l.rstrip("\n").split("\t")
            if len(p) == 2 and p[0].isdigit():
                n = int(p[0])
                tot += n
                freq[p[1]] = freq.get(p[1], 0) + n
    return freq, tot


def legivel(regex):
    s = regex.replace("\\b", "")
    for _ in range(5):
        s = re.sub(r"\((?:\?:)?([^()|]*)(?:\|[^()]*)?\)\??", r"\1", s)
    s = re.sub(r"\[[^\]]*\]\{[^}]*\}|\[[^\]]*\]|[\\^$*+?{}]|\d+,\d+", " ", s)
    s = s.split("|")[0]
    return re.sub(r"\s+", " ", s).strip()[:50] or regex[:30]


FONTES = {
    "CETEMPúblico": dict(periodo="1991-1998", variedade="PT", registo="imprensa", palavras="~180 milhões",
                         acesso="livre para investigação (Linguateca)", url="https://www.linguateca.pt/CETEMPublico/"),
    "CHAVE": dict(periodo="1994-1995", variedade="PT e BR", registo="imprensa (Público e Folha de S. Paulo)",
                  palavras="~65 + 42 milhões", acesso="listas de frequência livres (Linguateca)",
                  url="https://www.linguateca.pt/acesso/ordenador.php"),
    "NOW (Corpus do Português)": dict(periodo="2012-2019", variedade="PT, BR, AO, MZ", registo="notícias em linha",
                                      palavras="1,1 mil milhões", acesso="registo gratuito; só consultas manuais",
                                      url="https://www.corpusdoportugues.org/now/"),
    "Project Gutenberg": dict(periodo="1840-1930", variedade="PT e BR", registo="literatura",
                              palavras="~2 + 0,9 milhões (selecção de prosa)", acesso="domínio público",
                              url="https://www.gutenberg.org/browse/languages/pt"),
    "Debates Parlamentares": dict(periodo="1935-2011 (pré-AO90)", variedade="PT", registo="oral formal e espontâneo",
                                  palavras="a recolher", acesso="livre (robots.txt: 2 s entre pedidos)",
                                  url="https://debates.parlamento.pt/"),
    "Linguateca — corpora orais": dict(periodo="vários", variedade="PT e BR", registo="oral informal e regional",
                                       palavras="a recolher", acesso="listas de frequência livres",
                                       url="https://www.linguateca.pt/acesso/ordenador.php"),
    "Dicionários Hunspell (Natura, VERO)": dict(periodo="actual", variedade="PT pré-AO, PT AO90, BR",
                                                registo="dicionário", acesso="GPL/LGPL/MPL",
                                                url="https://natura.di.uminho.pt/download/sources/Dictionaries/hunspell/"),
    "Testes da skill": dict(periodo="2026", variedade="gerado", registo="vários",
                            acesso="testes/ no repositório", url=""),
}
FENOMENOS = {
    "Grafia AO90": "Formas do Acordo de 1990 (ação, atual, projeto) a repor na grafia anterior. Mapa de 1397 pares em `dados/ao90_preao.tsv`, tirado do [[CETEMPúblico]] e validado com os [[Dicionários Hunspell (Natura, VERO)]].",
    "Léxico PT-BR": "Palavras com equivalente diferente em Portugal e no Brasil (equipe/equipa, ônibus/autocarro). Curadoria a partir do [[CHAVE]].",
    "Léxico digital": "Vocabulário da tecnologia (celular/telemóvel, tela/ecrã), medido no [[NOW (Corpus do Português)]].",
    "Gerúndio": "«Estar + gerúndio» é brasileiro na norma actual; em Portugal, «estar a + infinitivo». No NOW, «está sendo» é ~1% de «está a ser» em PT.",
    "Colocação pronominal": "Ênclise como regra em PT-PT; próclise com atractores. Próclise em início de frase é brasileira.",
    "Comprimento das frases": "Assinatura de IA mais forte medida: frases curtas e uniformes. Público: média 24 palavras, 19% com 35 ou mais.",
    "Marcas de IA": "Vocabulário e fórmulas típicas de texto gerado (crucial, jornada, em suma, paralelismo negativo).",
    "Tiques descobertos": "Tiques encontrados automaticamente comparando textos gerados com o [[CETEMPúblico]] (ferramentas/descobrir_tiques.py).",
    "Tiques de ficção": "Tiques da ficção gerada, encontrados contra prosa literária portuguesa do [[Project Gutenberg]].",
    "Sobre-correcção": "Tiques criados pela própria skill (hora exacta, cheiro, «duas ou três»).",
    "Fala informal": "Marcas da oralidade portuguesa (tá bem, tou, pá) e brasileira (tô, a gente).",
    "Tratamento": "Formas de tratamento (tu, você, o senhor, V. Ex.ª).",
}
REGISTOS = {
    "Académico": "Impessoal ou plural de modéstia; frase longa articulada; citação APA, Chicago, MLA ou NP 405.",
    "Formal": "Cartas e e-mails institucionais: «Exmo. Senhor», «Com os melhores cumprimentos».",
    "Corrente": "Colegas e conhecidos em tom cordial.",
    "Informal": "Amigos e família: tu, elipses, marcas orais portuguesas.",
    "Literário": "Narrativa e diálogo: travessão, vozes distintas do narrador e das personagens.",
    "Oral formal": "Discurso e debate parlamentar; referência: [[Debates Parlamentares]].",
}
TESTES = [
    ("Bateria — sem skill", 20, 4829, 31, 6.4, 9.1, -0.06, "Linha de base, ferramenta Skill bloqueada."),
    ("Bateria — v1.5", 20, 4137, 0, 0.0, 4.8, -0.06, ""),
    ("Bateria — v1.6", 20, 4367, 0, 0.0, 3.0, 0.02, "Primeira versão com alvo de comprimento de frase."),
    ("Difíceis — sem skill", 10, 3331, 63, 18.9, 13.2, -0.06, ""),
    ("Difíceis — v1.6", 10, 2620, 0, 0.0, 5.0, -0.03, ""),
]
SINTAXE = [
    ("SX — gerúndio com estar", r"\b(est\w+) \w+ndo\b", "erro", "Gerúndio", "estar a + infinitivo"),
    ("SX — continuar ou ficar com gerúndio", r"\b(continu\w+|fic\w+) \w+ndo\b", "aviso", "Gerúndio", "continuar a / ficar a + infinitivo"),
    ("SX — próclise em início de frase", r"^(Me|Te|Lhe|Lhes|Vos) \w+", "erro", "Colocação pronominal", "ênclise: «Disse-me»"),
    ("SX — possessivo sem artigo", r"^(Meu|Minha|Seu|Sua|Nosso|Nossa) \w+", "aviso", "Colocação pronominal", "«O meu…», «A minha…»"),
    ("SX — ter que", r"\bter que\b", "aviso", "Léxico PT-BR", "ter de"),
    ("OR — meses com minúscula", r"\b(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\b", "erro", "Grafia AO90", "Janeiro, Fevereiro…"),
    ("OR — hífenes pré-AO90", r"\b(fim de semana|hei de|há de|cor de rosa|paraquedas)\b", "erro", "Grafia AO90", "fim-de-semana, hei-de…"),
    ("OR — mapa AO90 → pré-AO90", r"", "erro", "Grafia AO90", "dados/ao90_preao.tsv (1397 pares)"),
    ("ES — comprimento das frases", r"", "aviso", "Comprimento das frases", "média 20-28 palavras e uma frase longa por parágrafo"),
]


def main():
    if os.path.exists(cofre.RAIZ):
        if "--forcar" not in sys.argv:
            sys.exit("o cofre já existe; use --forcar para o recriar")
        shutil.rmtree(cofre.RAIZ)

    for t, p in FONTES.items():
        cofre.escrever("fonte", t, p, f"# {t}\n\n{p.get('url', '')}\n")
    for t, d in FENOMENOS.items():
        cofre.escrever("fenomeno", t, {}, f"# {t}\n\n{d}\n")
    for t, d in REGISTOS.items():
        cofre.escrever("registo", t, {}, f"# {t}\n\n{d}\n\nVer também `references/registos.md` na skill.\n")
    for titulo, n, pal, err, epm, apm, margem, nota in TESTES:
        cofre.escrever("teste", titulo, dict(textos=n, palavras=pal, erros=err, erros_por_mil=epm,
                                             avisos_por_mil=apm, margem_pt=margem, fonte=cofre.ligacao("Testes da skill")),
                       f"# {titulo}\n\n{nota}\n\nResultados em `testes/resultados/` e `testes/analises/resumo.md`.\n")

    # medições
    medicoes = []
    for l in open(os.path.join(DADOS, "now_medicoes.tsv"), encoding="utf-8"):
        if l.startswith("#") or not l.strip():
            continue
        forma, pt, br, razao, leitura = l.rstrip("\r\n").split("\t")
        t = f"NOW — {forma}"
        cofre.escrever("medicao", t, dict(fonte=cofre.ligacao("NOW (Corpus do Português)"), forma=forma,
                                          por_milhao_pt=float(pt), por_milhao_br=float(br),
                                          razao_br_pt=float(razao) if razao not in ("—", "") else None,
                                          metodo="consulta manual, vista Chart por país", data=HOJE),
                       f"# {t}\n\n{leitura}\n")
        medicoes.append((t, forma, float(pt), float(br)))
    pt_f, pt_t = ler_freq("formas.chavept945.txt")
    br_f, br_t = ler_freq("formas.chavebr945.txt")

    def chave(forma):
        a, b = pt_f.get(forma, 0), br_f.get(forma, 0)
        if a + b < 5:
            return None
        ppt, pbr = a / pt_t * 1e6, b / br_t * 1e6
        t = f"CHAVE — {forma}"
        cofre.escrever("medicao", t, dict(fonte=cofre.ligacao("CHAVE"), forma=forma, ocorr_pt=a, ocorr_br=b,
                                          por_milhao_pt=round(ppt, 2), por_milhao_br=round(pbr, 2),
                                          razao_br_pt=round((pbr + 0.5) / (ppt + 0.5), 1),
                                          metodo="listas de frequência Público vs Folha 1994-1995", data=HOJE),
                       f"# {t}\n\nOcorrências: Público {a}, Folha {b}.\n")
        medicoes.append((t, forma, ppt, pbr))
        return t

    # regras: brasileirismos
    n_regras, titulos = 0, set()

    def unico(t):
        base, i = t, 2
        while cofre.nome_ficheiro(t).lower() in titulos:
            t = f"{base} ({i})"
            i += 1
        titulos.add(cofre.nome_ficheiro(t).lower())
        return t

    for ordem, (grupo, c) in enumerate(ler_tsv("brasileirismos.tsv")):
        formas, alt, nivel = c[0], c[1], c[2]
        nota = c[3] if len(c) > 3 else ""
        ev = [chave(f) for f in formas.split("|") if " " not in f]
        ev = [e for e in ev if e]
        pad = re.compile(r"(?<![\w-])(" + formas + r")(?![\w-])", re.I)
        ev += [t for t, forma, *_ in medicoes if t.startswith("NOW") and pad.search(forma)]
        titulo = unico(f"BR — {formas.split('|')[0]}")
        cofre.escrever("regra", titulo, dict(
            categoria="brasileirismo", padrao=formas, alternativa=alt, nivel=nivel, nota=nota,
            estado="medida" if ev else "presumida", grupo=grupo, ordem=ordem,
            fenomeno=cofre.ligacao("Léxico digital" if "digital" in grupo else
                                   "Fala informal" if formas.split("|")[0] in ("pra", "tá", "tô", "a gente", "você") else
                                   "Léxico PT-BR"),
            evidencia=[cofre.ligacao(e) for e in dict.fromkeys(ev)]),
            f"# {titulo}\n\nEm PT-PT: **{alt}**. {nota}\n")
        n_regras += 1

    # regras: marcas de IA
    for ordem, (grupo, c) in enumerate(ler_tsv("vocabulario_ia.tsv")):
        padrao, limite, sug = c[0], int(c[1]), c[2]
        pad = re.compile(padrao, re.I)
        ev = [t for t, forma, *_ in medicoes if pad.search(forma)]
        descoberto = "descobertos" in grupo or "ficção" in grupo
        if descoberto:
            ev.append("Bateria — sem skill" if "descobertos" in grupo else "Bateria — v1.6")
        fen = ("Tiques de ficção" if "ficção" in grupo else
               "Sobre-correcção" if "própria skill" in sug else
               "Tiques descobertos" if descoberto else "Marcas de IA")
        titulo = unico(f"IA — {legivel(padrao)}")
        cofre.escrever("regra", titulo, dict(
            categoria="marca-ia", padrao=padrao, limite=limite, sugestao=sug, nivel="aviso",
            estado="medida" if ev else "presumida", grupo=grupo, ordem=ordem,
            fenomeno=cofre.ligacao(fen), evidencia=[cofre.ligacao(e) for e in dict.fromkeys(ev)]),
            f"# {titulo}\n\n{sug}. Limite: {limite} por texto.\n")
        n_regras += 1

    # regras implementadas directamente no verificador (não geradas)
    for titulo, padrao, nivel, fen, alt in SINTAXE:
        ev = [t for t, forma, *_ in medicoes if padrao and re.search(padrao, forma, re.I)]
        cofre.escrever("regra", titulo, dict(
            categoria="sintaxe" if titulo.startswith("SX") else "estilo" if titulo.startswith("ES") else "grafia",
            padrao=padrao, alternativa=alt, nivel=nivel, gerado=False, implementacao="scripts/verificar.py",
            estado="medida" if ev or titulo.startswith(("OR — mapa", "ES")) else "presumida",
            fenomeno=cofre.ligacao(fen), evidencia=[cofre.ligacao(e) for e in ev]),
            f"# {titulo}\n\nImplementada em código no verificador. Em PT-PT: **{alt}**.\n")
        n_regras += 1

    escrever_indices()
    escrever_config()
    print(f"cofre criado: {n_regras} regras, {len(medicoes)} medições")


def escrever_indices():
    cofre.escrever("indice", "Painel", {}, """# Painel

Fonte de verdade da `portugues-skill`. As regras editam-se aqui; os TSV da skill geram-se com
`python ferramentas/gerar_dados.py`.

## Regras por categoria e estado
```dataview
TABLE length(rows) AS "regras"
FROM "Regras"
GROUP BY categoria + " · " + estado
```

## Medições por fonte
```dataview
TABLE length(rows) AS "medições"
FROM "Medições"
GROUP BY fonte
```

## Regras por fenómeno
```dataview
TABLE length(rows) AS "regras"
FROM "Regras"
GROUP BY fenomeno
```
""")
    cofre.escrever("indice", "Regras sem medição", {}, """# Regras sem medição

Regras ainda presumidas: a lista de trabalho para as próximas medições.

```dataview
TABLE categoria, nivel, padrao
FROM "Regras"
WHERE estado = "presumida"
SORT nivel ASC, categoria ASC
```
""")
    cofre.escrever("indice", "Medições recentes", {}, """# Medições

```dataview
TABLE forma, por_milhao_pt AS "PT/milhão", por_milhao_br AS "BR/milhão", razao_br_pt AS "BR÷PT", fonte
FROM "Medições"
SORT razao_br_pt DESC
```
""")


def escrever_config():
    obs = os.path.join(cofre.RAIZ, ".obsidian")
    os.makedirs(obs, exist_ok=True)
    open(os.path.join(obs, "app.json"), "w", encoding="utf-8").write(
        '{\n  "propertiesInDocument": "visible",\n  "showFrontmatter": true\n}\n')
    cores = [("path:Regras", 0xE15759), ("path:Medições", 0x4E79A7), ("path:Fontes", 0x59A14F),
             ("path:Fenómenos", 0xF28E2B), ("path:Registos", 0xB07AA1), ("path:Testes", 0x76B7B2)]
    grupos = ",\n".join('    {"query": "%s", "color": {"a": 1, "rgb": %d}}' % (q, c) for q, c in cores)
    open(os.path.join(obs, "graph.json"), "w", encoding="utf-8").write(
        '{\n  "colorGroups": [\n' + grupos + '\n  ],\n  "showTags": false,\n  "showAttachments": false\n}\n')


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
