"""Funções puras do conversor fictício da aula A03."""


def converter(reais_texto, dolar_texto, euro_texto):
    try:
        reais = float(reais_texto.strip().replace(",", "."))
        cotacao_dolar = float(dolar_texto.strip().replace(",", "."))
        cotacao_euro = float(euro_texto.strip().replace(",", "."))
    except (AttributeError, ValueError):
        return None, "Informe números válidos em todos os campos."

    if reais < 0:
        return None, "Informe um valor em reais igual ou superior a zero."
    if cotacao_dolar <= 0 or cotacao_euro <= 0:
        return None, "As cotações devem ser maiores que zero."

    resultado = {
        "reais": reais,
        "cotacao_dolar": cotacao_dolar,
        "cotacao_euro": cotacao_euro,
        "dolar": reais / cotacao_dolar,
        "euro": reais / cotacao_euro,
    }
    return resultado, "Conversão salva com sucesso."
