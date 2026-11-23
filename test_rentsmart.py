"""Testes automatizados do RentSmart (biblioteca padrão unittest).

Execute com:  python -m unittest -v
"""

import csv
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from contrato import TaxaContratual
from entrada import ler_inteiro, ler_opcao, ler_sim_nao
from formatacao import formatar_moeda
from imoveis import Apartamento, Casa, Estudio, Imovel
from orcamento import Orcamento


class TestImoveis(unittest.TestCase):
    def test_apartamento_2_quartos_garagem_sem_criancas(self):
        apto = Apartamento(quartos=2, garagem=True, tem_criancas=False)
        self.assertEqual(apto.calcular_subtotal(), 1200.0)
        self.assertEqual(apto.calcular_desconto(1200.0), 60.0)
        self.assertEqual(apto.calcular_aluguel_mensal(), 1140.0)

    def test_apartamento_com_criancas_sem_desconto(self):
        self.assertEqual(Apartamento(2, True, tem_criancas=True).calcular_aluguel_mensal(), 1200.0)

    def test_apartamento_basico(self):
        self.assertEqual(Apartamento().calcular_aluguel_mensal(), 700.0)

    def test_casa_2_quartos_garagem(self):
        self.assertEqual(Casa(quartos=2, garagem=True).calcular_aluguel_mensal(), 1450.0)

    def test_casa_nunca_tem_desconto(self):
        casa = Casa(2, True)
        self.assertEqual(casa.calcular_desconto(casa.calcular_subtotal()), 0.0)

    def test_estudio_4_vagas(self):
        self.assertEqual(Estudio(vagas=4).calcular_aluguel_mensal(), 1570.0)

    def test_estudio_2_vagas_e_sem_vagas(self):
        self.assertEqual(Estudio(vagas=2).calcular_aluguel_mensal(), 1450.0)
        self.assertEqual(Estudio(vagas=0).calcular_aluguel_mensal(), 1200.0)

    def test_estudio_com_1_vaga_e_recusado(self):
        with self.assertRaises(ValueError):
            Estudio(vagas=1)

    def test_3_quartos_e_recusado(self):
        with self.assertRaises(ValueError):
            Casa(quartos=3)

    def test_imovel_e_abstrato(self):
        with self.assertRaises(TypeError):
            Imovel()


class TestTaxaContratual(unittest.TestCase):
    def test_5_parcelas(self):
        taxa = TaxaContratual(5)
        self.assertEqual(taxa.valor_parcela(), 400.0)
        self.assertEqual([taxa.valor_parcela_do_mes(m) for m in range(1, 6)], [400.0] * 5)
        self.assertEqual([taxa.valor_parcela_do_mes(m) for m in range(6, 13)], [0.0] * 7)

    def test_3_parcelas_somam_exatamente_2000(self):
        taxa = TaxaContratual(3)
        self.assertEqual(taxa.lista_parcelas(), [666.67, 666.67, 666.66])
        self.assertAlmostEqual(sum(taxa.lista_parcelas()), 2000.0, places=2)

    def test_parcelas_fora_do_intervalo(self):
        for parcelas in (0, 6):
            with self.assertRaises(ValueError):
                TaxaContratual(parcelas)


class TestOrcamento(unittest.TestCase):
    def setUp(self):
        self.orcamento = Orcamento(Apartamento(2, True, False), TaxaContratual(5))

    def test_projecao_tem_12_meses(self):
        projecao = self.orcamento.gerar_projecao()
        self.assertEqual(len(projecao), 12)
        self.assertEqual(projecao[0]["total_mes"], 1540.0)
        self.assertEqual(projecao[5]["total_mes"], 1140.0)
        self.assertEqual(self.orcamento.total_projecao(), 1140.0 * 12 + 2000.0)

    def test_resumo_mostra_valores(self):
        resumo = self.orcamento.montar_resumo()
        for trecho in ("R$ 1.140,00", "-R$ 60,00", "5x de R$ 400,00", "R$ 2.000,00"):
            self.assertIn(trecho, resumo)

    def test_exportar_csv(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = self.orcamento.exportar_csv(Path(pasta) / "teste.csv")
            with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
                linhas = list(csv.reader(arquivo, delimiter=";"))
        self.assertEqual(linhas[0], ["mes", "aluguel", "parcela_contrato", "total_mes"])
        self.assertEqual(len(linhas), 13)
        self.assertEqual(linhas[1], ["1", "1140,00", "400,00", "1540,00"])
        self.assertEqual(linhas[12], ["12", "1140,00", "0,00", "1140,00"])


class TestFormatacao(unittest.TestCase):
    def test_formatar_moeda(self):
        self.assertEqual(formatar_moeda(1140), "R$ 1.140,00")
        self.assertEqual(formatar_moeda(666.67), "R$ 666,67")
        self.assertEqual(formatar_moeda(-60), "-R$ 60,00")


class TestEntrada(unittest.TestCase):
    """Entradas inválidas devem ser recusadas e perguntadas novamente."""

    def _executar(self, funcao, respostas, *args, **kwargs):
        with patch("builtins.input", side_effect=respostas), redirect_stdout(io.StringIO()):
            return funcao(*args, **kwargs)

    def test_menu_recusa_opcao_4(self):
        self.assertEqual(self._executar(ler_opcao, ["4", "x", "2"], "> ", ["1", "2", "3"]), "2")

    def test_quartos_recusa_3_e_texto(self):
        self.assertEqual(self._executar(ler_inteiro, ["3", "dois", "2"], "> ", 1, 2), 2)

    def test_parcelas_recusa_6(self):
        self.assertEqual(self._executar(ler_inteiro, ["6", "0", "5"], "> ", 1, 5), 5)

    def test_vagas_estudio_recusa_1(self):
        self.assertEqual(self._executar(ler_inteiro, ["1", "4"], "> ", minimo=2), 4)

    def test_sim_nao(self):
        self.assertTrue(self._executar(ler_sim_nao, ["talvez", "S"], "?"))
        self.assertFalse(self._executar(ler_sim_nao, ["não"], "?"))


if __name__ == "__main__":
    unittest.main()
