import sqlite3

def create_tables():
    conn = sqlite3.connect('contrato.db')
    cursor = conn.cursor()
    
    # Create titulo_eventos table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS titulo_eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        cidade TEXT,
        estado TEXT,
        data_inicio TEXT,
        data_fim TEXT
    )
    ''')
    
    # Create fornecedores table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fornecedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        razao_social TEXT NOT NULL,
        cnpj TEXT,
        observacao TEXT
    )
    ''')
    
    conn.commit()
    print("Tables created successfully")
    conn.close()

if __name__ == "__main__":
    create_tables()
