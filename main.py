"""RentSmart - sistema de orçamento de locação da R.M Imóveis.

Execute com:  python main.py
"""

from pathlib import Path

from contrato import TaxaContratual
from entrada import ler_inteiro, ler_opcao, ler_sim_nao
from formatacao import formatar_moeda
from imoveis import Apartamento, Casa, Estudio, Imovel
from orcamento import Orcamento

TIPOS_IMOVEL = {"1": Apartamento, "2": Casa, "3": Estudio}
PASTA_DO_PROJETO = Path(__file__).resolve().parent


def exibir_menu() -> None:
    print("=" * 56)
    print("RENTSMART - R.M IMÓVEIS".center(56))
    print("Orçamento de locação".center(56))
    print("=" * 56)
    print("Tipos de imóvel:")
    for codigo, classe in TIPOS_IMOVEL.items():
        print(f"  {codigo} - {classe.NOME:<12} aluguel-base {formatar_moeda(classe.VALOR_BASE)}")


def ler_imovel() -> Imovel:
    """Pergunta o tipo de imóvel e suas opções e devolve o objeto criado."""
    tipo = ler_opcao("\nEscolha o tipo de imóvel (1, 2 ou 3): ", TIPOS_IMOVEL)
    classe = TIPOS_IMOVEL[tipo]

    if classe is Estudio:
        vagas = 0
        if ler_sim_nao(
            f"Deseja estacionamento? (pacote de {Estudio.VAGAS_NO_PACOTE} vagas por "
            f"{formatar_moeda(Estudio.VALOR_PACOTE_VAGAS)} + "
            f"{formatar_moeda(Estudio.VALOR_VAGA_ADICIONAL)} por vaga extra)"
        ):
            vagas = ler_inteiro(
                f"Quantas vagas? (mínimo {Estudio.VAGAS_NO_PACOTE}): ",
                minimo=Estudio.VAGAS_NO_PACOTE,
            )
        return Estudio(vagas)

    quartos = ler_inteiro(
        f"Número de quartos (1 ou 2; o 2º quarto custa + {formatar_moeda(classe.ADICIONAL_QUARTO)}): ",
        minimo=1,
        maximo=2,
    )
    garagem = ler_sim_nao(f"Deseja vaga de garagem (+ {formatar_moeda(classe.VALOR_GARAGEM)})?")

    if classe is Apartamento:
        tem_criancas = ler_sim_nao("Possui crianças?")
        return Apartamento(quartos, garagem, tem_criancas)
    return Casa(quartos, garagem)


def ler_taxa_contratual() -> TaxaContratual:
    parcelas = ler_inteiro(
        f"Em quantas vezes deseja pagar a taxa contratual de "
        f"{formatar_moeda(TaxaContratual.VALOR)}? "
        f"({TaxaContratual.MIN_PARCELAS} a {TaxaContratual.MAX_PARCELAS}): ",
        minimo=TaxaContratual.MIN_PARCELAS,
        maximo=TaxaContratual.MAX_PARCELAS,
    )
    return TaxaContratual(parcelas)


def main() -> None:
    exibir_menu()
    imovel = ler_imovel()
    taxa = ler_taxa_contratual()

    orcamento = Orcamento(imovel, taxa)
    orcamento.exibir_resumo()

    try:
        caminho = orcamento.exportar_csv(PASTA_DO_PROJETO / Orcamento.ARQUIVO_PADRAO)
    except PermissionError:
        print("\n[!] Não foi possível gravar o CSV. Se ele estiver aberto no Excel, "
              "feche-o e execute o programa novamente.")
    else:
        print(f"\nProjeção de {Orcamento.MESES_PROJECAO} meses salva em:\n  {caminho}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nOperação cancelada pelo usuário.")
