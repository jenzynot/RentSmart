"""Orçamento de locação: resumo na tela e projeção de 12 meses em CSV."""

import csv
from pathlib import Path

from contrato import TaxaContratual
from formatacao import formatar_decimal, formatar_moeda
from imoveis import Imovel


class Orcamento:
    """Reúne um imóvel e uma taxa contratual para gerar o orçamento.

    O orçamento não precisa saber qual tipo de imóvel recebeu: ele apenas
    chama os métodos definidos em ``Imovel`` (polimorfismo).
    """

    MESES_PROJECAO = 12
    ARQUIVO_PADRAO = "orcamento_12_meses.csv"
    LARGURA = 56

    def __init__(self, imovel: Imovel, taxa: TaxaContratual) -> None:
        self.imovel = imovel
        self.taxa = taxa

    # ------------------------------------------------------------------ #
    # Projeção
    # ------------------------------------------------------------------ #
    def gerar_projecao(self) -> list[dict[str, float]]:
        """Uma linha por mês com aluguel, parcela do contrato e total."""
        aluguel = self.imovel.calcular_aluguel_mensal()
        projecao = []
        for mes in range(1, self.MESES_PROJECAO + 1):
            parcela = self.taxa.valor_parcela_do_mes(mes)
            projecao.append(
                {
                    "mes": mes,
                    "aluguel": aluguel,
                    "parcela_contrato": parcela,
                    "total_mes": round(aluguel + parcela, 2),
                }
            )
        return projecao

    def total_projecao(self) -> float:
        return round(sum(linha["total_mes"] for linha in self.gerar_projecao()), 2)

    # ------------------------------------------------------------------ #
    # Resumo na tela
    # ------------------------------------------------------------------ #
    def _linha(self, rotulo: str, valor: str, recuo: int = 2) -> str:
        espaco = self.LARGURA - recuo - len(rotulo) - len(valor)
        return " " * recuo + rotulo + " " * max(espaco, 1) + valor

    def _descricao_parcelamento(self) -> str:
        """Ex.: '5x de R$ 400,00' ou '2x de R$ 666,67 + 1x de R$ 666,66'."""
        grupos: list[list] = []  # [valor, quantidade]
        for valor in self.taxa.lista_parcelas():
            if grupos and grupos[-1][0] == valor:
                grupos[-1][1] += 1
            else:
                grupos.append([valor, 1])
        return " + ".join(f"{qtd}x de {formatar_moeda(valor)}" for valor, qtd in grupos)

    def montar_resumo(self) -> str:
        imovel = self.imovel
        dupla = "=" * self.LARGURA
        simples = "-" * self.LARGURA
        subtotal = imovel.calcular_subtotal()
        desconto = imovel.calcular_desconto(subtotal)

        linhas = [
            "",
            dupla,
            "R.M IMÓVEIS - ORÇAMENTO DE LOCAÇÃO".center(self.LARGURA),
            dupla,
            f"Imóvel: {imovel.NOME}",
        ]
        for rotulo, valor in imovel.caracteristicas().items():
            linhas.append(f"  {rotulo}: {valor}")

        linhas += [simples, "ALUGUEL MENSAL"]
        linhas.append(self._linha("Aluguel-base", formatar_moeda(imovel.VALOR_BASE)))
        for descricao, valor in imovel.calcular_adicionais().items():
            linhas.append(self._linha(f"+ {descricao}", formatar_moeda(valor)))
        if desconto > 0:
            linhas.append(self._linha("Subtotal", formatar_moeda(subtotal)))
            linhas.append(self._linha(f"- {imovel.descricao_desconto()}", formatar_moeda(-desconto)))
        linhas += [
            simples,
            self._linha("VALOR DO ALUGUEL MENSAL", formatar_moeda(imovel.calcular_aluguel_mensal())),
            dupla,
            "TAXA CONTRATUAL (cobrada à parte do aluguel)",
            self._linha("Valor total", formatar_moeda(self.taxa.VALOR)),
            self._linha("Parcelamento", self._descricao_parcelamento()),
            dupla,
            self._linha(
                f"Custo total em {self.MESES_PROJECAO} meses (aluguel + taxa)",
                formatar_moeda(self.total_projecao()),
                recuo=0,
            ),
            dupla,
        ]
        return "\n".join(linhas)

    def exibir_resumo(self) -> None:
        print(self.montar_resumo())

    # ------------------------------------------------------------------ #
    # Exportação
    # ------------------------------------------------------------------ #
    def exportar_csv(self, caminho: str | Path = ARQUIVO_PADRAO) -> Path:
        """Grava a projeção em CSV (separador ';' e UTF-8 com BOM para o Excel).

        Retorna o caminho absoluto do arquivo gerado.
        """
        caminho = Path(caminho).resolve()
        colunas = ["mes", "aluguel", "parcela_contrato", "total_mes"]
        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(colunas)
            for linha in self.gerar_projecao():
                escritor.writerow(
                    [
                        linha["mes"],
                        formatar_decimal(linha["aluguel"]),
                        formatar_decimal(linha["parcela_contrato"]),
                        formatar_decimal(linha["total_mes"]),
                    ]
                )
        return caminho
