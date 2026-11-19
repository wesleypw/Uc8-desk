# Meu registro A19 — Academia e demonstrações individuais

Nome/código individual, turma e data: Pietro Bastos — 15/11/2026

> Partes técnicas preenchidas com o que foi **realmente executado** (Python 3.12.3, Linux). **[PREENCHER]** = depende
> da sua voz, da apresentação em sala ou do feedback; *(rascunho)* = texto-base para reescrever.

## Retomada sem consulta
Minha hipótese inicial para cada item:

**[PREENCHER — de memória]** Perguntas da aula: (1) que instrução permite ao colega iniciar sem explicação oral (A18)? (2) o que deve acompanhar uma correção (A18)?
(3) como selecionar o alvo depois de ordenar a listagem (A15)? (4) que evidência mostra que cancelar exclusão preservou o cadastro (A15)?

## Arquitetura antes do código
Desenho dos módulos, dependências e duração dos dados:

```
demo_candidata.py -> controller.py / repositorio.py (candidata validada na A18)  -> banco de ensaio (temporário ou --banco)
backup_sqlite.py  -> API backup do SQLite: origem (somente leitura) -> destino NOVO -> conferência por outra conexão
entrega.py        -> lista/zipa só o que deve ser entregue (sem .db, __pycache__, .venv, .git, .env)
academia_amostra.py -> só leitura/análise (listas em memória + JSON)
verificar.py      -> confere demonstração, mapa da academia, backup e entrega
```
Duração: o banco de ensaio e a cópia ficam em arquivo; a montagem da venda só existe em memória; a amostra da academia existe só enquanto o programa roda.

## Matriz de execução
Para cada caso, registre previsão, observado, correção e nova execução.

T01 — Minha demonstração apresenta uma execução e uma explicação próprias.
Previsão: `python demo_candidata.py` mostra 2 × 6,50 → 1300 → 1131 centavos no PIX (R$ 11,31) e a venda 1 gravada.
Observado: exatamente isso, mais a venda 2 no Débito (1196); `verificar.py` confere esses valores (T01 ok).
Correção/reteste ou pendência: a **execução** está verificada; a **explicação própria** é sua, na apresentação — **[PREENCHER]**.

T02 — Demo inclui fluxo válido, falha/cancelamento e persistência/relatório.
Previsão: o roteiro tem etapas Válido, Recusa, Correção, Persistência e Relatório.
Observado: as nove etapas apareceram: quantidade 0 recusada, finalizar sem cliente recusado, correções gravaram a venda 2; reabrir o banco listou as duas vendas; o CSV trouxe `1;Casquinha;2;650;1300;Débito;R$ 11,96` (T02 ok).
Correção/reteste ou pendência: sem correção. O cancelamento da confirmação na janela foi coberto na A17/A18 (tela virtual).

T03 — Pergunta técnica tem explicação individual, além da tela pronta.
Previsão: consigo apontar o arquivo e a evidência da decisão.
Observado: rascunho no `roteiro-demo.md` (transação em `registrar_venda`; evidência: defeito controlado `esperado (0, 0), obtido (1, 2)`).
Correção/reteste ou pendência: **pendente** — a explicação individual precisa ser sua, falada/escrita com suas palavras.

T04 — Mapa da academia distingue entidade, responsabilidade e armazenamento observado.
Previsão: alunos 41 e 92, plano 7, matrícula 101 (41→7); o controller devolve cópia; armazenamento só em memória/JSON; excluir o aluno 41 deixaria a matrícula 101 órfã; corrigir o nome não exige novo ID.
Observado: tudo conferiu (T04 ok); a amostra não contém Tkinter, SQLite nem leitura/escrita de arquivo, então camadas de GUI e banco não podem ser afirmadas pela leitura.
Correção/reteste ou pendência: sem correção.

T05 — Backup usa destino novo e não sobrescreve cópia anterior.
Previsão: segunda chamada com o mesmo destino levanta `FileExistsError` e a primeira cópia fica byte a byte igual; um destino novo funciona.
Observado: conferiu comparando o hash SHA-256 antes e depois (T05 ok); pela linha de comando: "Backup recusado: O destino já existe e não será sobrescrito", código de saída 1.
Correção/reteste ou pendência: sem correção.

T06 — Origem ausente não cria silenciosamente banco vazio.
Previsão: `FileNotFoundError`, sem criar a origem nem o destino; pasta de destino inexistente também é recusada.
Observado: a pasta de ensaio continuou vazia após a recusa (T06 ok); pela linha de comando: "Backup recusado: Banco de origem não encontrado".
Correção/reteste ou pendência: o backup abre a origem em modo somente leitura (`mode=ro`), justamente para um caminho errado não virar banco novo.

T07 — Cópia abre e contém registros conhecidos; integridade conferida.
Previsão: com um 3º cliente adicionado antes do backup, a cópia tem 3 clientes; `PRAGMA integrity_check` → `ok`; ID 2 = "Rui fictício"; a venda 1 (PIX, 1131) veio junto; um 4º cliente adicionado depois só aparece na origem.
Observado: tudo conferiu por consultas em outra conexão (T07 ok); a origem continuou aceitando gravações.
Correção/reteste ou pendência: sem correção.

T08 — Entrega exclui ambientes/caches/dados reais e documenta limites.
Previsão: `entrega.py` deixa de fora `.db`, `.sqlite3`, `.pyc`, `__pycache__`, `.venv`, `venv`, `.git`, `.env`, `-wal`, `.zip`; mantém `.py` e `.md`; o roteiro descreve limites.
Observado: numa árvore de teste com esses itens a lista final foi `README.md, main.py, sub/modulo.py`; o zip tem o mesmo conteúdo; a pasta real da A19 não vazou nada e o roteiro tem "Limite e próximo teste" (T08 ok).
Correção/reteste ou pendência: sem correção. **[PREENCHER]** confirmar que o banco real de verdade (`dados.db`) não está na pasta que você entrega.

T09 — Feedback indica evidência por indicador e teste de recuperação.
Previsão: —
Observado: ainda não há feedback.
Correção/reteste ou pendência: **pendente** — depende de quem avalia; anote abaixo em "Para a A20".

Extras (erro depois de válido, limites e correção): backup válido; destino repetido recusado; origem que não é SQLite recusada sem sobrar cópia parcial e sem alterar a origem; banco vazio copiado (resumo `{}`); novo destino funciona (Extras ok).

## Explicação individual
Uma decisão que consigo justificar: *(rascunho — reescreva)* abrir a origem do backup só para leitura e usar a API `backup()` em vez de copiar o arquivo: o backup fica consistente e um caminho errado não cria um banco vazio que pareça uma cópia boa.
Uma dificuldade, apoio e próxima tentativa: *(rascunho — ajuste ao que for verdade)* garantir que uma falha no meio não deixe uma cópia parcial: se algo der errado, `criar_backup` apaga o destino. Usei um assistente de IA como apoio. Próxima tentativa: **[PREENCHER]**

## Arquivos
Versão executada e arquivos baixados: `demo_candidata.py`, `backup_sqlite.py`, `entrega.py`, `academia_amostra.py`, `verificar.py`, `roteiro-demo.md`, `registro-a19.md` e a candidata (`main.py`, `tela_venda.py`, `componentes.py`, `controller.py`, `repositorio.py`, `memoria.py`, `modelos.py`, `pagamento.py`, `arquivos.py`, `perfis.py`, `relatorios.py`, `comparar_ctk.py`).
Caminho de dados fictícios usado (se houver): bancos temporários nos testes; `origem-ficticia.db`/`copia-nova.db` em pasta de ensaio quando rodar `backup_sqlite.py`.
Entrega pelo fluxo combinado conferida por mim: **[PREENCHER]**

## Teoria e transferência
Consigo explicar uma decisão apontando código e execução.
Minha explicação: *(rascunho)* a decisão da transação está em `repositorio.py` (`registrar_venda`); a execução que a sustenta é `python verificar.py` da A18 (T04) e a demonstração (`venda 1 gravada` só depois do banco).
Consigo distinguir existência da cópia de recuperação conferida.
Minha explicação: *(rascunho)* um arquivo criado só prova que existe; a cópia só é "conferida" depois de abrir por outra conexão, passar no `integrity_check` e achar registros conhecidos (T07).
Consigo identificar origem, destino novo e consulta usada para verificar o backup.
Minha explicação: *(rascunho)* origem `origem-ficticia.db`, destino `copia-nova.db` (não pode existir); consultas: `PRAGMA integrity_check`, `SELECT id, nome FROM clientes WHERE id = 2` e `SELECT count(*) FROM clientes`.
Ligação entre o ensaio e meus arquivos da atividade: **[PREENCHER]**
Minha previsão antes da alteração guiada e o resultado observado: **[PREENCHER]** (a aula sugere acrescentar outra linha na origem antes do backup e prever a contagem; no T07 previ 3 clientes e observei 3).

## Continuação em casa
Arquivos/versão executados: os listados em "Arquivos".
Pasta e comando usados: na pasta da A19, `python demo_candidata.py`, `python verificar.py` e `python backup_sqlite.py origem-ficticia.db copia-nova.db` (em pasta de ensaio).
Justificativa de 5–8 linhas ou nome do áudio de cerca de 60 segundos: **[PREENCHER]**
Decisão do meu código sobre demonstração sustentada por evidências, comparação de responsabilidades e backup conferido: *(rascunho)* a demo roda sozinha e imprime o que observou; o mapa da academia só afirma o que os dados mostram; o backup só vale depois da consulta na cópia.
Minha explicação / anexo: **[PREENCHER]**

## Checklist da interface
Controles e rótulos que conferi: a candidata não mudou na A19; os controles foram conferidos na A18 (captura sob Xvfb).
Percurso por Tab/Shift+Tab e acionamento: na A18 a ordem do Tab foi conferida por script; Espaço aciona botão `ttk`, Enter não. **[PREENCHER]** conferir à mão.
Mensagem após erro e possibilidade de corrigir: a demo mostra as recusas (quantidade 0 e falta de cliente) e as correções.
Redimensionamento e comportamento que observei: **[PREENCHER]**

## Pendências
O que não executei e por quê, incluindo falta de ambiente: não rodei no seu Windows nem apresentei em sala; T03 e T09 dependem de você e de quem avalia; mouse, teclado físico e redimensionamento não foram testados.
Caso para nova tentativa em sala: demonstração completa com `python main.py --banco ensaio.db` e um backup conferido na frente de quem avalia.

## Para a A20
Versão que demonstrei: **[PREENCHER]**
Evidência observada e feedback recebido: **[PREENCHER]**
Pendência escolhida para revalidar: **[PREENCHER]**
Entrada, ação e resultado que espero no reteste: **[PREENCHER]**
