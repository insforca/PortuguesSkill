---
tipo: indice
---

# Painel

Fonte de verdade da `portugues-skill`. As regras editam-se aqui; os TSV da skill geram-se com
`python ferramentas/gerar_dados.py`.

## Regras por categoria e estado
```dataview
TABLE length(rows) AS "regras"
FROM "Regras"
GROUP BY categoria + " · " + estado
```

## Medições por fonte
```dataview
TABLE length(rows) AS "medições"
FROM "Medições"
GROUP BY fonte
```

## Regras por fenómeno
```dataview
TABLE length(rows) AS "regras"
FROM "Regras"
GROUP BY fenomeno
```
