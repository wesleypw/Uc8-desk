# Meu registro A16 — Controllers e contratos: concluir clientes

Nome/código individual, turma e data: Pietro Bastos — 15/11/2026

> Como ler este registro: as partes técnicas (arquitetura, matriz, arquivos, pendências) foram preenchidas com o que
> foi **realmente executado** (Python 3.12.3, Tk 8.6, Linux com tela virtual Xvfb). Os trechos marcados com
> **[PREENCHER]** pedem a sua voz ou algo que só você pode conferir no seu computador; os marcados com
> *(rascunho)* têm um texto-base que você deve reescrever com suas palavras antes de entregar.

## Retomada sem consulta
Minha hipótese inicial para cada item:

**[PREENCHER — responda de memória, antes de reler o código]** Sugestão de perguntas para você responder:
1. O que o controller recebe da janela e o que ele devolve?
2. O que precisa ser igual entre `RepositorioMemoria` e `RepositorioSqlite` para o controller funcionar com os dois?
3. O que acontece com os dados de cada um quando a janela fecha?

## Arquitetura antes do código
Desenho dos módulos, dependências e duração dos dados:

```
main.py (janela: PainelCadastro x2)  ->  controller.py (CadastroController)  ->  repositório (contrato)
                                                                                  |- memoria.py     (dados somem ao fechar)
                                                                                  |- repositorio.py (SQLite: persiste no arquivo .db)
controller.py usa: pagamento.py (texto -> centavos) e repositorio.validar_id; NÃO importa tkinter.
modelos.py, arquivos.py, perfis.py, relatorios.py: reaproveitados das aulas anteriores.
```
- A janela só lê campos e mostra mensagens; quem decide inclusão x edição é o `codigo` (None = incluir, número = editar).
- Contrato dos dois repositórios: `adicionar_*` devolve o ID; `listar_*` devolve cópias ordenadas por ID;
  `editar_*`/`excluir_*` levantam `ValueError` se o ID não existe; `excluir_*` exige `confirmado=True`.
- Duração: memória vive no objeto (nova instância = vazio); SQLite vive no arquivo `dados_pizzaria.db` (reabre com dados).

## Matriz de execução
Para cada caso, registre previsão, observado, correção e nova execução.

T01 — Controller executa sem importar Tkinter.
Previsão: importar `controller`, `memoria` e `repositorio` num processo novo não coloca `tkinter` em `sys.modules`.
Observado: `verificar.py` rodou o import em subprocesso e a checagem passou (T01 ok).
Correção/reteste ou pendência: sem correção. Reteste com mutação não aplicável.

T02 — Mesmo contrato com memória/SQLite inclui, lista e edita por ID.
Previsão: a mesma sequência (incluir Ana e Bruno, editar o ID 1, incluir/editar produto) dá exatamente as mesmas respostas
nas duas implementações: IDs 1 e 2, `{"acao": "editado", "id": 1}` e a lista `[{id 1 "Ana Maria"}, {id 2 "Bruno"}]`.
Observado: os dois repositórios produziram a lista esperada (T02 ok).
Correção/reteste ou pendência: mutação de teste (memória deixando de reaproveitar o contador de ID) foi detectada pelo verificador.

T03 — Memória começa vazia numa nova instância; SQLite reabre com dados.
Previsão: `RepositorioMemoria()` novo lista `[]`; `RepositorioSqlite` reaberto no mesmo arquivo traz Lia e Picolé (300 centavos).
Observado: confere (T03 ok).
Correção/reteste ou pendência: sem correção.

T04 — Editar/excluir clientes mantém alvo por ID.
Previsão: com Ana(1), Bruno(2), Carla(3): excluir o ID 2 e editar o ID 3 altera "Carla" (e não a segunda linha);
o próximo cliente recebe ID 4 (o 2 não volta); excluir/editar o ID 2 de novo é recusado.
Observado: lista final `[1 Ana, 3 Carla Souza]`, depois `[1, 3, 4]`; as duas recusas ocorreram (T04 ok), em memória e em SQLite.
Correção/reteste ou pendência: sem correção.

T05 — Cancelar exclusão de cliente não altera banco nem lista.
Previsão: `excluir(..., confirmado=False)` levanta erro e a lista continua `[{id 1, "Ana"}]`; na janela, responder "Não" não chama o controller.
Observado: controller recusou e a lista não mudou (T05 ok); na janela (T09) a tabela e o banco ficaram iguais após cancelar.
Correção/reteste ou pendência: sem correção.

T06 — Tipo de cadastro desconhecido é rejeitado.
Previsão: `listar/salvar/excluir("fornecedor", ...)` levantam "Tipo de cadastro desconhecido" sem tocar nos dados.
Observado: as três operações foram recusadas e o cliente existente permaneceu (T06 ok). Mutação (aceitar qualquer tipo) foi detectada.
Correção/reteste ou pendência: sem correção.

T07 — Falha do repositório é comunicada e conserva formulário.
Previsão: se o repositório falha, o erro chega à janela, aparece em caixa de erro e os campos digitados continuam preenchidos.
Observado: o controller propagou a falha simulada (T07 ok); na janela, nome em branco gerou caixa de erro, o campo continuou como digitado e,
após corrigir para "Bia", o salvamento funcionou (parte do T09).
Correção/reteste ou pendência: mutação (limpar os campos na falha) foi detectada pelo verificador.

T08 — Cópia retornada pela memória não permite alterar o armazenamento por fora.
Previsão: alterar o nome ou o preço na lista devolvida e acrescentar um item "intruso" não muda o que `listar_*` devolve depois.
Observado: o armazenamento continuou `[{id 1, "Ana"}]` e `[{id 1, "Sorvete", 500}]` (T08 ok). Mutação (sem `deepcopy`) foi detectada.
Correção/reteste ou pendência: sem correção.

T09 — Componentes mantêm campos/seleções independentes.
Previsão: um rascunho no painel de produtos não é afetado por salvar um cliente; selecionar na tabela de clientes não muda a seleção de produtos.
Observado: confere sob Xvfb (T09 ok): rascunho preservado, `codigo_selecionado` independente em cada painel.
Correção/reteste ou pendência: executado em ambiente gráfico virtual; **[PREENCHER]** confirmar uma vez à mão no seu Windows.

Extras (erro depois de caso válido, limites e correção): preço 0,01 e 100.000,00 aceitos; 0, negativo, "abc", vazio e 100.000,01 recusados
sem gravar nada; correção na nova tentativa gravou (Extras ok).

## Explicação individual
Uma decisão que consigo justificar: *(rascunho — reescreva)* separei o `controller` da janela e fiz o `PainelCadastro` receber o tipo e os campos como
parâmetros. Assim o mesmo componente serve para produtos e clientes e posso testar a lógica sem abrir nenhuma janela.
Uma dificuldade, apoio e próxima tentativa: *(rascunho — ajuste ao que for verdade para você)* ao reaproveitar a A15 percebi que o `modelos.py`
da A15 estava quebrado (`Produto` e `Item` usavam `self.preco_centavos`/`self.qtd` antes de atribuir), então usei a versão da A14,
que funciona. Usei um assistente de IA como apoio para montar e testar esta etapa. Próxima tentativa: **[PREENCHER]**

## Arquivos
Versão executada e arquivos baixados: `main.py`, `controller.py`, `memoria.py`, `repositorio.py`, `modelos.py`, `pagamento.py`, `arquivos.py`, `perfis.py`, `relatorios.py`, `verificar.py`.
Caminho de dados fictícios usado (se houver): `dados_pizzaria.db` (criado ao lado do `main.py` na primeira execução com SQLite); com `--memoria` nenhum arquivo é criado.
Entrega pelo fluxo combinado conferida por mim: **[PREENCHER]**

## Teoria e transferência
Consigo seguir uma chamada da interface ao controller e ao repositório.
Minha explicação: *(rascunho)* Salvar → `PainelCadastro.salvar()` lê os campos → `CadastroController.salvar(tipo, nome, preco_texto, codigo)` →
converte o preço em centavos com `preco_para_centavos` → chama `adicionar_*` (se `codigo` é None) ou `editar_*` → o repositório valida e grava → o controller devolve `{"acao", "id"}` → a janela atualiza a tabela.
Consigo descrever o contrato e o que fica igual nas duas implementações.
Minha explicação: *(rascunho)* mesmos nomes de método, mesmos parâmetros, mesmo formato de retorno (IDs inteiros, listas de dicionários ordenadas) e mesmos erros (`ValueError`).
Consigo distinguir a duração dos dados em memória e SQLite.
Minha explicação: *(rascunho)* memória: some quando o objeto some; SQLite: fica no arquivo e volta ao reabrir (T03).
Ligação entre o ensaio e meus arquivos da atividade: **[PREENCHER]**
Minha previsão antes da alteração guiada e o resultado observado: **[PREENCHER — depende do ensaio feito em sala]**

## Continuação em casa
Arquivos/versão executados: os listados em "Arquivos".
Pasta e comando usados: na pasta da aula, `python verificar.py` (tela real ou virtual) e `python main.py` / `python main.py --memoria`.
Justificativa de 5–8 linhas ou nome do áudio de cerca de 60 segundos: **[PREENCHER]**
Decisão do meu código sobre controller, contrato de repositório, componentes e conclusão do CRUD de clientes: *(rascunho)* o controller não conhece Tkinter; o contrato garante que memória e SQLite são trocáveis; o componente é um só para dois cadastros; clientes agora editam e excluem por ID, com confirmação.
Minha explicação / anexo: **[PREENCHER]**

## Checklist da interface
Controles e rótulos que conferi: abas Catálogo e Clientes; rótulos "Nome do item", "Preço por unidade (R$)", "Nome da pessoa cliente"; botões Salvar/Novo/Excluir; indicador "Modo: novo item" / "Editando item ID n". Conferido em captura de tela sob Xvfb.
Percurso por Tab/Shift+Tab e acionamento: Medido com eventos (Tk 8.6): o Tab percorre campo → campo → botões; **Espaço** aciona o botão em foco e **Enter não aciona `ttk.Button`** (Enter só salva dentro dos campos, por causa do `bind`). O texto de ajuda da janela já diz isso. **[PREENCHER]** confirmar à mão no Windows.
Mensagem após erro e possibilidade de corrigir: erro mostra caixa e linha vermelha; os campos continuam preenchidos para corrigir (T07/T09).
Redimensionamento e comportamento que observei: tabela e campos usam `sticky`/`weight` e acompanham a janela. **[PREENCHER]** confirmar arrastando a borda da janela.

## Pendências
O que não executei e por quê, incluindo falta de ambiente: não rodei no seu Windows nem com tela física; interação manual por mouse/teclado, redimensionamento e entrega no fluxo combinado ficam por sua conta.
Caso para nova tentativa em sala: T09 com tela real.
