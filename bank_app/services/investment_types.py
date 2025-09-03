
class Investimento:
    def __init__(self, nome, taxa_mensal):
        self.nome = nome
        self.taxa_mensal = taxa_mensal

    def calcular_retorno(self, valor, meses):
        # Lógica de juros compostos como exemplo
        return valor * ((1 + self.taxa_mensal) ** meses) - valor

class Poupanca(Investimento):
    def __init__(self):
        super().__init__("Poupança", 0.0065)

class CDB(Investimento):
    def __init__(self):
        super().__init__("CDB", 0.0090)

class TesouroDireto(Investimento):
    def __init__(self):
        super().__init__("Tesouro Direto", 0.0075)