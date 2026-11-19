"""A19 (candidata validada na A18) — Sorveteria integrada: Venda + Catálogo + Clientes sobre o mesmo banco SQLite.

Execução (na pasta deste arquivo):
    python main.py                       # usa dados.db ao lado do main.py
    python main.py --banco ensaio.db     # usa outro arquivo (ex.: cópia de ensaio)

"""
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from componentes import criar_painel_clientes, criar_painel_produtos
from controller import CadastroController, VendaController
from repositorio import RepositorioSqlite
from tela_venda import PainelVenda

BANCO_PADRAO = "dados.db"
PASTA_AULA = Path(__file__).resolve().parent


def caminho_do_banco(argumentos):
    """--banco CAMINHO escolhe o arquivo; sem a opção, usa o banco padrão ao lado do main.py."""
    if "--banco" in argumentos:
        posicao = argumentos.index("--banco")
        if posicao + 1 >= len(argumentos):
            raise SystemExit("Uso: python main.py [--banco CAMINHO.db]")
        caminho = Path(argumentos[posicao + 1])
        if not caminho.is_absolute():
            caminho = PASTA_AULA / caminho
        return caminho.resolve()
    return PASTA_AULA / BANCO_PADRAO


def criar_janela(repositorio=None, dialogos=None, caminho_banco=None):
    janela = tk.Tk()
    janela.title("Sorveteria — Vendas e cadastros")
    janela.geometry("720x640")
    janela.columnconfigure(0, weight=1)
    janela.rowconfigure(0, weight=1)
    if repositorio is None:
        caminho_banco = Path(caminho_banco or caminho_do_banco([])).resolve()
        repositorio = RepositorioSqlite(caminho_banco)
    elif caminho_banco is None:
        caminho_banco = getattr(repositorio, "caminho", None)
    descricao = Path(caminho_banco).name if caminho_banco else "configurado externamente"

    cadastro = CadastroController(repositorio)
    venda = VendaController(repositorio)

    base = ttk.Frame(janela, padding=10)
    base.grid(row=0, column=0, sticky="nsew")
    base.columnconfigure(0, weight=1)

    ttk.Label(
        base,
        text=f"Gestão da sorveteria  |  Banco ativo: {descricao}",
        font=("Arial", 11, "bold"),
    ).grid(row=0, column=0, sticky="w", pady=(0, 8))

    base.rowconfigure(1, weight=1)

    notebook = ttk.Notebook(base)
    notebook.grid(row=1, column=0, sticky="nsew")
    painel_venda = PainelVenda(notebook, venda, dialogos)
    painel_produtos = criar_painel_produtos(notebook, cadastro, dialogos)
    painel_clientes = criar_painel_clientes(notebook, cadastro, dialogos)
    notebook.add(painel_venda, text=" Venda ")
    notebook.add(painel_produtos, text=" Catálogo ")
    notebook.add(painel_clientes, text=" Clientes ")

    def ao_trocar_de_aba(_evento):
        # Ao voltar para a venda, recarrega clientes/produtos: cadastros novos aparecem.
        if notebook.nametowidget(notebook.select()) is painel_venda and not painel_venda.finalizada:
            painel_venda.atualizar_listas()

    notebook.bind("<<NotebookTabChanged>>", ao_trocar_de_aba)

    ttk.Label(base, text="Atalhos: Tab/Shift+Tab navegam; Espaço aciona botões; Enter adiciona item ou salva cadastro.",
              font=("Arial", 8), foreground="gray").grid(
                  row=2, column=0, sticky="w", pady=(8, 0)
              )

    janela.notebook = notebook
    janela.paineis = {"venda": painel_venda, "produto": painel_produtos, "cliente": painel_clientes}
    janela.controllers = {"cadastro": cadastro, "venda": venda}
    return janela


if __name__ == "__main__":
    criar_janela(caminho_banco=caminho_do_banco(sys.argv[1:])).mainloop()
