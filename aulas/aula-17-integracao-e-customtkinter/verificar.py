# A17 — verificações T01–T10 do registro. Os valores esperados são escritos à mão ANTES da chamada
# (ex.: 2 x 6,50 = 13,00; PIX x 0,87 = 11,31), nunca calculados pela função que está sendo testada.
import csv
import sqlite3
import sys
import tempfile
from contextlib import closing
from pathlib import Path

from controller import CadastroController, VendaController
from repositorio import RepositorioSqlite

PASTA = Path(__file__).resolve().parent


def recusa(funcao, *args, **kwargs):
    try:
        funcao(*args, **kwargs)
    except ValueError as erro:
        return str(erro)
    raise AssertionError("Era esperado ValueError, mas a operação foi aceita.")


def contar(caminho, tabela):
    with closing(sqlite3.connect(caminho)) as con:
        return con.execute(f"SELECT count(*) FROM {tabela}").fetchone()[0]


def cenario(tmp, nome_banco="vendas.db"):
    """Banco de ensaio (nunca o principal): 2 clientes, 2 produtos."""
    caminho = Path(tmp) / nome_banco
    repo = RepositorioSqlite(caminho)
    ana = repo.adicionar_cliente("Ana")
    bruno = repo.adicionar_cliente("Bruno")
    casquinha = repo.adicionar_produto("Casquinha", "6,50")
    milk = repo.adicionar_produto("Milkshake", "15,90")
    return caminho, repo, {"ana": ana, "bruno": bruno, "casquinha": casquinha, "milk": milk}


def venda_pronta(repo, ids, qtd="2", cliente="ana", produto="casquinha"):
    ctrl = VendaController(repo)
    ctrl.selecionar_cliente(ids[cliente])
    ctrl.adicionar_item(ids[produto], qtd)
    return ctrl


def t01_ids_e_reabertura():
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        del repo
        reaberto = RepositorioSqlite(caminho)
        ctrl = VendaController(reaberto)
        assert [(c["id"], c["nome"]) for c in ctrl.clientes()] == [(1, "Ana"), (2, "Bruno")]
        assert [(p["id"], p["nome"], p["preco_centavos"]) for p in ctrl.produtos()] == [
            (1, "Casquinha", 650), (2, "Milkshake", 1590)]
        ctrl.adicionar_item(2, "1")                        # entra pelo ID, não pela posição
        assert ctrl.pedido.linhas()[0]["nome"] == "Milkshake"
        recusa(ctrl.adicionar_item, 99, "1")               # ID que não existe
    print("T01 ok — catálogo e clientes vêm do banco por ID, inclusive após reabrir")


def t03_catalogo_mudou():
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        # (a) preço mudou
        ctrl = venda_pronta(repo, ids)
        repo.editar_produto(ids["casquinha"], "Casquinha", "7,00")
        mensagem = recusa(ctrl.finalizar, "PIX", True)
        assert "catálogo mudou" in mensagem
        assert contar(caminho, "vendas") == 0 and contar(caminho, "itens_venda") == 0
        assert ctrl.pedido.status == "ABERTO" and len(ctrl.pedido.itens) == 1   # montagem preservada
        recusa(ctrl.adicionar_item, ids["casquinha"], "1")                      # somar não repreciaria em silêncio
        assert ctrl.revisar_montagem()[0]["motivo"] == "preco"
        comprovante = ctrl.finalizar("PIX", True)                               # 2 x 7,00 = 14,00 -> x0,87 = 12,18
        assert comprovante["subtotal_centavos"] == 1400 and comprovante["total_centavos"] == 1218
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        # (b) produto sumiu
        ctrl = venda_pronta(repo, ids)
        repo.excluir_produto(ids["casquinha"], confirmado=True)
        assert "saiu do catálogo" in recusa(ctrl.finalizar, "PIX", True)
        assert contar(caminho, "vendas") == 0
        assert ctrl.revisar_montagem()[0]["motivo"] == "removido"
        assert "vazia" in recusa(ctrl.finalizar, "PIX", True)                   # nada sobrou para vender
    print("T03 ok — preço mudou/produto sumiu: recusa sem venda parcial; revisar e confirmar de novo funciona")


def t04_cliente_ausente():
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        ctrl = VendaController(repo)
        ctrl.adicionar_item(ids["casquinha"], "1")
        assert "Selecione o cliente" in recusa(ctrl.finalizar, "PIX", True)     # nunca selecionado
        assert "Selecione o cliente" in recusa(ctrl.selecionar_cliente, None)
        assert "não existe" in recusa(ctrl.selecionar_cliente, 99)              # ID inexistente
        assert contar(caminho, "vendas") == 0
        ctrl.selecionar_cliente(ids["bruno"])                                   # correção + nova tentativa
        assert ctrl.finalizar("PIX", True)["venda_id"] == 1
    print("T04 ok — cliente ausente/inexistente é orientado; corrigir e tentar de novo grava")


def t05_valores_do_pix():
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        ctrl = venda_pronta(repo, ids, qtd="2")                                 # 2 x 6,50
        assert ctrl.previa("PIX") == {"forma": "PIX", "fator": "0.87", "subtotal_centavos": 1300, "total_centavos": 1131}
        comprovante = ctrl.finalizar("PIX", True)
        assert comprovante["subtotal_centavos"] == 1300
        assert comprovante["total_centavos"] == 1131
        assert comprovante["total_formatado"] == "R$ 11,31"
        venda = repo.listar_vendas()[0]
        assert (venda["subtotal_centavos"], venda["total_centavos"], venda["forma"]) == (1300, 1131, "PIX")
        assert venda["itens"] == [{"produto_id": 1, "nome": "Casquinha", "quantidade": 2,
                                   "preco_centavos": 650, "subtotal_centavos": 1300}]
    # outras formas, valores calculados à mão: 13,00 x 0,92 = 11,96 ; 13,00 x 1,00 = 13,00
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        ctrl = venda_pronta(repo, ids, qtd="2")
        assert ctrl.previa("Débito")["total_centavos"] == 1196
        assert ctrl.previa("Crédito 1x")["total_centavos"] == 1300
        recusa(ctrl.previa, "Cheque")
    print("T05 ok — 2 x 6,50 no PIX: 13,00 -> 11,31 (e Débito 11,96, Crédito 13,00)")


def t06_transacao_desfaz_tudo():
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        itens = [{"produto_id": ids["casquinha"], "quantidade": 1, "preco_centavos": 650},
                 {"produto_id": 999, "quantidade": 1, "preco_centavos": 100}]   # a SEGUNDA inserção falha (FK)
        assert "desfeita" in recusa(repo.registrar_venda, ids["ana"], itens, "PIX")
        assert contar(caminho, "vendas") == 0 and contar(caminho, "itens_venda") == 0
        # um caso válido logo depois comprova que o banco continua utilizável
        assert repo.registrar_venda(ids["ana"], itens[:1], "PIX") == 1
        assert contar(caminho, "vendas") == 1 and contar(caminho, "itens_venda") == 1

    class RepositorioQueFalhaAoGravar:
        def listar_clientes(self):
            return [{"id": 1, "nome": "Ana"}]

        def listar_produtos(self):
            return [{"id": 1, "nome": "Casquinha", "preco_centavos": 650}]

        def registrar_venda(self, cliente_id, itens, forma):
            raise ValueError("Falha simulada na gravação.")

    ctrl = VendaController(RepositorioQueFalhaAoGravar())
    ctrl.selecionar_cliente(1)
    ctrl.adicionar_item(1, "2")
    recusa(ctrl.finalizar, "PIX", True)
    assert ctrl.pedido.status == "ABERTO" and ctrl.pedido.comprovante is None and ctrl.venda_id is None
    assert len(ctrl.pedido.itens) == 1, "a montagem não pode ser apagada quando o banco falha"
    print("T06 ok — falha na segunda inserção desfaz venda e itens; sem comprovante e com a montagem preservada")


def t07_finalizacao_unica():
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        ctrl = venda_pronta(repo, ids)
        ctrl.finalizar("PIX", True)
        assert contar(caminho, "vendas") == 1 and contar(caminho, "itens_venda") == 1
        recusa(ctrl.finalizar, "PIX", True)                 # repetir não grava outra
        recusa(ctrl.adicionar_item, ids["milk"], "1")       # montagem fechada
        assert contar(caminho, "vendas") == 1 and contar(caminho, "itens_venda") == 1
        reaberto = RepositorioSqlite(caminho)               # reabertura confere a venda
        assert [v["id"] for v in reaberto.listar_vendas()] == [1]
        ctrl.nova_venda()                                   # nova venda é outra: libera de novo
        ctrl.selecionar_cliente(ids["bruno"])
        ctrl.adicionar_item(ids["milk"], "1")
        assert ctrl.finalizar("Crédito 1x", True)["venda_id"] == 2
    print("T07 ok — sucesso grava uma venda e bloqueia nova finalização; reabertura confere")


def t08_exclusao_vinculada():
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        cadastro = CadastroController(repo)
        venda_pronta(repo, ids).finalizar("PIX", True)
        assert "vinculado" in recusa(cadastro.excluir, "produto", ids["casquinha"], True)
        assert "vinculado" in recusa(cadastro.excluir, "cliente", ids["ana"], True)
        assert [p["id"] for p in repo.listar_produtos()] == [1, 2]
        assert [c["id"] for c in repo.listar_clientes()] == [1, 2]
        cadastro.excluir("produto", ids["milk"], True)       # sem venda: continua podendo excluir
        cadastro.excluir("cliente", ids["bruno"], True)
        assert [p["id"] for p in repo.listar_produtos()] == [1]
        assert [c["id"] for c in repo.listar_clientes()] == [1]
    print("T08 ok — cadastro vinculado a venda não é excluído; sem vínculo, exclui")


def t09_csv_do_comprovante():
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        destino = Path(tmp) / "venda.csv"
        ctrl = venda_pronta(repo, ids)
        assert "Finalize" in recusa(ctrl.exportar_csv, destino)    # sem comprovante não exporta
        assert not destino.exists()
        ctrl.finalizar("PIX", True)
        repo.editar_produto(ids["casquinha"], "Casquinha", "99,00")  # catálogo muda DEPOIS da venda
        ctrl.exportar_csv(destino)
        with open(destino, encoding="utf-8-sig", newline="") as arq:
            linhas = list(csv.reader(arq, delimiter=";"))
        assert linhas[0] == ["ID", "Nome", "Quantidade", "Preco_Unitario_Centavos", "Subtotal_Centavos",
                             "Forma_Pagamento", "Total_Pedido_Formatado"]
        assert linhas[1] == ["1", "Casquinha", "2", "650", "1300", "PIX", "R$ 11,31"]   # retrato da venda
        assert len(linhas) == 2
    print("T09 ok — CSV sai do comprovante confirmado (preço antigo e total 11,31), não do catálogo atual")


def t10_comparacao_opcional():
    import importlib
    import comparar_ctk
    original = sys.modules.get("customtkinter", "ausente")
    try:
        sys.modules["customtkinter"] = None           # simula biblioteca ausente
        assert comparar_ctk.criar_comparacao() is None
        assert comparar_ctk.medir_teclado() is None
        importlib.reload(sys.modules["controller"])   # o núcleo continua carregando
    finally:
        if original == "ausente":
            sys.modules.pop("customtkinter", None)
        else:
            sys.modules["customtkinter"] = original
    print("T10 ok (núcleo) — sem CustomTkinter a comparação devolve None e o núcleo segue funcionando")


class DialogosFalsos:
    def __init__(self, caminho_csv=""):
        self.mensagens = []
        self.resposta_confirmar = True
        self.caminho_csv = caminho_csv

    def info(self, titulo, texto):
        self.mensagens.append(("info", texto))

    def aviso(self, titulo, texto):
        self.mensagens.append(("aviso", texto))

    def erro(self, titulo, texto):
        self.mensagens.append(("erro", texto))

    def confirmar(self, titulo, texto):
        self.mensagens.append(("confirmar", texto))
        return self.resposta_confirmar

    def salvar_arquivo(self, titulo, nome_inicial):
        return self.caminho_csv


def t_gui_fluxo_completo():
    """T02 + partes de T03/T04/T07/T09/T10 na janela. Roda só com tkinter e ambiente gráfico."""
    try:
        import tkinter as tk
        import main
        tmp_ctx = tempfile.TemporaryDirectory()
        tmp = tmp_ctx.name
        caminho, repo, ids = cenario(tmp)
        dialogos = DialogosFalsos(caminho_csv=str(Path(tmp) / "gui.csv"))
        raiz = main.criar_janela(repositorio=repo, dialogos=dialogos, caminho_banco=caminho)
    except Exception as erro:
        print(f"GUI PENDENTE — sem tkinter/ambiente gráfico aqui ({type(erro).__name__}); rode no seu computador.")
        return None

    try:
        venda = raiz.paineis["venda"]
        cadastro = raiz.controllers["cadastro"]
        raiz.update()

        # T02: cadastro novo só aparece depois da atualização explícita
        antes = len(venda.combo_cliente["values"])
        cadastro.salvar("cliente", "Carla")
        assert len(venda.combo_cliente["values"]) == antes, "a lista não deveria mudar sozinha"
        venda.atualizar_listas()
        assert len(venda.combo_cliente["values"]) == antes + 1 and "Carla" in venda.combo_cliente["values"][-1]

        # T04 na janela: sem cliente, orienta e mantém a montagem
        venda.combo_produto.current(0)
        venda.entry_qtd.delete(0, tk.END)
        venda.entry_qtd.insert(0, "0")
        assert venda.adicionar() is False and dialogos.mensagens[-1][0] == "erro"       # quantidade 0 recusada
        assert venda.entry_qtd.get() == "0", "o campo deve manter o valor para corrigir"
        venda.entry_qtd.delete(0, tk.END)
        venda.entry_qtd.insert(0, "2")                                                   # correção
        assert venda.adicionar() is True
        assert venda.finalizar() is False and "Selecione o cliente" in dialogos.mensagens[-1][1]
        assert len(venda.tabela.get_children()) == 1

        # finalizar cancelado preserva tudo
        venda.combo_cliente.current(0)
        dialogos.resposta_confirmar = False
        assert venda.finalizar() is False and contar(caminho, "vendas") == 0
        dialogos.resposta_confirmar = True

        # T03 na janela: preço muda -> recusa; revisar -> grava
        repo.editar_produto(ids["casquinha"], "Casquinha", "7,00")
        assert venda.finalizar() is False and "catálogo mudou" in dialogos.mensagens[-1][1]
        assert contar(caminho, "vendas") == 0
        venda.revisar()
        assert venda.finalizar() is True
        assert "12,18" in dialogos.mensagens[-1][1] or "R$ 12,18" in dialogos.mensagens[-1][1]

        # T07 na janela: botões travados e CSV liberado
        assert str(venda.btn_finalizar.cget("state")) == "disabled"
        assert str(venda.btn_exportar.cget("state")) == "normal"
        assert contar(caminho, "vendas") == 1

        # T09 na janela
        assert venda.exportar() is True and Path(dialogos.caminho_csv).exists()
        dialogos.caminho_csv = ""
        assert venda.exportar() is False                                                 # cancelar não quebra

        # nova venda libera de novo
        venda.nova_venda()
        assert str(venda.btn_finalizar.cget("state")) == "normal" and not venda.tabela.get_children()

        # aba de venda segue sendo atualizada ao trocar de aba (evento real do Notebook)
        cadastro.salvar("produto", "Picolé", "3,00")
        raiz.notebook.select(raiz.paineis["produto"])
        raiz.update()
        raiz.notebook.select(venda)
        raiz.update()
        assert any("Picolé" in valor for valor in venda.combo_produto["values"])
    finally:
        raiz.destroy()
        tmp_ctx.cleanup()
    print("GUI ok — T02 (atualização explícita) e fluxo da janela: recusas, revisão, gravação, CSV e nova venda")
    return True


def t_extras():
    """Erro após válido, limites e correção com nova execução."""
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        ctrl = VendaController(repo)
        ctrl.selecionar_cliente(ids["ana"])
        ctrl.adicionar_item(ids["casquinha"], "1")                    # válido
        for ruim in ("0", "-1", "abc", "", "1,5"):
            recusa(ctrl.adicionar_item, ids["milk"], ruim)            # inválidos
        assert ctrl.pedido.total_centavos() == 650                    # o válido anterior foi preservado
        ctrl.adicionar_item(ids["milk"], "1")                         # correção
        assert ctrl.pedido.total_centavos() == 650 + 1590
        recusa(ctrl.alterar_quantidade, ids["milk"], "0")             # editar para 0 é recusado...
        assert ctrl.pedido.total_centavos() == 650 + 1590             # ...e a montagem fica igual
        ctrl.alterar_quantidade(ids["milk"], "1")                     # editar para 1 continua funcionando
        recusa(ctrl.remover_item, 99)
        ctrl.remover_item(ids["milk"])
        assert ctrl.pedido.total_centavos() == 650
    print("Extras ok — recusas preservam a montagem; correção e remoção funcionam")


def verificar():
    t01_ids_e_reabertura()
    t03_catalogo_mudou()
    t04_cliente_ausente()
    t05_valores_do_pix()
    t06_transacao_desfaz_tudo()
    t07_finalizacao_unica()
    t08_exclusao_vinculada()
    t09_csv_do_comprovante()
    t10_comparacao_opcional()
    t_extras()
    resultado_gui = t_gui_fluxo_completo()
    return resultado_gui is True      # GUI pendente não conta como sucesso


if __name__ == "__main__":
    if verificar():
        print("Casos executados: previsões e resultados conferem.")
    else:
        print("Verificações ainda incompletas (veja os casos PENDENTES acima).")
