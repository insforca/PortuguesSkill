---
name: escrita-pt-pt
description: Norma de escrita em português europeu (PT-PT) com a ortografia ANTERIOR ao Acordo Ortográfico de 1990 (acção, óptimo, actual, director, Janeiro, pára, fim-de-semana). Usar SEMPRE que se escreva, reescreva, traduza ou reveja qualquer texto em português para o utilizador — ensaios, trabalhos académicos, teses, recensões, contos, novelas, romances, livros, cartas, e-mails. Usar também por cima de skills calibradas para PT-BR (humanizar, paralelismo-negativo, better-portuguese, pesquisador-br): o léxico, a sintaxe e a ortografia desta skill prevalecem. Gatilhos — escrever em português, ensaio, trabalho académico, romance, novela, conto, rever texto, converter para a ortografia antiga, desfazer o Acordo, pré-AO90.
metadata:
  author: insforca
  version: "1.0.0"
  license: MIT
  repository: https://github.com/insforca/PortuguesSkill
---

# Escrita em português europeu (ortografia pré-AO90)

Todo o texto em português que produzires para o utilizador segue três camadas, por esta ordem de prioridade:

1. **Ortografia anterior ao AO90** (norma de 1945, como se escrevia em Portugal até 2009–2015). Ver `references/ortografia-pre-ao90.md`.
2. **Português europeu** no léxico, na sintaxe e na colocação dos pronomes. Ver `references/lexico-sintaxe-pt-pt.md`.
3. **Convenções do género** do texto (académico, ensaístico ou literário), descritas abaixo.

Quando outra skill instalada estiver calibrada para PT-BR (`humanizar`, `humanizer-pt-br`, `better-portuguese`, `pesquisador-br`), aplica as regras de *estilo* dela, mas nunca o vocabulário, a sintaxe ou a ortografia brasileira: esta skill prevalece. A `paralelismo-negativo` é neutra e pode ser usada sem adaptação.

## Regras inegociáveis

- **Nunca** escrever na grafia do AO90 (ação, ótimo, atual, diretor, janeiro, para [verbo], fim de semana, hei de).
- **Nunca** usar o gerúndio progressivo brasileiro ("estou fazendo"); em PT-PT é "estou a fazer".
- **Nunca** inventar citações, referências, páginas ou DOI. Se a fonte não estiver verificada, dizê-lo e marcar `[REFERÊNCIA A CONFIRMAR]`.
- Na dúvida sobre a grafia pré-AO90 de uma palavra, **não adivinhar**: assinalar ao utilizador e sugerir a consulta do Dicionário Priberam (opção "grafia antes do Acordo") ou do Vocabulário Ortográfico do Português.
- Ao converter um texto em AO90 para a grafia antiga, não "corrigir" palavras cuja consoante sempre se pronunciou e se manteve igual (facto, pacto, ficção, convicção, egípcio, rapto, núpcias). E nunca transformar "fato" em "facto" sem ver o sentido: em PT-PT "fato" é vestuário.

## Trabalhos académicos (Portugal)

- **Estilo de citação:** perguntar sempre qual o exigido pelo docente, curso ou revista. Em Portugal os mais comuns são **APA 7.ª ed.** (Ciências Sociais, Psicologia, Educação), **Chicago — notas e bibliografia** (História, Filosofia, Letras, Artes), **MLA** (Estudos Literários) e a **NP 405** (norma portuguesa de referências bibliográficas). Não usar ABNT, que é brasileira.
- Na falta de indicação, em Letras/Humanidades propor Chicago (notas de rodapé); nas Ciências Sociais, APA.
- **Registo:** impessoal ou primeira pessoa do plural ("procuraremos demonstrar"), conforme a área; a primeira pessoa do singular é aceitável em ensaio e em Humanidades, se o docente a admitir.
- **Estrutura típica:** Introdução (problema, pergunta, hipótese/tese, metodologia, plano), Desenvolvimento por capítulos, Conclusão (resposta à pergunta, limites, pistas futuras), Bibliografia, Anexos.
- **Denominações portuguesas:** "dissertação de mestrado", "tese de doutoramento" (não "doutorado"), "relatório de estágio", "trabalho final", "recensão", "orientador(a)", "arguente", "provas públicas", "unidade curricular", "docente", "licenciatura".
- Resumo + palavras-chave em português e *Abstract* + *Keywords* em inglês, quando exigido.

## Ensaio

- Uma tese clara logo no início; cada parágrafo avança o argumento, não o recapitula.
- Voz própria, primeira pessoa permitida, digressão controlada — a tradição de Montaigne, de Eduardo Lourenço, de António Sérgio.
- Citações curtas e integradas; a fonte em nota ou entre parênteses, consoante o estilo escolhido.

## Ficção (contos, novelas, romances)

- Diálogos com **travessão** (—), à maneira portuguesa, não com aspas: `— Vens amanhã? — perguntou ela.`
- Registo oral português nas falas: "tu" entre íntimos, "você" com cautela (pode soar distante ou rude), formas de tratamento ("o senhor", "a senhora", "a menina", "o doutor").
- Léxico, topónimos, comida, objectos e hábitos portugueses quando a acção se passa em Portugal; não misturar realidades brasileiras sem intenção.
- Trabalhar por cenas e marcos do enredo; as skills `writing-beats`, `writing-shape` e `writing-fragments` ajudam na estrutura, e esta skill fixa a língua.
- Manter uma "bíblia" do livro (personagens, cronologia, lugares, registo de cada voz) num ficheiro à parte para preservar a coerência entre capítulos.

## Revisão final (checklist)

Antes de entregar, verificar:

1. Grafia pré-AO90: consoantes mudas (c/p), acentos diferenciais, hífenes, maiúsculas em meses e estações.
2. Léxico e sintaxe PT-PT: "a + infinitivo", ênclise, vocabulário europeu.
3. Sem tiques de IA: correr mentalmente a lista da `humanizar` e a `paralelismo-negativo`.
4. Citações e referências coerentes com o estilo escolhido e todas verificáveis.
