# A17 (OPCIONAL): o mesmo mini-formulário em ttk e em CustomTkinter, para comparar teclado e foco.
# O núcleo (banco, venda, CSV) NÃO depende deste arquivo: sem CustomTkinter, tudo continua funcionando.
#   pip install customtkinter      (só se quiser rodar a comparação)
#   python comparar_ctk.py         # abre a janela de comparação
#   python comparar_ctk.py --medir # imprime as medições de Tab/Espaço/Enter
import sys
import tkinter as tk
from tkinter import ttk


def _importar_ctk():
    try:
        import customtkinter as ctk
        return ctk
    except ImportError:
        return None


def criar_comparacao():
    """Devolve a janela de comparação, ou None se o CustomTkinter não estiver instalado."""
    ctk = _importar_ctk()
    if ctk is None:
        return None

    janela = ctk.CTk()
    janela.title("A17 — ttk x CustomTkinter (comparação opcional)")
    janela.geometry("620x300")
    janela.columnconfigure((0, 1), weight=1)
    eventos = tk.StringVar(value="Use Tab, Shift+Tab, Espaço e Enter e observe o registro abaixo.")

    def anotar(texto):
        return lambda _e: eventos.set(texto)

    # --- coluna ttk ---
    esquerda = ttk.LabelFrame(janela, text=" ttk ", padding=10)
    esquerda.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
    ttk.Label(esquerda, text="Nome:").pack(anchor="w")
    entrada_ttk = ttk.Entry(esquerda)
    entrada_ttk.pack(fill="x", pady=4)
    botao_ttk = ttk.Button(esquerda, text="Salvar (ttk)", command=lambda: eventos.set("ttk: botão acionado"))
    botao_ttk.pack(fill="x", pady=4)
    entrada_ttk.bind("<FocusIn>", anotar("ttk: foco na entrada"))
    botao_ttk.bind("<FocusIn>", anotar("ttk: foco no botão"))

    # --- coluna CustomTkinter ---
    direita = ctk.CTkFrame(janela)
    direita.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
    ctk.CTkLabel(direita, text="Nome:").pack(anchor="w", padx=10, pady=(10, 0))
    entrada_ctk = ctk.CTkEntry(direita)
    entrada_ctk.pack(fill="x", padx=10, pady=4)
    botao_ctk = ctk.CTkButton(direita, text="Salvar (CTk)", command=lambda: eventos.set("CTk: botão acionado"))
    botao_ctk.pack(fill="x", padx=10, pady=4)
    entrada_ctk._entry.bind("<FocusIn>", anotar("CTk: foco na entrada"))

    ttk.Label(janela, textvariable=eventos, wraplength=560).grid(row=1, column=0, columnspan=2, padx=8, pady=8)
    janela.entradas = {"ttk": entrada_ttk, "ctk": entrada_ctk}
    janela.botoes = {"ttk": botao_ttk, "ctk": botao_ctk}
    return janela


def _ciclo_tab(raiz, partida, rotulos, passos=6):
    partida.focus_force()
    raiz.update()
    ordem = []
    atual = raiz.focus_get()
    for _ in range(passos):
        ordem.append(rotulos.get(str(atual), type(atual).__name__))
        proximo = atual.tk_focusNext()
        proximo.focus_force()
        raiz.update()
        atual = raiz.focus_get()
    return ordem


def _cliques_por_tecla(raiz, alvo, tecla, contador):
    contador[0] = 0
    alvo.focus_force()
    raiz.update()
    alvo.event_generate(tecla)
    raiz.update()
    return contador[0]


def medir_teclado():
    """Mede, com eventos reais do Tk, o ciclo do Tab e o acionamento do botão por Espaço/Enter.

    Devolve None se o CustomTkinter não estiver instalado (a comparação é opcional).
    """
    ctk = _importar_ctk()
    if ctk is None:
        return None
    resultado = {}

    raiz = tk.Tk()
    quadro = ttk.Frame(raiz)
    quadro.pack()
    e1, e2 = ttk.Entry(quadro), ttk.Entry(quadro)
    e1.pack()
    e2.pack()
    contador = [0]
    botao = ttk.Button(quadro, text="Salvar", command=lambda: contador.__setitem__(0, contador[0] + 1))
    botao.pack()
    raiz.update()
    rotulos = {str(e1): "Entrada 1", str(e2): "Entrada 2", str(botao): "Botão"}
    resultado["ttk"] = {
        "ciclo_tab": _ciclo_tab(raiz, e1, rotulos),
        "espaco": _cliques_por_tecla(raiz, botao, "<space>", contador),
        "enter": _cliques_por_tecla(raiz, botao, "<Return>", contador),
    }
    raiz.destroy()

    raiz = ctk.CTk()
    e1, e2 = ctk.CTkEntry(raiz), ctk.CTkEntry(raiz)
    e1.pack()
    e2.pack()
    contador = [0]
    botao = ctk.CTkButton(raiz, text="Salvar", command=lambda: contador.__setitem__(0, contador[0] + 1))
    botao.pack()
    raiz.update()
    rotulos = {str(e1._entry): "Entrada 1", str(e2._entry): "Entrada 2", str(botao._canvas): "Botão"}
    resultado["ctk"] = {
        "ciclo_tab": _ciclo_tab(raiz, e1._entry, rotulos),
        "espaco": _cliques_por_tecla(raiz, botao._canvas, "<space>", contador),
        "enter": _cliques_por_tecla(raiz, botao._canvas, "<Return>", contador),
    }
    raiz.destroy()
    return resultado


if __name__ == "__main__":
    if _importar_ctk() is None:
        print("CustomTkinter não está instalado. A comparação é opcional; o restante da A17 funciona sem ele.")
        print("Para experimentar: pip install customtkinter")
    elif "--medir" in sys.argv:
        for nome, dados in medir_teclado().items():
            print(f"{nome}: ciclo do Tab = {dados['ciclo_tab']}; Espaço aciona = {dados['espaco']}; Enter aciona = {dados['enter']}")
    else:
        criar_comparacao().mainloop()
