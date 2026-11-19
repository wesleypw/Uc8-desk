# A16 — verificações dos casos T01–T09 do registro. Os valores esperados são escritos à mão
# ANTES de chamar o código (nunca calculados pela mesma função que está sendo testada).
import subprocess
import sys
import tempfile
from pathlib import Path

from controller import CadastroController
from memoria import RepositorioMemoria
from repositorio import RepositorioSqlite

PASTA = Path(__file__).resolve().parent


def recusa(funcao, *args, **kwargs):
    """Executa e exige ValueError; devolve a mensagem."""
    try:
        funcao(*args, **kwargs)
    except ValueError as erro:
        return str(erro)
    raise AssertionError("Era esperado ValueError, mas a operação foi aceita.")


def fabricas(tmp):
    """As duas implementações do mesmo contrato."""
    return {
        "memoria": lambda: RepositorioMemoria(),
        "sqlite": lambda: RepositorioSqlite(Path(tmp) / "dados.db"),
    }


def t01_controller_sem_tkinter():
    codigo = "import sys, controller, memoria, repositorio; assert 'tkinter' not in sys.modules"
    r = subprocess.run([sys.executable, "-c", codigo], cwd=PASTA, capture_output=True, text=True)
    assert r.returncode == 0, f"controller/memória importaram tkinter: {r.stderr}"
    print("T01 ok — controller, memória e repositório importam sem tkinter")


def roteiro_contrato(repo):
    """Mesma sequência de chamadas para qualquer repositório; devolve o que foi observado."""
    ctrl = CadastroController(repo)
    obs = []
    obs.append(ctrl.salvar("cliente", "  Ana  "))
    obs.append(ctrl.salvar("cliente", "Bruno"))
    obs.append(ctrl.salvar("cliente", "Ana Maria", codigo=1))
    obs.append(ctrl.listar("cliente"))
    obs.append(ctrl.salvar("produto", "Sorvete", "7,50"))
    obs.append(ctrl.salvar("produto", "Sorvete Duplo", "12,00", codigo=1))
    obs.append(ctrl.listar("produto"))
    return obs


def t02_mesmo_contrato():
    esperado = [
        {"acao": "incluido", "id": 1},
        {"acao": "incluido", "id": 2},
        {"acao": "editado", "id": 1},
        [{"id": 1, "nome": "Ana Maria"}, {"id": 2, "nome": "Bruno"}],
        {"acao": "incluido", "id": 1},
        {"acao": "editado", "id": 1},
        [{"id": 1, "nome": "Sorvete Duplo", "preco_centavos": 1200}],
    ]
    with tempfile.TemporaryDirectory() as tmp:
        for nome, fabrica in fabricas(tmp).items():
            assert roteiro_contrato(fabrica()) == esperado, f"{nome} divergiu do contrato"
    print("T02 ok — memória e SQLite incluem, listam e editam por ID com o mesmo formato")


def t03_duracao_dos_dados():
    with tempfile.TemporaryDirectory() as tmp:
        mem = RepositorioMemoria()
        mem.adicionar_cliente("Lia")
        assert RepositorioMemoria().listar_clientes() == [], "nova instância da memória deve começar vazia"
        caminho = Path(tmp) / "dados.db"
        sql = RepositorioSqlite(caminho)
        sql.adicionar_cliente("Lia")
        sql.adicionar_produto("Picolé", "3,00")
        del sql
        reaberto = RepositorioSqlite(caminho)
        assert reaberto.listar_clientes() == [{"id": 1, "nome": "Lia"}]
        assert reaberto.listar_produtos() == [{"id": 1, "nome": "Picolé", "preco_centavos": 300}]
    print("T03 ok — memória nasce vazia; SQLite reabre com os dados")


def t04_alvo_por_id():
    with tempfile.TemporaryDirectory() as tmp:
        for nome, fabrica in fabricas(tmp).items():
            ctrl = CadastroController(fabrica())
            for n in ("Ana", "Bruno", "Carla"):
                ctrl.salvar("cliente", n)
            ctrl.excluir("cliente", 2, True)                    # tira o do meio
            ctrl.salvar("cliente", "Carla Souza", codigo=3)      # a posição 2 agora é o ID 3
            assert ctrl.listar("cliente") == [{"id": 1, "nome": "Ana"}, {"id": 3, "nome": "Carla Souza"}], nome
            assert ctrl.salvar("cliente", "Davi") == {"acao": "incluido", "id": 4}, f"{nome}: ID 2 não pode ser reutilizado"
            recusa(ctrl.excluir, "cliente", 2, True)             # já não existe: não é 'sucesso'
            recusa(ctrl.salvar, "cliente", "Fantasma", codigo=2)
            assert [c["id"] for c in ctrl.listar("cliente")] == [1, 3, 4], nome
    print("T04 ok — editar/excluir clientes age sempre no ID escolhido; ID removido não volta")


def t05_cancelar_exclusao():
    with tempfile.TemporaryDirectory() as tmp:
        for nome, fabrica in fabricas(tmp).items():
            ctrl = CadastroController(fabrica())
            ctrl.salvar("cliente", "Ana")
            antes = ctrl.listar("cliente")
            recusa(ctrl.excluir, "cliente", 1, False)
            assert ctrl.listar("cliente") == antes == [{"id": 1, "nome": "Ana"}], nome
    print("T05 ok — sem confirmação nada é excluído")


def t06_tipo_desconhecido():
    ctrl = CadastroController(RepositorioMemoria())
    ctrl.salvar("cliente", "Ana")
    for operacao, args in ((ctrl.listar, ("fornecedor",)),
                           (ctrl.salvar, ("fornecedor", "X")),
                           (ctrl.excluir, ("fornecedor", 1, True))):
        assert "Tipo de cadastro desconhecido" in recusa(operacao, *args)
    assert ctrl.listar("cliente") == [{"id": 1, "nome": "Ana"}]
    print("T06 ok — tipo desconhecido é rejeitado sem tocar nos dados")


class RepositorioQueFalha:
    """Repositório de teste: toda gravação falha, como um disco cheio."""

    def adicionar_cliente(self, nome):
        raise ValueError("Falha simulada ao gravar o cliente.")

    def adicionar_produto(self, nome, preco):
        raise ValueError("Falha simulada ao gravar o produto.")

    def listar_clientes(self):
        return []

    def listar_produtos(self):
        return []


def t07_falha_do_repositorio():
    ctrl = CadastroController(RepositorioQueFalha())
    assert "Falha simulada" in recusa(ctrl.salvar, "cliente", "Ana")   # a falha chega a quem chamou
    assert "Falha simulada" in recusa(ctrl.salvar, "produto", "Sorvete", "5,00")
    print("T07 ok (controller) — a falha sobe para a janela; o teste da janela está em T09")


def t08_copia_da_memoria():
    mem = RepositorioMemoria()
    mem.adicionar_cliente("Ana")
    mem.adicionar_produto("Sorvete", "5,00")
    lista = mem.listar_clientes()
    lista[0]["nome"] = "ALTERADO POR FORA"
    lista.append({"id": 99, "nome": "Intruso"})
    produtos = mem.listar_produtos()
    produtos[0]["preco_centavos"] = 1
    assert mem.listar_clientes() == [{"id": 1, "nome": "Ana"}]
    assert mem.listar_produtos() == [{"id": 1, "nome": "Sorvete", "preco_centavos": 500}]
    print("T08 ok — alterar o que listar devolveu não muda o armazenamento")


def t_extras_validacao():
    """Erro depois de caso válido, limites e correção com nova execução."""
    with tempfile.TemporaryDirectory() as tmp:
        for nome, fabrica in fabricas(tmp).items():
            ctrl = CadastroController(fabrica())
            ctrl.salvar("produto", "Sorvete", "7,50")                      # válido
            recusa(ctrl.salvar, "produto", "", "5,00")                     # nome vazio
            recusa(ctrl.salvar, "produto", "Picolé", "abc")                # preço ilegível
            recusa(ctrl.salvar, "produto", "Picolé", "0")                  # zero
            recusa(ctrl.salvar, "produto", "Picolé", "-1")                 # negativo
            recusa(ctrl.salvar, "produto", "Picolé", "100000,01")          # acima do limite
            assert len(ctrl.listar("produto")) == 1, f"{nome}: recusa não pode gravar nada"
            assert ctrl.salvar("produto", "Picolé", "0,01")["id"] == 2     # limite inferior aceito
            assert ctrl.salvar("produto", "Luxo", "100000,00")["id"] == 3  # limite superior aceito
            assert ctrl.salvar("produto", "Picolé", "3,00", codigo=2)["acao"] == "editado"   # correção
            assert [p["preco_centavos"] for p in ctrl.listar("produto")] == [750, 300, 10000000], nome
    print("Extras ok — recusas não gravam; limites 0,01 e 100.000,00 valem; correção funciona")


def t09_componentes_gui():
    """Roda só se houver tkinter e ambiente gráfico; senão avisa que ficou pendente."""
    try:
        import tkinter as tk
        import main
        raiz = main.criar_janela(RepositorioMemoria(), dialogos=DialogosFalsos(), descricao_armazenamento="teste")
    except Exception as erro:
        print(f"T09 PENDENTE — sem tkinter/ambiente gráfico aqui ({type(erro).__name__}); rode no seu computador.")
        return None

    try:
        d = raiz.paineis["produto"].dialogos
        prod, cli = raiz.paineis["produto"], raiz.paineis["cliente"]
        assert prod is not cli

        # cada painel guarda os próprios campos
        prod.entradas["nome"].insert(0, "Rascunho de produto")
        cli.entradas["nome"].insert(0, "Ana")
        assert prod.entradas["nome"].get() == "Rascunho de produto" and cli.entradas["nome"].get() == "Ana"
        assert cli.salvar() is True
        raiz.update()
        assert prod.entradas["nome"].get() == "Rascunho de produto", "salvar cliente mexeu no formulário de produto"
        assert cli.entradas["nome"].get() == "" and len(cli.tabela.get_children()) == 1

        # seleções independentes
        prod.entradas["preco"].insert(0, "5,00")
        assert prod.salvar() is True
        raiz.update()
        cli.tabela.selection_set("1")
        raiz.update()
        assert cli.codigo_selecionado == 1 and prod.codigo_selecionado is None
        prod.tabela.selection_set("1")
        raiz.update()
        assert prod.codigo_selecionado == 1 and cli.codigo_selecionado == 1
        prod.novo()
        assert prod.codigo_selecionado is None and cli.codigo_selecionado == 1

        # falha ao salvar conserva o formulário e avisa (T07 na janela)
        cli.novo()
        cli.entradas["nome"].insert(0, "   ")
        d.mensagens.clear()
        assert cli.salvar() is False
        assert cli.entradas["nome"].get() == "   " and d.mensagens[-1][0] == "erro"
        cli.entradas["nome"].delete(0, tk.END)
        cli.entradas["nome"].insert(0, "Bia")      # correção + nova tentativa
        assert cli.salvar() is True

        # cancelar exclusão não altera lista nem banco (T05 na janela)
        cli.tabela.selection_set("1")
        raiz.update()
        d.resposta_confirmar = False
        antes = list(cli.tabela.get_children())
        assert cli.excluir() is False
        assert list(cli.tabela.get_children()) == antes
        assert [c["id"] for c in raiz.controller.listar("cliente")] == [1, 2]
        d.resposta_confirmar = True
        assert cli.excluir() is True
        assert [c["id"] for c in raiz.controller.listar("cliente")] == [2]
    finally:
        raiz.destroy()
    print("T09 ok — painéis independentes; falha conserva o formulário; cancelar não altera nada")
    return True


class DialogosFalsos:
    """Substitui as caixas de mensagem (que travariam o teste esperando um clique)."""

    def __init__(self):
        self.mensagens = []
        self.resposta_confirmar = True

    def info(self, titulo, texto):
        self.mensagens.append(("info", texto))

    def aviso(self, titulo, texto):
        self.mensagens.append(("aviso", texto))

    def erro(self, titulo, texto):
        self.mensagens.append(("erro", texto))

    def confirmar(self, titulo, texto):
        self.mensagens.append(("confirmar", texto))
        return self.resposta_confirmar


def verificar():
    t01_controller_sem_tkinter()
    t02_mesmo_contrato()
    t03_duracao_dos_dados()
    t04_alvo_por_id()
    t05_cancelar_exclusao()
    t06_tipo_desconhecido()
    t07_falha_do_repositorio()
    t08_copia_da_memoria()
    t_extras_validacao()
    resultado_gui = t09_componentes_gui()
    # Só devolve True se TUDO foi executado; T09 pendente não conta como sucesso.
    return resultado_gui is True


if __name__ == "__main__":
    if verificar():
        print("Casos executados: previsões e resultados conferem.")
    else:
        print("Verificações ainda incompletas (veja os casos PENDENTES acima).")
