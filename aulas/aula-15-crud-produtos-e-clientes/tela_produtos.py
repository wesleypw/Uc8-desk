import tkinter as tk
from tkinter import messagebox, ttk

from repositorio import RepositorioSqlite


def criar_aba_produtos(notebook, repo: RepositorioSqlite):
    aba_produtos = ttk.Frame(notebook, padding=12)
    aba_produtos.columnconfigure(1, weight=1)
    aba_produtos.rowconfigure(4, weight=1)
    notebook.add(aba_produtos, text=" CRUD de Produtos ")

    ttk.Label(aba_produtos, text="Nome do Produto:").grid(
        row=0, column=0, sticky="w", pady=4
    )
    entry_nome_prod = ttk.Entry(aba_produtos)
    entry_nome_prod.grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=4)

    ttk.Label(aba_produtos, text="Preço Unitário (R$):").grid(
        row=1, column=0, sticky="w", pady=4
    )
    entry_preco_prod = ttk.Entry(aba_produtos)
    entry_preco_prod.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=4)

    lbl_modo_prod = ttk.Label(
        aba_produtos,
        text="Modo: Inclusão de Novo Produto",
        foreground="blue",
        font=("Arial", 9, "bold"),
    )
    lbl_modo_prod.grid(row=2, column=0, columnspan=2, sticky="w", pady=4)

    aviso_produtos = ttk.Label(
        aba_produtos,
        text="Selecione um item na tabela para editar/excluir ou preencha para incluir.",
        foreground="gray",
    )
    aviso_produtos.grid(row=3, column=0, columnspan=2, sticky="w", pady=4)

    colunas_prod = ("id", "nome", "preco_centavos")
    tabela_produtos = ttk.Treeview(
        aba_produtos, columns=colunas_prod, show="headings", height=7
    )
    tabela_produtos.heading("id", text="ID")
    tabela_produtos.heading("nome", text="Nome do Produto")
    tabela_produtos.heading("preco_centavos", text="Preço (Centavos)")
    tabela_produtos.column("id", width=60, anchor="center")
    tabela_produtos.column("nome", width=280, anchor="w")
    tabela_produtos.column("preco_centavos", width=120, anchor="e")
    tabela_produtos.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=6)

    scroll_prod = ttk.Scrollbar(
        aba_produtos, orient="vertical", command=tabela_produtos.yview
    )
    tabela_produtos.configure(yscrollcommand=scroll_prod.set)
    scroll_prod.grid(row=4, column=2, sticky="ns", pady=6)

    id_produto_selecionado = tk.IntVar(value=0)

    def atualizar_listagem_produtos():
        """Atualiza a tabela de produtos consultando o SQLite."""
        for item in tabela_produtos.get_children():
            tabela_produtos.delete(item)
        for produto in repo.listar_produtos():
            tabela_produtos.insert(
                "",
                "end",
                iid=produto["id"],
                values=(
                    produto["id"],
                    produto["nome"],
                    produto["preco_centavos"],
                ),
            )

    def limpar_formulario_produtos():
        """Reseta o formulário para o modo de inclusão."""
        id_produto_selecionado.set(0)
        entry_nome_prod.delete(0, tk.END)
        entry_preco_prod.delete(0, tk.END)
        lbl_modo_prod.configure(
            text="Modo: Inclusão de Novo Produto", foreground="blue"
        )
        aviso_produtos.configure(
            text="Preencha os dados e clique em Salvar.", foreground="gray"
        )
        entry_nome_prod.focus_set()

    def ao_selecionar_produto(event):
        """Carrega o produto selecionado no formulário para edição."""
        selecao = tabela_produtos.selection()
        if not selecao:
            return

        item_id = int(selecao[0])
        produto = next(
            (item for item in repo.listar_produtos() if item["id"] == item_id),
            None,
        )
        if produto:
            id_produto_selecionado.set(produto["id"])
            entry_nome_prod.delete(0, tk.END)
            entry_nome_prod.insert(0, produto["nome"])
            entry_preco_prod.delete(0, tk.END)
            entry_preco_prod.insert(
                0, f"{produto['preco_centavos'] / 100:.2f}".replace(".", ",")
            )
            lbl_modo_prod.configure(
                text=f"Modo: Editando Produto ID {produto['id']}",
                foreground="darkorange",
            )
            aviso_produtos.configure(
                text="Altere os campos e clique em Salvar ou clique em Novo.",
                foreground="black",
            )

    tabela_produtos.bind("<<TreeviewSelect>>", ao_selecionar_produto)

    def salvar_produto():
        """Inclui um produto ou atualiza o produto selecionado."""
        nome = entry_nome_prod.get()
        preco_txt = entry_preco_prod.get()
        id_atual = id_produto_selecionado.get()

        try:
            if id_atual == 0:
                novo_id = repo.adicionar_produto(nome, preco_txt)
                messagebox.showinfo(
                    "Sucesso", f"Produto cadastrado com sucesso (ID: {novo_id})."
                )
            else:
                repo.editar_produto(id_atual, nome, preco_txt)
                messagebox.showinfo(
                    "Sucesso", f"Produto ID {id_atual} atualizado com sucesso."
                )

            atualizar_listagem_produtos()
            limpar_formulario_produtos()
        except Exception as erro:
            messagebox.showerror(
                "Erro de Operação", f"Não foi possível salvar o produto:\n{erro}"
            )
            aviso_produtos.configure(text=f"Erro: {erro}", foreground="red")

    def excluir_produto_selecionado():
        """Exclui o produto selecionado após confirmação explícita."""
        id_atual = id_produto_selecionado.get()
        if id_atual == 0:
            messagebox.showwarning(
                "Aviso", "Selecione um produto na tabela para excluir."
            )
            return

        confirmado = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o produto ID {id_atual}?",
        )
        if confirmado:
            try:
                repo.excluir_produto(id_atual, confirmado=True)
                messagebox.showinfo(
                    "Excluído", f"Produto ID {id_atual} removido com sucesso."
                )
                atualizar_listagem_produtos()
                limpar_formulario_produtos()
            except Exception as erro:
                messagebox.showerror("Erro", f"Falha ao excluir:\n{erro}")

    frame_botoes_prod = ttk.Frame(aba_produtos)
    frame_botoes_prod.grid(
        row=5, column=0, columnspan=2, sticky="ew", pady=(6, 0)
    )
    frame_botoes_prod.columnconfigure((0, 1, 2), weight=1)

    ttk.Button(frame_botoes_prod, text="Salvar", command=salvar_produto).grid(
        row=0, column=0, sticky="ew", padx=2
    )
    ttk.Button(
        frame_botoes_prod, text="Novo", command=limpar_formulario_produtos
    ).grid(row=0, column=1, sticky="ew", padx=2)
    ttk.Button(
        frame_botoes_prod,
        text="Excluir",
        command=excluir_produto_selecionado,
    ).grid(row=0, column=2, sticky="ew", padx=2)

    atualizar_listagem_produtos()
    return aba_produtos
