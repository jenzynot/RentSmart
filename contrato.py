"""Taxa contratual da R.M Imóveis, cobrada separadamente do aluguel."""


class TaxaContratual:
    VALOR = 2000.0
    MIN_PARCELAS = 1
    MAX_PARCELAS = 5

    def __init__(self, parcelas: int = 1) -> None:
        if not self.MIN_PARCELAS <= parcelas <= self.MAX_PARCELAS:
            raise ValueError(
                f"A taxa contratual pode ser parcelada de {self.MIN_PARCELAS} a "
                f"{self.MAX_PARCELAS} vezes (informado: {parcelas})."
            )
        self.parcelas = parcelas

    def valor_parcela(self) -> float:
        """Valor de cada parcela, arredondado em centavos."""
        return round(self.VALOR / self.parcelas, 2)

    def valor_parcela_do_mes(self, mes: int) -> float:
        """Parcela cobrada no mês informado (1 a 12); zero após a última.

        A última parcela absorve a diferença de arredondamento, garantindo que
        a soma seja exatamente o valor da taxa (ex.: 3x = 666,67 + 666,67 + 666,66).
        """
        if mes < 1 or mes > self.parcelas:
            return 0.0
        if mes == self.parcelas:
            return round(self.VALOR - self.valor_parcela() * (self.parcelas - 1), 2)
        return self.valor_parcela()

    def lista_parcelas(self) -> list[float]:
        return [self.valor_parcela_do_mes(mes) for mes in range(1, self.parcelas + 1)]
