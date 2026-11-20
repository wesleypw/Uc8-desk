"""Versão completa da interface do conversor da aula A03."""
import tkinter as tk
from tkinter import ttk

from calculos_moedas import converter


def criar_janela():
    janela = tk.Tk()
    janela.title("Conversor fictício — A03")
    janela.columnconfigure(1, weight=1)
    registro = {}

    ttk.Label(janela, text="Reais:").grid(row=0, column=0, padx=12, pady=6, sticky="w")
    entrada_reais = ttk.Entry(janela)
    entrada_reais.grid(row=0, column=1, padx=12, pady=6, sticky="ew")
    ttk.Label(janela, text="Cotação do dólar:").grid(row=1, column=0, padx=12, pady=6, sticky="w")
    entrada_dolar = ttk.Entry(janela)
    entrada_dolar.grid(row=1, column=1, padx=12, pady=6, sticky="ew")
    ttk.Label(janela, text="Cotação do euro:").grid(row=2, column=0, padx=12, pady=6, sticky="w")
    entrada_euro = ttk.Entry(janela)
    entrada_euro.grid(row=2, column=1, padx=12, pady=6, sticky="ew")

    def ao_calcular():
        resultado, mensagem = converter(
            entrada_reais.get(),
            entrada_dolar.get(),
            entrada_euro.get(),
        )
        if resultado is not None:
            registro.clear()
            registro.update(resultado)
        resultado_label.configure(text=mensagem)

    def ao_exibir():
        if not registro:
            resultado_label.configure(text="Ainda não há conversão salva nesta sessão.")
            return
        resultado_label.configure(
            text=(
                f"Reais: {registro['reais']:.2f} | "
                f"Dólares: {registro['dolar']:.2f} | "
                f"Euros: {registro['euro']:.2f}"
            )
        )

    def ao_limpar():
        entrada_reais.delete(0, tk.END)
        entrada_dolar.delete(0, tk.END)
        entrada_euro.delete(0, tk.END)
        entrada_reais.focus_set()

    ttk.Button(janela, text="Calcular", command=ao_calcular).grid(row=3, column=0, padx=12, pady=8)
    ttk.Button(janela, text="Exibir", command=ao_exibir).grid(row=3, column=1, padx=12, pady=8)
    ttk.Button(janela, text="Limpar campos", command=ao_limpar).grid(row=4, column=0, columnspan=2, pady=6)
    resultado_label = ttk.Label(janela, wraplength=390)
    resultado_label.grid(row=5, column=0, columnspan=2, padx=12, pady=8, sticky="w")
    entrada_reais.focus_set()
    return janela


if __name__ == "__main__":
    criar_janela().mainloop()
