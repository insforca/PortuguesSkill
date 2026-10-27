"""Prepara uma consulta MANUAL ao Corpus do Português (corpus NOW, 2012-2019) para tirar uma dúvida.

O site não permite acesso automático: este script não faz pedidos nenhuns. Imprime a expressão
pronta a colar (com as contracções separadas, como o corpus as guarda), os passos a seguir e o
modelo da nota de medição para o cofre (conhecimento/Medições/).

Uso:
  python consulta_cdp.py "tela do celular" ["ecrã do telemóvel" ...]
"""
import re
import sys

# Contracções que o corpus guarda separadas («do» -> «de o»). Ordem: as mais longas primeiro.
CONTRACCOES = {
    "àquela": "a aquela", "àquele": "a aquele", "àquilo": "a aquilo",
    "daquela": "de aquela", "daquele": "de aquele", "daquilo": "de aquilo", "daqui": "de aqui",
    "naquela": "em aquela", "naquele": "em aquele", "naquilo": "em aquilo",
    "deste": "de este", "desta": "de esta", "destes": "de estes", "destas": "de estas",
    "desse": "de esse", "dessa": "de essa", "disso": "de isso", "disto": "de isto",
    "neste": "em este", "nesta": "em esta", "nesse": "em esse", "nessa": "em essa",
    "nisso": "em isso", "nisto": "em isto", "dele": "de ele", "dela": "de ela", "deles": "de eles",
    "delas": "de elas", "nele": "em ele", "nela": "em ela",
    "num": "em um", "numa": "em uma", "nuns": "em uns", "numas": "em umas",
    "dum": "de um", "duma": "de uma",
    "do": "de o", "da": "de a", "dos": "de os", "das": "de as",
    "no": "em o", "na": "em a", "nos": "em os", "nas": "em as",
    "pelo": "por o", "pela": "por a", "pelos": "por os", "pelas": "por as",
    "à": "a a", "às": "a as",
}


def separar(expr):
    return " ".join(CONTRACCOES.get(w.lower(), w) for w in expr.split())


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if not argv:
        print(__doc__)
        return 2
    print("Corpus do Português — consulta manual (não automatizar: o site bloqueia e proíbe)")
    print("1. Abrir https://www.corpusdoportugues.org/now/ com sessão iniciada.")
    print("2. Carregar em «Chart», colar a expressão abaixo e carregar em «See frequency by section».")
    print("3. Carregar em «(BY COUNTRY)» e anotar a coluna «PER MIL» de Portugal e do Brasil.\n")
    for expr in argv:
        q = separar(expr)
        nota = re.sub(r'[\\/:*?"<>|#^\[\]]', "-", f"NOW — {expr}")
        print(f"«{expr}»  →  colar:  {q}")
        print(f"   nota para o cofre: conhecimento/Medições/{nota}.md")
        print("   ---\n   tipo: medicao\n   fonte: '[[NOW (Corpus do Português)]]'")
        print(f"   forma: '{expr}'\n   por_milhao_pt: \n   por_milhao_br: \n   razao_br_pt: ")
        print("   metodo: 'consulta manual, vista Chart por país'\n   data: \n   ---\n")
    print("Depois de criar a nota, ligá-la à regra (propriedade «evidencia») e correr ferramentas/gerar_dados.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
