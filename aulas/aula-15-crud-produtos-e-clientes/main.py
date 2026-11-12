"""Interface principal da aplicação da Aula 15."""

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from perfis import SessaoDemo
from repositorio import RepositorioSqlite
from tela_clientes import criar_aba_clientes
from tela_produtos import criar_aba_produtos


def criar_janela():
    janela = tk.Tk()
    janela.title("A15 — Pizzaria & Sorveteria (CRUD Completo)")
    janela.geometry("680x580")
    janela.columnconfigure(0, weight=1)
    janela.rowconfigure(0, weight=1)

    caminho_db = Path("dados_pizzaria.db").resolve()
    repo = RepositorioSqlite(caminho_db)
    sessao = SessaoDemo()

    base = ttk.Frame(janela, padding=10)
    base.grid(row=0, column=0, sticky="nsew")
    base.columnconfigure(0, weight=1)
    base.rowconfigure(1, weight=1)

    lbl_banco = ttk.Label(
        base,
        text=f"Banco SQLite: {caminho_db.name}",
        font=("Arial", 9, "italic"),
        foreground="gray",
    )
    lbl_banco.grid(row=0, column=0, sticky="w", pady=(0, 6))

    notebook = ttk.Notebook(base)
    notebook.grid(row=1, column=0, sticky="nsew")
    criar_aba_produtos(notebook, repo)
    criar_aba_clientes(notebook, repo)

    ttk.Label(
        base,
        text="Use Tab/Shift+Tab para navegar. Pressione Enter para acionar os botões.",
        font=("Arial", 8),
        foreground="gray",
    ).grid(row=2, column=0, sticky="w", pady=(8, 0))

    return janela


if __name__ == "__main__":
    criar_janela().mainloop()
