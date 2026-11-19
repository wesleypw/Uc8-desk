# A19: demonstração da candidata em dados fictícios, sem janela, que outra pessoa consegue repetir.
#   python demo_candidata.py            # usa uma pasta temporária (nada fica salvo)
#   python demo_candidata.py ensaio.db  # grava no banco de ensaio indicado (precisa NÃO existir)
import csv
import sys
import tempfile
from pathlib import Path

from controller import VendaController
from repositorio import RepositorioSqlite


def executar(caminho_banco, caminho_csv):
    """Roda o roteiro e devolve a lista de etapas {etapa, acao, observado}. Só usa o código da candidata."""
    etapas = []

    def registrar(etapa, acao, observado):
        etapas.append({"etapa": etapa, "acao": acao, "observado": observado})

    repo = RepositorioSqlite(caminho_banco)
    ana = repo.adicionar_cliente("Ana (fictícia)")
    casquinha = repo.adicionar_produto("Casquinha", "6,50")
    registrar("Problema", "anotar a venda de 2 casquinhas para a Ana, pagando no PIX", f"cliente {ana}, produto {casquinha}")

    # fluxo válido
    venda = VendaController(repo)
    venda.selecionar_cliente(ana)
    venda.adicionar_item(casquinha, "2")
    previa = venda.previa("PIX")
    registrar("Válido", "montar 2 x 6,50 e conferir a prévia no PIX",
              f"subtotal {previa['subtotal_centavos']} -> total {previa['total_centavos']} centavos")
    comprovante = venda.finalizar("PIX", True)
    registrar("Válido", "finalizar a venda", f"venda {comprovante['venda_id']} gravada: {comprovante['total_formatado']}")

    # recusa e correção: outra venda, desta vez sem cliente e com quantidade inválida
    venda.nova_venda()
    try:
        venda.adicionar_item(casquinha, "0")
        observado = "ACEITOU (inesperado)"
    except ValueError as erro:
        observado = f"recusado: {erro}"
    registrar("Recusa", "adicionar quantidade 0", observado)
    venda.adicionar_item(casquinha, "2")
    registrar("Correção", "informar quantidade 2", f"montagem com {venda.pedido.total_centavos()} centavos")
    try:
        venda.finalizar("PIX", True)
        observado = "ACEITOU (inesperado)"
    except ValueError as erro:
        observado = f"recusado: {erro}"
    registrar("Recusa", "finalizar sem escolher o cliente", observado)
    venda.selecionar_cliente(ana)
    registrar("Correção", "escolher a cliente e finalizar", f"venda {venda.finalizar('Débito', True)['venda_id']} gravada no Débito")

    # persistência (reabrindo o arquivo) e relatório
    reaberto = RepositorioSqlite(caminho_banco)
    vendas = reaberto.listar_vendas()
    registrar("Persistência", "reabrir o banco e listar as vendas",
              "; ".join(f"venda {v['id']} {v['forma']} total {v['total_centavos']}" for v in vendas))
    venda.exportar_csv(caminho_csv)
    with open(caminho_csv, encoding="utf-8-sig", newline="") as arq:
        linhas = list(csv.reader(arq, delimiter=";"))
    registrar("Relatório", "exportar o CSV da última venda", f"{len(linhas) - 1} linha(s): {';'.join(linhas[1])}")
    return etapas


def imprimir(etapas):
    for numero, e in enumerate(etapas, 1):
        print(f"{numero}. [{e['etapa']}] {e['acao']}\n     -> {e['observado']}")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        raise SystemExit("Uso: python demo_candidata.py [banco-de-ensaio.db]")
    if len(sys.argv) == 2:
        banco = Path(sys.argv[1])
        if not banco.is_absolute():
            banco = Path(__file__).resolve().parent / banco
        banco = banco.resolve()
        if banco.exists():
            raise SystemExit(f"{banco} já existe; use um nome novo para não misturar com outros dados.")
        imprimir(executar(banco, banco.with_suffix(".csv")))
    else:
        with tempfile.TemporaryDirectory() as tmp:
            imprimir(executar(Path(tmp) / "demo.db", Path(tmp) / "demo.csv"))
