# PortuguesSkill — `portugues-skill`: escrita em português europeu (pré-AO90)

Skill para agentes de IA (Claude Code, Cursor, Codex e outros) que escrevem em **português europeu** com a **ortografia anterior ao Acordo Ortográfico de 1990**: acção, óptimo, actual, director, Janeiro, pára, pêlo, fim-de-semana, hei-de.

Até agora, todas as skills de português no ecossistema eram calibradas para o português do Brasil. Esta preenche essa lacuna.

## O que inclui

- **Ortografia pré-AO90** — consoantes mudas, acentos diferenciais, hífenes, maiúsculas em meses e estações, com a lista das palavras que *não* se alteram na conversão (facto, contacto, ficção…).
- **Léxico e sintaxe de Portugal** — "estar a + infinitivo", ênclise e próclise, mesóclise, vocabulário europeu (ecrã, telemóvel, doutoramento, unidade curricular), aspas « ».
- **Convenções por género** — trabalhos académicos em Portugal (APA, Chicago, MLA, NP 405; nunca ABNT), ensaio e ficção (diálogo com travessão, formas de tratamento).
- **Anti-IA próprio de PT-PT** — tabela de trocas de vocabulário (crucial, impactar, jornada, desafiador, mergulhar…), padrões de estrutura e de ritmo, decalques do inglês e brasileirismos que denunciam texto gerado.
- **Registos da fala culta de Portugal** — académico, formal (Exmo. Senhor, Com os melhores cumprimentos), corrente, informal e literário, com a tabela de tratamento (tu, você, o senhor, V. Ex.ª).
- **Defesa da grafia anterior ao Acordo** — os argumentos etimológicos, fonéticos e literários.
- **Fluxo de revisão em várias passagens** e exemplos de antes e depois para cada registo.
- **Corpus de calibração** — excertos de Camilo, Eça, Antero, Ramalho, Fialho, Trindade Coelho, Raul Brandão, Sá-Carneiro e Pessoa (domínio público, normalizados para a grafia pré-AO90), com notas de estilo; documentos oficiais e discursos parlamentares de 1950 a 1976 (Assembleia Nacional, Câmara Corporativa, Assembleia Constituinte, Preâmbulo da Constituição de 1976); fichas dos anos 50 a 70 (Sophia, Agustina, Cardoso Pires, Maria Judite de Carvalho, Saramago cronista, Eduardo Lourenço); e contrastes entre a versão "IA" e o original, para ancorar a voz.
- **Prioridade sobre skills PT-BR** — pode ser usada por cima de `humanizar`, `better-portuguese` e afins.

## Verificador automático

A skill inclui um verificador (`scripts/verificar.py`) que assinala, em qualquer texto:

- **grafia AO90** (*ação*, *atual*, *projeto*, *infraestrutura*) com a forma pré-AO90 correcta;
- **grafia brasileira** (*econômico*, *idéia*, *freqüente*);
- **brasileirismos lexicais** (*equipe*, *controle*, *usuário*, *ônibus*, *aposentadoria*) com a alternativa portuguesa;
- **sintaxe**: *estar + gerúndio*, próclise em início de frase, possessivo sem artigo, *ter que*;
- **maiúsculas e hífenes** pré-AO90 (*Janeiro*, *fim-de-semana*, *hei-de*);
- **marcas de IA**: vocabulário (*crucial*, *jornada*, *desempenha um papel*), fórmulas vazias, paralelismo negativo, excesso de travessões, perguntas e exclamações, parágrafos e frases de tamanho uniforme.

```bash
python -m pip install spylls                 # uma vez
python scripts/instalar_dicionarios.py        # uma vez: dicionários Hunspell
python scripts/verificar.py texto.md
```

Sem os dicionários, o verificador funciona em modo reduzido.

### Origem dos dados

- `dados/ao90_preao.tsv`: 1397 pares AO90 → pré-AO90, gerados a partir das formas reais do **CETEMPúblico** (Linguateca; *Público*, 1991–1998), validadas com os dicionários Hunspell do **Projecto Natura** (Universidade do Minho).
- `dados/brasileirismos.tsv`: curadoria manual a partir da comparação de frequências do corpus **CHAVE** (Linguateca): *Público* contra *Folha de S. Paulo*, 1994–1995, os mesmos anos e o mesmo género.
- `dados/vocabulario_ia.tsv`: marcas de texto gerado por IA, com limites por texto.
- O script que gera as listas está em `ferramentas/gerar_listas.py`.
- Os dicionários (Natura, GPL/LGPL/MPL; VERO pt_BR, LGPL/MPL) não são redistribuídos: `instalar_dicionarios.py` descarrega-os das fontes oficiais.

## Cofre de conhecimento (Obsidian)

A pasta `Portuguese Skill/` é um cofre Obsidian e a **fonte de verdade** das regras: cada regra é uma nota ligada às medições e às fontes que a justificam (CETEMPúblico, CHAVE, NOW, corpora orais, debates parlamentares, testes). Os ficheiros `dados/brasileirismos.tsv` e `dados/vocabulario_ia.tsv` geram-se com `python ferramentas/gerar_dados.py`, que valida as regras (regex inválidos, evidências em falta, contradições entre regra e medição). Abrir a pasta no Obsidian com o plugin Dataview para ver os painéis em `00 Índices/`.

## Testes

Ver `testes/README.md`: controlos do verificador e uma bateria de 20 pedidos que se corre a cada versão, com e sem a skill, para medir o efeito de cada alteração.

## Instalação

```bash
npx skills add insforca/PortuguesSkill
```

## Estrutura

```
pt-pt/antesAO90/
  SKILL.md
  references/ortografia-pre-ao90.md
  references/lexico-sintaxe-pt-pt.md
  references/anti-ia-pt-pt.md
  references/registos.md
  references/exemplos.md
  references/corpus/            (README, seculo-xix, seculo-xx-1900-1955, documentos-oficiais, anos-50-70, contrastes)
  scripts/verificar.py          verificador
  scripts/instalar_dicionarios.py
  dados/                        ao90_preao.tsv, brasileirismos.tsv, vocabulario_ia.tsv
ferramentas/gerar_listas.py     gera as listas a partir dos corpora (para quem mantém a skill)
testes/                         controlos e bateria de pedidos
```

Correcções e sugestões são bem-vindas por *issue* ou *pull request*.

Licença MIT · autor: insforca
