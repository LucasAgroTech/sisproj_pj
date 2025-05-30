# models/db_manager.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'contrato.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Usuários (usuário inicial: admin/admin)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL -- hashed em produção
    );
    """)

    # Logs de acesso e ações
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        acao TEXT NOT NULL,
        data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Demanda
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS demanda (
        codigo INTEGER PRIMARY KEY AUTOINCREMENT,
        data_entrada TEXT,
        solicitante TEXT,
        data_protocolo TEXT,
        oficio TEXT,
        nup_sei TEXT,
        status TEXT
    );
    """)

    # Carta Acordo
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS carta_acordo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_demanda INTEGER,
        instituicao TEXT, instrumento TEXT, subprojeto TEXT, ta TEXT, pta TEXT, acao TEXT,
        resultado TEXT, meta TEXT, contrato TEXT, vigencia_inicial TEXT, vigencia_final TEXT,
        instituicao_2 TEXT, cnpj TEXT, titulo_projeto TEXT, objetivo TEXT,
        valor_estimado REAL, total_contrato REAL, observacoes TEXT,
        FOREIGN KEY (codigo_demanda) REFERENCES demanda(codigo)
    );
    """)

    # Produtos e Serviços
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos_servicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_demanda INTEGER,
        fornecedor TEXT, modalidade TEXT, objetivo TEXT,
        vigencia_inicial TEXT, vigencia_final TEXT,
        observacao TEXT, valor_estimado REAL, total_contrato REAL,
        FOREIGN KEY (codigo_demanda) REFERENCES demanda(codigo)
    );
    """)

    # Eventos - agora com campos de custeio incluídos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_demanda INTEGER,
        instituicao TEXT, instrumento TEXT, subprojeto TEXT, ta TEXT, pta TEXT, acao TEXT,
        resultado TEXT, meta TEXT,
        titulo_evento TEXT, fornecedor TEXT,
        observacao TEXT, valor_estimado REAL, total_contrato REAL,
        FOREIGN KEY (codigo_demanda) REFERENCES demanda(codigo)
    );
    """)


    # Aditivos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aditivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_contrato INTEGER,
        tipo_contrato TEXT, -- ('carta_acordo', 'produtos_servicos', 'eventos')
        tipo_aditivo TEXT,  -- ('tempo', 'valor', 'ambos')
        descricao TEXT,
        valor_aditivo REAL,
        nova_vigencia_final TEXT,
        data_registro TEXT
        -- Relacionamento manual com o contrato, dependendo do tipo
    );
    """)


    # Adicione aqui criação de outras tabelas conforme o crescimento

    # Usuário admin padrão (só insere se não existir)
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin'))  # Troque por hash
        conn.commit()

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
