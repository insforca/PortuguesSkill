# PortuguesSkill — escrita em português europeu (pré-AO90)

Skill para agentes de IA (Claude Code, Cursor, Codex e outros) que escrevem em **português europeu** com a **ortografia anterior ao Acordo Ortográfico de 1990**: acção, óptimo, actual, director, Janeiro, pára, pêlo, fim-de-semana, hei-de.

Até agora, todas as skills de português no ecossistema eram calibradas para o português do Brasil. Esta preenche essa lacuna.

## O que inclui

- **Ortografia pré-AO90** — consoantes mudas, acentos diferenciais, hífenes, maiúsculas em meses e estações, com a lista das palavras que *não* se alteram na conversão (facto, contacto, ficção…).
- **Léxico e sintaxe de Portugal** — "estar a + infinitivo", ênclise e próclise, mesóclise, vocabulário europeu (ecrã, telemóvel, doutoramento, unidade curricular), aspas « ».
- **Convenções por género** — trabalhos académicos em Portugal (APA, Chicago, MLA, NP 405; nunca ABNT), ensaio e ficção (diálogo com travessão, formas de tratamento).
- **Prioridade sobre skills PT-BR** — pode ser usada por cima de `humanizar`, `better-portuguese` e afins.

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
```

Correcções e sugestões são bem-vindas por *issue* ou *pull request*.

Licença MIT · autor: insforca
