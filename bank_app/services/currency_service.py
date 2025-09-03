from utils.currency_api import get_cambio
from models.transaction import Transacao

def cambio(conta, moeda_destino, valor_em_reais):
    # A função get_cambio agora espera a moeda de origem (a que você quer comprar)
    taxa = get_cambio(moeda_destino)

    if taxa is None:
        # A mensagem de erro detalhada agora será impressa pela função get_cambio
        print("\nOperação de câmbio falhou.")
        return None

    print(f"Cotação atual: 1 {moeda_destino} = R${taxa:.2f}")

    if conta.saque(valor_em_reais):
        valor_convertido = valor_em_reais / taxa
        descricao = f"Câmbio de R${valor_em_reais:.2f} para {valor_convertido:.2f} {moeda_destino}"
        conta.historico.append(Transacao("Câmbio", valor_em_reais, descricao=descricao))
        return valor_convertido
    else:
        # A função conta.saque já imprime "Saldo insuficiente."
        return None