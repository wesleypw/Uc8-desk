# A16: o controller coordena a ação; não importa tkinter e não lê nenhuma Entry.
from pagamento import preco_para_centavos
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
