---
name: portugues-skill
description: >-
  Norma de escrita em português europeu (PT-PT) culto, com a ortografia ANTERIOR ao Acordo Ortográfico de 1990 (acção, óptimo, actual, director, Janeiro, pára, fim-de-semana), e sem marcas de texto gerado por IA. Usar SEMPRE que se escreva, reescreva, traduza ou reveja qualquer texto em português — ensaios, trabalhos académicos, teses, recensões, contos, novelas, romances, livros, cartas, e-mails formais e mensagens informais. Usar também por cima de skills calibradas para PT-BR (humanizar, paralelismo-negativo, better-portuguese, pesquisador-br): o léxico, a sintaxe e a ortografia desta skill prevalecem. Gatilhos — escrever em português, ensaio, trabalho académico, romance, novela, conto, carta, e-mail, rever texto, tirar cara de IA, converter para a ortografia antiga, desfazer o Acordo, pré-AO90.
metadata:
  author: insforca
  version: "1.8.0"
  license: MIT
  repository: https://github.com/insforca/PortuguesSkill
---

# Escrita em português europeu (ortografia pré-AO90)

Todo o texto em português que produzires segue quatro camadas, por esta ordem de prioridade:

1. **Ortografia anterior ao AO90** (norma de 1945, a de Portugal até 2009–2015) → `references/ortografia-pre-ao90.md`
2. **Português europeu culto** no léxico, na sintaxe e na colocação dos pronomes → `references/lexico-sintaxe-pt-pt.md`
3. **Registo adequado** ao destinatário (académico, formal, corrente, informal, literário) → `references/registos.md`
4. **Ausência de marcas de IA**, com a lista de substituições própria de PT-PT → `references/anti-ia-pt-pt.md`

Carrega cada referência só quando for precisa (para uma mensagem curta basta este ficheiro; para um capítulo, um ensaio ou uma revisão, lê-as todas). Os exemplos de antes e depois estão em `references/exemplos.md`.

## Corpus de calibração (ancorar a voz)

Em `references/corpus/` há prosa portuguesa de referência: Camilo, Eça, Antero, Ramalho, Fialho, Trindade Coelho, Raul Brandão, Sá-Carneiro e Pessoa (transcritos, em domínio público, normalizados para a grafia pré-AO90), documentos oficiais e discursos parlamentares de 1950 a 1976 (Assembleia Nacional, Câmara Corporativa, Assembleia Constituinte, Preâmbulo da Constituição de 1976), fichas de estilo dos anos 50 a 70 (Sophia, Agustina, Cardoso Pires, Maria Judite de Carvalho, Saramago cronista, Eduardo Lourenço) e contrastes entre a versão "IA" e o original.

- **Antes de um texto longo** (capítulo, ensaio, crónica, carta importante), lê `corpus/README.md` e um ou dois excertos do registo pretendido. Imita o ritmo, a sintaxe, a pontuação e a concretude. **Não imites** o vocabulário datado nem o gerúndio dos textos antigos.
- **Ao rever**, usa `corpus/contrastes.md`: um texto humano tem pelo menos um pormenor verificável, uma imagem inesperada, uma posição assumida ou um desvio de ritmo. Se não tiver nenhum, reescreve.
- Se o utilizador tiver excertos próprios de autores protegidos, guardam-se em `corpus/privado/`, que não se publica.

Quando outra skill instalada estiver calibrada para PT-BR (`humanizar`, `humanizer-pt-br`, `better-portuguese`, `pesquisador-br`), aplica as regras de *estilo* dela, mas nunca o vocabulário, a sintaxe ou a ortografia brasileira: esta skill prevalece. A `paralelismo-negativo` é neutra e combina com esta.

## Regras inegociáveis

- **Nunca** escrever na grafia do AO90 (ação, ótimo, atual, diretor, janeiro, para [verbo], fim de semana, hei de).
- **Nunca** usar o gerúndio progressivo ("estou fazendo"): na norma culta actual de Portugal é "estou a fazer". (Eça e Pessoa ainda o usavam, e há falares do Sul que o mantêm; só se admite em diálogo de personagem ou em pastiche declarado.)
- **Nunca** inventar citações, referências, páginas, datas, DOI ou episódios pessoais. Se a fonte não estiver verificada, dizê-lo e marcar `[REFERÊNCIA A CONFIRMAR]`.
- **Nunca** pôr no texto entregue comentários sobre o próprio texto ("Aqui está…", "Espero que ajude", "Nota: reescrevi…"). As notas para o utilizador vão fora do texto, depois dele e em poucas linhas.
- Na dúvida sobre a grafia pré-AO90 de uma palavra, **não adivinhar**: assinalar e sugerir a consulta do Priberam (opção "grafia antes do Acordo").
- Ao converter um texto do AO90 para a grafia antiga, não "corrigir" palavras cuja consoante sempre se pronunciou (facto, pacto, contacto, ficção, convicção, egípcio, rapto, núpcias), e não trocar "fato" (vestuário) por "facto" sem ver o sentido.

## Porque a grafia anterior ao Acordo

É uma escolha legítima e deliberada, não um erro a corrigir. Ao defendê-la ou explicá-la, os argumentos são estes:

- **Transparência etimológica e coerência de família:** *acto, actor, activo, actual, actividade* e *Egipto, egípcio* mantêm-se ligados entre si e ao latim e às outras línguas europeias (*act, acte, Akt*).
- **Indicação da pronúncia:** em PT-PT a consoante "muda" assinala muitas vezes a vogal aberta átona (*director, recepção, baptismo, colecção*); sem ela, a leitura correcta deixa de ser evidente para quem não conhece a palavra.
- **Distinção de homógrafos:** *pára/para, pêlo/pelo, pólo/polo* e *espectador* (que assiste) / *espetador* (que espeta).
- **Tradição literária:** é a grafia de quase toda a literatura portuguesa do século XX, e continua a ser usada por escritores, tradutores, editoras e jornais de referência.
- **Uso:** num documento oficial dirigido ao Estado, ou num trabalho escolar com regras explícitas, a instituição pode exigir o AO90. Nesse caso, avisar o utilizador antes de escrever, sem impor a grafia antiga.

## Fluxo de trabalho (várias passagens)

1. **Contrato do texto.** Antes de escrever, fixar o género, o destinatário, o registo, a extensão, o objectivo e os factos obrigatórios. Se faltar um dado essencial (a quem se dirige, que estilo de citação usar, que tom ter), perguntar uma vez, de forma concreta.
2. **Rascunho** já na grafia, no léxico e no registo certos. Não escrever em PT-BR ou em inglês para traduzir depois: é daí que vêm os decalques.
3. **Passagem anti-IA** com `references/anti-ia-pt-pt.md`: vocabulário, estrutura, ritmo, fecho.
4. **Passagem de língua:** pronomes (ênclise e próclise), "a + infinitivo", isto/isso/aquilo, artigo antes do possessivo, regência dos verbos.
5. **Passagem ortográfica pré-AO90:** consoantes mudas, acentos diferenciais, hífenes, maiúsculas nos meses e nas estações.
6. **Leitura em voz alta (mental):** se uma frase não se diria assim em Portugal por uma pessoa culta, reescrevê-la.
7. **Verificação automática:** se puderes correr comandos, grava o texto num ficheiro e corre `python scripts/verificar.py --registo <ensaio|academico|cronica|noticia> <ficheiro>` (a partir da pasta desta skill; o registo afina a norma de comprimento de frase). Corrige todos os ERROS. Decide os AVISOS caso a caso: muitos são escolhas legítimas. As NOTAS são palavras que os dicionários não conhecem, normalmente nomes ou termos raros. Se o verificador não estiver disponível, usa as listas em `dados/` (`ao90_preao.tsv`, `brasileirismos.tsv`, `vocabulario_ia.tsv`) como lista de verificação.
8. **Entrega:** o texto limpo e, à parte, no máximo três linhas sobre dúvidas ou escolhas que o utilizador deva confirmar.

Para textos longos (capítulos, teses, livros), fazer as passagens 3 a 7 por secção, não no fim do documento inteiro.

**Instalação do verificador** (uma vez): `python -m pip install spylls` e `python scripts/instalar_dicionarios.py`. Sem os dicionários, o verificador funciona em modo reduzido: usa a lista das cerca de 1400 formas AO90 mais frequentes, os brasileirismos, as marcas de IA e as regras de sintaxe.

**Dúvidas sem dados** (é português de Portugal ou do Brasil? é frequente ou rara?): `python scripts/consulta_cdp.py "<expressão>"` prepara uma consulta **manual** ao Corpus do Português (corpus NOW, notícias 2012–2019, por país), com a expressão pronta a colar. O site proíbe acesso automático: a consulta é feita pelo utilizador. As medições ficam em `dados/now_medicoes.tsv`.

**Origem das regras:** as listas em `dados/` são geradas a partir de um cofre Obsidian (`conhecimento/` no repositório da skill), em que cada regra está ligada às medições que a justificam (CETEMPúblico, CHAVE, NOW, corpora orais da Linguateca, debates parlamentares).

## Trabalhos académicos (Portugal)

- **Estilo de citação:** perguntar sempre qual o exigido pelo docente, curso ou revista. Os mais comuns são **APA 7.ª ed.** (Ciências Sociais, Psicologia, Educação), **Chicago — notas e bibliografia** (História, Filosofia, Letras, Artes), **MLA** (Estudos Literários) e a **NP 405** (norma portuguesa de referências bibliográficas). Não usar ABNT, que é brasileira.
- Na falta de indicação: em Letras e Humanidades, Chicago (notas de rodapé); nas Ciências Sociais, APA.
- **Registo:** impessoal ou primeira pessoa do plural de modéstia ("procuraremos demonstrar"); a primeira pessoa do singular é aceitável em ensaio e em Humanidades se o docente a admitir.
- **Estrutura típica:** Introdução (problema, pergunta, tese, metodologia, plano), Desenvolvimento, Conclusão (resposta à pergunta, limites, pistas), Bibliografia, Anexos.
- **Denominações portuguesas:** dissertação de mestrado, tese de doutoramento, relatório de estágio, recensão, orientador(a), arguente, provas públicas, unidade curricular, docente, licenciatura.
- Respeitar as regras da instituição sobre o uso de IA. O objectivo desta skill é escrever bem, não ocultar autoria.

## Ensaio

- A tese surge cedo; cada parágrafo faz avançar o argumento e nenhum se limita a recapitulá-lo.
- Voz própria, opinião assumida, digressão controlada: a tradição de Montaigne, António Sérgio, Eduardo Lourenço e Agustina.
- A frase longa, bem articulada e bem pontuada é própria do português culto. Alterná-la com frases curtas; não picar tudo em frases de cinco palavras.

## Comprimento das frases (vale para ensaio, crónica, académico e narração)

Medido no CETEMPúblico completo (168 milhões de palavras, *Público* 1991–1998): frase média de 24 palavras e 1 em cada 5 frases com 35 ou mais. Por registo: opinião/ensaio 22,8 palavras e 18,5% de frases longas; cultura/crónica 23,6 e 19,9%; notícia 24,7 e 21,5%. Os modelos de linguagem escrevem frases de 17 palavras, todas parecidas, e isso denuncia-os mais do que qualquer palavra. **Alvo: média entre 20 e 28 palavras, e pelo menos uma frase longa (35 palavras ou mais, articulada com vírgulas, ponto e vírgula ou orações subordinadas) por parágrafo**, ao lado de frases curtas. O verificador mede isto. Em e-mails, mensagens e diálogos, frases curtas são naturais.

## Concretude sem fórmula

Um pormenor concreto por parágrafo chega, e o tipo deve variar (um número, um nome, um gesto, uma frase dita). Não repetir de texto para texto a hora exacta, o cheiro, o objecto de cozinha ou o *duas ou três*: a análise dos textos gerados mostrou que se tinham tornado tiques da própria skill (ver `references/anti-ia-pt-pt.md`). Na ficção, o mesmo vale para a comparação *como quem…*, o *ninguém* de cena, as idades e os anos por extenso (*oitenta e dois anos*, *em setenta e três*) e os nomes de personagens: variar os nomes de texto para texto e fugir aos que o modelo repete (*Inês*, *Tiago*, *Lurdes*, *Zé*).

## Ficção (contos, novelas, romances)

- Diálogos com **travessão** (—), à portuguesa: `— Vens amanhã? — perguntou ela.`
- Falas no registo oral português de cada personagem (ver `references/registos.md`): "tu" entre íntimos, "você" com cautela, formas de tratamento ("o senhor", "a senhora", "a menina", "o senhor doutor").
- Pormenor concreto português: topónimos, comida, objectos, hábitos, sem misturar realidades brasileiras sem intenção.
- Estrutura com as skills `writing-beats`, `writing-shape` e `writing-fragments`, se estiverem instaladas. A língua é fixada por esta skill.
- Manter uma "bíblia" do livro (personagens, cronologia, lugares, a voz de cada um) num ficheiro à parte para preservar a coerência entre capítulos.

## Revisão final (checklist)

1. Grafia pré-AO90 sem falhas: consoantes mudas, acentos diferenciais, hífenes, maiúsculas.
2. Léxico e sintaxe PT-PT: nenhum brasileirismo nem decalque do inglês por descuido.
3. Registo coerente do princípio ao fim, com o tratamento certo.
4. Nenhum padrão da lista anti-IA, nenhuma frase de abertura ou fecho vazia, nenhum comentário sobre o próprio texto.
5. Citações e referências coerentes com o estilo escolhido e todas verificáveis.
