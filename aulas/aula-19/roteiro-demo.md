# Minha demonstração individual — A19

> Tudo o que está descrito abaixo foi **executado** nesta pasta (Python 3.12.3). Onde aparece
> **[PREENCHER]**, o texto precisa da sua voz ou de algo que só você observa na sua máquina.

## Demonstração do fluxo
Problema e requisito escolhido: registrar a venda de 2 casquinhas para uma cliente pagando no PIX, e a venda só ser considerada feita se o banco gravar tudo (venda + itens na mesma transação).

Arquivos/caminho e comando: abra o terminal **na pasta A19** (a que contém `demo_candidata.py`) e rode:
```
python demo_candidata.py          # percurso sem janela, em banco temporário (nada fica salvo)
python main.py --banco ensaio.db  # a mesma candidata com janela, em banco de ensaio
python verificar.py               # confere a demonstração, o backup e a entrega
```
A versão demonstrada é a candidata validada na A18 (mesmos `controller.py`, `repositorio.py` e `tela_venda.py`).

Fluxo válido com dados fictícios: criar a cliente "Ana (fictícia)" e a "Casquinha" a 6,50; montar 2 unidades; a prévia mostra
subtotal 1300 centavos e total **1131** (PIX, ×0,87); finalizar grava a **venda 1** e o comprovante diz **R$ 11,31**.
*O que a pessoa deve observar:* a linha `venda 1 gravada: R$ 11,31` aparece só depois que o banco confirmou.

Caso de erro ou cancelamento: em uma nova venda, adicionar quantidade **0** é recusado ("Quantidade inválida. Informe um número inteiro positivo."); informar **2** corrige.
Finalizar sem escolher a cliente também é recusado ("Selecione o cliente da venda antes de finalizar."); escolher a cliente e finalizar no Débito grava a **venda 2** (1196 centavos).
Na janela, responder "Não" à confirmação preserva a montagem e não grava nada.

Persistência e relatório: reabrir o arquivo mostra `venda 1 PIX total 1131; venda 2 Débito total 1196`.
O CSV exportado da última venda tem a linha `1;Casquinha;2;650;1300;Débito;R$ 11,96`.

Limite e próximo teste: a janela ainda não tem tela de histórico de vendas nem botão para alterar a quantidade de um item, e a execução aqui foi sem mouse/teclado reais. Próximo teste: repetir `python main.py --banco ensaio.db` à mão no Windows, finalizar uma venda e conferir o CSV exportado.

## Pergunta técnica individual
Decisão que consigo explicar com código/evidência: *(rascunho — reescreva)* gravar a venda e os itens na mesma transação em
`repositorio.py` (`registrar_venda`, bloco `with con:`). Evidência: em `verificar.py` da A18 (T04), uma venda com um item de produto inexistente deixou 0 vendas e 0 itens;
quando o commit foi movido para dentro do laço (defeito controlado), o teste acusou `esperado (0, 0), obtido (1, 2)`.
**[PREENCHER]** diga com suas palavras por que isso importa para quem usa o sistema.

## Comparação com academia
Entidades e IDs observados: alunos 41 (Lia fictícia) e 92 (Rui fictício); plano 7 (valor 10000 centavos); matrícula 101 ligando aluno 41 ao plano 7.
Camadas e armazenamento comprovados pela leitura: o arquivo traz comentários de `models/` (entidades e vínculos por ID), `utils/persistencia.py` (só `representar_json`),
`controllers/` (`consultar_matricula`, que devolve uma cópia) e `views/` (apenas comentário). O armazenamento comprovado é **listas em memória** e uma representação em JSON.
Respostas às duas perguntas da amostra (conferidas em `verificar.py`, T04): excluir o aluno 41 deixaria a matrícula 101 órfã, então faltaria uma regra de vínculo;
corrigir só o nome de Lia não exige outro ID, porque o vínculo usa `aluno_id = 41`.
O que não pude afirmar somente pelo README: que existam janelas, banco de dados ou arquivos reais na academia — a amostra não tem Tkinter, SQLite nem leitura/escrita de arquivo, e não é o sistema original completo.

## Backup em cópia
Ao abrir o programa, `dados.db` não atualiza `copia-nova.db` automaticamente. Cada cadastro, edição, exclusão ou venda altera somente o banco ativo. Para atualizar a cópia, execute o comando de backup manual. Se a execução usar `--banco CAMINHO.db`, informe essa origem ao comando de backup.
Também é possível executar `python backup_sqlite.py`: o script compara o banco padrão com `copia-nova.db` e só atualiza a cópia se estiver ausente ou diferente. Para indicar outros bancos, use `python backup_sqlite.py origem.db copia.db`; os caminhos relativos apontam para a pasta atual do terminal. Confira as linhas `Origem` e `Cópia` exibidas pelo comando para confirmar os arquivos usados.
Segurança da atualização: a nova cópia é criada em arquivo temporário e verificada antes de substituir o destino. Se a origem não existir ou ocorrer uma falha, o backup anterior permanece intacto. A origem nunca é substituída. Se o Windows informar que não foi possível atualizar, feche programas que estejam usando o arquivo de backup e tente novamente.
Consulta de dados conhecidos na cópia: por outra conexão, `PRAGMA integrity_check` → `ok`; `SELECT id, nome FROM clientes WHERE id = 2` → `(2, 'Rui fictício')`.
Ao adicionar dados na origem e executar novamente o mesmo comando com `copia-nova.db`, os novos dados também aparecem no backup atualizado.
Próxima ação após feedback: **[PREENCHER]** (o feedback ainda não foi recebido).
