from models.account import Conta # Sua classe base atual

class ContaCorrente(Conta):
    def __init__(self, num_conta, proprietario, saldo=0.0, limite_cheque_especial=500.0):
        super().__init__(num_conta, proprietario, saldo)
        self.limite_cheque_especial = limite_cheque_especial

    # Polimorfismo: Reescrevendo o método saque
    def saque(self, quantidade):
        saldo_disponivel = self.saldo + self.limite_cheque_especial
        if 0 < quantidade <= saldo_disponivel:
            self.saldo -= quantidade
            # Lógica para registrar a transação...
            return True
        return False

    def cobrar_taxa_manutencao(self):
        # Lógica específica da conta corrente
        self.saldo -= 15.0 
        print("Taxa de manutenção de R$15,00 cobrada.")

class ContaPoupanca(Conta):
    def __init__(self, num_conta, proprietario, saldo=0.0):
        super().__init__(num_conta, proprietario, saldo)
        self.taxa_rendimento = 0.005 # 0.5%

    def render_juros(self):
        rendimento = self.saldo * self.taxa_rendimento
        self.saldo += rendimento
        print(f"Rendimento de R${rendimento:.2f} aplicado.")
        # Lógica para registrar a transação de rendimento...