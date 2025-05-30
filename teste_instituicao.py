import sqlite3

# Conectar ao banco
conn = sqlite3.connect('contrato.db')
cursor = conn.cursor()

# Buscar eventos
cursor.execute("SELECT * FROM eventos")
eventos = cursor.fetchall()

instituicoes_opcoes = ["OPAS", "FIOCRUZ"]

for evento in eventos:
    print(f"\nEvento ID {evento[0]}:")
    print(f"  Valor original instituição (índice 11): {evento[11]} (tipo: {type(evento[11])})")
    
    # Testar a lógica atual
    if evento[11] is not None:
        instituicao_padrao = evento[11]
        print(f"  Usando valor existente: {instituicao_padrao}")
    else:
        instituicao_padrao = instituicoes_opcoes[0]
        print(f"  Usando valor padrão: {instituicao_padrao}")
    
    print(f"  Resultado final: {instituicao_padrao}")

conn.close() 