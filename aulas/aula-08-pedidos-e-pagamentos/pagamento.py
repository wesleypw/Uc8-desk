# A08: pagamento.py — Sorveteria
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re

FATORES = {
    'Dinheiro': '0.87',
    'PIX': '0.87',
    'Débito': '0.92',
    'Crédito 1x': '1.00'
}

def valor_monetario(texto, permitir_zero=True):
    """Valida e converte texto para Decimal monetário."""
    if texto is None:
        raise ValueError("Texto nulo.")
    limpo = str(texto).strip()
    if not re.match(r'^[+-]?\d+([.,]\d{1,2})?$', limpo):
        raise ValueError("Formato monetário inválido.")
    
    normalizado = limpo.replace(',', '.')
    val = Decimal(normalizado)
    
    if val < 0:
        raise ValueError("Valor não pode ser negativo.")
    if not permitir_zero and val == 0:
        raise ValueError("Valor não pode ser zero.")
    if val > Decimal('1000000.00'):
        raise ValueError("Valor acima do limite máximo de 1.000.000,00.")
    return val

def calcular_pagamento(subtotal_texto, forma):
    """Calcula pagamento sem desconto acumulado, retornando subtotal, desconto e total."""
    if forma not in FATORES:
        raise ValueError(f"Forma de pagamento desconhecida: {forma}")
    
    subtotal_dec = valor_monetario(subtotal_texto, permitir_zero=False)
    fator = Decimal(FATORES[forma])
    
    total_dec = (subtotal_dec * fator).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    desconto_dec = (subtotal_dec - total_dec).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return subtotal_dec, desconto_dec, total_dec

def preco_para_centavos(texto):
    val = valor_monetario(texto)
    return int((val * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))