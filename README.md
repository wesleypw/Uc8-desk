# UC8 - Aulas de Python e Sistemas

Este repositório reúne as atividades e mini projetos desenvolvidos durante as aulas do curso UC8. A organização está em pastas por aula, e cada pasta funciona como um projeto independente.

## Como usar este repositório

1. Abra o terminal no diretório raiz do projeto.
2. Navegue até a pasta da aula desejada.
3. Execute o arquivo principal com Python.

Exemplo:

```bash
cd aulas/aula-03-conversor-de-moedas
python a03.py
```

Se o seu ambiente usar `python3` no lugar de `python`, substitua o comando:

```bash
python3 a03.py
```

Importante:
- Cada pasta é um exercício separado.
- Alguns projetos usam somente Python puro.
- Alguns usam Tkinter, SQLite e arquivos CSV.
- Não execute todos os arquivos ao mesmo tempo; cada aula pode depender do contexto da pasta.

---

## Estrutura geral

```text
UC8/
├── README.md
└── aulas/
    ├── aula-02-cadastro-em-memoria/
    ├── aula-03-conversor-de-moedas/
    ├── aula-04-media-escolar/
    ├── aula-05-organizacao-sistema-escolar/
    ├── aula-06-objetos-e-modulos/
    ├── aula-07-produtos-e-pedidos/
    ├── aula-08-pedidos-e-pagamentos/
    ├── aula-09-atualizacao-e-remocao/
    ├── aula-10-pizzaria-modelo-de-pedido/
    ├── aula-11-pizzaria-ciclo-do-pedido/
    ├── aula-12-catalogo-json/
    ├── aula-13-relatorios-csv-e-perfis/
    ├── aula-14-persistencia-sqlite/
    ├── aula-15-crud-produtos-e-clientes/
    ├── aula-16-controllers-coponentes-e-contratos/
    ├── aula-17-integracao-e-customtkinter/
    ├── aula-18-revisao-teste-e-readme/
    └── aula-19-academia-e-demonstracoes-individuais/
```

---

## Instruções por aula

### aula-02-cadastro-em-memoria

Arquivo principal:
- `a02.py` — cadastro em memória de dados simples, usado para praticar estruturas básicas e manipulação de listas.

Como executar:
```bash
cd aulas/aula-02-cadastro-em-memoria
python a02.py
```

### aula-03-conversor-de-moedas

Arquivo principal:
- `a03.py` — conversor de valores monetários; serve para praticar entrada de dados, regras de negócio e cálculos.

Como executar:
```bash
cd aulas/aula-03-conversor-de-moedas
python a03.py
```

### aula-04-media-escolar

Arquivo principal:
- `a04.py` — cálculo de média escolar com base em notas, útil para exercitar condicionais, listas e validações.

Como executar:
```bash
cd aulas/aula-04-media-escolar
python a04.py
```

### aula-05-organizacao-sistema-escolar

Arquivos:
- `escolar_grupos.py` — lógica de organização e agrupamento dos dados escolares.
- `escolar_janelas.py` — versão com interface gráfica, utilizando janelas e interações visuais.
- `registro-a05.md` — anotações da aula e evolução do sistema.

Como executar:
```bash
cd aulas/aula-05-organizacao-sistema-escolar
python escolar_janelas.py
```

### aula-06-objetos-e-modulos

Arquivos:
- `aluno.py` — definição da classe `Aluno` e comportamento relacionado ao aluno.
- `main.py` — arquivo principal para testar e utilizar a estrutura do sistema.
- `verificar_modelo.py` — validações e checagens de consistência do modelo.
- `registro-a06.md` e `registro-a06-2026-09-05.md` — registros da aula e evolução do projeto.

Como executar:
```bash
cd aulas/aula-06-objetos-e-modulos
python main.py
```

### aula-07-produtos-e-pedidos

Arquivos:
- `main.py` — aplicação principal do sistema de produtos e pedidos.
- `modelos.py` — classes e estruturas do domínio do projeto.
- `verificar.py` — script de verificação e validação funcional.
- `registro-a07.md` e `registro-a07-2026-11-01.md` — registros do conteúdo da aula.

Como executar:
```bash
cd aulas/aula-07-produtos-e-pedidos
python main.py
```

### aula-08-pedidos-e-pagamentos

Arquivos:
- `main.py` — execução principal do fluxo de pedidos.
- `modelos.py` — modelos do domínio, incluindo pedidos e itens.
- `pagamento.py` — regras de cálculo e formas de pagamento.
- `registro-a08.md` e `registro-a08-2026-11-02.md` — registros e observações da aula.
- `verificar.py` — testes rápidos para confirmar o funcionamento.

Como executar:
```bash
cd aulas/aula-08-pedidos-e-pagamentos
python main.py
```

### aula-09-atualizacao-e-remocao

Arquivos:
- `main.py` — fluxo principal de atualização e remoção de dados.
- `modelos.py` — modelos do sistema.
- `pagamento.py` — cálculos e regras de pagamento.
- `registro-a09.md` e `registro-a09-2026-11-02.md` — documentação e registros da aula.
- `verificar.py` — testes e validações.

Como executar:
```bash
cd aulas/aula-09-atualizacao-e-remocao
python main.py
```

### aula-10-pizzaria-modelo-de-pedido

Arquivos:
- `main.py` — aplicação principal da pizzaria.
- `modelos.py` — classes e entidades do sistema.
- `pagamento.py` — cálculo de pagamentos.
- `comparar_pysimplegui.py` — comparação da interface em PySimpleGUI.
- `registro-a10.md` e `registro-a10-2026-11-04.md` — registros da aula.
- `verificar.py` — checagem funcional.

Como executar:
```bash
cd aulas/aula-10-pizzaria-modelo-de-pedido
python main.py
```

### aula-11-pizzaria-ciclo-do-pedido

Arquivos:
- `main.py` — execução do ciclo completo do pedido.
- `modelos.py` — modelos principais.
- `pagamento.py` — regras financeiras e formas de pagamento.
- `registro-a11.md` e `registro-a11-2026-11-04.md` — documentação do desenvolvimento.
- `verificar.py` — validação do comportamento do sistema.

Como executar:
```bash
cd aulas/aula-11-pizzaria-ciclo-do-pedido
python main.py
```

### aula-12-catalogo-json

Arquivos:
- `main.py` — aplicação principal do catálogo.
- `modelos.py` — classes do domínio.
- `pagamento.py` — lógica de pagamento.
- `arquivos.py` — leitura e escrita de arquivos, incluindo JSON.
- `registro-a12.md` e `registro-a12-2026-11-05.md` — registros da aula.
- `verificar.py` — testes do catálogo.

Como executar:
```bash
cd aulas/aula-12-catalogo-json
python main.py
```

### aula-13-relatorios-csv-e-perfis

Arquivos:
- `main.py` — aplicação principal.
- `modelos.py` — entidade do sistema.
- `pagamento.py` — regras de pagamento.
- `perfis.py` — gerenciamento de perfis e configuração de usuários.
- `arquivos.py` — manipulação de arquivos e dados.
- `relatorios.py` — geração de relatórios em CSV e outros formatos.
- `registro-a13.md` e `registro-a13-2026-11-09.md` — registros da aula.
- `verificar.py` — teste funcional da entrega.

Como executar:
```bash
cd aulas/aula-13-relatorios-csv-e-perfis
python main.py
```

### aula-14-persistencia-sqlite

Arquivos:
- `main.py` — aplicação principal do sistema.
- `modelos.py` — entidades e regras do domínio.
- `pagamento.py` — decisões de pagamento.
- `perfis.py` — perfis e contextualização do sistema.
- `arquivos.py` — leitura/escrita de arquivos.
- `relatorios.py` — relatórios.
- `repositorio.py` — camada de persistência em SQLite.
- `registro-a14.md` e `registro-a14-2026-11-10.md` — registros da aula.
- `verificar.py` — validação do banco e fluxo do sistema.

Como executar:
```bash
cd aulas/aula-14-persistencia-sqlite
python main.py
```

### aula-15-crud-produtos-e-clientes

Arquivos:
- `main.py` — aplicação principal.
- `modelos.py` — modelos do domínio.
- `pagamento.py` — pagamentos.
- `perfis.py` — perfis.
- `arquivos.py` — manipulação de arquivos.
- `relatorios.py` — relatórios.
- `repositorio.py` — acesso ao banco SQLite.
- `tela_clientes.py` — interface para cadastro e edição de clientes.
- `tela_produtos.py` — interface para cadastro e edição de produtos.
- `dados_pizzaria.db` — banco de dados SQLite usado pelos testes e execução.
- `registro-a15.md` e `registro-a15-2026-11-10.md` — registros da aula.
- `verificar.py` — checagem da funcionalidade do CRUD.

Como executar:
```bash
cd aulas/aula-15-crud-produtos-e-clientes
python main.py
```

### aula-16-controllers-coponentes-e-contratos

Arquivos:
- `main.py` — aplicação principal da entrega.
- `controller.py` — controle de regras de negócio e ações.
- `memoria.py` — implementação em memória do repositório.
- `modelos.py` — entidades do sistema.
- `pagamento.py` — regras do pagamento.
- `perfis.py` — perfis e filtros.
- `arquivos.py` — manipulação de arquivos e integração de dados.
- `relatorios.py` — relatórios e exportações.
- `repositorio.py` — abstração de dados e persistência.
- `verificar.py` — validação do fluxo.
- `registro-a16.md` — registro da aula.

Como executar:
```bash
cd aulas/aula-16-controllers-coponentes-e-contratos
python main.py
```

### aula-17-integracao-e-customtkinter

Arquivos:
- `main.py` — aplicação principal.
- `comparar_ctk.py` — comparação entre Tkinter e CustomTkinter.
- `componentes.py` — componentes reutilizáveis da interface.
- `controller.py` — regras e controllers.
- `memoria.py` — armazenamento temporário em memória.
- `modelos.py` — classes do domínio.
- `pagamento.py` — lógica de pagamento.
- `perfis.py` — perfis do sistema.
- `relatorios.py` — geração de relatórios.
- `repositorio.py` — camada de persistência.
- `tela_venda.py` — painel da venda.
- `verificar.py` — testes do projeto.
- `registro-a17.md` — registro da aula.

Como executar:
```bash
cd aulas/aula-17-integracao-e-customtkinter
python main.py
```

### aula-18-revisao-teste-e-readme

Arquivos:
- `main.py` — janela principal com abas de venda, catálogo e clientes.
- `tela_venda.py` — painel de venda e montagem do pedido.
- `componentes.py` — diálogos e componentes reutilizáveis da interface.
- `controller.py` — controllers de cadastro e venda.
- `repositorio.py` — acesso a SQLite para cadastros e vendas.
- `memoria.py` — armazenamento em memória para testes e comparação.
- `modelos.py` — modelos do domínio.
- `pagamento.py` — cálculos e regras de pagamento.
- `arquivos.py` — manipulação de arquivos e exportações.
- `perfis.py` — perfis e contexto do sistema.
- `relatorios.py` — geração de relatórios.
- `comparar_ctk.py` — comparação de interface com CustomTkinter.
- `verificar.py` — suíte de testes automatizados.
- `README-A18.md` — instruções específicas da atividade A18.
- `registro-a18.md` — registro da aula.

Como executar:
```bash
cd aulas/aula-18-revisao-teste-e-readme
python verificar.py
python main.py
```

### aula-19-academia-e-demonstracoes-individuais

Arquivos:
- `main.py` — aplicação principal da demonstração.
- `academia_amostra.py` — modelo de demonstração de academia.
- `arquivos.py` — manipulação de arquivos.
- `backup_sqlite.py` — backup do banco SQLite.
- `componentes.py` — componentes reutilizáveis.
- `controller.py` — controle dos fluxos do sistema.
- `demo_candidata.py` — demonstração individual/ensaios.
- `entrega.py` — entrega final do projeto.
- `memoria.py` — implementação em memória.
- `modelos.py` — entidades e regras do domínio.
- `pagamento.py` — processamento de pagamentos.
- `perfis.py` — perfis do sistema.
- `relatorios.py` — relatórios.
- `repositorio.py` — persistência de dados.
- `tela_venda.py` — painel de venda.
- `verificar.py` — validações e testes.
- `roteiro-demo.md` — roteiro para demonstração.
- `registro-a19.md` — registro da aula.

Como executar:
```bash
cd aulas/aula-19-academia-e-demonstracoes-individuais
python main.py
```

---

## Dicas gerais

- O ambiente ideal é Python 3.10+.
- Para projetos com interface gráfica, pode ser necessário instalar ou confirmar o Tkinter.
- Em algumas aulas, há dependência do banco SQLite, então verifique se a pasta do projeto possui o arquivo `.db` ou se ele será criado na execução.
- Para aprender melhor, execute as aulas em ordem: de `aula-02` até `aula-19`.
- Os arquivos `registro-*.md` são anotações de aula e ajudam a entender o contexto do projeto.

---

## Observação final

Este repositório foi organizado como material didático. Cada aula é uma etapa do aprendizado, partindo de lógica simples até sistemas com interfaces gráficas, banco de dados, relatórios e testes. O melhor caminho é abrir a pasta da aula, ler o arquivo principal e os registros e, em seguida, rodar o projeto em execução.
