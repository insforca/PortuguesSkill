# Testes da skill

Dois tipos de teste, com objectivos diferentes.

## 1. Controlos do verificador (`controlo/`)

Medem se o **verificador** funciona, não se a skill escreve bem.

- `positivo/`: excertos de documentos oficiais (1950–1976) e exemplos «depois» da skill. Devem dar **0 erros**.
- `negativo/`: versões «IA» dos contrastes e exemplos «antes». Devem ser todos assinalados.

```bash
python ../pt-pt/antesAO90/scripts/verificar.py controlo/positivo/*.md controlo/negativo/*.md
```

Atenção: os controlos negativos foram escritos pelo mesmo autor das regras, por isso são fáceis de apanhar. Não provam que o verificador apanha tudo.

## 2. Bateria de pedidos (`pedidos.tsv`, `correr.py`)

Mede a **skill**: 20 pedidos fixos em vários registos (académico, ensaio, crónica, formal, corrente, informal, ficção), gerados com o Claude Code em modo não interactivo e avaliados pelo verificador.

```bash
python correr.py gerar v1.5                    # com a skill
python correr.py gerar sem-skill --sem-skill   # linha de base, sem a skill
python correr.py avaliar sem-skill v1.5        # tabela comparativa
```

Cada geração corre numa pasta temporária neutra, para que memórias ou o CLAUDE.md de um projecto não contaminem o resultado. Os textos ficam em `resultados/<etiqueta>/` e a avaliação detalhada em `resultados/<etiqueta>/avaliacao.md`.

**Correr a cada nova versão da skill** e comparar com a anterior. Uma alteração que aumente os erros por mil palavras deve ser revista.

Limites: o verificador mede o que é mensurável (grafia, léxico, algumas construções, marcas de IA conhecidas). Não mede a qualidade da prosa, a adequação do registo nem a verdade do conteúdo. Para isso, ler os textos.
