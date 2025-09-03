from models.transaction import Transacao

def solicitar_emprestimo(conta, valor):
    """Adiciona um valor de empréstimo ao saldo da conta e à dívida, e registra a transação."""
    if valor > 0:
        conta.deposito(valor)
        conta._divida_emprestimo += valor # <-- ATUALIZA A DÍVIDA
        # Modifica a última transação (que foi um depósito)
        if conta.historico:
            conta.historico[-1].tipo = "Empréstimo"
            conta.historico[-1].descricao = f"Crédito de empréstimo de R${valor:.2f}"
    else:
        print("\nO valor do empréstimo deve ser positivo.\n")