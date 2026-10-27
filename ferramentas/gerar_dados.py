"""Gera os ficheiros de dados da skill a partir do cofre (Portuguese Skill/) e valida as regras.

O cofre é a fonte de verdade: cada regra é uma nota em Portuguese Skill/Regras/ com as medições
que a justificam. Este script escreve dados/brasileirismos.tsv e dados/vocabulario_ia.tsv
(no formato que scripts/verificar.py lê) e a nota «00 Índices/Contradições».

Validações (a geração falha se alguma falhar):
  - padrão regex inválido ou repetido;
  - ligação de evidência para uma nota que não existe;
  - regra com estado «medida» sem nenhuma evidência;
  - brasileirismo de nível «erro» cuja medição mostra razão BR/PT < 3 (contradição), salvo se a
    nota tiver a propriedade contradicao_explicada com a justificação.

Uso:
  python gerar_dados.py              valida e escreve os TSV no repositório e na skill instalada
  python gerar_dados.py --verificar  só valida
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cofre  # noqa: E402

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DESTINOS = [os.path.join(REPO, "pt-pt", "antesAO90", "dados"),
            os.path.expanduser("~/.claude/skills/portugues-skill/dados")]
LIMIAR_CONTRADICAO = 3.0

CABECALHO_BR = ("# Brasileirismos lexicais — GERADO a partir do cofre Portuguese Skill/ (ferramentas/gerar_dados.py).\n"
                "# Não editar à mão: editar as notas em Portuguese Skill/Regras/.\n"
                "# Só léxico: a grafia brasileira (ação, ônibus, econômico) é detectada pelos dicionários.\n"
                "# forma(s) separadas por |\talternativa em PT-PT\tnível (erro|aviso)\tnota\n")
CABECALHO_IA = ("# Marcas de texto gerado por IA — GERADO a partir do cofre Portuguese Skill/ (ferramentas/gerar_dados.py).\n"
                "# Expressão regular (sem distinção de maiúsculas)\tlimite por texto\tsugestão\n")


def validar(regras, medicoes):
    erros, contradicoes, vistos = [], [], {}
    for r in regras:
        t = r["_titulo"]
        pad = r.get("padrao") or ""
        if r.get("gerado") is not False:
            try:
                re.compile(pad)
            except re.error as e:
                erros.append(f"{t}: regex inválido ({e})")
            if pad in vistos:
                erros.append(f"{t}: padrão repetido em «{vistos[pad]}»")
            vistos[pad] = t
        ev = [cofre.alvo(x) for x in (r.get("evidencia") or [])]
        for e in ev:
            if e not in medicoes and not os.path.exists(os.path.join(cofre.RAIZ, "Testes", e + ".md")):
                erros.append(f"{t}: evidência inexistente [[{e}]]")
        if r.get("estado") == "medida" and not ev:
            erros.append(f"{t}: estado «medida» sem evidência")
        if r.get("categoria") == "brasileirismo" and r.get("nivel") == "erro" and not r.get("contradicao_explicada"):
            for e in ev:
                m = medicoes.get(e)
                if m and isinstance(m.get("razao_br_pt"), (int, float)) and m["razao_br_pt"] < LIMIAR_CONTRADICAO \
                        and (m.get("por_milhao_pt", 0) + m.get("por_milhao_br", 0)) >= 1:
                    contradicoes.append((t, e, m["razao_br_pt"]))
    return erros, contradicoes


def gerar_tsv(regras, categoria, cabecalho, linha):
    sel = sorted((r for r in regras if r.get("categoria") == categoria and r.get("gerado") is not False),
                 key=lambda r: (r.get("ordem", 9999), r["_titulo"]))
    saida, grupo = [cabecalho], "base"
    for r in sel:
        g = r.get("grupo") or "base"
        if g != grupo:
            saida.append(f"# --- {g} ---\n")
            grupo = g
        saida.append(linha(r) + "\n")
    return "".join(saida), len(sel)


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    regras = cofre.todas("regra")
    medicoes = {m["_titulo"]: m for m in cofre.todas("medicao")}
    erros, contradicoes = validar(regras, medicoes)

    linhas = ["# Contradições", "",
              f"Brasileirismos de nível «erro» com uma medição em que a razão BR/PT é inferior a {LIMIAR_CONTRADICAO}.",
              "Gerado por `ferramentas/gerar_dados.py`.", ""]
    linhas += [f"- [[{t}]] ← [[{e}]] (razão {r})" for t, e, r in contradicoes] or ["Nenhuma."]
    cofre.escrever("indice", "Contradições", {}, "\n".join(linhas))

    presumidas = [r for r in regras if r.get("estado") == "presumida"]
    print(f"{len(regras)} regras ({len(presumidas)} presumidas), {len(medicoes)} medições")
    for e in erros:
        print("ERRO:", e)
    for t, e, r in contradicoes:
        print(f"CONTRADIÇÃO: {t} ← {e} (razão {r})")
    if erros or contradicoes:
        print("geração interrompida")
        return 1
    if "--verificar" in argv:
        return 0

    br, nbr = gerar_tsv(regras, "brasileirismo", CABECALHO_BR,
                        lambda r: "\t".join([r["padrao"], r["alternativa"], r["nivel"]] + ([r["nota"]] if r.get("nota") else [])))
    ia, nia = gerar_tsv(regras, "marca-ia", CABECALHO_IA,
                        lambda r: "\t".join([r["padrao"], str(r.get("limite", 0)), r["sugestao"]]))
    for d in DESTINOS:
        if os.path.isdir(d):
            open(os.path.join(d, "brasileirismos.tsv"), "w", encoding="utf-8", newline="\n").write(br)
            open(os.path.join(d, "vocabulario_ia.tsv"), "w", encoding="utf-8", newline="\n").write(ia)
            print(f"escrito em {os.path.abspath(d)}: {nbr} brasileirismos, {nia} marcas de IA")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
