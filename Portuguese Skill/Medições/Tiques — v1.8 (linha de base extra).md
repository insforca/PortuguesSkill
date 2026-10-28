---
tipo: medicao
fonte: ["[[CETEMPúblico]]", "[[Testes da skill]]"]
metodo: 'ferramentas/descobrir_tiques.py + contagem por 10 mil palavras'
data: '2026-10-28'
leitura: 'tiques introduzidos pela própria skill v1.8'
---

# Tiques — v1.8 (linha de base extra)

42 textos gerados com a v1.8 (`testes/resultados/base-extra-v1.8`, 13 585 palavras) contra o CETEMPúblico (`.cache/corpora/pt.txt`) e contra os mesmos 42 pedidos sem a skill (`base-extra`). Relatório completo em `testes/analises/tiques_v1.8_extra.md`.

| forma | sem skill | v1.8 | Público (por 10 mil palavras) |
|---|---|---|---|
| convém | 2,0 | 8,6 (11 de 42 textos) | 0,2 |
| parece-me | 0,7 | 3,6 | 0,1 |
| quem | 39,7 | 44,0 (28 de 42 textos) | 8,1 |
| julgava | 0 | 3,6 | 0,03 |

*Convém* e *parece-me* são tiques criados pela skill: a regra do registo culto empurrou o modelo para estas fórmulas. *Quem* como sujeito genérico já é hábito do Claude sem a skill (5 vezes o Público); a skill acentua-o. *Julgava* aparece só em ficção e fica sob observação.

Regras: [[IA — convém]], [[IA — parece-me]], [[IA — quem genérico]].
