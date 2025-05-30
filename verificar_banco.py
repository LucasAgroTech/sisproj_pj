import sqlite3

# Conectar ao banco
conn = sqlite3.connect('contrato.db')
cursor = conn.cursor()

# Verificar tabelas existentes
print("Tabelas existentes:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tabelas = cursor.fetchall()
for tabela in tabelas:
    print(f"- {tabela[0]}")

print("\nEstrutura da tabela eventos:")
cursor.execute("PRAGMA table_info(eventos)")
colunas = cursor.fetchall()
for coluna in colunas:
    print(f"- {coluna}")

# Verificar se existe tabela evento_custeio
print("\nVerificando se existe tabela evento_custeio...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='evento_custeio';")
if cursor.fetchone():
    print("Tabela evento_custeio encontrada!")
    cursor.execute("PRAGMA table_info(evento_custeio)")
    colunas_custeio = cursor.fetchall()
    for coluna in colunas_custeio:
        print(f"- {coluna}")
else:
    print("Tabela evento_custeio não encontrada.")

conn.close() 