from datetime import datetime

class Transacao:
    def __init__(self, tipo, valor, descricao="", timestamp=None):
        self._tipo = tipo
        self._valor = valor
        self._descricao = descricao
        self._timestamp = timestamp if timestamp else datetime.now()

    # --- tipo ---
    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, valor):
        if isinstance(valor, str) and valor.strip():
            self._tipo = valor.strip()
        else:
            raise ValueError("O tipo da transação não pode ser vazio.")

    # --- valor ---
    @property
    def valor(self):
        return self._valor

    # Não há setter para 'valor', pois ele não deve ser alterado após a criação.
    
    # --- timestamp (apenas getter, não deve ser alterado) ---
    @property
    def timestamp(self):
        return self._timestamp

    # --- descricao ---
    @property
    def descricao(self):
        return self._descricao
    
    @descricao.setter
    def descricao(self, valor):
        self._descricao = str(valor) # Garante que a descrição seja sempre uma string

    def __str__(self):
        desc_info = f" ({self.descricao})" if self.descricao else ""
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.tipo}: R${self.valor:.2f}{desc_info}"