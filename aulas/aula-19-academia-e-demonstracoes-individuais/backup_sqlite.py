# A19: confere o banco padrão e atualiza copia-nova.db somente quando necessário.
#   python backup_sqlite.py
# Também aceita caminhos explícitos: python backup_sqlite.py origem.db copia.db
import sys
from contextlib import closing
from itertools import zip_longest
from pathlib import Path
import os
import sqlite3
import tempfile


def _abrir_somente_leitura(caminho):
    """Abre sem poder criar nem escrever: um caminho errado vira erro, não um banco vazio novo."""
    return sqlite3.connect(Path(caminho).resolve().as_uri() + "?mode=ro", uri=True)


def criar_backup(origem, destino):
    """Copia `origem` para `destino`, atualizando-o só depois de conferir a nova cópia.

    - origem ausente        -> FileNotFoundError (nenhum arquivo é criado, nem a origem, nem o destino);
    - origem igual ao destino -> ValueError (a origem nunca é substituída);
    - pasta do destino ausente -> FileNotFoundError;
    - falha no meio ou cópia sem integridade -> a cópia anterior permanece intacta.
    Devolve o caminho (Path) da cópia criada ou atualizada.
    """
    origem, destino = Path(origem), Path(destino)
    if not origem.is_file():
        raise FileNotFoundError(f"Banco de origem não encontrado: {origem}")
    if origem == destino or (destino.exists() and origem.samefile(destino)):
        raise ValueError("A origem e o destino do backup não podem ser o mesmo arquivo.")
    if not destino.resolve().parent.is_dir():
        raise FileNotFoundError(f"A pasta do destino não existe: {destino.resolve().parent}")

    with tempfile.NamedTemporaryFile(
        prefix=f".{destino.name}.", suffix=".tmp", dir=destino.resolve().parent, delete=False
    ) as temporario:
        caminho_temporario = Path(temporario.name)

    try:
        # A cópia é preparada em arquivo temporário para preservar o backup anterior se algo falhar.
        with closing(_abrir_somente_leitura(origem)) as entrada, closing(
            sqlite3.connect(caminho_temporario)
        ) as saida:
            entrada.backup(saida)
        with closing(_abrir_somente_leitura(caminho_temporario)) as copia:
            resultado = copia.execute("PRAGMA integrity_check").fetchone()[0]
        if resultado != "ok":
            raise sqlite3.DatabaseError(f"A cópia falhou na verificação de integridade: {resultado}")
        try:
            os.replace(caminho_temporario, destino)
        except PermissionError as erro:
            raise PermissionError(
                f"Não foi possível atualizar {destino}; feche programas que estejam usando o backup e tente novamente."
            ) from erro
    except BaseException:
        caminho_temporario.unlink(missing_ok=True)
        raise
    return destino


def bancos_iguais(origem, destino):
    """Compara estrutura e conteúdo SQLite sem depender dos bytes físicos dos arquivos."""
    origem, destino = Path(origem), Path(destino)
    if not origem.is_file():
        raise FileNotFoundError(f"Banco de origem não encontrado: {origem}")
    if not destino.is_file():
        return False
    if origem.samefile(destino):
        raise ValueError("A origem e o destino do backup não podem ser o mesmo arquivo.")

    sentinela = object()
    with closing(_abrir_somente_leitura(origem)) as principal, closing(
        _abrir_somente_leitura(destino)
    ) as copia:
        return all(
            linha_principal == linha_copia
            for linha_principal, linha_copia in zip_longest(
                principal.iterdump(), copia.iterdump(), fillvalue=sentinela
            )
        )


def sincronizar_backup(origem, destino):
    """Atualiza a cópia apenas quando ela não existe ou difere do banco principal."""
    return atualizar_backup(origem, destino)


def atualizar_backup(origem, destino):
    """Substitui o backup somente quando a origem difere da cópia."""
    if bancos_iguais(origem, destino):
        return False
    criar_backup(origem, destino)
    return True


def consultar_copia(destino, sql, parametros=()):
    """Consulta a cópia por uma conexão independente (somente leitura)."""
    with closing(_abrir_somente_leitura(destino)) as con:
        return con.execute(sql, parametros).fetchall()


def resumo_da_copia(destino):
    """{tabela: quantidade de linhas} lido da cópia, para conferir o que foi copiado."""
    tabelas = [t for (t,) in consultar_copia(
        destino, "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    return {t: consultar_copia(destino, f'SELECT count(*) FROM "{t}"')[0][0] for t in tabelas}


if __name__ == "__main__":
    pasta = Path(__file__).resolve().parent
    if len(sys.argv) == 1:
        origem = pasta / "dados_sorveteria.db"
        destino = pasta / "copia-nova.db"
    elif len(sys.argv) == 3:
        origem, destino = Path(sys.argv[1]), Path(sys.argv[2])
    else:
        print("Uso: python backup_sqlite.py [origem.db copia.db]")
        raise SystemExit(2)
    destino_existia = Path(destino).exists()
    try:
        alterado = sincronizar_backup(origem, destino)
    except (OSError, ValueError, sqlite3.Error) as erro:
        print(f"Backup recusado: {erro}")
        raise SystemExit(1)
    acao = "atualizado" if destino_existia else "criado"
    if alterado:
        print(f"Backup {acao} e conferido: {destino}")
    else:
        print(f"Backup já estava atualizado: {destino}")
    for tabela, linhas in resumo_da_copia(destino).items():
        print(f"  {tabela}: {linhas} linha(s)")
