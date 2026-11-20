"""Funções puras do estado confirmado da aula A02."""


def registrar(campos, registro):
    nome = campos["nome"].strip()
    sobrenome = campos["sobrenome"].strip()
    idade_texto = campos["idade"].strip()

    if not nome or not sobrenome:
        return "Informe o nome e o sobrenome antes de salvar."

    try:
        idade = int(idade_texto)
    except ValueError:
        return "Informe uma idade inteira maior que zero."

    if idade <= 0:
        return "Informe uma idade inteira maior que zero."

    registro.clear()
    registro.update(nome=nome.title(), sobrenome=sobrenome.title(), idade=idade)
    return "Cadastro salvo com sucesso."


def exibir(registro):
    if not registro:
        return "Ainda não há cadastro salvo nesta sessão."
    return (
        f"Cadastro: {registro['nome']} {registro['sobrenome']} "
        f"| Idade: {registro['idade']} anos"
    )
