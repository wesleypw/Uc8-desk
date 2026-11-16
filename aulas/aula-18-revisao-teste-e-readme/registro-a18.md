# Meu registro A18 — Regressão, correções e README reproduzível

Nome/código individual, turma e data: Pietro Bastos — 15/11/2026

> Partes técnicas preenchidas com o que foi **realmente executado** (Python 3.12.3, Tk 8.6, Linux, tela virtual Xvfb).
> **[PREENCHER]** = depende da sua voz ou de conferência no seu computador; *(rascunho)* = texto-base para reescrever.

## Retomada sem consulta
Minha hipótese inicial para cada item:

**[PREENCHER — de memória]** Perguntas: (1) de onde deve vir o valor esperado de um teste? (2) que caso "vizinho" confere uma correção?
(3) o que outra pessoa precisa para executar pelo README sem falar com você?

## Arquitetura antes do código
Desenho dos módulos, dependências e duração dos dados:

A candidata é a integração da A17, sem mudar o desenho:
```
main.py -> tela_venda.py / componentes.py -> controller.py (Cadastro + Venda) -> repositorio.py (SQLite) | memoria.py
verificar.py (regressão) e README-A18.md (como rodar) acompanham a entrega
```
Os testes usam bancos temporários; o banco real (`dados_sorveteria.db`) nunca é tocado. A montagem do pedido dura só em memória; cadastros e vendas duram no arquivo.

## Matriz de execução
Para cada caso, registre previsão, observado, correção e nova execução.

T01 — Valores conhecidos, erro após válido e cancelamento repetidos.
Previsão: `6,50`→650, `R$ 1.234,56`→123456, `0,01`→1, `100.000,00`→10000000; 2×6,50 no PIX 1131, Débito 1196, Crédito 1300 (calculados no papel); repetir não muda; quantidade `0` depois de uma montagem válida é recusada e preserva o total (1950 com qtd 3), `1` volta a funcionar (650); cancelar exclusão 3 vezes não remove ninguém.
Observado: tudo conferiu, nas duas execuções seguidas (T01 ok).
Correção/reteste ou pendência: defeito controlado numa cópia (`Pedido.atualizar` aceitando `0` e apagando a linha) foi detectado; restaurado, passou.

T02 — ID estável após reorganizar listagem.
Previsão: ordenando Carla(1), Ana(2), Bruno(3) por nome, a 1ª posição é o ID 2; editar por esse ID muda "Ana"; depois de excluir o ID 1, editar o ID 3 muda "Bruno" mesmo ele tendo trocado de posição.
Observado: `{1 Carla, 2 Ana Paula, 3 Bruno}` e depois `[(2 Ana Paula), (3 Bruno Lima)]` (T02 ok).
Correção/reteste ou pendência: sem correção.

T03 — Persistência reaberta no mesmo caminho.
Previsão: ao reabrir o mesmo arquivo: clientes Ana e Bruno, preços 650 e 1590, venda 1 de Ana com total 1131; abrir de novo não duplica (2 clientes, 1 venda).
Observado: conferiu (T03 ok).
Correção/reteste ou pendência: sem correção.

T04 — Falha transacional sem venda parcial.
Previsão: com 3 itens em que o 3º tem produto inexistente → 0 vendas e 0 itens; e se o produto some entre a conferência e a gravação (corrida simulada) → 0/0, Pedido continua ABERTO com 2 itens e sem ID de venda.
Observado: conferiu (T04 ok).
Correção/reteste ou pendência: defeito controlado (commit após cada item) falhou com `vendas/itens após falha: esperado (0, 0), obtido (1, 2)`; restaurado, passou.

T05 — Exportação CSV coerente com o comprovante.
Previsão: 2×6,50 + 1×15,90 = 28,90 → PIX ×0,87 = 25,143 → 25,14; linhas `Casquinha;2;1300` e `Milkshake;1;1590`; soma dos subtotais 2890; total `R$ 25,14` em todas as linhas; banco e comprovante com (2890, 2514).
Observado: conferiu (T05 ok).
Correção/reteste ou pendência: defeito controlado (gravar o subtotal em vez do total pago) falhou com `total em todas as linhas: esperado {'R$ 25,14'}, obtido {'R$ 28,90'}`; restaurado, passou.

T06 — Teste propositalmente errado falha; previsão restaurada passa.
Previsão: a expectativa errada 1200 para o PIX de 2×6,50 falha com mensagem "esperado 1200, obtido 1131"; a previsão certa (1131) passa.
Observado: confirmado (T06 ok).
Correção/reteste ou pendência: sem correção; é um teste do próprio teste.

T07 — Execução pelo README em outra pasta.
Previsão: copiando só os arquivos listados na entrega para uma pasta vazia, `python verificar.py` roda e passa, sem criar `.db` na pasta.
Observado: a cópia executou, T01/T03/T05/T06 apareceram e nenhum banco foi criado (T07 ok).
Correção/reteste ou pendência: **pendente**: ainda falta outra pessoa executar pelo README no computador dela.

T08 — Teclado, foco e mensagens inspecionados.
Previsão (escrita antes de rodar): ordem do Tab na Venda = cliente → atualizar → produto → qtd → adicionar → tabela → remover → revisar → forma → finalizar → nova (Exportar fica fora porque começa desabilitado); só widgets ttk; erro sem cliente orienta "Selecione o cliente" e dá para corrigir.
Observado: a ordem observada foi exatamente essa; nenhum widget do CustomTkinter na janela; a mensagem orientou e, escolhendo o cliente, a nova tentativa gravou (T08 ok).
Correção/reteste ou pendência: feito em tela virtual; **[PREENCHER]** repetir à mão no Windows. Medição anterior: Espaço aciona botão ttk; Enter não.

T09 — Pendências identificadas sem inventar aprovação.
Previsão: o script lista o que ele não pode aprovar e, sem ambiente gráfico, não declara sucesso.
Observado: sem display, o T08 saiu como PENDENTE e a última linha foi "Verificações ainda incompletas"; com Xvfb, a linha final foi "Casos executados…", mantendo a lista de pendências humanas.
Correção/reteste ou pendência: pendências humanas: execução por outra pessoa, teste manual no Windows, entrega pelo fluxo combinado (também no README).

## Explicação individual
Uma decisão que consigo justificar: *(rascunho — reescreva)* escrever as expectativas à mão (por exemplo 13,00 × 0,87 = 11,31) em vez de calcular com o próprio código, para o teste conseguir apontar um erro do código.
Uma dificuldade, apoio e próxima tentativa: *(rascunho — ajuste ao que for verdade)* ao reaproveitar a A15 vi que o `modelos.py` dela dava `AttributeError` (`self.preco_centavos` usado antes de atribuir); usei o da A14 e retestei. Usei um assistente de IA como apoio. Próxima tentativa: **[PREENCHER]**

## Arquivos
Versão executada e arquivos baixados: `main.py`, `tela_venda.py`, `componentes.py`, `controller.py`, `repositorio.py`, `memoria.py`, `modelos.py`, `pagamento.py`, `arquivos.py`, `perfis.py`, `relatorios.py`, `comparar_ctk.py`, `verificar.py`, `README-A18.md`.
Caminho de dados fictícios usado (se houver): bancos temporários nos testes; `dados_sorveteria.db` ou `--banco ensaio.db` ao rodar a janela.
Entrega pelo fluxo combinado conferida por mim: **[PREENCHER]**

## Teoria e transferência
Consigo explicar a origem independente da expectativa de um teste.
Minha explicação: *(rascunho)* o valor esperado vem de uma regra conhecida ou de uma conta feita fora do código (papel/calculadora), não do resultado da função que está sendo testada; senão o teste confirma o erro.
Consigo escolher um caso vizinho para conferir uma correção.
Minha explicação: *(rascunho)* depois de corrigir a quantidade `0`, testo também `1` e uma quantidade maior; depois de corrigir a transação, testo a venda válida logo em seguida.
Consigo orientar outra pessoa a executar pelo README com dados de ensaio.
Minha explicação: *(rascunho)* abrir o terminal na pasta do `main.py`, rodar `python verificar.py` e, para a janela, `python main.py --banco ensaio.db`, sem tocar no banco original.
Ligação entre o ensaio e meus arquivos da atividade: **[PREENCHER]**
