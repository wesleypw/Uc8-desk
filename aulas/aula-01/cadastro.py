"""A01 — prática 2. Conferir um cadastro fictício na interface."""
import tkinter as tk
from tkinter import ttk


def conferir(nome_texto, idade_texto):
    nome = nome_texto.strip()
    idade_texto = idade_texto.strip()

    if not nome:
        return "Informe um nome fictício."

    try:
        idade = int(idade_texto)
    except ValueError:
        return "Informe uma idade inteira maior que zero."

    if idade <= 0:
        return "Informe uma idade inteira maior que zero."

    return f"Cadastro confirmado: {nome} | Idade: {idade} anos."


def conferir_cadastro():
    nome = entrada_nome.get()
    idade = entrada_idade.get()
    resultado.configure(text=conferir(nome, idade))


def criar_janela():
    global entrada_nome, entrada_idade, resultado

    janela = tk.Tk()
    janela.title("Conferir cadastro fictício")
    janela.columnconfigure(1, weight=1)
    ttk.Label(janela, text="Nome fictício:").grid(row=0, column=0, padx=12, pady=8, sticky="w")
    entrada_nome = ttk.Entry(janela)
    entrada_nome.grid(row=0, column=1, padx=12, pady=8, sticky="ew")
    ttk.Label(janela, text="Idade fictícia:").grid(row=1, column=0, padx=12, pady=8, sticky="w")
    entrada_idade = ttk.Entry(janela)
    entrada_idade.grid(row=1, column=1, padx=12, pady=8, sticky="ew")
    ttk.Button(janela, text="Conferir cadastro", command=conferir_cadastro).grid(
        row=2, column=0, columnspan=2, pady=8
    )
    resultado = ttk.Label(
        janela,
        text="Nenhum cadastro conferido nesta sessão.",
        wraplength=360,
    )
    resultado.grid(row=3, column=0, columnspan=2, padx=12, pady=8, sticky="w")
    entrada_nome.focus_set()
    return janela


if __name__ == "__main__":
    criar_janela().mainloop()
