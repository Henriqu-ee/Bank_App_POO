from database.db_manager import criar_tabelas, salvar_conta, carregar_conta
from database.db_transaction_manager import salvar_transacao, criar_tabela_transacoes, deletar_transacoes
from models.user import User
from models.account import Conta
from models.account_types import ContaCorrente, ContaPoupanca
from services.loan_service import solicitar_emprestimo
from services.transfer_service import transferir, transferir_externo
from services.notification_service import definir_alerta, verificar_alerta
from services.currency_service import cambio 
from services.payment_service import pagar_conta
from services.checkbook_service import solicitar_talao
from services.support_service import registrar_suporte, listar_mensagens
from services.investment_types import Poupanca, CDB, TesouroDireto

criar_tabelas()

users = []
contas = []

def procurar_conta(num_conta): # procura na lista de contas carregadas
    # Remove a conta da lista de cache, se ela existir
    contas[:] = [c for c in contas if c.num_conta != num_conta]

    # Sempre carrega a conta do banco de dados para garantir dados atualizados
    conta = carregar_conta(num_conta)
    if conta:
        contas.append(conta) # Adiciona a versão "fresca" ao cache
    return conta


def criando_user():
    while True:
        nome = input("Nome do titular: ")
        nome_valido = nome.strip().replace(' ', '')
        if nome_valido and nome_valido.isalpha():
            break
        else:
            print("\nNome inválido. O nome não pode ser vazio e deve conter apenas letras.\n")

    while True:
        try:
            cpf = int(input("CPF: "))
            if cpf <= 0:
                raise ValueError("O CPF deve ser um número positivo.")
            break
        except ValueError:
            print("\nCPF inválido. Por favor, digite apenas números inteiros positivos.\n")

    while True:
        try:
            num_conta = int(input("Número da conta: "))
            if num_conta <= 0:
                raise ValueError("O número da conta deve ser positivo.")
            break
        except ValueError:
            print("\nNúmero de conta inválido. Por favor, digite apenas números inteiros positivos.\n")

    while True:
        tipo_conta_input = input("Qual tipo de conta deseja criar? (1 - Corrente, 2 - Poupança): ")
        if tipo_conta_input in ["1", "2"]:
            break
        else:
            print("\nOpção inválida. Escolha 1 ou 2.\n")

    user = User(nome.strip(), cpf)

    if tipo_conta_input == "1":
        conta = ContaCorrente(num_conta, user)
        print("\nConta Corrente criada com sucesso!")
    else: # tipo_conta_input == "2"
        conta = ContaPoupanca(num_conta, user)
        print("\nConta Poupança criada com sucesso!")

    salvar_conta(conta)
    print(f"Conta número {conta.num_conta} para {user.nome} registrada.\n")

def depositar():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)

    if conta:
        try:
            quantidade = float(input("Valor para depósito: "))
            if quantidade <= 0:
                print("\nO valor do depósito deve ser positivo.\n")
                return
        except ValueError:
            print("\nValor inválido. Por favor, digite um número.\n")
            return

        conta.deposito(quantidade)
        transacao = conta.historico[-1]
        salvar_transacao(conta.num_conta, transacao)
        salvar_conta(conta)

        print(f"\nDepósito de R${quantidade:.2f} realizado com sucesso!\n")
        verificar_alerta(conta)
    else:
        print("\nConta não encontrada.\n")

def sacar():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)

    if conta:
        quantidade = float(input("Valor para saque: "))
        if conta.saque(quantidade):
            salvar_transacao(conta.num_conta, conta.historico[-1])
            salvar_conta(conta)

            print(f"\nSaque de R${quantidade:.2f} realizado com sucesso!\n")
            verificar_alerta(conta)
        else:
            print("\nSaldo insuficiente.\n")
    else:
        print("\nConta não encontrada.\n")
        
def realizar_emprestimo():
    """Interface para o usuário solicitar um empréstimo."""
    acc_num = input("Número da conta para receber o empréstimo: ")
    conta = procurar_conta(acc_num)

    if not conta:
        print("\n[ERRO] Conta não encontrada.\n")
        return

    try:
        valor = float(input("Valor do empréstimo a ser solicitado: R$"))
        # A validação de valor > 0 já é feita pelo serviço, mas é bom ter aqui também.
        if valor <= 0:
            print("\n[ERRO] O valor do empréstimo deve ser um número positivo.\n")
            return
    except ValueError:
        print("\n[ERRO] Valor inválido. Por favor, digite um número.\n")
        return

    # Chama a função do serviço para executar a lógica de negócio
    solicitar_emprestimo(conta, valor)

    # Salva as alterações no banco de dados
    salvar_conta(conta)
    salvar_transacao(conta.num_conta, conta.historico[-1])

    print(f"\nEmpréstimo de R${valor:.2f} creditado com sucesso na conta {acc_num}.\n")
    verificar_alerta(conta)

def transferir_entre_contas():
    acc_origem = input("Conta de origem: ")
    acc_destino = input("Conta de destino: ")
    quantidade = float(input("Valor da transferência: "))

    origem = procurar_conta(acc_origem)
    destino = procurar_conta(acc_destino)

    if origem and destino: # Verifica se ambas as contas existem
        if transferir(origem, destino, quantidade):
            salvar_transacao(origem.num_conta, origem.historico[-1])
            salvar_transacao(destino.num_conta, destino.historico[-1])
            salvar_conta(origem)
            salvar_conta(destino)

            print("\nTransferência realizada com sucesso!\n")
            verificar_alerta(origem)
        else:
            print("\nSaldo insuficiente na conta de origem.\n")
    else:
        print("\nConta(s) não encontrada(s).\n")

def realizar_transferencia_externa():
    """Interface para realizar uma transferência para fora do banco (PIX/TED), com validação completa de erros."""
    # 1. Validação: A conta de origem existe?
    acc_num_origem = input("Número da sua conta: ")
    conta_origem = procurar_conta(acc_num_origem)

    if not conta_origem:
        print("\n[ERRO] Sua conta de origem não foi encontrada.\n")
        return

    chave_destino = input("Digite a chave (CPF, e-mail, etc.) do destinatário: ")

    # 2. Validação: O valor é um número válido e positivo?
    try:
        valor = float(input("Valor a ser transferido: R$"))
        if valor <= 0:
            print("\n[ERRO] O valor da transferência deve ser um número positivo.\n")
            return
    except ValueError:
        print("\n[ERRO] Valor inválido. Por favor, digite um número.\n")
        return

    # 3. VALIDAÇÃO CRUCIAL: O saldo é suficiente?
    # Esta verificação é feita ANTES de chamar o serviço.
    if conta_origem.saldo < valor:
        print(f"\n[ERRO] Saldo insuficiente para realizar a transferência.")
        print(f"Saldo atual: R${conta_origem.saldo:.2f} | Valor da transferência: R${valor:.2f}\n")
        return

    # Se todas as validações passaram, podemos prosseguir com segurança.
    print("\nProcessando transferência...")
    if transferir_externo(conta_origem, valor, chave_destino):
        salvar_conta(conta_origem)
        salvar_transacao(conta_origem.num_conta, conta_origem.historico[-1])
        print("Transferência externa realizada com sucesso!\n")
        verificar_alerta(conta_origem)
    else:
        # Este 'else' agora serve como uma proteção para erros inesperados,
        # já que o erro de saldo insuficiente foi tratado antes.
        print("Falha inesperada ao realizar a transferência externa.\n")

def definir_alerta_saldo():
    """Define um alerta de saldo para uma conta."""
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if conta:
        try:
            limite = float(input("Definir alerta para quando o saldo for menor que: R$"))
            if limite < 0:
                print("\nO limite não pode ser negativo.\n")
                return
            
            definir_alerta(conta, limite)
            salvar_conta(conta) # <-- PASSO CRUCIAL: Salva a alteração no banco
            
            print(f"\nAlerta de saldo definido para R${limite:.2f} na conta {acc_num}.\n")
        except ValueError:
            print("\nValor de limite inválido.\n")
    else:
        print("\nConta não encontrada.\n")


def pagar_parcela_emprestimo():
    """Interface para o usuário pagar uma parte da dívida do empréstimo."""
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)

    if not conta:
        print("\n[ERRO] Conta não encontrada.\n")
        return
    
    if conta.divida_emprestimo == 0:
        print("\nVocê não possui dívidas de empréstimo nesta conta.\n")
        return

    print(f"Sua dívida atual é de: R${conta.divida_emprestimo:.2f}")
    try:
        valor = float(input("Valor a pagar: R$"))
    except ValueError:
        print("\n[ERRO] Valor inválido.\n")
        return

    if conta.pagar_emprestimo(valor):
        salvar_conta(conta)
        salvar_transacao(conta.num_conta, conta.historico[-1])
        print("\nPagamento realizado com sucesso!")
        print(f"Nova dívida: R${conta.divida_emprestimo:.2f}\n")
    else:
        # As mensagens de erro específicas (saldo insuficiente, etc.) já são impressas pelo método.
        print("\nFalha ao realizar o pagamento.\n")

def ver_saldo():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if conta:
        print(f"\n--- Saldo da Conta {acc_num} ---")
        print(f"Saldo disponível: R${conta.saldo:.2f}")
        if isinstance(conta, ContaCorrente):
            print(f"Limite de Cheque Especial: R${conta.limite_cheque_especial:.2f}")
            print(f"Saldo total (com limite): R${conta.saldo + conta.limite_cheque_especial:.2f}")
        if conta.divida_emprestimo > 0:
            print(f"Dívida de Empréstimo: R${conta.divida_emprestimo:.2f}")
        print("---------------------------------\n")
    else:
        print("\nConta não encontrada.\n")

def ver_historico():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if conta:
        print("\n--- Histórico de Transações ---")
        if not conta.historico:
            print("\nNenhuma transação registrada.\n")
        else:
            for transacao in conta.historico:
                print(f"- {transacao}")
            print() # Adiciona uma linha em branco no final para melhor formatação
    else:
        print("\nConta não encontrada.\n")

def limpar_historico():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if conta:
        confirm = input("Tem certeza que deseja apagar TODO o histórico? (s/n): ").lower()
        if confirm == "s":
            conta.historico.clear()                 # Limpa na memória
            deletar_transacoes(conta.num_conta)     # Limpa no banco
            salvar_conta(conta)                     # Atualiza saldo
            print("\nHistórico apagado com sucesso!\n")
        else:
            print("\nOperação cancelada.\n")
    else:
        print("\nConta não encontrada.\n")

def pagamento_de_conta():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if conta:
        descricao = input("Descrição da conta (ex: Conta de luz): ")
        valor = float(input("Valor a pagar: "))
        if pagar_conta(conta, descricao, valor):
            salvar_transacao(conta.num_conta, conta.historico[-1])
            salvar_conta(conta)
            print("\nPagamento realizado com sucesso!\n")
            verificar_alerta(conta)
        else:
            print("\nSaldo insuficiente para pagar a conta.\n")
    else:
        print("\nConta não encontrada.\n")

def solicitar_talao_cheques():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if conta:
        try:
            quantidade = int(input("Quantidade de talões a solicitar (R$15,00 cada): "))
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            print("\nQuantidade inválida. Deve ser um número inteiro positivo.\n")
            return
        if solicitar_talao(conta, quantidade):
            salvar_transacao(conta.num_conta, conta.historico[-1])
            salvar_conta(conta)
            print(f"\n{quantidade} talão(ões) solicitado(s) com sucesso!\n")
            verificar_alerta(conta)
        else:
            salvar_transacao(conta.num_conta, conta.historico[-1])
            salvar_conta(conta)
            print("\nSaldo insuficiente para solicitar talão.\n")
    else:
        print("\nConta não encontrada.\n")

def suporte_cliente():
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if conta:
        print("\n1 - Enviar nova mensagem")
        print("2 - Ver mensagens anteriores")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            mensagem = input("Descreva seu problema ou dúvida: ")
            registrar_suporte(acc_num, mensagem)
            print("\nMensagem enviada com sucesso. Um atendente entrará em contato.\n")
        elif opcao == "2":
            mensagens = listar_mensagens(acc_num)
            if mensagens:
                print("\n--- Histórico de Suporte ---")
                for linha in mensagens:
                    print(linha.strip())
                print()
            else:
                print("\nNenhuma mensagem registrada.\n")
        else:
            print("\nOpção inválida.\n")
    else:
        print("\nConta não encontrada.\n")

def aplicar_investimento_opcao():
    """Aplica um valor em um dos tipos de investimento disponíveis."""
    acc_num = input("Número da conta: ")
    conta = procurar_conta(acc_num)
    if not conta:
        print("\nConta não encontrada.\n")
        return

    # 1. Mapeia a escolha do usuário para a classe de investimento correspondente
    investimentos = {
        "1": Poupanca(),
        "2": CDB(),
        "3": TesouroDireto()
    }

    print("\nTipos de Investimento Disponíveis:")
    for key, inv in investimentos.items():
        print(f"{key} - {inv.nome} (Taxa mensal aprox.: {inv.taxa_mensal:.2%})")
    
    opcao = input("Escolha uma opção de investimento: ")
    investimento_escolhido = investimentos.get(opcao)

    if not investimento_escolhido:
        print("\nOpção de investimento inválida.\n")
        return

    try:
        valor = float(input("Valor a ser investido: R$"))
        meses = int(input("Por quantos meses: "))
        if valor <= 0 or meses <= 0:
            print("\nValor e meses devem ser números positivos.\n")
            return
    except ValueError:
        print("\nEntrada inválida. Por favor, digite apenas números.\n")
        return

    # 2. Usa o método polimórfico para calcular o retorno
    retorno_estimado = investimento_escolhido.calcular_retorno(valor, meses)

    print(f"\nInvestindo em {investimento_escolhido.nome}...")
    print(f"Retorno estimado após {meses} meses: R${retorno_estimado:.2f}")
    
    # 3. Executa o saque e salva a transação
    if conta.saque(valor):
        salvar_conta(conta)
        # A transação de saque já é registrada pelo método .saque(),
        # então não precisamos adicionar outra.
        print(f"\nInvestimento de R${valor:.2f} realizado com sucesso!\n")
    else:
        # A mensagem de saldo insuficiente já é impressa pelo método .saque()
        print("\nOperação de investimento falhou.\n")

def aplicar_rendimento_poupanca():
    acc_num = input("Número da conta poupança: ")
    conta = procurar_conta(acc_num)
    if isinstance(conta, ContaPoupanca):
        conta.render_juros()
        salvar_conta(conta) # Salva o novo saldo
        print("\nRendimento aplicado com sucesso!\n")
    elif conta:
        print("\nEsta operação é válida apenas para Contas Poupança.\n")
    else:
        print("\nConta não encontrada.\n")

def cobrar_taxa_cc():
    acc_num = input("Número da conta corrente: ")
    conta = procurar_conta(acc_num)
    if isinstance(conta, ContaCorrente):
        conta.cobrar_taxa_manutencao()
        salvar_conta(conta) # Salva o novo saldo
        print("\nTaxa de manutenção cobrada com sucesso!\n")
    elif conta:
        print("\nEsta operação é válida apenas para Contas Corrente.\n")
    else:
        print("\nConta não encontrada.\n")


def menu():
    while True:
        print("\\n----- Sistema Bancário Alagoas -----")
        print("1 - Criar conta")
        print("2 - Depositar")
        print("3 - Sacar")
        print("4 - Transferir (entre contas do banco)")
        print("5 - Transferir (para outros bancos - PIX/TED)")
        print("6 - Ver saldo")
        print("7 - Ver histórico de transações")
        print("8 - Solicitar Empréstimo")
        print("9 - Pagar Empréstimo")
        print("10 - Definir alerta de saldo")
        print("11 - Câmbio de moedas")
        print("12 - Aplicar em Investimentos")
        print("13 - Limpar histórico da conta")
        print("14 - Pagar conta")
        print("15 - Solicitar talão de cheques")
        print("16 - Suporte ao Cliente")
        print("17 - Aplicar rendimento (Poupança)")
        print("18 - Cobrar taxa de manutenção (Corrente)")
        print("19 - Sair")



        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            criando_user()
        elif opcao == "2":
            depositar()
        elif opcao == "3":
            sacar()
        elif opcao == "4":
            transferir_entre_contas()
        elif opcao == "5":
            realizar_transferencia_externa()
        elif opcao == "6":
            ver_saldo()
        elif opcao == "7":
            ver_historico()
        elif opcao == "8":
            realizar_emprestimo()
        elif opcao == "9":
            pagar_parcela_emprestimo()
        elif opcao == "10":
            definir_alerta_saldo()
        elif opcao == "11":
            conta = procurar_conta(input("Número da conta: "))
            if conta:
                moeda = input("Para qual moeda (USD, EUR, JPY): ").upper()
                valor = float(input("Valor em R$: "))
                valor_convertido = cambio(conta, moeda, valor)
                if valor_convertido is not None:
                    salvar_transacao(conta.num_conta, conta.historico[-1])
                    salvar_conta(conta)
                    print(f"\nOperação realizada com sucesso! Valor convertido: {valor_convertido:.2f} {moeda}\n")
                else:
                    print("\nOperação de câmbio falhou.\n")
            else:
                print("\nConta não encontrada.\n")
        elif opcao == "12":
            aplicar_investimento_opcao()
        elif opcao == "13":
            limpar_historico()
        elif opcao == "14":
            pagamento_de_conta()
        elif opcao == "15":
            solicitar_talao_cheques()
        elif opcao == "16":
            suporte_cliente()
        elif opcao == "17":
            aplicar_rendimento_poupanca()
        elif opcao == "18":
            cobrar_taxa_cc()
        elif opcao == "19":
            print("\nEncerrando o sistema. Obrigado!\n")
            break
        else:
            print("\nOpção inválida!\n")

if __name__ == "__main__":
    criar_tabelas()
    criar_tabela_transacoes()
    menu()

