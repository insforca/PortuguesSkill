"""Gera o Google Apps Script que cria o teste cego público num Google Forms.

Junta os excertos humanos de autores em domínio público (testes/teste_cego_publico/humanos.json,
grafia actualizada para a norma anterior ao AO90) com os textos emparelhados gerados pela skill
(testes/resultados/cego-publico-v1.8, pedidos em testes/pedidos_cego_publico.tsv), baralha-os e
dá a cada um um código neutro (T01-T20).

Saída em .cache/teste_cego_publico/ (fora do git até o estudo acabar, para a chave não circular):
  criar_formulario.gs   colar em script.google.com e executar a função criarTeste
  chave.tsv             código, id de origem, H/I

Uso:
  python criar_formulario_cego.py [--semente 5]
"""
import json
import os
import random
import re
import sys

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
HUMANOS = os.path.join(REPO, "testes", "teste_cego_publico", "humanos.json")
IA = os.path.join(REPO, "testes", "resultados", "cego-publico-v1.8")
DESTINO = os.path.join(REPO, ".cache", "teste_cego_publico")

TITULO = "Humano ou máquina? Teste de leitura em português europeu"
DESCRICAO = (
    "Vinte excertos de prosa portuguesa no estilo de 1870 a 1920 (crónica, viagens, memórias, ensaio e conto). "
    "Metade foi escrita por autores portugueses dessa época; a outra metade foi gerada por inteligência artificial "
    "a imitar o mesmo género, assunto e época. Todos os textos estão na ortografia portuguesa anterior ao Acordo "
    "Ortográfico de 1990 (nos textos antigos, a grafia foi actualizada).\n\n"
    "Para cada excerto, diga se o acha escrito por uma pessoa ou por inteligência artificial. Não há respostas "
    "erradas por falta de cultura literária: interessa a sua primeira impressão. Demora cerca de 15 minutos.\n\n"
    "As respostas são anónimas e servem um estudo sobre a escrita de inteligência artificial em português "
    "europeu. Não é pedido nome nem e-mail.")
CONFIRMACAO = (
    "Obrigado pela participação. Os excertos humanos são de Raul Brandão, Ramalho Ortigão, Eça de Queirós, "
    "Wenceslau de Moraes, Fialho de Almeida, Jaime de Magalhães Lima, Maria Amália Vaz de Carvalho, "
    "Ana de Castro Osório, Alberto Pimentel e Teixeira de Queiroz (obras em domínio público, Project Gutenberg). "
    "Pedimos que não divulgue as respostas a quem ainda não participou.")
PERFIL = [
    ("Onde aprendeu o português?", ["Portugal", "Brasil", "Angola", "Moçambique", "Cabo Verde",
                                    "Outro país de língua portuguesa", "Não é a minha língua materna"]),
    ("Idade", ["Menos de 25", "25 a 39", "40 a 59", "60 ou mais"]),
    ("Com que frequência lê literatura portuguesa anterior a 1950?", ["Frequentemente", "Às vezes", "Raramente ou nunca"]),
    ("Com que frequência usa ferramentas de inteligência artificial (ChatGPT, Claude, Gemini…)?",
     ["Todas as semanas", "Às vezes", "Nunca"]),
]

GS = """// Cria o teste cego no Google Forms. Colar em https://script.google.com (Novo projecto),
// guardar e executar a função criarTeste. Os endereços do formulário aparecem no registo de execução.
var TITULO = __TITULO__;
var DESCRICAO = __DESCRICAO__;
var CONFIRMACAO = __CONFIRMACAO__;
var PERFIL = __PERFIL__;
var TEXTOS = __TEXTOS__;

function criarTeste() {
  var form = FormApp.create(TITULO);
  form.setDescription(DESCRICAO);
  form.setIsQuiz(true);
  form.setCollectEmail(false);
  form.setShuffleQuestions(true);  // baralha dentro de cada secção
  form.setProgressBar(true);
  form.setConfirmationMessage(CONFIRMACAO);

  PERFIL.forEach(function (p) {
    form.addMultipleChoiceItem().setTitle(p[0]).setChoiceValues(p[1]).setRequired(true);
  });

  form.addPageBreakItem().setTitle('Os excertos')
    .setHelpText('Leia cada excerto e escolha uma resposta. A ordem é diferente para cada pessoa.');
  TEXTOS.forEach(function (t) {
    var item = form.addMultipleChoiceItem();
    item.setTitle('Excerto ' + t.codigo + ': quem o escreveu?');
    item.setHelpText(t.texto);
    item.setChoices([
      item.createChoice('Uma pessoa', t.origem === 'H'),
      item.createChoice('Inteligência artificial', t.origem === 'I')
    ]);
    item.setPoints(1);
    item.setRequired(true);
  });

  form.addPageBreakItem().setTitle('Para terminar');
  form.addParagraphTextItem()
    .setTitle('Que pistas usou para decidir? (opcional)')
    .setHelpText('Palavras, pontuação, ritmo, assunto, o que for.');

  Logger.log('Endereço para responder: ' + form.getPublishedUrl());
  Logger.log('Endereço para editar: ' + form.getEditUrl());
}
"""


def limpar(texto):
    """Os textos já foram pedidos com o tamanho do par humano: só sai a formatação Markdown."""
    pars = [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip() and not p.strip().startswith("#")]
    return "\n\n".join(re.sub(r"(\*{1,2}|_)([^*_\n]+)\1", r"\2", p) for p in pars)


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    semente = int(argv[argv.index("--semente") + 1]) if "--semente" in argv else 5
    with open(HUMANOS, encoding="utf-8") as f:
        itens = [(h["id"], "H", h["texto"]) for h in json.load(f)]
    for nome in sorted(os.listdir(IA)):
        if nome.endswith(".md") and nome != "avaliacao.md":
            with open(os.path.join(IA, nome), encoding="utf-8") as f:
                itens.append((os.path.splitext(nome)[0], "I", limpar(f.read())))
    random.Random(semente).shuffle(itens)
    textos = [{"codigo": f"T{k:02d}", "origem": o, "texto": t} for k, (_, o, t) in enumerate(itens, 1)]
    js = lambda v: json.dumps(v, ensure_ascii=False)
    gs = (GS.replace("__TITULO__", js(TITULO)).replace("__DESCRICAO__", js(DESCRICAO))
          .replace("__CONFIRMACAO__", js(CONFIRMACAO)).replace("__PERFIL__", js(PERFIL))
          .replace("__TEXTOS__", json.dumps(textos, ensure_ascii=False, indent=1)))
    os.makedirs(DESTINO, exist_ok=True)
    with open(os.path.join(DESTINO, "criar_formulario.gs"), "w", encoding="utf-8") as f:
        f.write(gs)
    with open(os.path.join(DESTINO, "chave.tsv"), "w", encoding="utf-8") as f:
        f.write("codigo\tid\torigem\n")
        for t, (i, o, _) in zip(textos, itens):
            f.write(f"{t['codigo']}\t{i}\t{o}\n")
    for t, (i, o, txt) in zip(textos, itens):
        print(t["codigo"], i, o, len(txt.split()), "palavras")
    print("script:", os.path.abspath(os.path.join(DESTINO, "criar_formulario.gs")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
