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
```

Correcções e sugestões são bem-vindas por *issue* ou *pull request*.

Licença MIT · autor: insforca
