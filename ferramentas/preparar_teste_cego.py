"""Prepara um teste cego: excertos humanos do Público e excertos gerados com a skill, baralhados.

Humanos: extractos do CETEMPúblico 1.7 das secções de opinião (opi) e cultura (clt), com
2 ou mais parágrafos e 120-230 palavras, sem anos nem números de quatro algarismos e com
poucos nomes próprios (para a época e a actualidade não denunciarem a origem).
Ficam de fora entrevistas (perguntas e respostas), datas, parênteses rectos e menções ao jornal.
IA: um texto por excerto humano, do mesmo género, sobre o mesmo assunto e situado na mesma
época (pedidos em testes/pedidos_cego.tsv, gerados com a skill), para o assunto e a época não
denunciarem a origem. Sem títulos nem formatação, cortados para um tamanho semelhante.

A página fica em .cache/teste_cego/ (fora do git: os extractos do CETEMPúblico não são
redistribuídos). Abre-se no browser; no fim mostra o resultado e uma linha para copiar.

Uso:
  python preparar_teste_cego.py --humanos [--n 10] [--semente 7]
      escolhe os excertos humanos e guarda-os em .cache/teste_cego/humanos.json
      (mostra secção e semestre de cada um, para escrever os pedidos emparelhados)
  python preparar_teste_cego.py <pasta_ia> [--semente 7]
      junta os excertos humanos guardados com os textos gerados e escreve a página
"""
import base64
import json
import os
import random
import re
import sys

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CETEM = os.path.join(REPO, ".cache", "corpora", "CETEMPublico1.7.txt")
DESTINO = os.path.join(REPO, ".cache", "teste_cego")
SECCAO = re.compile(r"\bsec=([a-z-]+)")
PALAVRA = re.compile(r"[A-Za-zÀ-ÿ]+")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preparar_corpora import juntar  # noqa: E402


def aceitavel(paragrafos):
    texto = "\n".join(paragrafos)
    n = len(PALAVRA.findall(texto))
    if len(paragrafos) < 2 or not 120 <= n <= 230:
        return False
    if re.search(r"\d{4}|\d+/\d+/\d+|\bcontos\b|escudos|\$|\[|PÚBLICO", texto):
        return False
    # entrevistas: «P. —», «R. —» ou parágrafos curtos que são só uma pergunta
    if any(re.match(r"[PR]\.? ?[—:-]", p) or (p.endswith("?") and len(p.split()) < 25) for p in paragrafos):
        return False
    # nomes próprios: palavras com maiúscula que não começam frase
    nomes = re.findall(r"(?<=[a-zà-ÿ,;] )[A-ZÀ-Ý][a-zà-ÿ]+", texto)
    if len(nomes) / n > 0.04:
        return False
    # frases cortadas ou excerto que começa a meio de uma citação
    return texto[0].isupper() and texto.rstrip()[-1] in ".!?»"


def humanos(n, semente):
    """Amostragem de reservatório sobre todos os extractos aceitáveis (em fluxo)."""
    rnd = random.Random(semente)
    escolhidos, vistos = [], 0
    sec, sem, paragrafos, frases, tokens = None, None, [], [], []
    with open(CETEM, encoding="latin-1", errors="replace") as f:
        for linha in f:
            l = linha.strip()
            if l.startswith("<ext"):
                m = SECCAO.search(l)
                sec = m.group(1) if m else None
                m = re.search(r"\bsem=(\w+)", l)
                sem = m.group(1) if m else ""
                paragrafos = []
            elif sec not in ("opi", "clt"):
                continue
            elif l == "<p>":
                frases = []
            elif l == "</p>":
                if frases:
                    # «Cabo--Verde»: hífen duplicado do formato do corpus
                    paragrafos.append(re.sub(r"(?<=\w)--(?=\w)", "-", " ".join(frases)))
            elif l == "<s>":
                tokens = []
            elif l == "</s>":
                frases.append(juntar(tokens))
            elif l == "</ext>":
                if aceitavel(paragrafos):
                    vistos += 1
                    item = {"seccao": sec, "semestre": sem, "texto": "\n\n".join(paragrafos)}
                    if len(escolhidos) < n:
                        escolhidos.append(item)
                    else:
                        j = rnd.randrange(vistos)
                        if j < n:
                            escolhidos[j] = item
            elif l and not l.startswith("<"):
                tokens.append(l)
    print(f"{vistos} extractos humanos aceitáveis; escolhidos {len(escolhidos)}")
    return escolhidos


def limpar_ia(texto):
    pars = [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip()]
    # fora: títulos e linhas só em itálico/negrito; ficam as falas curtas de diálogo
    pars = [re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", p) for p in pars
            if not p.startswith("#") and not re.fullmatch(r"[*_].*[*_]", p)
            and (p.startswith("—") or len(PALAVRA.findall(p)) > 12)]
    # começa no 2.º parágrafo (como os extractos do corpus) se o resto ainda chegar às 120 palavras
    inicio = pars[1:] if len(PALAVRA.findall("\n".join(pars[1:]))) >= 120 else pars
    saida = []
    for p in inicio:
        saida.append(p)
        if len(PALAVRA.findall("\n".join(saida))) >= 140:
            break
    return "\n\n".join(saida)


def ia(pasta):
    return [(os.path.splitext(f)[0], limpar_ia(open(os.path.join(pasta, f), encoding="utf-8").read()))
            for f in sorted(os.listdir(pasta)) if f.endswith(".md") and f != "avaliacao.md"]


PAGINA = """<!doctype html>
<html lang="pt-PT"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Teste cego</title>
<style>
:root { --fundo:#faf8f4; --texto:#222; --suave:#666; --linha:#ddd; --marca:#2a5d8f; --cartao:#fff; }
@media (prefers-color-scheme: dark) { :root { --fundo:#1b1b1b; --texto:#e8e6e1; --suave:#aaa; --linha:#333; --marca:#7fb0e0; --cartao:#242424; } }
body { background:var(--fundo); color:var(--texto); font:17px/1.6 Georgia, serif; margin:0; padding:24px 16px; }
main { max-width:720px; margin:auto; }
.cartao { background:var(--cartao); border:1px solid var(--linha); border-radius:6px; padding:16px 20px; margin:20px 0; }
.cartao p { margin:0 0 .8em; }
.num { color:var(--suave); font:13px system-ui, sans-serif; }
.escolha { font:15px system-ui, sans-serif; display:flex; gap:16px; flex-wrap:wrap; align-items:center; }
.escolha input[type=text] { flex:1; min-width:200px; padding:4px 6px; }
button { font:15px system-ui, sans-serif; padding:8px 16px; background:var(--marca); color:#fff; border:0; border-radius:4px; cursor:pointer; }
textarea { width:100%; height:120px; font:13px monospace; }
.certo { color:#2e7d32; } .errado { color:#c62828; }
</style></head><body><main>
<h1>Teste cego</h1>
<p>Vinte excertos de textos de opinião, ensaio e crónica. Uns foram escritos por pessoas e publicados num jornal português; outros foram gerados por IA. Para cada um, escolha <b>Humano</b> ou <b>IA</b> e, se quiser, anote o que o levou a decidir. A chave só aparece no fim.</p>
<div id="lista"></div>
<button onclick="corrigir()">Ver resultado</button>
<div id="resultado"></div>
</main>
<script>
const TEXTOS = __TEXTOS__;
const CHAVE = JSON.parse(atob("__CHAVE__"));
const lista = document.getElementById("lista");
TEXTOS.forEach((t, k) => {
  const d = document.createElement("div"); d.className = "cartao";
  d.innerHTML = `<div class="num">Texto ${k + 1}</div>` + t.split("\\n\\n").map(p => `<p>${p.replace(/&/g,"&amp;").replace(/</g,"&lt;")}</p>`).join("") +
    `<div class="escolha"><label><input type="radio" name="t${k}" value="H"> Humano</label>` +
    `<label><input type="radio" name="t${k}" value="I"> IA</label>` +
    `<input type="text" id="n${k}" placeholder="O que o denunciou (opcional)"></div><div id="r${k}" class="num"></div>`;
  lista.appendChild(d);
});
function corrigir() {
  let certos = 0, respondidos = 0, linhas = [];
  TEXTOS.forEach((t, k) => {
    const e = document.querySelector(`input[name=t${k}]:checked`);
    const v = e ? e.value : "-";
    if (e) respondidos++;
    const ok = v === CHAVE[k].o;
    if (ok) certos++;
    document.getElementById("r" + k).innerHTML = e ? `<span class="${ok ? "certo" : "errado"}">${ok ? "Certo" : "Errado"}</span> — era ${CHAVE[k].o === "H" ? "humano" : "IA"} (${CHAVE[k].id})` : `era ${CHAVE[k].o === "H" ? "humano" : "IA"} (${CHAVE[k].id})`;
    linhas.push(`${k + 1}\\t${CHAVE[k].id}\\t${CHAVE[k].o}\\t${v}\\t${document.getElementById("n" + k).value}`);
  });
  document.getElementById("resultado").innerHTML = `<h2>${certos} certos em ${TEXTOS.length} (${respondidos} respondidos)</h2>` +
    `<p>Ao acaso dá cerca de 10. Copie as linhas abaixo e cole-as na conversa:</p><textarea readonly>${linhas.join("\\n")}</textarea>`;
}
</script></body></html>
"""


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if not argv:
        print(__doc__)
        return 2
    n = int(argv[argv.index("--n") + 1]) if "--n" in argv else 10
    semente = int(argv[argv.index("--semente") + 1]) if "--semente" in argv else 7
    os.makedirs(DESTINO, exist_ok=True)
    guardados = os.path.join(DESTINO, "humanos.json")
    if argv[0] == "--humanos":
        hs = humanos(n, semente)
        with open(guardados, "w", encoding="utf-8") as f:
            json.dump(hs, f, ensure_ascii=False, indent=1)
        for k, h in enumerate(hs, 1):
            print(f"\n== H{k:02d} sec={h['seccao']} sem={h['semestre']} "
                  f"({len(PALAVRA.findall(h['texto']))} palavras)\n{h['texto']}")
        return 0
    with open(guardados, encoding="utf-8") as f:
        hs = json.load(f)
    itens = [(f"H{k + 1:02d}", "H", h["texto"]) for k, h in enumerate(hs)]
    itens += [(i, "I", t) for i, t in ia(argv[0])]
    random.Random(semente).shuffle(itens)
    chave = [{"id": i, "o": o} for i, o, _ in itens]
    pagina = (PAGINA.replace("__TEXTOS__", json.dumps([t for _, _, t in itens], ensure_ascii=False))
              .replace("__CHAVE__", base64.b64encode(json.dumps(chave).encode()).decode()))
    open(os.path.join(DESTINO, "teste.html"), "w", encoding="utf-8").write(pagina)
    with open(os.path.join(DESTINO, "excertos.md"), "w", encoding="utf-8") as f:
        for k, (i, o, t) in enumerate(itens, 1):
            f.write(f"## {k}. {i} ({'humano' if o == 'H' else 'IA'})\n\n{t}\n\n")
    for i, o, t in itens:
        print(f"{i} {o} {len(PALAVRA.findall(t))} palavras")
    print("página:", os.path.abspath(os.path.join(DESTINO, "teste.html")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
