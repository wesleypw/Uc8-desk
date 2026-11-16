# A17: reaproveitado da A16 (versão testada).
from copy import deepcopy

from repositorio import validar_nome, validar_preco, validar_id


class RepositorioMemoria:
    """Guarda produtos e clientes em dicionários (id -> registro).

    Contrato igual ao do RepositorioSqlite:
      - adicionar_* devolve o ID novo (inteiro, começa em 1, nunca é reaproveitado);
      - listar_* devolve CÓPIAS, ordenadas por ID;
      - editar_*/excluir_* levantam ValueError se o ID não existir;
      - excluir_* só age com confirmado=True.
    """

    def __init__(self):
        self._produtos = {}
        self._clientes = {}
        self._proximo_produto = 1
        self._proximo_cliente = 1

    # ---------- produtos ----------
    def adicionar_produto(self, nome, preco):
        nome_validado = validar_nome(nome)
        centavos = validar_preco(preco)
        codigo = self._proximo_produto
        self._proximo_produto += 1
        self._produtos[codigo] = {"id": codigo, "nome": nome_validado, "preco_centavos": centavos}
        return codigo

    def listar_produtos(self):
        # deepcopy: quem recebe a lista não consegue alterar o armazenamento por fora.
        return deepcopy([self._produtos[c] for c in sorted(self._produtos)])

    def editar_produto(self, codigo, nome, preco):
        id_valido = validar_id(codigo)
        nome_validado = validar_nome(nome)
        centavos = validar_preco(preco)
        if id_valido not in self._produtos:
            raise ValueError(f"Produto com ID {id_valido} não encontrado para edição.")
        self._produtos[id_valido] = {"id": id_valido, "nome": nome_validado, "preco_centavos": centavos}
        return True

    def excluir_produto(self, codigo, confirmado=False):
        id_valido = validar_id(codigo)
        if not confirmado:
            raise ValueError("A exclusão deve ser explicitamente confirmada.")
        if id_valido not in self._produtos:
            raise ValueError(f"Produto com ID {id_valido} não encontrado para exclusão.")
        del self._produtos[id_valido]
        return True

    # ---------- clientes ----------
    def adicionar_cliente(self, nome):
        nome_validado = validar_nome(nome)
        codigo = self._proximo_cliente
        self._proximo_cliente += 1
        self._clientes[codigo] = {"id": codigo, "nome": nome_validado}
        return codigo

    def listar_clientes(self):
        return deepcopy([self._clientes[c] for c in sorted(self._clientes)])

    def editar_cliente(self, codigo, nome):
        id_valido = validar_id(codigo)
        nome_validado = validar_nome(nome)
        if id_valido not in self._clientes:
            raise ValueError(f"Cliente com ID {id_valido} não encontrado para edição.")
        self._clientes[id_valido] = {"id": id_valido, "nome": nome_validado}
        return True

    def excluir_cliente(self, codigo, confirmado=False):
        id_valido = validar_id(codigo)
        if not confirmado:
            raise ValueError("A exclusão deve ser explicitamente confirmada.")
        if id_valido not in self._clientes:
            raise ValueError(f"Cliente com ID {id_valido} não encontrado para exclusão.")
        del self._clientes[id_valido]
        return True
