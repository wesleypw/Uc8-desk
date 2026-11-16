# A18 — regressão da candidata. Cada expectativa é escrita À MÃO, de forma independente do código testado
# (ex.: 2 x 6,50 = 13,00 e PIX x 0,87 = 11,31 foram calculados no papel; nunca por .previa() ou .finalizar()).
import csv
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import closing
from pathlib import Path

from controller import CadastroController, VendaController
from pagamento import preco_para_centavos
from repositorio import RepositorioSqlite

PASTA = Path(__file__).resolve().parent
# Arquivos que formam a entrega; o T07 copia exatamente estes para outra pasta.
ARQUIVOS_ENTREGA = ["main.py", "tela_venda.py", "componentes.py", "controller.py", "repositorio.py", "memoria.py",
                    "modelos.py", "pagamento.py", "arquivos.py", "perfis.py", "relatorios.py", "comparar_ctk.py",
                    "verificar.py", "README-A18.md"]
# O que um script NÃO consegue aprovar: fica declarado, nunca marcado como feito (T09).
PENDENCIAS_HUMANAS = [
    "Execução pelo README por outra pessoa, no computador dela.",
    "Teste manual com mouse, teclado físico e redimensionamento no Windows.",
    "Entrega pelo fluxo combinado (conferência por quem entrega).",
]


def recusa(funcao, *args, **kwargs):
    try:
        funcao(*args, **kwargs)
    except ValueError as erro:
        return str(erro)
    raise AssertionError("Era esperado ValueError, mas a operação foi aceita.")


def conferir(rotulo, obtido, esperado):
    assert obtido == esperado, f"{rotulo}: esperado {esperado!r}, obtido {obtido!r}"


def contar(caminho, tabela):
    with closing(sqlite3.connect(caminho)) as con:
        return con.execute(f"SELECT count(*) FROM {tabela}").fetchone()[0]


def cenario(tmp):
    caminho = Path(tmp) / "ensaio.db"
    repo = RepositorioSqlite(caminho)
    ids = {"ana": repo.adicionar_cliente("Ana"), "bruno": repo.adicionar_cliente("Bruno"),
           "casquinha": repo.adicionar_produto("Casquinha", "6,50"),
           "milk": repo.adicionar_produto("Milkshake", "15,90")}
    return caminho, repo, ids


def venda_pronta(repo, ids, qtd="2"):
    ctrl = VendaController(repo)
    ctrl.selecionar_cliente(ids["ana"])
    ctrl.adicionar_item(ids["casquinha"], qtd)
    return ctrl


# ---------------------------------------------------------------- T01
def valores_conhecidos():
    conferir("6,50", preco_para_centavos("6,50"), 650)
    conferir("R$ 1.234,56", preco_para_centavos("R$ 1.234,56"), 123456)
    conferir("0,01", preco_para_centavos("0,01"), 1)
    conferir("100.000,00", preco_para_centavos("100.000,00"), 10000000)
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        ctrl = venda_pronta(repo, ids, "2")
        conferir("PIX 2x6,50", ctrl.previa("PIX")["total_centavos"], 1131)
        conferir("Débito 2x6,50", ctrl.previa("Débito")["total_centavos"], 1196)
        conferir("Crédito 2x6,50", ctrl.previa("Crédito 1x")["total_centavos"], 1300)


def t01_conhecidos_erro_e_cancelamento():
    valores_conhecidos()
    valores_conhecidos()                                  # repetir não pode mudar o resultado
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        ctrl = venda_pronta(repo, ids, "1")               # válido
        recusa(ctrl.adicionar_item, ids["milk"], "0")     # erro depois de válido
        conferir("montagem após erro", ctrl.pedido.total_centavos(), 650)
        ctrl.alterar_quantidade(ids["casquinha"], "3")                 # 3 x 6,50 = 19,50
        conferir("quantidade 3", ctrl.pedido.total_centavos(), 1950)
        recusa(ctrl.alterar_quantidade, ids["casquinha"], "0")         # editar para 0 é recusado...
        conferir("após tentar 0", ctrl.pedido.total_centavos(), 1950)  # ...e a montagem é preservada
        ctrl.alterar_quantidade(ids["casquinha"], "1")                 # editar para 1 volta a funcionar
        conferir("quantidade 1", ctrl.pedido.total_centavos(), 650)
        cadastro = CadastroController(repo)
        for _ in range(3):                                # cancelamento repetido
            recusa(cadastro.excluir, "cliente", ids["bruno"], False)
        conferir("clientes após cancelar 3x", [c["id"] for c in repo.listar_clientes()], [1, 2])
    print("T01 ok — valores conhecidos (2 execuções), erro após válido e cancelamento repetido")


# ---------------------------------------------------------------- T02
def t02_id_estavel():
    with tempfile.TemporaryDirectory() as tmp:
        repo = RepositorioSqlite(Path(tmp) / "ids.db")
        for nome in ("Carla", "Ana", "Bruno"):            # IDs 1, 2, 3
            repo.adicionar_cliente(nome)
        cadastro = CadastroController(repo)
        reorganizada = sorted(cadastro.listar("cliente"), key=lambda c: c["nome"])   # Ana, Bruno, Carla
        conferir("1ª posição reorganizada", reorganizada[0]["id"], 2)
        cadastro.salvar("cliente", "Ana Paula", codigo=reorganizada[0]["id"])       # age no ID, não na posição
        conferir("depois de editar", {c["id"]: c["nome"] for c in cadastro.listar("cliente")},
                 {1: "Carla", 2: "Ana Paula", 3: "Bruno"})
        cadastro.excluir("cliente", 1, True)
        cadastro.salvar("cliente", "Bruno Lima", codigo=3)                           # Bruno mudou de posição
        conferir("após excluir o 1", [(c["id"], c["nome"]) for c in cadastro.listar("cliente")],
                 [(2, "Ana Paula"), (3, "Bruno Lima")])
    print("T02 ok — editar/excluir agem no ID mesmo depois de reorganizar ou remover linhas")


# ---------------------------------------------------------------- T03
def t03_persistencia():
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        venda_pronta(repo, ids, "2").finalizar("PIX", True)
        del repo
        reaberto = RepositorioSqlite(caminho)             # mesmo caminho; iniciar() não pode apagar nada
        conferir("clientes", [c["nome"] for c in reaberto.listar_clientes()], ["Ana", "Bruno"])
        conferir("produtos", [p["preco_centavos"] for p in reaberto.listar_produtos()], [650, 1590])
        venda = reaberto.listar_vendas()[0]
        conferir("venda", (venda["id"], venda["cliente"], venda["total_centavos"]), (1, "Ana", 1131))
        RepositorioSqlite(caminho)                        # abrir de novo não duplica nada
        conferir("sem duplicar", (contar(caminho, "clientes"), contar(caminho, "vendas")), (2, 1))
    print("T03 ok — dados e venda reabrem no mesmo caminho, sem duplicar")


# ---------------------------------------------------------------- T04
def t04_falha_transacional():
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        itens = [{"produto_id": ids["casquinha"], "quantidade": 1, "preco_centavos": 650},
                 {"produto_id": ids["milk"], "quantidade": 1, "preco_centavos": 1590},
                 {"produto_id": 999, "quantidade": 1, "preco_centavos": 100}]       # a TERCEIRA falha
        recusa(repo.registrar_venda, ids["ana"], itens, "PIX")
        conferir("vendas/itens após falha", (contar(caminho, "vendas"), contar(caminho, "itens_venda")), (0, 0))

        class RepositorioComCorrida(RepositorioSqlite):
            """Simula: o produto some entre a conferência do catálogo e a gravação."""

            def registrar_venda(self, cliente_id, itens, forma):
                with closing(sqlite3.connect(self.caminho)) as con:
                    with con:
                        con.execute("DELETE FROM produtos WHERE id = ?", (ids["milk"],))
                return super().registrar_venda(cliente_id, itens, forma)

        corrida = RepositorioComCorrida(caminho)
        ctrl = VendaController(corrida)
        ctrl.selecionar_cliente(ids["ana"])
        ctrl.adicionar_item(ids["casquinha"], "1")
        ctrl.adicionar_item(ids["milk"], "1")
        recusa(ctrl.finalizar, "PIX", True)
        conferir("após a corrida", (contar(caminho, "vendas"), contar(caminho, "itens_venda")), (0, 0))
        conferir("montagem preservada", (ctrl.pedido.status, len(ctrl.pedido.itens), ctrl.venda_id), ("ABERTO", 2, None))
    print("T04 ok — falha no 3º item e produto removido durante a gravação: nenhuma venda parcial")


# ---------------------------------------------------------------- T05
def t05_csv_coerente():
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        ctrl = venda_pronta(repo, ids, "2")                # 2 x 6,50 = 13,00
        ctrl.adicionar_item(ids["milk"], "1")              # + 15,90 = 28,90 ; x 0,87 = 25,143 -> 25,14
        comprovante = ctrl.finalizar("PIX", True)
        destino = Path(tmp) / "relatorio.csv"
        ctrl.exportar_csv(destino)
        with open(destino, encoding="utf-8-sig", newline="") as arq:
            linhas = list(csv.reader(arq, delimiter=";"))
        corpo = linhas[1:]
        conferir("linhas", [(l[1], l[2], l[4]) for l in corpo], [("Casquinha", "2", "1300"), ("Milkshake", "1", "1590")])
        conferir("soma dos subtotais", sum(int(l[4]) for l in corpo), 2890)
        conferir("total em todas as linhas", {l[6] for l in corpo}, {"R$ 25,14"})
        venda = repo.listar_vendas()[0]
        conferir("banco x comprovante", (venda["subtotal_centavos"], venda["total_centavos"]), (2890, 2514))
        conferir("comprovante", (comprovante["subtotal_centavos"], comprovante["total_centavos"]), (2890, 2514))
    print("T05 ok — CSV, comprovante e banco concordam: 28,90 -> 25,14 no PIX")


# ---------------------------------------------------------------- T06
def t06_teste_errado_falha_e_previsao_restaurada_passa():
    with tempfile.TemporaryDirectory() as tmp:
        caminho, repo, ids = cenario(tmp)
        obtido = venda_pronta(repo, ids, "2").previa("PIX")["total_centavos"]
        try:
            conferir("PIX 2x6,50 (expectativa PROPOSITALMENTE errada)", obtido, 1200)
        except AssertionError as erro:
            mensagem = str(erro)
        else:
            raise AssertionError("Um teste com expectativa errada precisava falhar, mas passou.")
        assert "esperado 1200, obtido 1131" in mensagem, mensagem
        conferir("PIX 2x6,50 (previsão restaurada)", obtido, 1131)
    print("T06 ok — expectativa errada (1200) falha com mensagem clara; a previsão restaurada (1131) passa")


# ---------------------------------------------------------------- T07
def t07_execucao_pelo_readme_em_outra_pasta():
    readme = (PASTA / "README-A18.md").read_text(encoding="utf-8")
    assert "python verificar.py" in readme and "python main.py" in readme, "README precisa trazer os comandos"
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp) / "copia_de_ensaio"
        destino.mkdir()
        for nome in ARQUIVOS_ENTREGA:
            shutil.copy2(PASTA / nome, destino / nome)      # só o que a entrega lista; sem banco real nem cache
        ambiente = dict(os.environ, A18_FILHO="1")
        r = subprocess.run([sys.executable, "verificar.py"], cwd=destino, capture_output=True, text=True,
                           env=ambiente, timeout=300)
        assert r.returncode == 0, r.stdout + r.stderr
        for caso in ("T01 ok", "T03 ok", "T05 ok", "T06 ok"):
            assert caso in r.stdout, f"{caso} não apareceu na execução em outra pasta:\n{r.stdout}"
        assert not list(destino.glob("*.db")), "a execução criou banco na pasta (deveria usar só bancos temporários)"
    print("T07 ok — a cópia em outra pasta executa `python verificar.py` como o README manda")


# ---------------------------------------------------------------- T08
def t08_teclado_foco_e_mensagens():
    try:
        import tkinter as tk
        import main
        tmp_ctx = tempfile.TemporaryDirectory()
        caminho, repo, ids = cenario(tmp_ctx.name)
        dialogos = DialogosFalsos()
        raiz = main.criar_janela(repositorio=repo, dialogos=dialogos, caminho_banco=caminho)
    except Exception as erro:
        print(f"T08 PENDENTE — sem tkinter/ambiente gráfico aqui ({type(erro).__name__}).")
        return None
    try:
        raiz.update()
        venda = raiz.paineis["venda"]
        nomes = {venda.combo_cliente: "cliente", venda.btn_atualizar: "atualizar", venda.combo_produto: "produto",
                 venda.entry_qtd: "qtd", venda.btn_adicionar: "adicionar", venda.tabela: "tabela",
                 venda.btn_remover: "remover", venda.btn_revisar: "revisar", venda.combo_forma: "forma",
                 venda.btn_finalizar: "finalizar", venda.btn_exportar: "exportar", venda.btn_nova: "nova"}
        # Previsão escrita antes de rodar: ordem de criação; "exportar" sai do ciclo porque começa desabilitado.
        esperado = ["cliente", "atualizar", "produto", "qtd", "adicionar", "tabela",
                    "remover", "revisar", "forma", "finalizar", "nova"]
        venda.combo_cliente.focus_force()
        raiz.update()
        obtido, atual = [], venda.combo_cliente
        for _ in range(len(esperado)):
            obtido.append(nomes.get(atual, type(atual).__name__))
            atual = atual.tk_focusNext()
            atual.focus_force()
            raiz.update()
        conferir("ordem do Tab na venda", obtido, esperado)

        # nenhum widget do CustomTkinter no núcleo: tudo é ttk e alcançável pelo teclado
        def percorrer(widget):
            yield widget
            for filho in widget.winfo_children():
                yield from percorrer(filho)
        assert not [w for w in percorrer(raiz) if type(w).__module__.startswith("customtkinter")]

        # mensagens orientam: dizem o que fazer e a pessoa pode corrigir
        venda.combo_cliente.set("")
        venda.combo_produto.current(0)
        venda.entry_qtd.delete(0, tk.END)
        venda.entry_qtd.insert(0, "1")
        assert venda.adicionar() is True
        dialogos.mensagens.clear()
        assert venda.finalizar() is False
        tipo, texto = dialogos.mensagens[-1]
        assert tipo == "erro" and "Selecione o cliente" in texto, dialogos.mensagens
        assert "Erro:" in venda.lbl_aviso.cget("text")
        venda.combo_cliente.current(0)                     # correção + nova tentativa
        assert venda.finalizar() is True
    finally:
        raiz.destroy()
        tmp_ctx.cleanup()
    print("T08 ok — ordem do Tab confere, só widgets ttk, mensagens de erro orientam e permitem corrigir")
    return True


class DialogosFalsos:
    def __init__(self):
        self.mensagens = []

    def info(self, titulo, texto):
        self.mensagens.append(("info", texto))

    def aviso(self, titulo, texto):
        self.mensagens.append(("aviso", texto))

    def erro(self, titulo, texto):
        self.mensagens.append(("erro", texto))

    def confirmar(self, titulo, texto):
        return True

    def salvar_arquivo(self, titulo, nome_inicial):
        return ""


# ---------------------------------------------------------------- T09
def t09_pendencias_sem_inventar_aprovacao(gui_executada):
    readme = (PASTA / "README-A18.md").read_text(encoding="utf-8")
    assert "Pendências" in readme, "o README precisa ter a seção Pendências"
    print("T09 — NÃO verificado por este script (precisa de pessoa/ambiente real):")
    for item in PENDENCIAS_HUMANAS:
        print("   -", item)
    if not gui_executada:
        print("   - Verificações com janela (T08) não rodaram: sem ambiente gráfico.")
    return gui_executada


def verificar():
    t01_conhecidos_erro_e_cancelamento()
    t02_id_estavel()
    t03_persistencia()
    t04_falha_transacional()
    t05_csv_coerente()
    t06_teste_errado_falha_e_previsao_restaurada_passa()
    if not os.environ.get("A18_FILHO"):
        t07_execucao_pelo_readme_em_outra_pasta()
    gui = t08_teclado_foco_e_mensagens() is True
    t09_pendencias_sem_inventar_aprovacao(gui)
    return gui        # sem janela verificada, não se declara sucesso total


if __name__ == "__main__":
    if verificar():
        print("Casos executados: previsões e resultados conferem.")
    else:
        print("Verificações ainda incompletas (veja os casos PENDENTES acima).")
