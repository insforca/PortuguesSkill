# Teste cego público (Google Forms)

Vinte excertos: dez de autores portugueses em domínio público (1873–1921, grafia actualizada para a norma
anterior ao AO90) e dez gerados pela skill v1.8 com o mesmo género, assunto, época e tamanho
(`testes/pedidos_cego_publico.tsv`; os pedidos não nomeiam os autores).

**Enquanto o estudo decorrer**, os excertos humanos (`humanos.json`), os textos gerados
(`testes/resultados/cego-publico-v1.8/`) e a chave (`.cache/teste_cego_publico/chave.tsv`) ficam fora do git,
para ninguém encontrar as respostas no repositório público. Publicam-se quando o formulário fechar.

## Criar o formulário

1. `python ferramentas/criar_formulario_cego.py` gera `.cache/teste_cego_publico/criar_formulario.gs`.
2. Abrir https://script.google.com, «Novo projecto», apagar o conteúdo, colar o ficheiro `.gs` e guardar.
3. Escolher a função `criarTeste` e carregar em «Executar». Na primeira vez, o Google pede autorização
   para o script criar formulários na sua conta: aceitar.
4. O «Registo de execução» mostra o endereço para responder e o endereço para editar.
5. No formulário, em **Definições → Questionários → Os inquiridos podem ver**: desligar «Respostas
   correctas» (para a chave não circular) e deixar «Valores dos pontos». Confirmar que «Recolher endereços
   de email» está desligado.
6. Fazer uma resposta de ensaio e apagá-la depois em «Respostas».

## Divulgar

- Ciberdúvidas: não tem fórum; a mensagem para a redacção está em `mensagem_ciberduvidas.md`.
- Objectivo: pelo menos 30 respostas de leitores de português europeu.

## Analisar

Exportar as respostas para CSV (separador «Respostas» → Google Sheets → Ficheiro → Transferir → CSV) e
cruzar cada coluna «Excerto Tnn» com `chave.tsv`: taxa de acerto global, por excerto e por perfil
(país, leitura de literatura antiga, uso de IA), comparada com 50%.
