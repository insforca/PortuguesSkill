"""Bateria de testes da skill: gera os textos com o Claude Code e avalia-os com o verificador.

Uso:
  python correr.py gerar <etiqueta> [--ids 01,02] [--sem-skill] [--conjunto pedidos_dificeis.tsv]
      Gera um texto por pedido de pedidos.tsv com `claude -p` e guarda-os em
      resultados/<etiqueta>/NN.md. Corre numa pasta temporária neutra, para que
      memórias ou CLAUDE.md do projecto não influenciem o resultado.
      Com --sem-skill, o pedido não menciona a skill e a ferramenta Skill é bloqueada
      (linha de base). Com --conjunto, usa outro ficheiro de pedidos (por omissão, pedidos.tsv).

  python correr.py avaliar <etiqueta> [<etiqueta2> ...]
      Corre o verificador sobre resultados/<etiqueta>/ e escreve a tabela de
      resultados em resultados/<etiqueta>/avaliacao.md. Com várias etiquetas,
      mostra uma comparação lado a lado.

Requisitos: Claude Code instalado (comando `claude`), Python 3.9+, e a skill
instalada (npx skills add insforca/PortuguesSkill). Os dicionários do verificador
são opcionais mas recomendados (scripts/instalar_dicionarios.py).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RESULTADOS = os.path.join(AQUI, "resultados")
INSTRUCAO = ("Usa a skill portugues-skill. Responde apenas com o texto pedido, "
             "sem introdução nem comentários. ")


def localizar_verificador():
    candidatos = [
        os.path.join(AQUI, "..", "pt-pt", "antesAO90", "scripts", "verificar.py"),
        os.path.expanduser("~/.claude/skills/portugues-skill/scripts/verificar.py"),
    ]
    for c in candidatos:
        if os.path.exists(c):
            return os.path.abspath(c)
    sys.exit("verificar.py não encontrado")


CONJUNTOS = ("pedidos.tsv", "pedidos_dificeis.tsv")


def ler_pedidos(conjunto="pedidos.tsv"):
    pedidos = []
    with open(os.path.join(AQUI, conjunto), encoding="utf-8") as f:
        for l in f:
            if l.startswith("#") or not l.strip():
                continue
            i, registo, pedido = l.rstrip("\r\n").split("\t")
            pedidos.append((i, registo, pedido))
    return pedidos


def gerar(etiqueta, ids=None, sem_skill=False, conjunto="pedidos.tsv"):
    destino = os.path.join(RESULTADOS, etiqueta)
    os.makedirs(destino, exist_ok=True)
    claude = shutil.which("claude")
    if not claude:
        sys.exit("comando `claude` não encontrado")
    neutra = tempfile.mkdtemp(prefix="pt-testes-")
    for i, registo, pedido in ler_pedidos(conjunto):
        if ids and i not in ids:
            continue
        saida = os.path.join(destino, f"{i}.md")
        if os.path.exists(saida):
            print(f"{i} já existe, a saltar")
            continue
        texto = pedido if sem_skill else INSTRUCAO + pedido
        print(f"{i} [{registo}] a gerar…", flush=True)
        cmd = [claude, "-p", texto, "--output-format", "text"]
        if sem_skill:
            # A skill está instalada globalmente e a descrição manda usá-la sempre que se
            # escreve em português: sem bloquear a ferramenta, a linha de base usa-a na mesma.
            cmd += ["--disallowedTools", "Skill"]
        r = subprocess.run(cmd, cwd=neutra, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        if r.returncode != 0:
            print(f"   falhou: {r.stderr.strip()[:300]}")
            continue
        with open(saida, "w", encoding="utf-8") as f:
            f.write(r.stdout.strip() + "\n")
    shutil.rmtree(neutra, ignore_errors=True)


def avaliar_uma(etiqueta):
    pasta = os.path.join(RESULTADOS, etiqueta)
    ficheiros = sorted(f for f in os.listdir(pasta) if f.endswith(".md") and f != "avaliacao.md")
    r = subprocess.run([sys.executable, "-I", localizar_verificador(), "--json"]
                       + [os.path.join(pasta, f) for f in ficheiros],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    dados = json.loads(r.stdout)
    registos = {i: reg for c in CONJUNTOS for i, reg, _ in ler_pedidos(c)}
    linhas, tot = [], {"palavras": 0, "ERRO": 0, "AVISO": 0}
    categorias = {}
    for caminho, d in dados.items():
        i = os.path.splitext(os.path.basename(caminho))[0]
        tot["palavras"] += d["palavras"]
        tot["ERRO"] += d["resumo"]["ERRO"]
        tot["AVISO"] += d["resumo"]["AVISO"]
        for o in d["ocorrencias"]:
            if o["nivel"] != "NOTA":
                categorias[(o["nivel"], o["categoria"])] = categorias.get((o["nivel"], o["categoria"]), 0) + 1
        exemplos = "; ".join(f"«{o['texto']}» ({o['categoria']})" for o in d["ocorrencias"]
                             if o["nivel"] == "ERRO")[:160]
        linhas.append(f"| {i} | {registos.get(i, '')} | {d['palavras']} | {d['resumo']['ERRO']} | "
                      f"{d['resumo']['AVISO']} | {exemplos} |")
    por_mil = lambda n: round(n / max(tot["palavras"], 1) * 1000, 1)
    md = [f"# Avaliação: {etiqueta}", "",
          f"**{len(dados)} textos · {tot['palavras']} palavras · {tot['ERRO']} erros "
          f"({por_mil(tot['ERRO'])} por mil palavras) · {tot['AVISO']} avisos ({por_mil(tot['AVISO'])} por mil)**", "",
          "| id | registo | palavras | erros | avisos | erros encontrados |", "|---|---|---|---|---|---|"] + linhas
    md += ["", "## Por categoria", "", "| nível | categoria | ocorrências |", "|---|---|---|"]
    md += [f"| {n} | {c} | {k} |" for (n, c), k in sorted(categorias.items(), key=lambda x: -x[1])]
    with open(os.path.join(pasta, "avaliacao.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    return tot, len(dados)


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) < 2 or argv[0] not in ("gerar", "avaliar"):
        print(__doc__)
        return 2
    if argv[0] == "gerar":
        ids = None
        if "--ids" in argv:
            ids = set(argv[argv.index("--ids") + 1].split(","))
        conjunto = argv[argv.index("--conjunto") + 1] if "--conjunto" in argv else "pedidos.tsv"
        gerar(argv[1], ids, "--sem-skill" in argv, conjunto)
        return 0
    etiquetas = [a for a in argv[1:] if not a.startswith("--")]
    print("| etiqueta | textos | palavras | erros | erros/1000 | avisos | avisos/1000 |")
    print("|---|---|---|---|---|---|---|")
    for e in etiquetas:
        tot, n = avaliar_uma(e)
        pm = lambda k: round(tot[k] / max(tot["palavras"], 1) * 1000, 1)
        print(f"| {e} | {n} | {tot['palavras']} | {tot['ERRO']} | {pm('ERRO')} | {tot['AVISO']} | {pm('AVISO')} |")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
