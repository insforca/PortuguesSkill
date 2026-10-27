---
tipo: regra
categoria: 'sintaxe'
padrao: '\b(est\w+) \w+ndo\b'
alternativa: 'estar a + infinitivo'
nivel: 'erro'
gerado: false
implementacao: 'scripts/verificar.py'
estado: 'medida'
fenomeno: '[[Gerúndio]]'
evidencia: ["[[NOW — está sendo]]", "[[NOW — estão fazendo]]", "[[Parlamento — discurso 1945-2011]]", "[[Parlamento — oral 1945-2011]]"]
---

# SX — gerúndio com estar

Implementada em código no verificador. Em PT-PT: **estar a + infinitivo**.

## Evolução em Portugal

Nos discursos parlamentares, o gerúndio passou de 63% (anos 40) a 1% (anos 90) das construções progressivas. Ver `testes/analises/parlamento.md`.
