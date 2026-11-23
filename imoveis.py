"""Modelos de imóveis da R.M Imóveis (RentSmart).

A classe-mãe ``Imovel`` concentra a regra comum (aluguel-base, adicional de
2º quarto, garagem e cálculo do aluguel mensal). Cada tipo de imóvel herda
dela e sobrescreve apenas o que muda: valores (constantes de classe),
desconto (Apartamento) ou regra de estacionamento (Estúdio).
"""

from formatacao import formatar_moeda


class Imovel:
    """Classe base (abstrata) para todos os tipos de imóvel."""

    NOME = "Imóvel"
    VALOR_BASE = 0.0
    ADICIONAL_QUARTO = 0.0
    VALOR_GARAGEM = 300.0
    QUARTOS_PERMITIDOS = (1, 2)

    def __init__(self, quartos: int = 1, garagem: bool = False) -> None:
        if type(self) is Imovel:
            raise TypeError("Imovel é uma classe abstrata: use Apartamento, Casa ou Estudio.")
        if quartos not in self.QUARTOS_PERMITIDOS:
            raise ValueError(f"{self.NOME}: número de quartos inválido ({quartos}).")
        self.quartos = quartos
        self.garagem = garagem

    # ------------------------------------------------------------------ #
    # Cálculos
    # ------------------------------------------------------------------ #
    def calcular_adicionais(self) -> dict[str, float]:
        """Retorna os adicionais aplicáveis, no formato {descrição: valor}."""
        adicionais: dict[str, float] = {}
        if self.quartos == 2:
            adicionais["2º quarto"] = self.ADICIONAL_QUARTO
        if self.garagem:
            adicionais["Garagem (1 vaga)"] = self.VALOR_GARAGEM
        return adicionais

    def calcular_subtotal(self) -> float:
        """Aluguel-base somado a todos os adicionais (antes do desconto)."""
        return round(self.VALOR_BASE + sum(self.calcular_adicionais().values()), 2)

    def calcular_desconto(self, subtotal: float) -> float:
        """Por padrão, nenhum desconto é aplicado."""
        return 0.0

    def descricao_desconto(self) -> str:
        return "Desconto"

    def calcular_aluguel_mensal(self) -> float:
        """Aluguel final: base + adicionais - desconto."""
        subtotal = self.calcular_subtotal()
        return round(subtotal - self.calcular_desconto(subtotal), 2)

    # ------------------------------------------------------------------ #
    # Apresentação
    # ------------------------------------------------------------------ #
    def caracteristicas(self) -> dict[str, str]:
        """Características escolhidas pelo cliente, para exibir no resumo."""
        return {
            "Quartos": str(self.quartos),
            "Garagem": "Sim" if self.garagem else "Não",
        }


class Apartamento(Imovel):
    NOME = "Apartamento"
    VALOR_BASE = 700.0
    ADICIONAL_QUARTO = 200.0
    PERCENTUAL_DESCONTO = 0.05  # aplicado quando não há crianças

    def __init__(self, quartos: int = 1, garagem: bool = False, tem_criancas: bool = True) -> None:
        super().__init__(quartos, garagem)
        self.tem_criancas = tem_criancas

    def calcular_desconto(self, subtotal: float) -> float:
        """5% sobre (base + adicionais) quando o cliente não possui crianças."""
        if self.tem_criancas:
            return 0.0
        return round(subtotal * self.PERCENTUAL_DESCONTO, 2)

    def descricao_desconto(self) -> str:
        return f"Desconto ({self.PERCENTUAL_DESCONTO:.0%} sem crianças)"

    def caracteristicas(self) -> dict[str, str]:
        dados = super().caracteristicas()
        dados["Crianças"] = "Sim" if self.tem_criancas else "Não"
        return dados


class Casa(Imovel):
    NOME = "Casa"
    VALOR_BASE = 900.0
    ADICIONAL_QUARTO = 250.0


class Estudio(Imovel):
    """Estúdio: sem adicional de quarto; estacionamento vendido em pacote."""

    NOME = "Estúdio"
    VALOR_BASE = 1200.0
    VAGAS_NO_PACOTE = 2
    VALOR_PACOTE_VAGAS = 250.0
    VALOR_VAGA_ADICIONAL = 60.0

    def __init__(self, vagas: int = 0) -> None:
        super().__init__(quartos=1, garagem=False)
        if vagas != 0 and vagas < self.VAGAS_NO_PACOTE:
            raise ValueError(
                f"Estúdio: o estacionamento é vendido a partir de {self.VAGAS_NO_PACOTE} vagas "
                f"(informado: {vagas})."
            )
        self.vagas = vagas

    def calcular_adicionais(self) -> dict[str, float]:
        adicionais: dict[str, float] = {}
        if self.vagas == 0:
            return adicionais
        adicionais[f"Estacionamento (pacote {self.VAGAS_NO_PACOTE} vagas)"] = self.VALOR_PACOTE_VAGAS
        extras = self.vagas - self.VAGAS_NO_PACOTE
        if extras > 0:
            rotulo = f"Vagas adicionais ({extras} x {formatar_moeda(self.VALOR_VAGA_ADICIONAL)})"
            adicionais[rotulo] = extras * self.VALOR_VAGA_ADICIONAL
        return adicionais

    def caracteristicas(self) -> dict[str, str]:
        return {"Vagas de estacionamento": str(self.vagas) if self.vagas else "Nenhuma"}
