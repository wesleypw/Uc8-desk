"""Versão completa da interface escolar da aula A04."""
import tkinter as tk
from tkinter import ttk

from medias import calcular


def criar_janela():
    janela = tk.Tk()
    janela.title("Sistema escolar fictício — A04")
    janela.columnconfigure(1, weight=1)
    registro = {}

    ttk.Label(janela, text="Dados fictícios. Cinco notas de 0 a 10; média simples.", wraplength=440).grid(
        row=0, column=0, columnspan=2, padx=12, pady=8, sticky="w"
    )
    ttk.Label(janela, text="Nome fictício:").grid(row=1, column=0, padx=12, pady=4, sticky="w")
    entrada_nome = ttk.Entry(janela)
    entrada_nome.grid(row=1, column=1, padx=12, pady=4, sticky="ew")
    ttk.Label(janela, text="Turma fictícia:").grid(row=2, column=0, padx=12, pady=4, sticky="w")
    entrada_turma = ttk.Entry(janela)
    entrada_turma.grid(row=2, column=1, padx=12, pady=4, sticky="ew")

    entradas_notas = []
    for numero in range(1, 6):
        linha = numero + 2
        ttk.Label(janela, text=f"Nota {numero} (0 a 10):").grid(
            row=linha, column=0, padx=12, pady=4, sticky="w"
        )
        entrada = ttk.Entry(janela)
        entrada.grid(row=linha, column=1, padx=12, pady=4, sticky="ew")
        entradas_notas.append(entrada)

    def ao_calcular():
        resultado, mensagem = calcular(
            entrada_nome.get(),
            entrada_turma.get(),
            [entrada.get() for entrada in entradas_notas],
        )
        if resultado is not None:
            registro.clear()
            registro.update(resultado)
        resultado_label.configure(text=mensagem)

    def ao_exibir():
        if not registro:
            resultado_label.configure(text="Ainda não há registro escolar salvo nesta sessão.")
            return
        notas = ", ".join(f"{nota:.1f}" for nota in registro["notas"])
        resultado_label.configure(
            text=(
                f"Aluno: {registro['nome']} | Turma: {registro['turma']} | "
                f"Notas: {notas} | Média: {registro['media']:.1f}"
            )
        )

    def ao_limpar():
        entrada_nome.delete(0, tk.END)
        entrada_turma.delete(0, tk.END)
        for entrada in entradas_notas:
            entrada.delete(0, tk.END)
        entrada_nome.focus_set()

    ttk.Button(janela, text="Calcular média", command=ao_calcular).grid(row=8, column=0, padx=12, pady=6)
    ttk.Button(janela, text="Exibir", command=ao_exibir).grid(row=8, column=1, padx=12, pady=6)
    ttk.Button(janela, text="Limpar campos", command=ao_limpar).grid(row=9, column=0, columnspan=2, pady=4)
    resultado_label = ttk.Label(janela, wraplength=440)
    resultado_label.grid(row=10, column=0, columnspan=2, padx=12, pady=6, sticky="w")
    entrada_nome.focus_set()
    return janela


if __name__ == "__main__":
    criar_janela().mainloop()
