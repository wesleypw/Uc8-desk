"""A16 — Interface fina: a janela lê os campos e mostra respostas; o controller coordena.

Execução:
    python main.py            # dados no SQLite (arquivo dados_pizzaria.db): persistem
    python main.py --memoria  # dados em memória: somem ao fechar a janela
"""
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from controller import CadastroController
from memoria import RepositorioMemoria
from modelos import formatar
from repositorio import RepositorioSqlite


class Dialogos:
    """Caixas de mensagem. Ficam num objeto próprio para poder trocá-las nos testes."""

    def info(self, titulo, texto):
        messagebox.showinfo(titulo, texto)

    def aviso(self, titulo, texto):
        messagebox.showwarning(titulo, texto)

    def erro(self, titulo, texto):
        messagebox.showerror(titulo, texto)

    def confirmar(self, titulo, texto):
        return messagebox.askyesno(titulo, texto)


class PainelCadastro(ttk.Frame):
    """Componente reutilizável: formulário + tabela + Salvar/Novo/Excluir de UM tipo.

    Cada instância guarda os próprios campos e a própria seleção, então o painel de
    produtos e o de clientes não interferem um no outro.
    """

    def __init__(self, master, controller, tipo, rotulo_item, campos, colunas, dialogos=None):
        super().__init__(master, padding=12)
        self.controller = controller
        self.tipo = tipo
        self.rotulo_item = rotulo_item
        self.campos = campos            # [(chave, rótulo)]
        self.colunas = colunas          # [(chave, título, largura, âncora)]
        self.dialogos = dialogos or Dialogos()
        self.codigo_selecionado = None  # None = modo inclusão; número = edição desse ID
        self.entradas = {}

        self.columnconfigure(1, weight=1)
        linha = 0
        for chave, rotulo in campos:
            ttk.Label(self, text=rotulo).grid(row=linha, column=0, sticky="w", pady=4)
            entrada = ttk.Entry(self)
            entrada.grid(row=linha, column=1, columnspan=2, sticky="ew", padx=(6, 0), pady=4)
            entrada.bind("<Return>", lambda _e: self.salvar())
            self.entradas[chave] = entrada
            linha += 1

        self.lbl_modo = ttk.Label(self, text=f"Modo: novo {rotulo_item}", foreground="blue",
                                  font=("Arial", 9, "bold"))
        self.lbl_modo.grid(row=linha, column=0, columnspan=3, sticky="w", pady=4)
        linha += 1

        self.lbl_aviso = ttk.Label(self, text="Informe os dados e clique em Salvar.",
                                   foreground="gray", wraplength=520)
        self.lbl_aviso.grid(row=linha, column=0, columnspan=3, sticky="w", pady=4)
        linha += 1

        self.tabela = ttk.Treeview(self, columns=[c[0] for c in colunas], show="headings", height=7)
        for chave, titulo, largura, ancora in colunas:
            self.tabela.heading(chave, text=titulo)
            self.tabela.column(chave, width=largura, anchor=ancora)
        self.tabela.grid(row=linha, column=0, columnspan=2, sticky="nsew", pady=6)
        rolagem = ttk.Scrollbar(self, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=rolagem.set)
        rolagem.grid(row=linha, column=2, sticky="ns", pady=6)
        self.rowconfigure(linha, weight=1)
        self.tabela.bind("<<TreeviewSelect>>", self._ao_selecionar)
        linha += 1

        botoes = ttk.Frame(self)
        botoes.grid(row=linha, column=0, columnspan=3, sticky="ew", pady=(6, 0))
        botoes.columnconfigure((0, 1, 2), weight=1)
        ttk.Button(botoes, text="Salvar", command=self.salvar).grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Button(botoes, text="Novo", command=self.novo).grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(botoes, text="Excluir", command=self.excluir).grid(row=0, column=2, sticky="ew", padx=2)

        self.atualizar()

    # ---------- leitura/escrita dos campos (única parte que conhece os widgets) ----------
    def valores(self):
        return {chave: entrada.get() for chave, entrada in self.entradas.items()}

    def _preencher(self, valores):
        for chave, entrada in self.entradas.items():
            entrada.delete(0, tk.END)
            entrada.insert(0, valores.get(chave, ""))

    def _linha_da_tabela(self, registro):
        if self.tipo == "produto":
            return (registro["id"], registro["nome"], formatar(registro["preco_centavos"]))
        return (registro["id"], registro["nome"])

    def _valores_do_registro(self, registro):
        if self.tipo == "produto":
            return {"nome": registro["nome"],
                    "preco": f"{registro['preco_centavos'] / 100:.2f}".replace(".", ",")}
        return {"nome": registro["nome"]}

    # ---------- ações ----------
    def atualizar(self):
        for iid in self.tabela.get_children():
            self.tabela.delete(iid)
        for registro in self.controller.listar(self.tipo):
            self.tabela.insert("", "end", iid=str(registro["id"]), values=self._linha_da_tabela(registro))

    def novo(self):
        self.codigo_selecionado = None
        self._preencher({})
        self.lbl_modo.configure(text=f"Modo: novo {self.rotulo_item}", foreground="blue")
        self.lbl_aviso.configure(text="Informe os dados e clique em Salvar.", foreground="gray")
        primeira = next(iter(self.entradas.values()))
        primeira.focus_set()

    def _ao_selecionar(self, _evento=None):
        selecao = self.tabela.selection()
        if not selecao:
            return
        codigo = int(selecao[0])
        registro = next((r for r in self.controller.listar(self.tipo) if r["id"] == codigo), None)
        if registro is None:
            return
        self.codigo_selecionado = codigo   # o alvo é o ID, não a posição na tabela
        self._preencher(self._valores_do_registro(registro))
        self.lbl_modo.configure(text=f"Editando {self.rotulo_item} ID {codigo}", foreground="darkorange")
        self.lbl_aviso.configure(text="Edite os campos e salve, ou clique em Novo.", foreground="black")

    def salvar(self):
        valores = self.valores()
        try:
            resultado = self.controller.salvar(
                self.tipo, valores.get("nome", ""), valores.get("preco", ""), self.codigo_selecionado)
        except Exception as erro:
            # Falha: avisa e MANTÉM os campos para a pessoa corrigir e tentar de novo.
            self.dialogos.erro("Não foi possível salvar", str(erro))
            self.lbl_aviso.configure(text=f"Erro: {erro}", foreground="red")
            primeira = next(iter(self.entradas.values()))
            primeira.focus_set()
            return False
        verbo = "cadastrado" if resultado["acao"] == "incluido" else "atualizado"
        self.atualizar()
        self.novo()
        self.dialogos.info("Sucesso", f"{self.rotulo_item.capitalize()} {verbo} (ID {resultado['id']}).")
        return True

    def excluir(self):
        if self.codigo_selecionado is None:
            self.dialogos.aviso("Aviso", f"Selecione um {self.rotulo_item} na tabela para excluir.")
            return False
        codigo = self.codigo_selecionado
        if not self.dialogos.confirmar("Confirmar exclusão", f"Excluir {self.rotulo_item} ID {codigo}?"):
            self.lbl_aviso.configure(text="Exclusão cancelada; nada foi alterado.", foreground="gray")
            return False   # cancelar não chama o controller: banco, lista e campos ficam como estavam
        try:
            self.controller.excluir(self.tipo, codigo, True)
        except Exception as erro:
            self.dialogos.erro("Falha ao excluir", str(erro))
            self.lbl_aviso.configure(text=f"Erro: {erro}", foreground="red")
            return False
        self.atualizar()
        self.novo()
        self.dialogos.info("Removido", f"{self.rotulo_item.capitalize()} ID {codigo} removido.")
        return True


def criar_painel_produtos(master, controller, dialogos=None):
    return PainelCadastro(
        master, controller, "produto", "item",
        campos=[("nome", "Nome do item:"), ("preco", "Preço por unidade (R$):")],
        colunas=[("id", "ID", 60, "center"), ("nome", "Item do catálogo", 280, "w"),
                 ("preco", "Preço", 120, "e")],
        dialogos=dialogos)


def criar_painel_clientes(master, controller, dialogos=None):
    return PainelCadastro(
        master, controller, "cliente", "cliente",
        campos=[("nome", "Nome da pessoa cliente:")],
        colunas=[("id", "ID", 60, "center"), ("nome", "Nome do cliente", 380, "w")],
        dialogos=dialogos)


def criar_janela(repositorio=None, dialogos=None, descricao_armazenamento=None):
    janela = tk.Tk()
    janela.title("A16 — Catálogo e Clientes (controller + contrato)")
    janela.geometry("700x600")
    janela.columnconfigure(0, weight=1)
    janela.rowconfigure(0, weight=1)

    if repositorio is None:
        caminho = Path(__file__).resolve().parent / "dados_pizzaria.db"
        repositorio = RepositorioSqlite(caminho)
        descricao_armazenamento = f"SQLite — {caminho.name} (os dados persistem)"
    controller = CadastroController(repositorio)

    base = ttk.Frame(janela, padding=10)
    base.grid(row=0, column=0, sticky="nsew")
    base.columnconfigure(0, weight=1)
    base.rowconfigure(1, weight=1)

    ttk.Label(base, text=f"Armazenamento: {descricao_armazenamento or 'repositório informado'}",
              font=("Arial", 9, "italic"), foreground="gray").grid(row=0, column=0, sticky="w", pady=(0, 6))

    notebook = ttk.Notebook(base)
    notebook.grid(row=1, column=0, sticky="nsew")
    painel_produtos = criar_painel_produtos(notebook, controller, dialogos)
    painel_clientes = criar_painel_clientes(notebook, controller, dialogos)
    notebook.add(painel_produtos, text=" Catálogo ")
    notebook.add(painel_clientes, text=" Clientes ")

    ttk.Label(base, text="Tab/Shift+Tab navegam; Espaço aciona o botão em foco; Enter nos campos salva.",
              font=("Arial", 8), foreground="gray").grid(row=2, column=0, sticky="w", pady=(8, 0))

    janela.paineis = {"produto": painel_produtos, "cliente": painel_clientes}
    janela.controller = controller
    return janela


if __name__ == "__main__":
    if "--memoria" in sys.argv:
        criar_janela(RepositorioMemoria(), descricao_armazenamento="memória (os dados somem ao fechar)").mainloop()
    else:
        criar_janela().mainloop()
