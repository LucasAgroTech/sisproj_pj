import sqlite3

# Conectar ao banco
conn = sqlite3.connect('contrato.db')
cursor = conn.cursor()

print("Estrutura completa da tabela evento_custeio:")
cursor.execute("PRAGMA table_info(evento_custeio)")
colunas_custeio = cursor.fetchall()
for coluna in colunas_custeio:
    print(f"- {coluna}")

print("\nDados existentes na tabela evento_custeio:")
cursor.execute("SELECT * FROM evento_custeio")
dados = cursor.fetchall()
print(f"Total de registros: {len(dados)}")
for i, dado in enumerate(dados[:5]):  # Mostrar apenas os primeiros 5
    print(f"Registro {i+1}: {dado}")

conn.close() 