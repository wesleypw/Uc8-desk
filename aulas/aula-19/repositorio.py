# A19 (candidata validada na A18): repositório da A16 + vendas gravadas em transação (venda e itens juntos).

from contextlib import closing, contextmanager
from datetime import datetime
from pathlib import Path
import sqlite3

from pagamento import FATORES, calcular_pagamento, preco_para_centavos


def validar_nome(nome):
    """Valida se o nome é uma string não vazia."""
    txt = str(nome).strip() if nome is not None else ""
    if not txt:
        raise ValueError("O nome é obrigatório e não pode ser vazio.")
    return txt


def validar_id(codigo):
    """Valida e converte o código/ID para um inteiro positivo (> 0)."""
    try:
        val = int(codigo)
        if val <= 0:
            raise ValueError("O ID deve ser um número inteiro positivo.")
        return val
    except (ValueError, TypeError):
        raise ValueError("ID inválido. Informe um número inteiro positivo.")


def validar_preco(preco):
    """
    Valida e converte o texto do preço para centavos inteiros.
    Aceita inteiros (já em centavos) ou textos monetários válidos (ex: '7,50' -> 750).
    Limita o preço máximo didático a R$ 100.000,00 (10.000.000 centavos).
    """
    if isinstance(preco, int):
        centavos = preco
    else:
        centavos = preco_para_centavos(preco)

    if centavos <= 0:
        raise ValueError("O preço deve ser maior que zero.")
    if centavos > 10_000_000:
        raise ValueError("O preço excede o limite máximo permitido de R$ 100.000,00.")

    return centavos


class RepositorioSqlite:
    """Repositório de persistência de dados utilizando SQLite (CRUD completo)."""

    def __init__(self, caminho, caminho_backup=None):
        if not caminho:
            raise ValueError("O caminho do banco de dados é obrigatório.")
        self.caminho = str(Path(caminho).resolve())
        self.caminho_backup = None
        self.iniciar()

    def conectar(self):
        """Retorna uma nova conexão; o SQLite só confere chaves estrangeiras se for pedido a cada conexão."""
        con = sqlite3.connect(self.caminho)
        con.execute("PRAGMA foreign_keys = ON")
        return con

    @contextmanager
    def transacao(self):
        """Confirma a transação sem atualizar cópias externas."""
        with closing(self.conectar()) as con:
            with con:
                yield con

    def iniciar(self):
        """Cria as tabelas 'produtos' e 'clientes' caso ainda não existam."""
        with self.transacao() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    preco_centavos INTEGER NOT NULL
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL
                )
            """)
        self.iniciar_vendas()

    def iniciar_vendas(self):
        """Cria 'vendas' e 'itens_venda'; os vínculos por ID são conferidos pelo próprio banco."""
        with self.transacao() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS vendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
                    forma TEXT NOT NULL,
                    subtotal_centavos INTEGER NOT NULL CHECK (subtotal_centavos > 0),
                    total_centavos INTEGER NOT NULL CHECK (total_centavos > 0),
                    criado_em TEXT NOT NULL
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS itens_venda (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venda_id INTEGER NOT NULL REFERENCES vendas(id),
                    produto_id INTEGER NOT NULL REFERENCES produtos(id),
                    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
                    preco_centavos INTEGER NOT NULL CHECK (preco_centavos > 0)
                )
            """)

    def adicionar_produto(self, nome, preco):
        """
        Insere um produto no banco utilizando consulta parametrizada.
        Retorna o ID gerado para a nova linha.
        """
        nome_validado = validar_nome(nome)
        preco_centavos = validar_preco(preco)

        with self.transacao() as con:
            cursor = con.execute(
                "INSERT INTO produtos (nome, preco_centavos) VALUES (?, ?)",
                (nome_validado, preco_centavos)
            )
            produto_id = cursor.lastrowid
        return produto_id

    def listar_produtos(self):
        """Retorna a lista de todos os produtos como dicionários."""
        with closing(self.conectar()) as con:
            cursor = con.execute("SELECT id, nome, preco_centavos FROM produtos ORDER BY id ASC")
            linhas = cursor.fetchall()
            return [
                {"id": linha[0], "nome": linha[1], "preco_centavos": linha[2]}
                for linha in linhas
            ]

    def editar_produto(self, codigo, nome, preco):
        """
        Atualiza o nome e o preço de um produto existente identificado pelo ID.
        Verifica o rowcount para garantir que a linha realmente existia.
        """
        id_valido = validar_id(codigo)
        nome_validado = validar_nome(nome)
        preco_centavos = validar_preco(preco)

        with self.transacao() as con:
            cursor = con.execute(
                "UPDATE produtos SET nome = ?, preco_centavos = ? WHERE id = ?",
                (nome_validado, preco_centavos, id_valido)
            )
            if cursor.rowcount == 0:
                raise ValueError(f"Produto com ID {id_valido} não encontrado para edição.")
        return True

    def excluir_produto(self, codigo, confirmado=False):
        """
        Exclui um produto do banco pelo ID, exigindo confirmação explícita.
        """
        id_valido = validar_id(codigo)
        if not confirmado:
            raise ValueError("A exclusão deve ser explicitamente confirmada.")

        try:
            with self.transacao() as con:
                cursor = con.execute(
                    "DELETE FROM produtos WHERE id = ?",
                    (id_valido,)
                )
                if cursor.rowcount == 0:
                    raise ValueError(f"Produto com ID {id_valido} não encontrado para exclusão.")
        except sqlite3.IntegrityError:
            raise ValueError(
                f"Produto ID {id_valido} está vinculado a vendas e não pode ser excluído."
            )
        return True

    def adicionar_cliente(self, nome):
        """Insere um cliente no banco utilizando consulta parametrizada. Retorna o ID gerado."""
        nome_validado = validar_nome(nome)
        with self.transacao() as con:
            cursor = con.execute(
                "INSERT INTO clientes (nome) VALUES (?)",
                (nome_validado,)
            )
            cliente_id = cursor.lastrowid
        return cliente_id

    def listar_clientes(self):
        """Retorna a lista de clientes cadastrados como dicionários."""
        with closing(self.conectar()) as con:
            cursor = con.execute("SELECT id, nome FROM clientes ORDER BY id ASC")
            linhas = cursor.fetchall()
            return [
                {"id": linha[0], "nome": linha[1]}
                for linha in linhas
            ]

    def editar_cliente(self, codigo, nome):
        """Atualiza o nome de um cliente existente identificado pelo ID."""
        id_valido = validar_id(codigo)
        nome_validado = validar_nome(nome)

        with self.transacao() as con:
            cursor = con.execute(
                "UPDATE clientes SET nome = ? WHERE id = ?",
                (nome_validado, id_valido)
            )
            if cursor.rowcount == 0:
                raise ValueError(f"Cliente com ID {id_valido} não encontrado para edição.")
        return True

    def excluir_cliente(self, codigo, confirmado=False):
        """Exclui um cliente do banco pelo ID, exigindo confirmação explícita."""
        id_valido = validar_id(codigo)
        if not confirmado:
            raise ValueError("A exclusão deve ser explicitamente confirmada.")

        try:
            with self.transacao() as con:
                cursor = con.execute(
                    "DELETE FROM clientes WHERE id = ?",
                    (id_valido,)
                )
                if cursor.rowcount == 0:
                    raise ValueError(f"Cliente com ID {id_valido} não encontrado para exclusão.")
        except sqlite3.IntegrityError:
            raise ValueError(
                f"Cliente ID {id_valido} está vinculado a vendas e não pode ser excluído."
            )
        return True

    # ---------- vendas ----------
    def registrar_venda(self, cliente_id, itens, forma):
        """Grava a venda e TODOS os itens na mesma conexão e transação.

        itens: lista de {"produto_id", "quantidade", "preco_centavos"} (preço visto na montagem).
        Se qualquer gravação falhar, o 'with con' desfaz o conjunto (rollback) e nada fica pela metade.
        Devolve o ID da venda. Só quem recebe esse ID pode anunciar sucesso.
        """
        cliente = validar_id(cliente_id)
        if forma not in FATORES:
            raise ValueError(f"Forma de pagamento inválida: '{forma}'.")
        if not itens:
            raise ValueError("A venda precisa de pelo menos um item.")

        linhas = []
        for item in itens:
            quantidade = item.get("quantidade")
            preco = item.get("preco_centavos")
            if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
                raise ValueError("Quantidade do item deve ser um inteiro positivo.")
            if not isinstance(preco, int) or isinstance(preco, bool) or preco <= 0:
                raise ValueError("Preço do item deve ser um inteiro positivo em centavos.")
            linhas.append((validar_id(item.get("produto_id")), quantidade, preco))

        subtotal = sum(q * p for _, q, p in linhas)
        _, _, total_decimal = calcular_pagamento(f"{subtotal / 100:.2f}", forma)
        total = int((total_decimal * 100).to_integral_value())
        agora = datetime.now().isoformat(timespec="seconds")

        try:
            with self.transacao() as con:
                venda_id = con.execute(
                    "INSERT INTO vendas (cliente_id, forma, subtotal_centavos, total_centavos, criado_em) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (cliente, forma, subtotal, total, agora),
                ).lastrowid
                for produto_id, quantidade, preco in linhas:
                    con.execute(
                        "INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_centavos) "
                        "VALUES (?, ?, ?, ?)",
                        (venda_id, produto_id, quantidade, preco),
                    )
        except sqlite3.IntegrityError as erro:
            raise ValueError(
                "Cliente ou produto da venda não existe mais; a venda foi desfeita por completo."
            ) from erro
        return venda_id

    def listar_vendas(self):
        """Vendas com seus itens, ordenadas por ID."""
        with closing(self.conectar()) as con:
            cabecalhos = con.execute(
                "SELECT v.id, v.cliente_id, c.nome, v.forma, v.subtotal_centavos, v.total_centavos, v.criado_em "
                "FROM vendas v JOIN clientes c ON c.id = v.cliente_id ORDER BY v.id ASC"
            ).fetchall()
            vendas = []
            for vid, cid, cnome, forma, subtotal, total, criado in cabecalhos:
                itens = con.execute(
                    "SELECT i.produto_id, p.nome, i.quantidade, i.preco_centavos "
                    "FROM itens_venda i JOIN produtos p ON p.id = i.produto_id "
                    "WHERE i.venda_id = ? ORDER BY i.id ASC",
                    (vid,),
                ).fetchall()
                vendas.append({
                    "id": vid, "cliente_id": cid, "cliente": cnome, "forma": forma,
                    "subtotal_centavos": subtotal, "total_centavos": total, "criado_em": criado,
                    "itens": [
                        {"produto_id": pid, "nome": nome, "quantidade": q,
                         "preco_centavos": preco, "subtotal_centavos": q * preco}
                        for pid, nome, q, preco in itens
                    ],
                })
            return vendas
