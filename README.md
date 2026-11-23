# RentSmart — Orçamento de Locação da R.M Imóveis

Sistema de linha de comando, escrito em Python com Programação Orientada a Objetos, que monta o orçamento de locação de apartamentos, casas e estúdios da **R.M Imóveis** e gera uma projeção de 12 meses em CSV.

Disciplina: *Algorithmic Thinking & Introduction to Object-Oriented Programming*

## Requisitos

- Python **3.10 ou superior**
- Nenhuma biblioteca externa: o projeto usa apenas a biblioteca padrão (`csv`, `pathlib`, `unittest`)

## Como executar

```bash
python main.py
```

O programa pergunta o tipo de imóvel e as opções desejadas, mostra o orçamento detalhado e salva o arquivo `orcamento_12_meses.csv` na pasta do projeto.

Para rodar os testes automatizados:

```bash
python -m unittest -v
```

## Regras de negócio

| Imóvel | Aluguel-base | 2º quarto | Estacionamento | Desconto |
|---|---|---|---|---|
| Apartamento | R$ 700,00 | + R$ 200,00 | 1 vaga: + R$ 300,00 | 5% se não tiver crianças |
| Casa | R$ 900,00 | + R$ 250,00 | 1 vaga: + R$ 300,00 | — |
| Estúdio | R$ 1.200,00 | não se aplica | pacote de 2 vagas: R$ 250,00 + R$ 60,00 por vaga adicional | — |

- **Taxa contratual:** R$ 2.000,00, parcelável de 1 a 5 vezes e exibida separadamente do aluguel. Quando a divisão não é exata (ex.: 3x), a última parcela absorve o arredondamento para que a soma seja exatamente R$ 2.000,00 (666,67 + 666,67 + 666,66).
- **Decisão de projeto:** o desconto de 5% do apartamento incide sobre **aluguel-base + 2º quarto + garagem**, já que o enunciado diz que ele é aplicado "após a aplicação dos adicionais correspondentes".

## Estrutura do projeto

```
RentSmart/
├── main.py             # fluxo principal (menu, perguntas, resumo e CSV)
├── imoveis.py          # Imovel (classe-mãe), Apartamento, Casa, Estudio
├── contrato.py         # TaxaContratual
├── orcamento.py        # Orcamento (resumo na tela + projeção + CSV)
├── entrada.py          # leitura de dados com validação
├── formatacao.py       # formatação em reais (R$ 1.140,00)
├── test_rentsmart.py   # testes automatizados
└── README.md
```

### Conceitos de POO aplicados

- **Herança:** `Apartamento`, `Casa` e `Estudio` herdam de `Imovel` e mudam apenas o que é diferente.
- **Polimorfismo:** `Orcamento` chama `calcular_aluguel_mensal()`, `calcular_adicionais()` e `caracteristicas()` sem saber qual tipo de imóvel recebeu.
- **Encapsulamento das regras:** preços ficam em constantes de classe (`VALOR_BASE`, `ADICIONAL_QUARTO`, `VALOR_GARAGEM`...). Mudar um preço exige alterar uma única linha.
- **Separação de responsabilidades:** cálculo do imóvel, taxa contratual, orçamento, entrada de dados e formatação ficam em módulos diferentes.
- **Validação reutilizável:** `ler_opcao`, `ler_inteiro` e `ler_sim_nao` repetem a pergunta até a resposta ser válida (com `try/except ValueError`), e as próprias classes recusam valores inválidos.

## Exemplo de execução

Apartamento com 2 quartos, garagem, sem crianças, taxa contratual em 5x:

```
========================================================
           R.M IMÓVEIS - ORÇAMENTO DE LOCAÇÃO
========================================================
Imóvel: Apartamento
  Quartos: 2
  Garagem: Sim
  Crianças: Não
--------------------------------------------------------
ALUGUEL MENSAL
  Aluguel-base                                 R$ 700,00
  + 2º quarto                                  R$ 200,00
  + Garagem (1 vaga)                           R$ 300,00
  Subtotal                                   R$ 1.200,00
  - Desconto (5% sem crianças)                 -R$ 60,00
--------------------------------------------------------
  VALOR DO ALUGUEL MENSAL                    R$ 1.140,00
========================================================
TAXA CONTRATUAL (cobrada à parte do aluguel)
  Valor total                                R$ 2.000,00
  Parcelamento                           5x de R$ 400,00
========================================================
Custo total em 12 meses (aluguel + taxa)    R$ 15.680,00
========================================================

Projeção de 12 meses salva em:
  ...\RentSmart\orcamento_12_meses.csv
```

### Arquivo CSV gerado

Separador `;` e codificação UTF-8 com BOM, para abrir direto no Excel em português:

```
mes;aluguel;parcela_contrato;total_mes
1;1140,00;400,00;1540,00
...
5;1140,00;400,00;1540,00
6;1140,00;0,00;1140,00
...
12;1140,00;0,00;1140,00
```

## Casos de teste

| Caso | Cálculo | Resultado |
|---|---|---|
| Apartamento, 2 quartos, garagem, sem crianças | (700 + 200 + 300) × 0,95 | R$ 1.140,00 |
| Casa, 2 quartos, garagem | 900 + 250 + 300 | R$ 1.450,00 |
| Estúdio com 4 vagas | 1.200 + 250 + 2 × 60 | R$ 1.570,00 |
| Taxa contratual em 5x | 2.000 ÷ 5 | R$ 400,00 nos meses 1 a 5; R$ 0,00 nos meses 6 a 12 |

Entradas inválidas recusadas (o programa pergunta de novo, sem quebrar): opção 4 no menu, 3 quartos, estúdio com 1 vaga, 6 parcelas e texto no lugar de número.
