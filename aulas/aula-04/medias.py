"""Funções puras para cálculo da média da aula A04."""


def calcular(nome_texto, turma_texto, notas_texto):
    nome = nome_texto.strip()
    turma = turma_texto.strip()

    if not nome or not turma:
        return None, "Preencha o nome e a turma para continuar."
    if len(notas_texto) != 5:
        return None, "Informe exatamente cinco notas."

    notas = []
    for texto in notas_texto:
        try:
            nota = float(texto.strip().replace(",", "."))
        except ValueError:
            return None, f"Não foi possível converter a nota '{texto}' em número."
        if not 0 <= nota <= 10:
            return None, f"Nota inválida: {nota}. Use um valor entre 0 e 10."
        notas.append(nota)

    resultado = {
        "nome": nome,
        "turma": turma,
        "notas": notas,
        "media": sum(notas) / len(notas),
    }
    return resultado, "Média calculada e registro salvo."
