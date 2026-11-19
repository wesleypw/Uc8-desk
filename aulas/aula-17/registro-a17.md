# Meu registro A17 — Sorveteria integrada e comparação visual

Nome/código individual, turma e data: Pietro Bastos — 15/11/2026

> As partes técnicas foram preenchidas com o que foi **realmente executado** (Python 3.12.3, Tk 8.6, Linux, tela virtual
> Xvfb, CustomTkinter 6.0.0). **[PREENCHER]** = depende da sua voz ou de conferência no seu computador;
> *(rascunho)* = texto-base para você reescrever.

## Retomada sem consulta
Minha hipótese inicial para cada item:

**[PREENCHER — de memória, antes de reler o código]** Perguntas: (1) por que venda e itens precisam da mesma transação?
(2) o que o banco e a montagem mostram se o segundo item falhar? (3) o que é "núcleo" e o que é comparação opcional?

## Arquitetura antes do código
Desenho dos módulos, dependências e duração dos dados:

```
main.py -> abas: PainelVenda (tela_venda.py) | PainelCadastro produtos | PainelCadastro clientes (componentes.py)
PainelVenda  -> VendaController  -> Pedido (modelos.py, em MEMÓRIA)  e  RepositorioSqlite
Cadastros    -> CadastroController ->                                    RepositorioSqlite (repositorio.py)
VendaController.finalizar: cliente? -> montagem não vazia? -> catálogo igual ao visto? -> previa (pagamento.py)
   -> repositorio.registrar_venda (UMA transação: venda + itens) -> só então Pedido.finalizar() gera o comprovante
exportar CSV: lê o comprovante (relatorios.exportar_csv), nunca os campos da janela nem o catálogo atual
comparar_ctk.py: OPCIONAL; núcleo não importa CustomTkinter
```
- Banco: tabelas `produtos`, `clientes`, `vendas` (cliente_id → clientes) e `itens_venda` (venda_id, produto_id); `PRAGMA foreign_keys = ON` a cada conexão.
- Duração: cadastros e vendas persistem no `.db`; a montagem (Pedido) vive só em memória até finalizar.

## Matriz de execução
Para cada caso, registre previsão, observado, correção e nova execução.

T01 — Catálogo/clientes vêm do banco por ID, inclusive após reabrir.
Previsão: após reabrir o arquivo, clientes `[(1,Ana),(2,Bruno)]` e produtos `[(1,Casquinha,650),(2,Milkshake,1590)]`; adicionar o ID 2 coloca "Milkshake" na montagem; ID 99 é recusado.
Observado: conferiu (T01 ok).
Correção/reteste ou pendência: sem correção.

T02 — Cadastro novo aparece após atualização explícita.
Previsão: cadastrar "Carla" pelo controller não altera a lista da aba Venda até `atualizar_listas()`; depois, ela aparece (e também ao voltar para a aba).
Observado: sob Xvfb a lista só mudou após a atualização; "Picolé" apareceu ao trocar de aba com evento real do Notebook.
Correção/reteste ou pendência: executado em tela virtual; **[PREENCHER]** confirmar clicando no seu computador.

T03 — Preço mudou ou produto sumiu: recusar confirmação sem venda parcial.
Previsão: com a casquinha na montagem a 6,50, mudar o preço para 7,00 → finalizar recusa, 0 vendas/0 itens, montagem intacta; "Revisar montagem" aplica 7,00 e a venda sai 14,00 → 12,18. Se o produto é excluído → recusa "saiu do catálogo"; revisar remove o item e a montagem vazia não finaliza.
Observado: conferiu nos dois cenários (T03 ok), no controller e na janela. Somar mais uma unidade com preço mudado também é recusado (não repreça a linha em silêncio).
Correção/reteste ou pendência: mutação (finalizar ignorando o catálogo) foi detectada.

T04 — Cliente inexistente ou não selecionado: orientar.
Previsão: sem cliente → "Selecione o cliente…"; ID 99 → "não existe"; nada gravado; escolher um cliente válido e repetir grava a venda 1.
Observado: conferiu (T04 ok) e na janela a mensagem apareceu sem perder a montagem; quantidade "0" foi recusada mantendo "0" no campo, e "2" corrigiu.
Correção/reteste ou pendência: sem correção.

T05 — Venda de duas unidades a 6,50 no PIX: 13,00 → 11,31.
Previsão: subtotal 1300, fator 0,87, total 1131 centavos, "R$ 11,31"; Débito 11,96; Crédito 13,00 (calculados à mão antes).
Observado: prévia, comprovante e linha gravada no banco deram 1300 → 1131; Débito 1196; Crédito 1300; forma inválida recusada.
Correção/reteste ou pendência: mutação (gravar o subtotal em vez do total) foi detectada.

T06 — Falha na segunda inserção desfaz venda e itens.
Previsão: venda com dois itens em que o segundo tem produto inexistente → erro; 0 linhas em `vendas` e em `itens_venda`; uma venda válida depois grava normalmente. No controller, falha do repositório mantém Pedido aberto, sem comprovante, com os itens.
Observado: conferiu: contagens 0/0 após a falha e 1/1 após a venda válida; montagem preservada (T06 ok).
Correção/reteste ou pendência: mutação (commit antes do fim, sem rollback) foi detectada.

T07 — Sucesso grava uma venda e bloqueia nova finalização.
Previsão: após finalizar há 1 venda e 1 item; finalizar de novo e adicionar item são recusados e nada novo é gravado; reabrir mostra a venda 1; "Nova venda" libera e a próxima recebe ID 2.
Observado: conferiu (T07 ok); na janela os botões de edição/finalização ficaram desabilitados e "Exportar CSV" habilitado.
Correção/reteste ou pendência: mutação (permitir finalização repetida) foi detectada.

T08 — Excluir cadastro vinculado é bloqueado.
Previsão: produto e cliente que já têm venda não são excluídos ("vinculado a vendas") e continuam na lista; os sem venda (Milkshake, Bruno) ainda são excluídos.
Observado: conferiu (T08 ok).
Correção/reteste ou pendência: mutação (sem `PRAGMA foreign_keys`) foi detectada.

T09 — CSV usa o comprovante confirmado e mantém totais.
Previsão: sem venda finalizada não exporta e nenhum arquivo é criado; depois de finalizar e mudar o preço no catálogo para 99,00, o CSV ainda mostra a linha `1;Casquinha;2;650;1300;PIX;R$ 11,31`.
Observado: conferiu (T09 ok); na janela, cancelar o diálogo de salvar não quebrou e a venda continuou gravada.
Correção/reteste ou pendência: sem correção.

T10 — Comparação ttk/CTk documenta teclado/foco; ausência da dependência não bloqueia núcleo.
Previsão: com `customtkinter` ausente, `criar_comparacao()` e `medir_teclado()` devolvem `None` e o núcleo importa normalmente.
Observado: confere (T10 ok). Com CustomTkinter 6.0.0 instalado, `python comparar_ctk.py --medir` mediu:
- ttk: ciclo do Tab = Entrada 1 → Entrada 2 → Botão → (repete); **Espaço aciona (1)**; **Enter aciona (0)**.
- CTk: ciclo do Tab = Entrada 1 → Entrada 2 → (repete), **o botão fica fora do ciclo**; Espaço (0) e Enter (0) não acionam. No código da biblioteca o botão só liga eventos de mouse (Enter/Leave/ButtonRelease-1).
Correção/reteste ou pendência: por isso a interface principal ficou em ttk (acessível por teclado). Não medi o clique do mouse no CTk com eventos sintéticos; **[PREENCHER]** conferir à mão se quiser.

## Explicação individual
Uma decisão que consigo justificar: *(rascunho — reescreva)* gravar a venda e os itens na mesma conexão com `with con:` — se algo falhar no meio, o banco desfaz tudo e a janela não mostra sucesso; o comprovante só é criado depois do ID devolvido pelo banco.
Uma dificuldade, apoio e próxima tentativa: *(rascunho — ajuste ao que for verdade para você)* o SQLite só confere vínculos por ID se `PRAGMA foreign_keys = ON` for ativado a cada conexão; sem isso a exclusão de cadastro vinculado passava. Usei um assistente de IA como apoio. Próxima tentativa: **[PREENCHER]**

## Arquivos
Versão executada e arquivos baixados: `main.py`, `tela_venda.py`, `componentes.py`, `controller.py`, `repositorio.py`, `memoria.py`, `modelos.py`, `pagamento.py`, `arquivos.py`, `perfis.py`, `relatorios.py`, `comparar_ctk.py`, `verificar.py`.
Caminho de dados fictícios usado (se houver): `dados.db` ao lado do `main.py` (ou outro arquivo com `python main.py --banco ensaio.db`). Os testes usam bancos temporários.
Entrega pelo fluxo combinado conferida por mim: **[PREENCHER]**

## Teoria e transferência
Consigo explicar por que venda e itens precisam da mesma transação.
Minha explicação: *(rascunho)* uma venda sem itens, ou itens sem venda, deixaria o banco incoerente; na mesma transação ou grava tudo, ou nada (T06).
Consigo prever banco e montagem após uma falha no item.
Minha explicação: *(rascunho)* o banco volta ao que era (0 vendas, 0 itens novos), nenhum comprovante é gerado e a montagem continua na tela para corrigir.
Consigo distinguir o núcleo integrado da comparação visual opcional.
Minha explicação: *(rascunho)* o núcleo (catálogo, clientes, venda, CSV) roda só com a biblioteca padrão; `comparar_ctk.py` é opcional e devolve `None` se faltar a dependência (T10).
Ligação entre o ensaio e meus arquivos da atividade: **[PREENCHER]**
Minha previsão antes da alteração guiada e o resultado observado: **[PREENCHER — depende do ensaio em sala]**

## Continuação em casa
Arquivos/versão executados: os listados em "Arquivos".
Pasta e comando usados: na pasta da aula, `python verificar.py` e `python main.py`.
Justificativa de 5–8 linhas ou nome do áudio de cerca de 60 segundos: **[PREENCHER]**
Decisão do meu código sobre transação venda/itens, rollback, IDs vinculados e coerência com o catálogo: *(rascunho)* `registrar_venda` faz tudo numa transação; vínculos por ID com chave estrangeira; o item guarda o preço visto e o controller compara com o catálogo antes de gravar, pedindo "Revisar montagem" se mudou.
Minha explicação / anexo: **[PREENCHER]**

## Checklist da interface
Controles e rótulos que conferi: abas Venda/Catálogo/Clientes; Cliente, Produto, Qtd, Adicionar, Atualizar listas, Remover item, Revisar montagem, Pagamento, Subtotal/Total, Finalizar venda, Exportar CSV, Nova venda (captura sob Xvfb; a tabela e a rolagem foram ajustadas após a primeira captura).
Percurso por Tab/Shift+Tab e acionamento: ver T10 (Espaço aciona botões `ttk`; Enter só funciona nos campos). **[PREENCHER]** conferir à mão.
Mensagem após erro e possibilidade de corrigir: erros mostram caixa e linha vermelha; quantidade e seleção continuam para corrigir; falha na venda mantém a montagem.
Redimensionamento e comportamento que observei: **[PREENCHER]**

## Pendências
O que não executei e por quê, incluindo falta de ambiente: não rodei no seu Windows nem com tela física; mouse, redimensionamento e entrega no fluxo combinado ficam por sua conta.
Caso para nova tentativa em sala: T02 e T10 com tela real.
