"""A01 - ensaio de validação no terminal."""


def conferir_cadastro(nome_texto, idade_texto):
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


if __name__ == "__main__":
    nome = input("Nome fictício: ")
    idade = input("Idade fictícia: ")
    print(conferir_cadastro(nome, idade))
