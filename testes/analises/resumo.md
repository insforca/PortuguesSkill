# Resumo dos testes (Outubro de 2026)

Modelo: Claude Opus 5.5 através do Claude Code em modo não interactivo (`claude -p`), numa pasta neutra.
«Sem a skill» = ferramenta Skill bloqueada (`--disallowedTools Skill`); sem isso, a skill instalada
era activada na mesma e a linha de base ficava contaminada.

## Verificador (erros e avisos por mil palavras)

| conjunto | textos | palavras | erros | erros/1000 | avisos/1000 |
|---|---|---|---|---|---|
| bateria normal, sem a skill | 20 | 4829 | 31 | 6,4 | 9,1 |
| bateria normal, v1.5 | 20 | 4137 | 0 | 0,0 | 4,8 |
| bateria normal, v1.6 | 20 | 4367 | 0 | 0,0 | 3,0 |
| pedidos difíceis, sem a skill | 10 | 3331 | 63 | 18,9 | 13,2 |
| pedidos difíceis, v1.6 | 10 | 2620 | 0 | 0,0 | 5,0 |
| bateria normal, v1.8 | 20 | 4193 | 0 | 0,0 | 2,6 |
| pedidos difíceis, v1.8 | 10 | 2596 | 0 | 0,0 | 4,6 |

Sem a skill, o modelo escreve PT-PT com o AO90 (*atual*, *ação*, *projeto*, *julho*) e com deslizes brasileiros (*Me informe*); nos pedidos difíceis (converter um texto brasileiro, rever um parágrafo AO90, traduzir do inglês) a taxa de erros triplica. Com a skill, zero erros nos dois conjuntos.

## Comprimento das frases (pedidos 01–08: académico, ensaio, crónica)

| | média | desvio | frases com 35+ palavras |
|---|---|---|---|
| *Público* (CETEMPúblico) | 24,0 | 14,7 | 19% |
| sem a skill | 16,8 | 8,8 | 5% |
| v1.5 | 17,5 | 8,3 | 4% |
| **v1.6** (com alvo explícito) | **22,2** | **10,9** | **17%** |
| v1.8 (normas por registo) | 22,9 | — | 15% |

O comprimento curto e uniforme das frases era a assinatura de IA mais forte que encontrámos; a v1.6 aproxima-se do perfil do *Público*.

## Estilometria (Delta de Burrows, perfil de imprensa; 86% de acerto PT/BR em validação)

| conjunto | margem PT (positivo = mais perto do Público) | textos mais perto de PT |
|---|---|---|
| sem a skill | −0,06 | 3/20 |
| v1.5 | −0,06 | 4/20 |
| v1.6 | **+0,02** | **8/20** |
| v1.8 | 0,00 | **10/20** |

Os números absolutos são baixos porque metade dos pedidos são cartas, mensagens e ficção, que se afastam do jornalismo por natureza. Interessa a comparação entre versões.

## Tiques descobertos automaticamente (`ferramentas/descobrir_tiques.py`)

- Contra o CETEMPúblico, nos textos sem a skill: *ao mesmo tempo*, *se quiseres, posso…*, *venho por este meio*, *desde já*, comentários como *cerca de 330 palavras*.
- Contra o CETEMPúblico, nos textos com a skill (v1.5): tiques criados pela própria skill — a hora exacta, o cheiro, *duas ou três*, *devagar*, objectos de cozinha.
- Contra prosa literária portuguesa (Project Gutenberg, comparação neutra à grafia), na ficção com a skill: *como quem…*, *ninguém*, idades e anos por extenso (*oitenta e…*), encenação espacial (*ao lado*, *por cima*) e nomes repetidos (*Inês*, *Tiago*, *Lurdes*).

Todos passaram para `dados/vocabulario_ia.tsv` e para as regras da skill (v1.6 e v1.7).

## Resultados negativos (também contam)

- **Perfil estilométrico literário PT/BR (1840–1920)**: 57,5% de acerto em livros de validação, abaixo do palpite fixo. No século XIX a prosa culta dos dois países era quase igual; não é usado.
- **Regra «pra/tá = erro»**: errada para fala portuguesa informal (*tá bem*, *pra onde vais*); passou a aviso. O brasileirismo verdadeiro é *tô* (em Portugal, *tou*).

## Leitura manual

- D08 (citações em APA): o modelo não inventou citações; marcou *[CITAÇÃO A CONFIRMAR]* e deu referências correctas.
- D01 (conversão de PT-BR): *equipa*, *registo*, *utilizadores*, *controlo*, *autocarro*, *Liguem-me*.
- A qualidade da prosa e a adequação do registo continuam a exigir leitura humana.

## v1.8 (Outubro de 2026)

- Fontes novas: CETEMPúblico completo (168 M palavras; normas de frase por secção), debates parlamentares 1945–2011 (408 sessões), corpora orais da Linguateca (Museu da Pessoa PT/BR, CORDIAL-SIN, C-Oral-Brasil).
- Achado principal: nos discursos parlamentares o gerúndio progressivo cai de 63% (anos 40) para 1% (anos 90) — a norma actual de «estar a + infinitivo» fixou-se entre os anos 60 e 80 (`parlamento.md`).
- Ficção da v1.8: desapareceram os tiques medidos na v1.6 (*como quem*, nomes repetidos, *cheira*, *devagar*).
- Regras e medições passam a viver no cofre Obsidian `Portuguese Skill/` (fonte de verdade; `ferramentas/gerar_dados.py`).

## Linha de base extra (Outubro de 2026)

42 textos novos sem a skill (14 588 palavras; `pedidos_base_extra.tsv`): 5,8 erros e 8,2 avisos por mil palavras, quase todos de grafia AO90. Com 23 mil palavras de referência IA, quatro marcas presumidas passaram a medidas: *desafios* (5× a prosa portuguesa), *ecossistemas* (16×), *não é… é* (6×) e *potencializar* (25×). Das 20 que ficam presumidas, 13 nunca aparecem nos textos do Claude (*explorar*, *mergulhar*, *tapeçaria*, *sinergias*…). Vêm de listas feitas para outros modelos. *Ou seja*, *por um lado* e *fundamental* aparecem até menos do que no Público e no Parlamento. Pormenor em `regras_medidas.md`.

## Bateria extra v1.8 e teste cego (Outubro de 2026)

- Os 42 pedidos extra com a v1.8: 0 erros e 1,6 avisos por mil palavras (sem a skill: 5,8 e 7,7). Nove avisos de brasileirismo eram falsos positivos (*arquivo distrital*, *baixar o preço*, *toda a gente*); os padrões passaram a exigir o contexto brasileiro. Com o padrão estreito, *a gente* pronome dá Folha ÷ Público = 7 (antes 1,3, contestada) e *legal* = fixe dá 8,3.
- Tiques novos, criados pela própria skill: *convém* (8,6 por 10 mil palavras; sem a skill 2,0; Público 0,2), *parece-me* e *quem* como sujeito genérico. Entraram no verificador e no SKILL.md (`tiques_v1.8_extra.md`).
- Teste cego (`ferramentas/preparar_teste_cego.py`): 10 excertos do Público (opinião e cultura, 1993–1998) e 10 textos da v1.8 emparelhados (mesmo género, assunto, época e tamanho; `pedidos_cego.tsv`). A página fica em `.cache/teste_cego/` (fora do git). Resultado da leitura humana: por fazer.
