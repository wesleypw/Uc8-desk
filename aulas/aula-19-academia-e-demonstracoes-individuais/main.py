"""A19 (candidata validada na A18) — Sorveteria integrada: Venda + Catálogo + Clientes sobre o mesmo banco SQLite.

Execução (na pasta deste arquivo):
    python main.py                       # usa dados_sorveteria.db ao lado do main.py
    python main.py --banco ensaio.db     # usa outro arquivo (ex.: cópia de ensaio)

Se copia-nova.db estiver aberta em outro programa, a interface ainda inicia, mas o backup
automático fica pausado até fechar esse arquivo e reiniciar o aplicativo.
"""
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from backup_sqlite import criar_backup
from componentes import criar_painel_clientes, criar_painel_produtos
from controller import CadastroController, VendaController
from repositorio import RepositorioSqlite
from tela_venda import PainelVenda

BANCO_PADRAO = "dados_sorveteria.db"


def caminho_do_banco(argumentos):
    """--banco CAMINHO escolhe o arquivo; sem a opção, usa o banco padrão ao lado do main.py."""
    if "--banco" in argumentos:
        posicao = argumentos.index("--banco")
        if posicao + 1 >= len(argumentos):
            raise SystemExit("Uso: python main.py [--banco CAMINHO.db]")
        return Path(argumentos[posicao + 1]).resolve()
    return Path(__file__).resolve().parent / BANCO_PADRAO


def criar_janela(repositorio=None, dialogos=None, caminho_banco=None):
    janela = tk.Tk()
    janela.title("Sorveteria — Vendas e cadastros")
    janela.geometry("720x640")
    janela.columnconfigure(0, weight=1)
    janela.rowconfigure(0, weight=1)
    aviso_backup = None

    if repositorio is None:
        caminho_banco = Path(caminho_banco or caminho_do_banco([])).resolve()
        caminho_copia = caminho_banco.with_name("copia-nova.db")
        repositorio = RepositorioSqlite(caminho_banco)
        try:
            criar_backup(caminho_banco, caminho_copia)
        except PermissionError:
            aviso_backup = (
                "Backup automático pausado: feche copia-nova.db e reinicie o aplicativo."
            )
        else:
            repositorio.caminho_backup = str(caminho_copia.resolve())
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

    linha_notebook = 1
    if aviso_backup:
        ttk.Label(base, text=aviso_backup, foreground="darkorange").grid(
            row=1, column=0, sticky="w", pady=(0, 6)
        )
        linha_notebook = 2
    base.rowconfigure(linha_notebook, weight=1)

    notebook = ttk.Notebook(base)
    notebook.grid(row=linha_notebook, column=0, sticky="nsew")
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
                  row=linha_notebook + 1, column=0, sticky="w", pady=(8, 0)
              )

    janela.notebook = notebook
    janela.paineis = {"venda": painel_venda, "produto": painel_produtos, "cliente": painel_clientes}
    janela.controllers = {"cadastro": cadastro, "venda": venda}
    return janela


if __name__ == "__main__":
    criar_janela(caminho_banco=caminho_do_banco(sys.argv[1:])).mainloop()
