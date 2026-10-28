---
tipo: teste
textos: 20
certos: 9
leitores: 1
data: '2026-10-28'
fonte: '[[Testes da skill]]'
---

# Teste cego 1 — v1.8

10 excertos do Público (opinião e cultura, 1993–1998) e 10 textos da v1.8 emparelhados (mesmo género, assunto, época e tamanho; `testes/pedidos_cego.tsv`, `ferramentas/preparar_teste_cego.py`). Um leitor: o autor da skill. Respostas em `testes/analises/teste_cego_1.tsv`.

**9 certos em 20**, abaixo do acaso (probabilidade de ≥ 9 ao acaso: 0,75). Dos 10 textos da IA, 8 foram dados como humanos; dos 10 humanos, 3 foram dados como IA.

Pistas que o leitor usou: aspas angulares «» e travessão (—). Ambas enganaram. Os três humanos tomados por IA (opinião, cinema e ciência) eram os que tinham «» e —, e no Público as aspas angulares são até 14 vezes mais frequentes do que nos textos da v1.8 (14,4 contra 1,0 por mil palavras). O travessão tem frequência semelhante nos dois (4,8 e 3,6). O único texto da IA apanhado com uma pista foi a ficção com diálogos em travessão, que é a convenção portuguesa.

Limites: um só leitor, que conhece a skill; 20 textos (intervalo de 95% para a taxa de acerto: cerca de 23% a 68%). Falta repetir com leitores que não conheçam o projecto.

Leitura: neste teste a v1.8 não se distingue da imprensa portuguesa dos anos 90. As pistas «anti-IA» importadas do inglês (o travessão) não servem para o português europeu, onde são norma.
