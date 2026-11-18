# A19 — verificações T01–T09. As expectativas são escritas À MÃO antes das chamadas
# (13,00 x 0,87 = 11,31; 13,00 x 0,92 = 11,96; contagens de linhas decididas antes de copiar).
import hashlib
import json
import sqlite3
import tempfile
import zipfile
from contextlib import closing
from pathlib import Path

import academia_amostra as academia
import backup_sqlite
import demo_candidata
import entrega
from repositorio import RepositorioSqlite
from controller import VendaController

PASTA = Path(__file__).resolve().parent
# O que um script NÃO consegue aprovar fica declarado aqui, nunca marcado como feito.
PENDENCIAS_HUMANAS = {
    "T01": "apresentar a demonstração com suas próprias palavras (a execução está verificada; a explicação é sua)",
    "T03": "responder a pergunta técnica individual explicando uma decisão apontando código e execução",
    "T09": "receber o feedback (evidência por indicador e teste de recuperação) de quem avalia",
}


def sha(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def recusa(tipo_erro, funcao, *args):
    try:
        funcao(*args)
    except tipo_erro as erro:
        return str(erro)
    raise AssertionError(f"Era esperado {tipo_erro.__name__}, mas a operação foi aceita.")


def conferir(rotulo, obtido, esperado):
    assert obtido == esperado, f"{rotulo}: esperado {esperado!r}, obtido {obtido!r}"


def banco_de_ensaio(tmp, nome="origem-ficticia.db"):
    """Origem fictícia: 2 clientes conhecidos, 1 produto e 1 venda."""
    caminho = Path(tmp) / nome
    repo = RepositorioSqlite(caminho)
    lia = repo.adicionar_cliente("Lia fictícia")
    repo.adicionar_cliente("Rui fictício")
    casquinha = repo.adicionar_produto("Casquinha", "6,50")
    venda = VendaController(repo)
    venda.selecionar_cliente(lia)
    venda.adicionar_item(casquinha, "2")
    venda.finalizar("PIX", True)
    return caminho, repo


# ---------------------------------------------------------------- T01 / T02
def t01_t02_demonstracao():
    with tempfile.TemporaryDirectory() as tmp:
        etapas = demo_candidata.executar(Path(tmp) / "demo.db", Path(tmp) / "demo.csv")
    por_etapa = {}
    for e in etapas:
        por_etapa.setdefault(e["etapa"], []).append(e["observado"])
    # T02: fluxo válido + recusa/correção + persistência + relatório, todos presentes
    for obrigatoria in ("Válido", "Recusa", "Correção", "Persistência", "Relatório"):
        assert obrigatoria in por_etapa, f"a demonstração não tem a etapa {obrigatoria}"
    # T01: execução real conferida com valores calculados no papel
    assert any("1300 -> total 1131" in o for o in por_etapa["Válido"]), por_etapa["Válido"]
    assert any("R$ 11,31" in o for o in por_etapa["Válido"])
    assert any("Quantidade inválida" in o for o in por_etapa["Recusa"]), por_etapa["Recusa"]
    assert any("Selecione o cliente" in o for o in por_etapa["Recusa"]), por_etapa["Recusa"]
    conferir("persistência", por_etapa["Persistência"], ["venda 1 PIX total 1131; venda 2 Débito total 1196"])
    conferir("relatório", por_etapa["Relatório"], ["1 linha(s): 1;Casquinha;2;650;1300;Débito;R$ 11,96"])
    roteiro = (PASTA / "roteiro-demo.md").read_text(encoding="utf-8")
    assert "python demo_candidata.py" in roteiro and "python verificar.py" in roteiro
    print("T01 ok — a demonstração executa e os valores batem (1300 -> 1131; Débito 1196); roteiro traz os comandos")
    print("T02 ok — a demonstração tem fluxo válido, recusa com correção, persistência (reabrindo) e relatório CSV")


# ---------------------------------------------------------------- T04
def t04_mapa_da_academia():
    # entidades e IDs, lidos dos dados (não de memória)
    conferir("alunos", [a["id"] for a in academia.ALUNOS], [41, 92])
    conferir("planos", [p["id"] for p in academia.PLANOS], [7])
    conferir("matrículas", [(m["id"], m["aluno_id"], m["plano_id"]) for m in academia.MATRICULAS], [(101, 41, 7)])
    # responsabilidade: o controller consulta uma matrícula e devolve CÓPIA; ID inexistente -> None
    assert academia.consultar_matricula(101) == {"id": 101, "aluno_id": 41, "plano_id": 7}
    assert academia.consultar_matricula(999) is None
    copia = academia.consultar_matricula(101)
    copia["aluno_id"] = 92
    assert academia.MATRICULAS[0]["aluno_id"] == 41, "alterar a cópia não pode mudar os dados"
    # armazenamento: a amostra só tem listas em memória e uma representação JSON
    assert json.loads(academia.representar_json({"alunos": academia.ALUNOS}))["alunos"][0]["id"] == 41
    fonte = (PASTA / "academia_amostra.py").read_text(encoding="utf-8")
    assert "import tkinter" not in fonte and "sqlite3" not in fonte and "open(" not in fonte, \
        "a amostra não tem GUI, banco nem arquivo: essas camadas não podem ser afirmadas pela leitura"
    # as duas perguntas da amostra, respondidas com os dados:
    matriculas_do_41 = [m["id"] for m in academia.MATRICULAS if m["aluno_id"] == 41]
    conferir("excluir o aluno 41 deixaria matrículas órfãs", matriculas_do_41, [101])   # falta regra de vínculo
    renomeada = [dict(a, nome="Lia corrigida") if a["id"] == 41 else dict(a) for a in academia.ALUNOS]
    assert next(a for a in renomeada if a["id"] == 41)["id"] == 41     # corrigir o nome não exige outro ID
    assert academia.MATRICULAS[0]["aluno_id"] == 41                    # o vínculo continua válido
    print("T04 ok — entidades/IDs (41, 92, 7, 101), controller devolve cópia, armazenamento só em memória/JSON; "
          "sem GUI/banco na amostra")


# ---------------------------------------------------------------- T05
def t05_atualiza_destino_existente():
    with tempfile.TemporaryDirectory() as tmp:
        origem, _ = banco_de_ensaio(tmp)
        primeira = Path(tmp) / "copia-1.db"
        backup_sqlite.criar_backup(origem, primeira)
        assinatura = sha(primeira)
        repo = RepositorioSqlite(origem)
        repo.adicionar_cliente("Davi fictício")
        assert backup_sqlite.criar_backup(origem, primeira) == primeira
        assert sha(primeira) != assinatura, "o backup existente deve receber as alterações da origem"
        conferir("clientes depois da atualização",
                 backup_sqlite.consultar_copia(primeira, "SELECT count(*) FROM clientes"), [(3,)])
        conferir("integridade depois da atualização",
                 backup_sqlite.consultar_copia(primeira, "PRAGMA integrity_check"), [("ok",)])
        recusa(ValueError, backup_sqlite.criar_backup, origem, origem)
        conferir("origem não foi substituída", len(repo.listar_clientes()), 3)
    print("T05 ok — repetir o backup atualiza a mesma cópia; a nova cópia passa na integridade")


# ---------------------------------------------------------------- T06
def t06_origem_ausente():
    with tempfile.TemporaryDirectory() as tmp:
        ausente, destino = Path(tmp) / "nao-existe.db", Path(tmp) / "copia.db"
        assert "não encontrado" in recusa(FileNotFoundError, backup_sqlite.criar_backup, ausente, destino)
        assert not ausente.exists(), "a origem ausente não pode ser criada como banco vazio"
        assert not destino.exists(), "nenhum destino pode ser criado"
        assert sorted(p.name for p in Path(tmp).iterdir()) == []
        recusa(FileNotFoundError, backup_sqlite.criar_backup, Path(tmp), Path(tmp) / "x.db")   # pasta não é banco
        origem, _ = banco_de_ensaio(tmp)
        recusa(FileNotFoundError, backup_sqlite.criar_backup, origem, Path(tmp) / "pasta-inexistente" / "c.db")
        assert not (Path(tmp) / "pasta-inexistente").exists()
    print("T06 ok — origem ausente/pasta de destino ausente são recusadas sem criar nenhum arquivo")


# ---------------------------------------------------------------- T07
def t07_copia_confere():
    with tempfile.TemporaryDirectory() as tmp:
        origem, repo = banco_de_ensaio(tmp)
        repo.adicionar_cliente("Davi fictício")                # 3º cliente ANTES do backup: previsão = 3 na cópia
        copia = backup_sqlite.criar_backup(origem, Path(tmp) / "copia-nova.db")
        conferir("integridade", backup_sqlite.consultar_copia(copia, "PRAGMA integrity_check"), [("ok",)])
        conferir("registro conhecido", backup_sqlite.consultar_copia(copia, "SELECT id, nome FROM clientes WHERE id = ?", (2,)),
                 [(2, "Rui fictício")])
        conferir("clientes na cópia", backup_sqlite.consultar_copia(copia, "SELECT count(*) FROM clientes"), [(3,)])
        conferir("venda na cópia", backup_sqlite.consultar_copia(
            copia, "SELECT id, forma, total_centavos FROM vendas"), [(1, "PIX", 1131)])
        conferir("resumo", backup_sqlite.resumo_da_copia(copia),
                 {"clientes": 3, "itens_venda": 1, "produtos": 1, "vendas": 1})
        # a origem continua utilizável e a cópia não acompanha o que vem depois
        repo.adicionar_cliente("Eva fictícia")
        conferir("origem depois do backup", len(RepositorioSqlite(origem).listar_clientes()), 4)
        conferir("cópia continua com 3", backup_sqlite.consultar_copia(copia, "SELECT count(*) FROM clientes"), [(3,)])
    print("T07 ok — cópia consultada por outra conexão: integridade ok, ID 2 = Rui, 3 clientes, venda 1; origem segue usável")


# ---------------------------------------------------------------- T08
def t08_entrega_limpa_e_limites():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        for relativo in ("main.py", "README.md", "dados_sorveteria.db", "ensaio.sqlite3", "__pycache__/main.cpython-312.pyc",
                         ".venv/lib/x.py", "venv/bin/python", ".git/config", ".env", "dados.db-wal", "entrega-a19.zip",
                         "sub/modulo.py", "sub/__pycache__/m.pyc"):
            alvo = base / relativo
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_text("x", encoding="utf-8")
        conferir("entrega filtrada", entrega.arquivos_da_entrega(base), ["README.md", "main.py", "sub/modulo.py"])
        with tempfile.TemporaryDirectory() as saida:
            zip_criado = entrega.montar_zip(base, Path(saida) / "entrega-teste-a19.zip")
            with zipfile.ZipFile(zip_criado) as z:
                conferir("conteúdo do zip", sorted(z.namelist()), ["README.md", "main.py", "sub/modulo.py"])
    # a pasta real desta aula também não pode vazar nada indevido
    real = entrega.arquivos_da_entrega(PASTA)
    indevidos = [a for a in real if a.endswith((".db", ".pyc", ".zip")) or "__pycache__" in a or a.startswith(".")]
    assert not indevidos, indevidos
    for esperado in ("backup_sqlite.py", "verificar.py", "roteiro-demo.md", "registro-a19.md", "entrega.py"):
        assert esperado in real, f"{esperado} deveria entrar na entrega"
    roteiro = (PASTA / "roteiro-demo.md").read_text(encoding="utf-8")
    trecho = roteiro.split("Limite e próximo teste:")[1].split("##")[0].strip()
    assert len(trecho) > 40, "o roteiro precisa documentar limites e o próximo teste"
    print("T08 ok — entrega sem .db/.pyc/__pycache__/.venv/.git/.env; arquivos da aula presentes; limites documentados")


# ---------------------------------------------------------------- T09
def t09_copia_automatica():
    with tempfile.TemporaryDirectory() as tmp:
        origem = Path(tmp) / "dados_sorveteria.db"
        copia = Path(tmp) / "copia-nova.db"
        repo = RepositorioSqlite(origem, copia)
        conferir("cópia inicial", backup_sqlite.consultar_copia(copia, "PRAGMA integrity_check"), [("ok",)])

        cliente = repo.adicionar_cliente("Lia")
        produto = repo.adicionar_produto("Casquinha", "6,50")
        conferir("cadastros copiados", backup_sqlite.consultar_copia(
            copia, "SELECT nome FROM clientes"), [("Lia",)])
        conferir("produto copiado", backup_sqlite.consultar_copia(
            copia, "SELECT nome, preco_centavos FROM produtos"), [("Casquinha", 650)])

        repo.editar_cliente(cliente, "Lia atualizada")
        repo.editar_produto(produto, "Casquinha grande", "8,00")
        conferir("edições copiadas", backup_sqlite.consultar_copia(
            copia, "SELECT nome FROM clientes"), [("Lia atualizada",)])
        conferir("edição de produto copiada", backup_sqlite.consultar_copia(
            copia, "SELECT nome, preco_centavos FROM produtos"), [("Casquinha grande", 800)])

        venda = repo.registrar_venda(cliente, [
            {"produto_id": produto, "quantidade": 2, "preco_centavos": 800}
        ], "PIX")
        conferir("venda copiada", backup_sqlite.consultar_copia(
            copia, "SELECT id, forma, total_centavos FROM vendas"), [(venda, "PIX", 1392)])
        conferir("item de venda copiado", backup_sqlite.consultar_copia(
            copia, "SELECT venda_id, produto_id, quantidade FROM itens_venda"),
            [(venda, produto, 2)])
        conferir("integridade final", backup_sqlite.consultar_copia(copia, "PRAGMA integrity_check"), [("ok",)])
    print("T09 ok — alterações de clientes, produtos e vendas atualizam automaticamente copia-nova.db")


# ---------------------------------------------------------------- extras
def t_extras_backup():
    """Falha na origem preserva o backup existente; bancos inválidos e vazios são tratados."""
    with tempfile.TemporaryDirectory() as tmp:
        origem, _ = banco_de_ensaio(tmp)
        valido = backup_sqlite.criar_backup(origem, Path(tmp) / "ok.db")                         # válido
        texto = Path(tmp) / "nao-e-banco.db"
        texto.write_text("isto não é um banco SQLite" * 20, encoding="utf-8")
        assinatura = sha(texto)
        assinatura_backup = sha(valido)
        recusa(sqlite3.DatabaseError, backup_sqlite.criar_backup, texto, valido)                   # origem inválida
        conferir("backup válido preservado após erro", sha(valido), assinatura_backup)
        conferir("origem inválida intacta", sha(texto), assinatura)
        vazio = Path(tmp) / "vazio.db"                                                           # limite: banco sem tabelas
        with closing(sqlite3.connect(vazio)):
            pass
        copia_vazia = backup_sqlite.criar_backup(vazio, Path(tmp) / "copia-vazia.db")
        conferir("resumo do vazio", backup_sqlite.resumo_da_copia(copia_vazia), {})
        assert backup_sqlite.criar_backup(origem, Path(tmp) / "ok-de-novo.db").exists()         # correção: nome novo
        assinatura_origem = sha(origem)
        assinatura_copia = sha(valido)
        assert not backup_sqlite.sincronizar_backup(origem, valido)
        conferir("cópia idêntica não foi regravada", sha(valido), assinatura_copia)
        RepositorioSqlite(origem).adicionar_cliente("Davi fictício")
        assert backup_sqlite.sincronizar_backup(origem, valido)
        conferir("cópia diferente atualizada", backup_sqlite.consultar_copia(
            valido, "SELECT count(*) FROM clientes"), [(3,)])
        assert sha(origem) != assinatura_origem
    print("Extras ok — erro preserva backup existente; origem inválida e banco vazio tratados")


def verificar():
    t01_t02_demonstracao()
    t04_mapa_da_academia()
    t05_atualiza_destino_existente()
    t06_origem_ausente()
    t07_copia_confere()
    t08_entrega_limpa_e_limites()
    t09_copia_automatica()
    t_extras_backup()
    print("Não verificado por script (precisa de pessoa):")
    for caso, texto in PENDENCIAS_HUMANAS.items():
        print(f"   - {caso}: {texto}")
    return True      # tudo o que um script pode verificar foi executado; as pendências acima continuam humanas


if __name__ == "__main__":
    if verificar():
        print("Casos automatizáveis executados: previsões e resultados conferem (pendências humanas listadas acima).")
    else:
        print("Verificações ainda incompletas.")
