"""Funções de leitura com validação.

Cada função repete a pergunta até receber uma resposta válida, evitando
escrever um laço de validação para cada pergunta do programa.
"""

RESPOSTAS_SIM = ("s", "sim")
RESPOSTAS_NAO = ("n", "nao", "não")


def ler_opcao(mensagem: str, opcoes_validas, aviso: str | None = None) -> str:
    """Lê uma opção entre as válidas (sem diferenciar maiúsculas/minúsculas)."""
    opcoes = [str(opcao).lower() for opcao in opcoes_validas]
    aviso = aviso or f"Opção inválida. Escolha entre: {', '.join(opcoes)}."
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta in opcoes:
            return resposta
        print(f"  [!] {aviso}")


def ler_inteiro(mensagem: str, minimo: int | None = None, maximo: int | None = None) -> int:
    """Lê um número inteiro dentro do intervalo [minimo, maximo]."""
    while True:
        resposta = input(mensagem).strip()
        try:
            valor = int(resposta)
        except ValueError:
            print("  [!] Valor inválido. Digite um número inteiro.")
            continue
        if minimo is not None and valor < minimo:
            print(f"  [!] O valor mínimo é {minimo}.")
        elif maximo is not None and valor > maximo:
            print(f"  [!] O valor máximo é {maximo}.")
        else:
            return valor


def ler_sim_nao(mensagem: str) -> bool:
    """Lê uma resposta s/n e devolve True para 'sim'."""
    resposta = ler_opcao(
        f"{mensagem} (s/n): ", RESPOSTAS_SIM + RESPOSTAS_NAO, aviso="Responda com 's' ou 'n'."
    )
    return resposta in RESPOSTAS_SIM
