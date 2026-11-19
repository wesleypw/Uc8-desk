# A19: o que entra na entrega e o que NÃO entra (ambientes, caches, dados reais).
#   python entrega.py            # só lista o que entraria
#   python entrega.py --zip      # cria entrega-a19.zip (fora da própria listagem) com esses arquivos
import sys
import zipfile
from pathlib import Path

PASTAS_EXCLUIDAS = {"__pycache__", ".venv", "venv", "env", ".git", ".idea", ".vscode", ".pytest_cache", "node_modules"}
SUFIXOS_EXCLUIDOS = {".pyc", ".pyo", ".db", ".sqlite", ".sqlite3", ".db-journal", ".db-wal", ".db-shm", ".zip", ".bak"}
NOMES_EXCLUIDOS = {".env", ".DS_Store", "Thumbs.db"}


def entra_na_entrega(caminho_relativo):
    partes = Path(caminho_relativo).parts
    nome = partes[-1]
    if any(p in PASTAS_EXCLUIDAS for p in partes[:-1]):
        return False
    return nome not in NOMES_EXCLUIDOS and Path(nome).suffix.lower() not in SUFIXOS_EXCLUIDOS


def arquivos_da_entrega(pasta):
    """Caminhos relativos (ordenados) de tudo que deve ser entregue em `pasta`."""
    pasta = Path(pasta)
    return sorted(str(p.relative_to(pasta)).replace("\\", "/") for p in pasta.rglob("*")
                  if p.is_file() and entra_na_entrega(p.relative_to(pasta)))


def montar_zip(pasta, destino_zip):
    pasta, destino_zip = Path(pasta), Path(destino_zip)
    if destino_zip.exists():
        raise FileExistsError(f"{destino_zip} já existe; remova ou escolha outro nome.")
    with zipfile.ZipFile(destino_zip, "w", zipfile.ZIP_DEFLATED) as arquivo:
        for relativo in arquivos_da_entrega(pasta):
            arquivo.write(pasta / relativo, relativo)
    return destino_zip


if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    lista = arquivos_da_entrega(base)
    print(f"Entrariam {len(lista)} arquivo(s):")
    for item in lista:
        print("  ", item)
    if "--zip" in sys.argv:
        try:
            print("ZIP criado:", montar_zip(base, base.parent / "entrega-a19.zip"))
        except FileExistsError as erro:
            print("ZIP não criado:", erro)
