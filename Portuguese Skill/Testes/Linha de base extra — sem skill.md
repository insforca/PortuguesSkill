---
tipo: teste
textos: 42
palavras: 14588
erros: 84
erros_por_mil: 5.8
avisos_por_mil: 8.2
fonte: '[[Testes da skill]]'
---

# Linha de base extra — sem skill

42 pedidos novos (`testes/pedidos_base_extra.tsv`: ensaio, opinião, académico, institucional, cartas, crónica, ficção, divulgação), gerados pelo Claude sem a skill (`--disallowedTools Skill`). Servem para medir as marcas de IA com mais texto: a referência IA passou de 8 285 para 23 034 palavras.

Erros: 74 de grafia AO90 em 84. Avisos mais frequentes: marcas de IA (39), comprimento das frases (32), ritmo (16).

Efeito na medição das regras (`ferramentas/medir_regras.py`): passaram a medidas «desafios» (5×), «ecossistemas» (16×), «não é… é» (6×) e «potencializar» (25×). Ficam 20 presumidas. Dessas, 13 não aparecem nenhuma vez nos textos do Claude («explorar», «mergulhar», «tapeçaria», «sinergias», «robusto», «jornadas»…). São tiques de outros modelos ou de traduções do inglês. Mantêm-se como aviso, mas não estão provadas para o Claude. «Ou seja», «por um lado» e «fundamental» aparecem menos no Claude do que na prosa portuguesa.

Decisão (2026-10-27): ficam como aviso, porque a skill também revê textos de outras ferramentas e de outros modelos.
