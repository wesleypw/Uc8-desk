# A18 (candidata): CadastroController (da A16, sem mudanças) + VendaController (montagem -> venda gravada).
# Nenhum dos dois importa tkinter nem lê Entry: recebem valores comuns.
from modelos import Item, Pedido, Produto
from pagamento import FATORES, calcular_pagamento, preco_para_centavos
from relatorios import exportar_csv
from repositorio import validar_id

TIPOS = ("produto", "cliente")


class CadastroController:
    """Recebe dados comuns (texto, ID) e chama o repositório combinado.

    Funciona com RepositorioMemoria e com RepositorioSqlite: ambos cumprem o mesmo contrato.
    Erros esperados saem como ValueError; quem chama (a janela) decide como mostrar.
    """

    def __init__(self, repositorio):
        if repositorio is None:
            raise ValueError("O controller precisa de um repositório.")
        self.repositorio = repositorio

    @staticmethod
    def _tipo(tipo):
        normalizado = str(tipo).strip().lower()
        if normalizado not in TIPOS:
            raise ValueError(f"Tipo de cadastro desconhecido: '{tipo}'.")
        return normalizado

    def listar(self, tipo):
        tipo = self._tipo(tipo)
        if tipo == "produto":
            return self.repositorio.listar_produtos()
        return self.repositorio.listar_clientes()

    def salvar(self, tipo, nome, preco_texto="", codigo=None):
        """codigo=None -> inclusão; codigo informado -> edição daquele ID.

        Devolve {"acao": "incluido"|"editado", "id": <ID>}.
        """
        tipo = self._tipo(tipo)
        if tipo == "produto":
            centavos = preco_para_centavos(preco_texto)  # texto -> centavos (inteiro)
            if codigo is None:
                novo = self.repositorio.adicionar_produto(nome, centavos)
                return {"acao": "incluido", "id": novo}
            self.repositorio.editar_produto(codigo, nome, centavos)
            return {"acao": "editado", "id": validar_id(codigo)}

        if codigo is None:
            novo = self.repositorio.adicionar_cliente(nome)
            return {"acao": "incluido", "id": novo}
        self.repositorio.editar_cliente(codigo, nome)
        return {"acao": "editado", "id": validar_id(codigo)}

    def excluir(self, tipo, codigo, confirmado):
        """Só exclui com confirmado=True; ID inexistente vira ValueError (nunca 'sucesso')."""
        tipo = self._tipo(tipo)
        if tipo == "produto":
            self.repositorio.excluir_produto(codigo, confirmado=confirmado)
        else:
            self.repositorio.excluir_cliente(codigo, confirmado=confirmado)
        return {"acao": "excluido", "id": validar_id(codigo)}


class VendaController:
    """Coordena a venda: montagem em memória -> conferência -> gravação no banco -> comprovante.

    A montagem (Pedido) guarda o preço VISTO quando o item entrou. Antes de gravar, o controller
    compara com o catálogo atual; se mudou, recusa e pede revisão (nada é gravado).
    O comprovante só existe depois que o banco confirmou a gravação.
    """

    def __init__(self, repositorio):
        if repositorio is None:
            raise ValueError("O controller precisa de um repositório.")
        self.repositorio = repositorio
        self.pedido = Pedido()
        self.cliente_id = None
        self.venda_id = None

    # ---------- consultas (sempre lidas do banco, por ID) ----------
    def clientes(self):
        return self.repositorio.listar_clientes()

    def produtos(self):
        return self.repositorio.listar_produtos()

    def _produto_atual(self, produto_id):
        codigo = validar_id(produto_id)
        for registro in self.repositorio.listar_produtos():
            if registro["id"] == codigo:
                return registro
        raise ValueError(f"Produto ID {codigo} não existe no catálogo.")

    # ---------- montagem ----------
    def selecionar_cliente(self, cliente_id):
        if cliente_id is None or str(cliente_id).strip() == "":
            raise ValueError("Selecione o cliente da venda antes de continuar.")
        codigo = validar_id(cliente_id)
        if not any(c["id"] == codigo for c in self.repositorio.listar_clientes()):
            raise ValueError(f"Cliente ID {codigo} não existe. Atualize a lista e escolha de novo.")
        self.cliente_id = codigo
        return codigo

    def adicionar_item(self, produto_id, quantidade_texto):
        atual = self._produto_atual(produto_id)
        codigo = str(atual["id"])
        visto = self.pedido.itens.get(codigo)
        if visto is not None and visto.produto.preco_centavos != atual["preco_centavos"]:
            # Somar mais uma unidade repreciaria a linha inteira sem avisar: peça revisão antes.
            raise ValueError(f"O preço de '{atual['nome']}' mudou desde que foi adicionado. Use Revisar montagem.")
        self.pedido.adicionar(Produto(codigo, atual["nome"], atual["preco_centavos"]), quantidade_texto)

    def alterar_quantidade(self, produto_id, quantidade_texto):
        self.pedido.atualizar(str(produto_id), quantidade_texto)

    def remover_item(self, produto_id):
        self.pedido.remover(str(produto_id))

    def conferir_catalogo(self):
        """Lista o que mudou no catálogo desde que os itens entraram na montagem (vazia = tudo certo)."""
        catalogo = {str(p["id"]): p for p in self.repositorio.listar_produtos()}
        divergencias = []
        for codigo, item in self.pedido.itens.items():
            atual = catalogo.get(codigo)
            if atual is None:
                divergencias.append({"produto_id": int(codigo), "nome": item.produto.nome, "motivo": "removido",
                                     "visto": item.produto.preco_centavos, "atual": None})
            elif atual["preco_centavos"] != item.produto.preco_centavos:
                divergencias.append({"produto_id": int(codigo), "nome": item.produto.nome, "motivo": "preco",
                                     "visto": item.produto.preco_centavos, "atual": atual["preco_centavos"]})
            elif atual["nome"] != item.produto.nome:
                divergencias.append({"produto_id": int(codigo), "nome": item.produto.nome, "motivo": "nome",
                                     "visto": item.produto.nome, "atual": atual["nome"]})
        return divergencias

    def revisar_montagem(self):
        """Aceita o catálogo atual: reprecifica/renomeia itens e remove os que sumiram. Devolve o que mudou."""
        divergencias = self.conferir_catalogo()
        atuais = {str(p["id"]): p for p in self.repositorio.listar_produtos()}
        for d in divergencias:
            codigo = str(d["produto_id"])
            quantidade = self.pedido.itens[codigo].qtd
            if d["motivo"] == "removido":
                self.pedido.remover(codigo)
            else:
                atual = atuais[codigo]
                self.pedido.itens[codigo] = Item(Produto(codigo, atual["nome"], atual["preco_centavos"]), quantidade)
        return divergencias

    # ---------- prévia e finalização ----------
    def previa(self, forma):
        """Subtotal e total pelo mesmo cálculo usado na gravação (pagamento.calcular_pagamento)."""
        subtotal = self.pedido.total_centavos()
        if subtotal <= 0:
            raise ValueError("A montagem está vazia.")
        _, fator, total = calcular_pagamento(f"{subtotal / 100:.2f}", forma)
        return {"forma": forma, "fator": str(fator), "subtotal_centavos": subtotal,
                "total_centavos": int((total * 100).to_integral_value())}

    @staticmethod
    def descrever(divergencias):
        partes = []
        for d in divergencias:
            if d["motivo"] == "removido":
                partes.append(f"'{d['nome']}' saiu do catálogo")
            elif d["motivo"] == "preco":
                partes.append(f"'{d['nome']}' mudou de {d['visto']} para {d['atual']} centavos")
            else:
                partes.append(f"'{d['nome']}' agora se chama '{d['atual']}'")
        return "; ".join(partes)

    def finalizar(self, forma, confirmado):
        self.pedido.exigir_aberto()          # venda já finalizada não finaliza de novo
        if not confirmado:
            raise ValueError("A confirmação da venda é necessária.")
        if self.cliente_id is None:
            raise ValueError("Selecione o cliente da venda antes de finalizar.")
        if not any(c["id"] == self.cliente_id for c in self.repositorio.listar_clientes()):
            raise ValueError("O cliente selecionado não existe mais. Atualize a lista e escolha de novo.")
        if not self.pedido.itens:
            raise ValueError("A montagem está vazia.")
        divergencias = self.conferir_catalogo()
        if divergencias:
            raise ValueError("O catálogo mudou: " + self.descrever(divergencias) + ". Use Revisar montagem e confirme de novo.")

        resumo = self.previa(forma)
        itens = [{"produto_id": int(i.produto.codigo), "quantidade": i.qtd, "preco_centavos": i.produto.preco_centavos}
                 for i in self.pedido.itens.values()]
        venda_id = self.repositorio.registrar_venda(self.cliente_id, itens, forma)  # falhou? sobe daqui; montagem fica
        self.venda_id = venda_id
        # Só depois da gravação bem-sucedida a montagem vira comprovante.
        return self.pedido.finalizar(forma, True, total_pago_centavos=resumo["total_centavos"], venda_id=venda_id)

    def exportar_csv(self, caminho):
        if self.pedido.comprovante is None:
            raise ValueError("Finalize a venda antes de exportar o CSV.")
        return exportar_csv(caminho, self.pedido.comprovante)   # lê o comprovante, não os campos da janela

    def nova_venda(self):
        self.pedido.novo()
        self.cliente_id = None
        self.venda_id = None
