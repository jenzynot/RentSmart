"""Funções de formatação de valores no padrão brasileiro."""


def formatar_moeda(valor: float) -> str:
    """Formata um valor em reais. Ex.: 1140.5 -> 'R$ 1.140,50'."""
    texto = f"{abs(valor):,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    sinal = "-" if valor < 0 else ""
    return f"{sinal}R$ {texto}"


def formatar_decimal(valor: float) -> str:
    """Número com vírgula decimal, sem separador de milhar (ideal para CSV/Excel pt-BR)."""
    return f"{valor:.2f}".replace(".", ",")
