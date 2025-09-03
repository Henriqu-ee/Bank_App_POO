from datetime import datetime 
from models.transaction import Transacao
from models.user import User

class Conta:
    def __init__(self, num_conta, proprietario, saldo=0.0):
        # Atributos privados inicializados
        self._num_conta = None
        self._proprietario = None
        self._saldo = 0.0
        self._alerta_saldo = None
        self._divida_emprestimo = 0.0
        self._historico = []

        # Setters são usados para validar e atribuir os valores iniciais
        self.num_conta = num_conta
        self.proprietario = proprietario
        self.saldo = saldo

    # --- num_conta ---
    @property
    def num_conta(self):
        return self._num_conta
    
    @num_conta.setter
    def num_conta(self, valor):
        if isinstance(valor, int) and valor > 0:
            self._num_conta = valor
        else:
            raise ValueError("Número da conta deve ser um inteiro positivo.")

    # --- proprietario ---
    @property
    def proprietario(self):
        return self._proprietario
    
    @proprietario.setter
    def proprietario(self, user: User):
        if isinstance(user, User):
            self._proprietario = user
        else:
            raise ValueError("Proprietário deve ser um nome válido.")

    # --- saldo ---
    @property
    def saldo(self):
        return self._saldo
    
    @saldo.setter
    def saldo(self, valor):
        if isinstance(valor, (int, float)) and valor >= 0:
            self._saldo = float(valor)
            if self.alerta_saldo and self._saldo < self.alerta_saldo:
                print(f"Alerta: Saldo da conta {self.num_conta} abaixo do limite de {self.alerta_saldo}. Saldo atual: {self._saldo}")
        else:
            raise ValueError("Saldo deve ser um número não negativo.")

    # --- alerta_saldo ---
    @property
    def alerta_saldo(self):
        return self._alerta_saldo
    
    @alerta_saldo.setter
    def alerta_saldo(self, valor):
        if valor is None or (isinstance(valor, (int, float)) and valor >= 0):
            self._alerta_saldo = valor
        else:
            raise ValueError("Alerta de saldo deve ser None ou um número não negativo.")

    # --- divida_emprestimo ---
    @property
    def divida_emprestimo(self):
        return self._divida_emprestimo

    def pagar_emprestimo(self, valor):
        """Paga uma parte da dívida do empréstimo, debitando do saldo da conta."""
        if valor <= 0:
            print("\n[ERRO] O valor do pagamento deve ser positivo.\n")
            return False
        if valor > self.saldo:
            print("\n[ERRO] Saldo insuficiente para realizar o pagamento.\n")
            return False
        if valor > self._divida_emprestimo:
            print(f"\n[ERRO] O valor do pagamento (R${valor:.2f}) é maior que a dívida atual (R${self._divida_emprestimo:.2f}).\n")
            return False

        self.saque(valor) # Debita o valor da conta
        self._divida_emprestimo -= valor
        # Modifica a última transação (que foi um saque) para refletir o pagamento
        if self.historico:
            self.historico[-1].tipo = "Pagamento Empréstimo"
            self.historico[-1].descricao = f"Pagamento de R${valor:.2f} da dívida."
        return True

    # --- historico ---
    @property
    def historico(self):
        return self._historico

    @historico.setter
    def historico(self, lista_transacoes):
        if isinstance(lista_transacoes, list):
            self._historico = lista_transacoes
        else:
            raise ValueError("Histórico deve ser uma lista de transações.")


    # Métodos que alteram o histórico
    def deposito(self, quantidade):
        if quantidade > 0.0:
            self.saldo += quantidade
            self._historico.append(Transacao("Depósito", quantidade))

    def saque(self, quantidade):
        if 0 < quantidade <= self.saldo:
            self.saldo -= quantidade
            self._historico.append(Transacao("Saque", quantidade))
            return True
        else:
            self._historico.append(Transacao("Saque falhou", quantidade, descricao="Saldo insuficiente"))
            return False

    def registrar_transferencia(self, valor, destino):
        self._historico.append(Transacao("Transferência enviada", valor, descricao=f"Para conta {destino.num_conta}"))

    def registrar_recebimento(self, valor, origem):
        self._historico.append(Transacao("Transferência recebida", valor, descricao=f"De conta {origem.num_conta}"))
