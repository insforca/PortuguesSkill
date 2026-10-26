"""Estilometria: quão perto está um texto da prosa portuguesa (Público) ou brasileira (Folha)?

Usa o Delta de Burrows sobre palavras gramaticais, pontuação, comprimento das frases e
colocação dos pronomes. Não depende de nenhuma lista de tiques: compara o perfil do texto
com o perfil médio de milhares de excertos reais de imprensa.

Uso:
  python estilometria.py texto.md [outro.md ...]        (relatório por texto)
  python estilometria.py --pasta resultados/v1.5         (média de uma pasta de textos)
  python estilometria.py --gerar-perfil pt.txt br.txt    (para quem mantém a skill)

Leitura:
  Delta PT / Delta BR  distância ao perfil do Público / da Folha (menor = mais perto)
  Margem PT            Delta BR − Delta PT (positivo = mais perto do português europeu)
  Traços desviantes    os traços em que o texto mais se afasta do Público

Limites: o perfil de referência é jornalístico (1991-1998); ficção, cartas e diálogos
afastam-se dele por natureza. Compare versões entre si com os mesmos pedidos, em vez de
ler os números absolutos. Textos com menos de 150 palavras dão medidas pouco estáveis.
"""
import json
import math
import os
import re
import statistics
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PERFIL = os.path.join(AQUI, "..", "dados", "perfil_estilometrico.json")

GRAMATICAIS = """o a os as um uma uns umas de do da dos das em no na nos nas num numa por pelo pela pelos
pelas para com sem sobre entre até desde contra ao à aos às que se não mais mas ou e nem como quando
onde porque pois porém contudo todavia aliás já ainda também só muito pouco tão bem mal sempre nunca
aqui ali lá cá isto isso aquilo este esta estes estas esse essa esses essas aquele aquela ele ela eles
elas eu tu você nós me te lhe lhes vos meu minha seu sua seus suas teu tua nosso nossa é foi era são
eram está estão estava tem têm tinha há havia ser ter estar vai pode podem deve assim então logo
porque depois antes agora hoje ontem cada todo toda todos todas outro outra outros mesmo mesma qual
quem cujo cuja""".split()
CLITICOS = r"-(me|te|se|lhe|lhes|nos|vos|o|a|os|as|lo|la|los|las|no|na)\b"
PALAVRA = re.compile(r"[a-zà-öø-ÿ]+(?:-[a-zà-öø-ÿ]+)*", re.IGNORECASE)


def tracos(texto):
    """Vector de traços por mil palavras, mais médias de frase."""
    palavras = [p.lower() for p in PALAVRA.findall(texto)]
    n = len(palavras)
    if n == 0:
        return None
    k = 1000 / n
    cont = {}
    for p in palavras:
        cont[p] = cont.get(p, 0) + 1
    t = {f"p:{w}": cont.get(w, 0) * k for w in GRAMATICAIS}
    for nome, sinal in ((",", ","), (";", ";"), (":", ":"), ("—", "—"), ("(", "("), ("?", "?"),
                        ("!", "!"), ("«", "«")):
        t[f"s:{nome}"] = texto.count(sinal) * k
    frases = [f for f in re.split(r"(?<=[.!?])\s+", texto) if PALAVRA.search(f)]
    tam = [len(PALAVRA.findall(f)) for f in frases] or [n]
    t["f:media"] = statistics.mean(tam)
    t["f:desvio"] = statistics.pstdev(tam)
    t["f:longas"] = sum(1 for x in tam if x > 35) / len(tam) * 100
    t["g:enclise"] = len(re.findall(r"[a-zà-ÿ]" + CLITICOS, texto, re.IGNORECASE)) * k
    t["g:gerundio"] = sum(1 for p in palavras if p.endswith("ndo") and len(p) > 5) * k
    t["g:a_infinitivo"] = len(re.findall(r"\b(est\w+|anda\w*|continu\w+|fic\w+)\s+a\s+\w+(ar|er|ir)\b",
                                         texto, re.IGNORECASE)) * k
    return t


def excertos(caminho, tamanho=250, maximo=6000):
    """Divide um corpus (artigos separados por linha em branco) em excertos de ~tamanho palavras."""
    atual, n_atual, saida = [], 0, []
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            if not linha.strip():
                continue
            atual.append(linha.strip())
            n_atual += len(linha.split())
            if n_atual >= tamanho:
                saida.append(" ".join(atual))
                atual, n_atual = [], 0
                if len(saida) >= maximo:
                    break
    return saida


N_TRACOS = 30  # só os traços que mais separam PT de BR; os restantes acrescentam ruído


def gerar_perfil(pt, br, treino=6000, teste=2000):
    ex = {"pt": [tracos(e) for e in excertos(pt, maximo=treino + teste)],
          "br": [tracos(e) for e in excertos(br, maximo=treino + teste)]}
    vt = {g: vs[:treino] for g, vs in ex.items()}
    todos = vt["pt"] + vt["br"]
    chaves = sorted(todos[0])
    media = {c: statistics.mean(v[c] for v in todos) for c in chaves}
    desvio = {c: statistics.pstdev([v[c] for v in todos]) or 1.0 for c in chaves}
    centro = {g: {c: statistics.mean((v[c] - media[c]) / desvio[c] for v in vs) for c in chaves}
              for g, vs in vt.items()}
    sel = sorted(chaves, key=lambda c: -abs(centro["pt"][c] - centro["br"][c]))[:N_TRACOS]
    centro = {g: {c: centro[g][c] for c in sel} for g in centro}
    # validação em excertos que não entraram no cálculo do perfil
    acertos = total = 0
    for g, vs in ex.items():
        for v in vs[treino:]:
            d = {h: delta(v, media, desvio, centro[h]) for h in centro}
            acertos += min(d, key=d.get) == g
            total += 1
    perfil = {"media": media, "desvio": desvio, "centro": centro,
              "info": {"excertos_treino": treino, "excertos_validacao": teste, "palavras_por_excerto": 250,
                       "tracos": sel, "validacao_acerto": round(acertos / total, 3),
                       "fontes": "CETEMPúblico 1.7 e CETENFolha 1.0 (Linguateca), amostras iniciais"}}
    with open(PERFIL, "w", encoding="utf-8") as f:
        json.dump(perfil, f, ensure_ascii=False, indent=0)
    print(f"perfil gravado com {len(sel)} traços; acerto PT/BR em {total} excertos reais "
          f"de validação: {acertos / total:.1%}")


def delta(v, media, desvio, centro):
    """Distância média, em desvios-padrão, aos traços seleccionados do centro de uma variedade."""
    return statistics.mean(abs((v[c] - media[c]) / desvio[c] - centro[c]) for c in centro)


def analisar(texto, perfil):
    v = tracos(texto)
    m, s, c = perfil["media"], perfil["desvio"], perfil["centro"]
    dpt, dbr = delta(v, m, s, c["pt"]), delta(v, m, s, c["br"])
    desvios = sorted(((v[k] - m[k]) / s[k] - c["pt"][k], k) for k in c["pt"])
    extremos = sorted(desvios, key=lambda x: -abs(x[0]))[:6]
    return dpt, dbr, extremos, v


def descrever(k):
    tipo, nome = k.split(":", 1)
    return {"p": f"«{nome}»", "s": f"sinal {nome}", "f": {"media": "comprimento médio da frase",
            "desvio": "variação no comprimento das frases", "longas": "frases com mais de 35 palavras"}.get(nome, nome),
            "g": {"enclise": "pronome depois do verbo (ênclise)", "gerundio": "gerúndios",
                  "a_infinitivo": "«estar a + infinitivo»"}.get(nome, nome)}[tipo]


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--gerar-perfil":
        gerar_perfil(argv[1], argv[2])
        return 0
    perfil = json.load(open(PERFIL, encoding="utf-8"))
    if argv[0] == "--pasta":
        for pasta in argv[1:]:
            ficheiros = sorted(f for f in os.listdir(pasta) if f.endswith(".md") and f != "avaliacao.md")
            res = [analisar(open(os.path.join(pasta, f), encoding="utf-8").read(), perfil) for f in ficheiros]
            dpt = statistics.mean(r[0] for r in res)
            dbr = statistics.mean(r[1] for r in res)
            mais_pt = sum(1 for r in res if r[0] < r[1])
            soma = {}
            for r in res:
                for z, k in r[2]:
                    soma[k] = soma.get(k, 0) + z
            top = sorted(soma.items(), key=lambda x: -abs(x[1]))[:6]
            print(f"== {pasta}: {len(res)} textos · Delta PT {dpt:.2f} · Delta BR {dbr:.2f} · "
                  f"margem PT {dbr - dpt:+.2f} · {mais_pt}/{len(res)} mais perto do Público")
            print("   traços que mais se afastam do Público: " + "; ".join(
                f"{descrever(k)} ({'acima' if z > 0 else 'abaixo'})" for k, z in top))
        return 0
    for nome in argv:
        dpt, dbr, extremos, _ = analisar(open(nome, encoding="utf-8").read(), perfil)
        print(f"== {nome}: Delta PT {dpt:.2f} · Delta BR {dbr:.2f} · margem PT {dbr - dpt:+.2f} "
              f"({'mais perto do Público' if dpt < dbr else 'mais perto da Folha'})")
        for z, k in extremos:
            print(f"   {descrever(k)}: {'acima' if z > 0 else 'abaixo'} do Público ({z:+.1f} desvios)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
