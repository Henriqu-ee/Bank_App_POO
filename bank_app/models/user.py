class User:
    def __init__(self, nome, cpf):
        self._nome = None
        self._cpf = None
        
        self.nome = nome
        self.cpf = cpf

    # --- nome ---
    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        if isinstance(valor, str) and valor.strip().replace(' ', '').isalpha():
            self._nome = valor.strip()
        else:
            raise ValueError("Nome não deve ser vazio e deve conter apenas letras e espaços.")

    # --- cpf ---
    @property
    def cpf(self):
        return self._cpf

    @cpf.setter
    def cpf(self, valor):
        # Garante que o CPF é um número inteiro e positivo
        if isinstance(valor, int) and valor > 0:
            self._cpf = valor
        else:
            raise ValueError("CPF deve ser um número inteiro positivo.")

    def __str__(self):
        return f"Nome: {self.nome}, CPF: {self.cpf}"