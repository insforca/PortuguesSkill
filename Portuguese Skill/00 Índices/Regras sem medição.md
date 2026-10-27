---
tipo: indice
---

# Regras sem medição

Regras ainda presumidas: a lista de trabalho para as próximas medições.

```dataview
TABLE categoria, nivel, padrao
FROM "Regras"
WHERE estado = "presumida"
SORT nivel ASC, categoria ASC
```
