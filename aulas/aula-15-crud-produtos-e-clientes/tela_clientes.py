import tkinter as tk
from tkinter import messagebox, ttk

from repositorio import RepositorioSqlite


def criar_aba_clientes(notebook, repo: RepositorioSqlite):
    aba_clientes = ttk.Frame(notebook, padding=12)
    aba_clientes.columnconfigure(1, weight=1)
    aba_clientes.rowconfigure(2, weight=1)
    notebook.add(aba_clientes, text=" Gestão de Clientes ")

    ttk.Label(aba_clientes, text="Nome do Cliente:").grid(
        row=0, column=0, sticky="w", pady=4
    )
    entry_nome_cli = ttk.Entry(aba_clientes)
    entry_nome_cli.grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=4)

    colunas_cli = ("id", "nome")
    tabela_clientes = ttk.Treeview(
        aba_clientes, columns=colunas_cli, show="headings", height=8
    )
    tabela_clientes.heading("id", text="ID")
    tabela_clientes.heading("nome", text="Nome do Cliente")
    tabela_clientes.column("id", width=60, anchor="center")
    tabela_clientes.column("nome", width=380, anchor="w")
    tabela_clientes.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=6)

    def atualizar_listagem_clientes():
        for item in tabela_clientes.get_children():
            tabela_clientes.delete(item)
        for cliente in repo.listar_clientes():
            tabela_clientes.insert(
                "",
                "end",
                iid=cliente["id"],
                values=(cliente["id"], cliente["nome"]),
            )

    def salvar_cliente():
        nome = entry_nome_cli.get()
        try:
            repo.adicionar_cliente(nome)
            atualizar_listagem_clientes()
            entry_nome_cli.delete(0, tk.END)
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso.")
        except Exception as erro:
            messagebox.showerror(
                "Erro", f"Não foi possível cadastrar o cliente:\n{erro}"
            )

    ttk.Button(
        aba_clientes, text="Cadastrar Cliente", command=salvar_cliente
    ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=4)

    atualizar_listagem_clientes()
    return aba_clientes
