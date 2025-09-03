import sqlite3
from models.user import User
from models.account import Conta
from models.account_types import ContaCorrente, ContaPoupanca
from database.db_transaction_manager import criar_tabela_transacoes, carregar_transacoes

DB_PATH = 'data/db.sqlite'

def conectar():
    """Cria uma conexão com o banco de dados."""
    return sqlite3.connect(DB_PATH)

def criar_tabelas():
    """Cria as tabelas do banco de dados se elas não existirem."""
    with conectar() as conn:
        cursor = conn.cursor()
        # 1. ADICIONADA A COLUNA 'divida_emprestimo'
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contas (
                num_conta TEXT PRIMARY KEY,
                nome TEXT,
                cpf TEXT,
                saldo REAL,
                alerta_saldo REAL,
                tipo_conta TEXT NOT NULL DEFAULT 'corrente',
                divida_emprestimo REAL DEFAULT 0.0
            )
        """)
        conn.commit()
    criar_tabela_transacoes()

def salvar_conta(conta):
    """Salva ou atualiza uma conta no banco de dados."""
    with conectar() as conn:
        cursor = conn.cursor()
        
        if isinstance(conta, ContaCorrente):
            tipo = 'corrente'
        elif isinstance(conta, ContaPoupanca):
            tipo = 'poupanca'
        else:
            tipo = 'base'

        # 2. ADICIONADO 'divida_emprestimo' AO INSERT E AOS VALORES
        cursor.execute("""
            INSERT OR REPLACE INTO contas (num_conta, nome, cpf, saldo, alerta_saldo, tipo_conta, divida_emprestimo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (conta.num_conta, conta.proprietario.nome, conta.proprietario.cpf, conta.saldo, conta.alerta_saldo, tipo, conta.divida_emprestimo))
        conn.commit()

def carregar_conta(num_conta):
    """Carrega uma conta do banco de dados pelo número da conta."""
    with conectar() as conn:
        cursor = conn.cursor()
        # 3. ADICIONADO 'divida_emprestimo' AO SELECT
        cursor.execute("SELECT num_conta, nome, cpf, saldo, alerta_saldo, tipo_conta, divida_emprestimo FROM contas WHERE num_conta = ?", (num_conta,))
        row = cursor.fetchone()
        if row:
            # E ADICIONADO 'db_divida' AO DESEMPACOTAMENTO
            db_num_conta, db_nome, db_cpf, db_saldo, db_alerta_saldo, db_tipo_conta, db_divida = row
            
            user = User(db_nome, int(db_cpf))
            
            if db_tipo_conta == 'corrente':
                conta = ContaCorrente(int(db_num_conta), user, db_saldo)
            elif db_tipo_conta == 'poupanca':
                conta = ContaPoupanca(int(db_num_conta), user, db_saldo)
            else:
                conta = Conta(int(db_num_conta), user, db_saldo)

            conta.alerta_saldo = db_alerta_saldo
            conta._divida_emprestimo = db_divida  # ATRIBUIÇÃO DO VALOR CARREGADO
            conta.historico = carregar_transacoes(num_conta)
            return conta
    return None

def procurar_conta(num_conta):
    """Wrapper para carregar_conta, usado no main."""
    return carregar_conta(num_conta)
