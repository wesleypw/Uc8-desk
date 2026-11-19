# Minha sorveteria — candidata A18

## Objetivo e limites
**Implementado**
- Cadastro de produtos e de clientes (incluir, editar por ID, excluir com confirmação), em SQLite.
- Venda: escolher cliente, montar itens, revisar preço/catálogo, escolher a forma de pagamento (PIX/Débito/Crédito) e finalizar.
- A venda e os itens são gravados **na mesma transação**: ou grava tudo, ou nada. Depois de gravar, o comprovante é criado e a finalização repetida é bloqueada.
- Cadastro vinculado a uma venda não pode ser excluído (chaves estrangeiras do SQLite).
- Exportação do CSV a partir do comprovante da venda.

**Ainda falta / limites**
- A janela não tem tela de histórico de vendas (`RepositorioSqlite.listar_vendas()` existe, mas só é usado nos testes).
- A janela não tem botão de alterar a quantidade de um item (remova e adicione de novo); o controller já tem `alterar_quantidade`.
- `RepositorioMemoria` só cobre cadastros: a venda exige o SQLite.
- `perfis.py` e `arquivos.py` vêm das aulas anteriores e estão na pasta, mas a janela atual não os usa.
- Dados fictícios apenas: não há login nem proteção de dados pessoais reais.

## Ambiente
Python e biblioteca gráfica usados: Python 3.12 (executado na versão 3.12.3), Tkinter/ttk com Tk 8.6.
Dependências efetivamente necessárias: somente a biblioteca padrão (`tkinter`, `sqlite3`, `csv`, `decimal`).
No Linux o Tkinter pode exigir o pacote do sistema `python3-tk`. O CustomTkinter (`pip install customtkinter`) é
**opcional** e só serve para `comparar_ctk.py`; sem ele, todo o resto funciona.

## Arquivos e execução
Estrutura da minha pasta:
```
main.py            janela principal (abas Venda, Catálogo, Clientes)
tela_venda.py      painel de venda
componentes.py     Dialogos e PainelCadastro (reutilizáveis)
controller.py      CadastroController e VendaController (sem tkinter)
repositorio.py     RepositorioSqlite (cadastros, vendas, itens)
memoria.py         RepositorioMemoria (mesmo contrato dos cadastros)
modelos.py  pagamento.py  arquivos.py  perfis.py  relatorios.py   módulos das aulas anteriores
comparar_ctk.py    comparação ttk x CustomTkinter (opcional)
verificar.py       regressão automática
README-A18.md      este arquivo
```
Comando, a partir de qual pasta: abra o terminal **na pasta que contém `main.py`** (o PowerShell, o Prompt ou o terminal do editor) e rode:
```
python verificar.py
python main.py
```
(No Linux/macOS pode ser `python3`.)

Caminho do banco fictício: `dados.db`, criado ao lado do `main.py` na primeira execução.
Os testes **nunca** usam esse arquivo: criam bancos temporários.

Como iniciar uma cópia de ensaio sem apagar a original:
```
python main.py --banco ensaio.db
```
usa (e cria, se não existir) outro arquivo. Para ensaiar com os mesmos dados, copie o banco antes
(`Copy-Item dados.db ensaio.db` no PowerShell; `cp dados.db ensaio.db` no Linux/macOS) e abra a cópia com `--banco`.

## Verificação
Comandos e resultados reais:
- `python verificar.py` imprime uma linha `T01 ok …` até `T08 ok …`, a lista de itens **não verificados por script**
  e termina com `Casos executados: previsões e resultados conferem.` Se não houver ambiente gráfico, o T08 aparece como
  `PENDENTE` e a última linha passa a ser `Verificações ainda incompletas`.
- Executado aqui (Python 3.12.3, Linux, tela virtual Xvfb): todos os casos T01–T08 passaram; o T07 repete a execução numa pasta de cópia.

Uma falha, a correção e o reteste:
- Ao reaproveitar a A15, o `verificar.py` dela falhou com `AttributeError: 'Produto' object has no attribute 'preco_centavos'`:
  no `modelos.py` da A15, `Produto.__init__` e `Item.__init__` usavam `self.preco_centavos`/`self.qtd` antes de atribuí-los.
  Correção: voltei ao `modelos.py` da A14 (que funciona) e o estendi com `total_pago_centavos`/`venda_id` em `Pedido.finalizar`.
  Reteste: `python verificar.py` (T01, T05 e T08 criam produtos e itens) passou.

Como conferir os relatórios:
- Finalize uma venda na aba Venda e clique em **Exportar CSV**. Abra no Excel/LibreOffice (separador `;`, UTF-8).
- Colunas: `ID;Nome;Quantidade;Preco_Unitario_Centavos;Subtotal_Centavos;Forma_Pagamento;Total_Pedido_Formatado`.
- A soma da coluna `Subtotal_Centavos` é o subtotal antes do desconto da forma de pagamento; a coluna `Total_Pedido_Formatado`
  repete o total pago. Exemplo conferido nos testes: 2 × R$ 6,50 + 1 × R$ 15,90 = 28,90 → PIX (×0,87) = **R$ 25,14**.

## Pendências
Não verificado por mim/por script:
- Execução pelo README por outra pessoa, no computador dela (o T07 só prova que uma cópia em outra pasta roda aqui).
- Teste manual com mouse, teclado físico e redimensionamento no Windows (no ensaio só foi usado Xvfb).
- Conferência da entrega pelo fluxo combinado.
