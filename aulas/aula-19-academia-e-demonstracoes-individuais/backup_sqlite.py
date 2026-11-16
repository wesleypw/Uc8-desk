# A19: backup de um banco SQLite fictício para uma cópia NOVA, conferida por outra conexão.
#   python backup_sqlite.py origem-ficticia.db copia-nova.db     (use uma pasta de ensaio)
# Regras: origem precisa existir; destino NÃO pode existir; a origem nunca é alterada nem restaurada por cima.
import sys
from contextlib import closing
from pathlib import Path
import sqlite3


def _abrir_somente_leitura(caminho):
    """Abre sem poder criar nem escrever: um caminho errado vira erro, não um banco vazio novo."""
    return sqlite3.connect(Path(caminho).resolve().as_uri() + "?mode=ro", uri=True)


def criar_backup(origem, destino):
    """Copia `origem` para `destino` com a API de backup do SQLite e confere a integridade da cópia.

    - origem ausente        -> FileNotFoundError (nenhum arquivo é criado, nem a origem, nem o destino);
    - destino já existente  -> FileExistsError (a cópia anterior permanece intacta);
    - pasta do destino ausente -> FileNotFoundError;
    - falha no meio ou cópia sem integridade -> o destino parcial é apagado e o erro sobe.
    Devolve o caminho (Path) da cópia criada.
    """
    origem, destino = Path(origem), Path(destino)
    if not origem.is_file():
        raise FileNotFoundError(f"Banco de origem não encontrado: {origem}")
    if destino.exists():
        raise FileExistsError(f"O destino já existe e não será sobrescrito: {destino}")
    if not destino.resolve().parent.is_dir():
        raise FileNotFoundError(f"A pasta do destino não existe: {destino.resolve().parent}")

    try:
        # backup pela conexão (consistente mesmo com a origem aberta), não por cópia crua do arquivo
        with closing(_abrir_somente_leitura(origem)) as entrada, closing(sqlite3.connect(destino)) as saida:
            entrada.backup(saida)
        # a conferência usa OUTRA conexão, aberta depois que a cópia foi fechada e gravada
        with closing(_abrir_somente_leitura(destino)) as copia:
            resultado = copia.execute("PRAGMA integrity_check").fetchone()[0]
        if resultado != "ok":
            raise sqlite3.DatabaseError(f"A cópia falhou na verificação de integridade: {resultado}")
    except BaseException:
        destino.unlink(missing_ok=True)      # nunca deixar uma cópia parcial parecendo válida
        raise
    return destino


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
    if len(sys.argv) != 3:
        print("Uso: python backup_sqlite.py origem-ficticia.db copia-nova.db")
        raise SystemExit(2)
    try:
        copia = criar_backup(sys.argv[1], sys.argv[2])
    except (FileNotFoundError, FileExistsError, sqlite3.Error) as erro:
        print(f"Backup recusado: {erro}")
        raise SystemExit(1)
    print(f"Backup criado e conferido: {copia}")
    for tabela, linhas in resumo_da_copia(copia).items():
        print(f"  {tabela}: {linhas} linha(s)")
