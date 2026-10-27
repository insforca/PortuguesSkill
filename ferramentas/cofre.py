"""Leitura e escrita das notas do cofre Obsidian (Portuguese Skill/), sem dependências externas.

As notas têm propriedades YAML simples no topo (texto, números, listas de ligações) e corpo
em Markdown. Este módulo lê e escreve só esse subconjunto de YAML, que é o que o Obsidian
mostra como «Propriedades».
"""
import json
import os
import re

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Portuguese Skill")
PASTAS = {"regra": "Regras", "medicao": "Medições", "fonte": "Fontes", "fenomeno": "Fenómenos",
          "registo": "Registos", "teste": "Testes", "indice": "00 Índices"}


def _valor_yaml(v):
    if v is None or v == "":
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        return "[" + ", ".join(json.dumps(x, ensure_ascii=False) for x in v) + "]"
    return "'" + str(v).replace("'", "''") + "'"


def _ler_valor(t):
    t = t.strip()
    if t == "":
        return None
    if t.startswith("'") and t.endswith("'"):
        return t[1:-1].replace("''", "'")
    if t.startswith('"') and t.endswith('"'):
        return json.loads(t)
    if t.startswith("["):
        return [json.loads(x) for x in re.findall(r'"(?:[^"\\]|\\.)*"', t)]
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    if re.fullmatch(r"-?\d+\.\d+", t):
        return float(t)
    if t in ("true", "false"):
        return t == "true"
    return t


def nome_ficheiro(titulo):
    """Título de nota -> nome de ficheiro válido no Windows e no Obsidian."""
    return re.sub(r'[\\/:*?"<>|#^\[\]]', "-", titulo).strip()


def escrever(tipo, titulo, props, corpo=""):
    pasta = os.path.join(RAIZ, PASTAS[tipo])
    os.makedirs(pasta, exist_ok=True)
    linhas = ["---", f"tipo: {tipo}"]
    for k, v in props.items():
        linhas.append(f"{k}: {_valor_yaml(v)}".rstrip())
    linhas.append("---")
    texto = "\n".join(linhas) + "\n\n" + corpo.strip() + "\n"
    caminho = os.path.join(pasta, nome_ficheiro(titulo) + ".md")
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
    return caminho


def ler(caminho):
    texto = open(caminho, encoding="utf-8").read()
    props, corpo = {}, texto
    m = re.match(r"---\n(.*?)\n---\n?(.*)", texto, re.S)
    if m:
        for linha in m.group(1).split("\n"):
            if ":" in linha and not linha.startswith(" "):
                k, _, v = linha.partition(":")
                props[k.strip()] = _ler_valor(v)
        corpo = m.group(2)
    props["_titulo"] = os.path.splitext(os.path.basename(caminho))[0]
    props["_corpo"] = corpo
    return props


def todas(tipo):
    pasta = os.path.join(RAIZ, PASTAS[tipo])
    if not os.path.isdir(pasta):
        return []
    return [ler(os.path.join(pasta, f)) for f in sorted(os.listdir(pasta)) if f.endswith(".md")]


def ligacao(titulo):
    return f"[[{nome_ficheiro(titulo)}]]"


def alvo(lig):
    """'[[Nome]]' ou '[[Nome|alias]]' -> 'Nome'."""
    m = re.match(r"\[\[([^\]|]+)", lig or "")
    return m.group(1) if m else lig
