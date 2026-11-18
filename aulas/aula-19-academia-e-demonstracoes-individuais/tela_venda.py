"""A19 (candidata validada na A18) — Painel de venda: cliente + itens + forma de pagamento -> venda gravada -> CSV.

A janela só lê os campos e mostra respostas. Regras, gravação e comprovante ficam no VendaController.
Regra de ouro: a confirmação só aparece DEPOIS que o controller devolve o comprovante (banco gravou).
"""
import tkinter as tk
from tkinter import ttk

from componentes import Dialogos
from modelos import formatar
from pagamento import FATORES


class PainelVenda(ttk.Frame):
    def __init__(self, master, controller, dialogos=None):
        super().__init__(master, padding=12)
        self.controller = controller
        self.dialogos = dialogos or Dialogos()
        self.ids_clientes = []   # posição do Combobox -> ID (o ID é o alvo, nunca o texto)
        self.ids_produtos = []
        self.finalizada = False
        self.janela_vendas = None

        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)

        # --- cliente ---
        ttk.Label(self, text="Cliente:").grid(row=0, column=0, sticky="w", pady=4)
        self.combo_cliente = ttk.Combobox(self, state="readonly")
        self.combo_cliente.grid(row=0, column=1, sticky="ew", padx=(6, 6), pady=4)
        self.btn_atualizar = ttk.Button(
            self, text="Atualizar vendas", command=self.atualizar_vendas
        )
        self.btn_atualizar.grid(row=0, column=2, sticky="e", pady=4)

        # --- produto + quantidade ---
        ttk.Label(self, text="Produto:").grid(row=1, column=0, sticky="w", pady=4)
        self.combo_produto = ttk.Combobox(self, state="readonly")
        self.combo_produto.grid(row=1, column=1, sticky="ew", padx=(6, 6), pady=4)
        quantidade = ttk.Frame(self)
        quantidade.grid(row=1, column=2, sticky="e", pady=4)
        ttk.Label(quantidade, text="Qtd:").pack(side="left")
        self.entry_qtd = ttk.Entry(quantidade, width=5)
        self.entry_qtd.insert(0, "1")
        self.entry_qtd.pack(side="left", padx=4)
        self.entry_qtd.bind("<Return>", lambda _e: self.adicionar())
        self.btn_adicionar = ttk.Button(quantidade, text="Adicionar", command=self.adicionar)
        self.btn_adicionar.pack(side="left")

        self.lbl_aviso = ttk.Label(self, text="Escolha o cliente, adicione itens e finalize.",
                                   foreground="gray", wraplength=560)
        self.lbl_aviso.grid(row=2, column=0, columnspan=3, sticky="w", pady=4)

        # --- itens da montagem (tabela + rolagem num quadro que ocupa a largura toda) ---
        quadro = ttk.Frame(self)
        quadro.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=6)
        quadro.columnconfigure(0, weight=1)
        quadro.rowconfigure(0, weight=1)
        colunas = ("codigo", "nome", "qtd", "preco", "subtotal")
        self.tabela = ttk.Treeview(quadro, columns=colunas, show="headings", height=6)
        for chave, titulo, largura, ancora, estica in (
                ("codigo", "Cód.", 50, "center", False), ("nome", "Item", 220, "w", True),
                ("qtd", "Qtd", 50, "center", False), ("preco", "Preço un.", 110, "e", False),
                ("subtotal", "Subtotal", 110, "e", False)):
            self.tabela.heading(chave, text=titulo)
            self.tabela.column(chave, width=largura, anchor=ancora, stretch=estica)
        self.tabela.grid(row=0, column=0, sticky="nsew")
        rolagem = ttk.Scrollbar(quadro, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=rolagem.set)
        rolagem.grid(row=0, column=1, sticky="ns")

        acoes = ttk.Frame(self)
        acoes.grid(row=4, column=0, columnspan=3, sticky="ew")
        self.btn_remover = ttk.Button(acoes, text="Remover item", command=self.remover)
        self.btn_remover.pack(side="left", padx=(0, 6))
        self.btn_revisar = ttk.Button(acoes, text="Revisar montagem", command=self.revisar)
        self.btn_revisar.pack(side="left")

        # --- pagamento ---
        pagamento = ttk.Frame(self)
        pagamento.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(10, 4))
        pagamento.columnconfigure(2, weight=1)
        ttk.Label(pagamento, text="Pagamento:").grid(row=0, column=0, sticky="w")
        self.combo_forma = ttk.Combobox(pagamento, state="readonly", values=list(FATORES), width=14)
        self.combo_forma.set("PIX")
        self.combo_forma.grid(row=0, column=1, padx=6)
        self.combo_forma.bind("<<ComboboxSelected>>", lambda _e: self._atualizar_totais())
        self.lbl_totais = ttk.Label(pagamento, text="", font=("Arial", 10, "bold"))
        self.lbl_totais.grid(row=0, column=2, sticky="e")

        finais = ttk.Frame(self)
        finais.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(6, 0))
        finais.columnconfigure((0, 1, 2), weight=1)
        self.btn_finalizar = ttk.Button(finais, text="Finalizar venda", command=self.finalizar)
        self.btn_finalizar.grid(row=0, column=0, sticky="ew", padx=2)
        self.btn_exportar = ttk.Button(finais, text="Exportar CSV", command=self.exportar, state="disabled")
        self.btn_exportar.grid(row=0, column=1, sticky="ew", padx=2)
        self.btn_nova = ttk.Button(finais, text="Nova venda", command=self.nova_venda)
        self.btn_nova.grid(row=0, column=2, sticky="ew", padx=2)

        self.atualizar_listas()
        self._redesenhar()

    # ---------- listas (clientes/produtos vêm do banco, por ID) ----------
    def atualizar_listas(self):
        """Atualização EXPLÍCITA: recarrega clientes e produtos do banco e mantém a escolha pelo ID."""
        cliente_antes = self._id_escolhido(self.combo_cliente, self.ids_clientes)
        produto_antes = self._id_escolhido(self.combo_produto, self.ids_produtos)
        clientes = self.controller.clientes()
        produtos = self.controller.produtos()
        self.ids_clientes = [c["id"] for c in clientes]
        self.ids_produtos = [p["id"] for p in produtos]
        self.combo_cliente["values"] = [f"{c['id']} — {c['nome']}" for c in clientes]
        self.combo_produto["values"] = [f"{p['id']} — {p['nome']} ({formatar(p['preco_centavos'])})" for p in produtos]
        self._restaurar(self.combo_cliente, self.ids_clientes, cliente_antes)
        self._restaurar(self.combo_produto, self.ids_produtos, produto_antes)

    def atualizar_vendas(self):
        try:
            self.atualizar_listas()
            vendas = self.controller.vendas()
        except Exception as erro:
            self.dialogos.erro("Não foi possível carregar as vendas", str(erro))
            self._mensagem(f"Erro: {erro}", "red")
            return False

        if self.janela_vendas is None or not self.janela_vendas.winfo_exists():
            self.janela_vendas = tk.Toplevel(self)
            self.janela_vendas.title("Vendas registradas")
            self.janela_vendas.geometry("900x360")
            self.janela_vendas.transient(self.winfo_toplevel())
            self.janela_vendas.columnconfigure(0, weight=1)
            self.janela_vendas.rowconfigure(1, weight=1)

            self.lbl_resumo_vendas = ttk.Label(self.janela_vendas, padding=(8, 8))
            self.lbl_resumo_vendas.grid(row=0, column=0, sticky="w")
            quadro_vendas = ttk.Frame(self.janela_vendas, padding=(8, 0, 8, 8))
            quadro_vendas.grid(row=1, column=0, sticky="nsew")
            quadro_vendas.columnconfigure(0, weight=1)
            quadro_vendas.rowconfigure(0, weight=1)
            colunas = ("id", "data", "cliente", "pagamento", "itens", "total")
            self.tabela_vendas = ttk.Treeview(
                quadro_vendas, columns=colunas, show="headings", height=10
            )
            for chave, titulo, largura, ancora, estica in (
                ("id", "Venda", 60, "center", False),
                ("data", "Data e hora", 145, "w", False),
                ("cliente", "Cliente", 150, "w", True),
                ("pagamento", "Pagamento", 100, "center", False),
                ("itens", "Itens", 280, "w", True),
                ("total", "Total", 100, "e", False),
            ):
                self.tabela_vendas.heading(chave, text=titulo)
                self.tabela_vendas.column(
                    chave, width=largura, anchor=ancora, stretch=estica
                )
            self.tabela_vendas.grid(row=0, column=0, sticky="nsew")
            rolagem_vendas = ttk.Scrollbar(
                quadro_vendas, orient="vertical", command=self.tabela_vendas.yview
            )
            self.tabela_vendas.configure(yscrollcommand=rolagem_vendas.set)
            rolagem_vendas.grid(row=0, column=1, sticky="ns")

        for iid in self.tabela_vendas.get_children():
            self.tabela_vendas.delete(iid)
        for venda in vendas:
            itens = ", ".join(
                f"{item['quantidade']}x {item['nome']}" for item in venda["itens"]
            )
            self.tabela_vendas.insert("", "end", values=(
                venda["id"],
                venda["criado_em"].replace("T", " "),
                venda["cliente"],
                venda["forma"],
                itens,
                formatar(venda["total_centavos"]),
            ))
        self.lbl_resumo_vendas.configure(
            text=f"{len(vendas)} venda(s) registrada(s)." if vendas
            else "Nenhuma venda registrada."
        )
        self.janela_vendas.deiconify()
        self.janela_vendas.lift()
        self._mensagem(f"Lista de vendas atualizada: {len(vendas)} venda(s).", "green")
        return True

    @staticmethod
    def _id_escolhido(combo, ids):
        posicao = combo.current()
        return ids[posicao] if 0 <= posicao < len(ids) else None

    @staticmethod
    def _restaurar(combo, ids, codigo):
        if codigo in ids:
            combo.current(ids.index(codigo))
        else:
            combo.set("")

    # ---------- desenho ----------
    def _redesenhar(self):
        for iid in self.tabela.get_children():
            self.tabela.delete(iid)
        for linha in self.controller.pedido.linhas():
            self.tabela.insert("", "end", iid=linha["codigo"], values=(
                linha["codigo"], linha["nome"], linha["quantidade"],
                formatar(linha["preco_unitario"]), formatar(linha["subtotal"])))
        self._atualizar_totais()

    def _atualizar_totais(self):
        subtotal = self.controller.pedido.total_centavos()
        if subtotal <= 0:
            self.lbl_totais.configure(text="Subtotal: R$ 0,00")
            return
        previa = self.controller.previa(self.combo_forma.get())
        self.lbl_totais.configure(
            text=f"Subtotal: {formatar(previa['subtotal_centavos'])}  |  "
                 f"Total no {previa['forma']}: {formatar(previa['total_centavos'])}")

    def _mensagem(self, texto, cor="gray"):
        self.lbl_aviso.configure(text=texto, foreground=cor)

    def _estado_finalizada(self, finalizada):
        self.finalizada = finalizada
        edicao = "disabled" if finalizada else "normal"
        for botao in (self.btn_adicionar, self.btn_remover, self.btn_revisar, self.btn_finalizar):
            botao.configure(state=edicao)
        self.btn_exportar.configure(state="normal" if finalizada else "disabled")

    # ---------- ações ----------
    def adicionar(self):
        posicao = self.combo_produto.current()
        if posicao < 0:
            self.dialogos.aviso("Aviso", "Escolha um produto na lista antes de adicionar.")
            return False
        try:
            self.controller.adicionar_item(self.ids_produtos[posicao], self.entry_qtd.get())
        except Exception as erro:
            self.dialogos.erro("Não foi possível adicionar", str(erro))
            self._mensagem(f"Erro: {erro}", "red")
            return False          # a quantidade digitada continua no campo para corrigir
        self.entry_qtd.delete(0, tk.END)
        self.entry_qtd.insert(0, "1")
        self._redesenhar()
        self._mensagem("Item adicionado à montagem.")
        return True

    def remover(self):
        selecao = self.tabela.selection()
        if not selecao:
            self.dialogos.aviso("Aviso", "Selecione um item da montagem para remover.")
            return False
        try:
            self.controller.remover_item(selecao[0])
        except Exception as erro:
            self.dialogos.erro("Não foi possível remover", str(erro))
            return False
        self._redesenhar()
        self._mensagem("Item removido da montagem.")
        return True

    def revisar(self):
        try:
            mudancas = self.controller.revisar_montagem()
        except Exception as erro:
            self.dialogos.erro("Não foi possível revisar", str(erro))
            return None
        self._redesenhar()
        if not mudancas:
            self._mensagem("Revisão feita: nada mudou no catálogo.")
        else:
            detalhes = self.controller.descrever(mudancas)
            self._mensagem(f"Montagem revisada: {detalhes}. Confira a prévia e finalize de novo.", "darkorange")
            self.dialogos.info("Montagem revisada", f"Foi aplicado o catálogo atual: {detalhes}.")
        return mudancas

    def finalizar(self):
        posicao = self.combo_cliente.current()
        codigo_cliente = self.ids_clientes[posicao] if 0 <= posicao < len(self.ids_clientes) else None
        forma = self.combo_forma.get()
        try:
            self.controller.selecionar_cliente(codigo_cliente)
            previa = self.controller.previa(forma)
        except Exception as erro:
            self.dialogos.erro("Antes de finalizar", str(erro))
            self._mensagem(f"Erro: {erro}", "red")
            return False
        pergunta = (f"Gravar a venda para o cliente ID {codigo_cliente}?\n\n"
                    f"Subtotal: {formatar(previa['subtotal_centavos'])}\n"
                    f"Pagamento: {forma}\nTotal: {formatar(previa['total_centavos'])}")
        if not self.dialogos.confirmar("Confirmar venda", pergunta):
            self._mensagem("Finalização cancelada; a montagem foi preservada.")
            return False
        try:
            comprovante = self.controller.finalizar(forma, True)
        except Exception as erro:
            # Falha (preço mudou, banco recusou...): nada foi gravado e a montagem continua na tela.
            self.dialogos.erro("Venda não gravada", str(erro))
            self._mensagem(f"Erro: {erro}", "red")
            self._redesenhar()
            return False
        self._estado_finalizada(True)
        self._mensagem(f"Venda {comprovante['venda_id']} gravada. Exporte o CSV ou inicie uma nova venda.", "green")
        self.dialogos.info("Venda gravada", f"Venda {comprovante['venda_id']} confirmada.\n"
                                           f"Total: {comprovante['total_formatado']} ({comprovante['forma_pagamento']}).")
        return True

    def exportar(self):
        caminho = self.dialogos.salvar_arquivo("Exportar comprovante CSV", f"venda-{self.controller.venda_id}.csv")
        if not caminho:
            self._mensagem("Exportação cancelada; a venda continua gravada.")
            return False
        try:
            self.controller.exportar_csv(caminho)
        except Exception as erro:
            self.dialogos.erro("Falha ao exportar", str(erro))
            self._mensagem(f"Erro: {erro}", "red")
            return False
        self._mensagem(f"CSV salvo em {caminho}", "green")
        self.dialogos.info("Exportação concluída", "O CSV foi gerado a partir do comprovante da venda.")
        return True

    def nova_venda(self):
        self.controller.nova_venda()
        self._estado_finalizada(False)
        self.combo_cliente.set("")
        self.atualizar_listas()
        self._redesenhar()
        self._mensagem("Nova venda iniciada.")
