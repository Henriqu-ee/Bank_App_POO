def transferir(origem, destino, valor):
    if origem.saque(valor):
        destino.deposito(valor)
        origem.registrar_transferencia(valor, destino)
        destino.registrar_recebimento(valor, origem)
        return True
    return False

def transferir_externo(conta_origem, valor, chave_destino):
    """Simula uma transferência para fora do banco (PIX/TED)."""
    if conta_origem.saque(valor):
        # O método saque já debita o valor e cria a transação.
        # Apenas modificamos a descrição da última transação para ser mais específica.
        if conta_origem.historico:
            conta_origem.historico[-1].tipo = "Transferência Externa"
            conta_origem.historico[-1].descricao = f"Envio para chave: {chave_destino}"
        return True
    return False