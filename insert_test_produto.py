import sqlite3

def insert_test_produto():
    """
    Inserts a test product with custeio data.
    """
    print("Inserting test product with custeio data...")
    
    # Connect to the database
    conn = sqlite3.connect('contrato.db')
    cursor = conn.cursor()
    
    try:
        # Insert a test product with custeio data
        cursor.execute("""
        INSERT INTO produtos_servicos (
            codigo_demanda, fornecedor, modalidade, objetivo, vigencia_inicial, vigencia_final,
            observacao, valor_estimado, total_contrato, instituicao, instrumento, subprojeto,
            ta, pta, acao, resultado, meta
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            16,  # codigo_demanda
            "Fornecedor Teste",  # fornecedor
            "Contrato",  # modalidade
            "Objetivo do teste",  # objetivo
            "01/01/2023",  # vigencia_inicial
            "31/12/2023",  # vigencia_final
            "Observação de teste",  # observacao
            1000.00,  # valor_estimado
            5000.00,  # total_contrato
            "OPAS",  # instituicao
            "TC 95",  # instrumento
            "",  # subprojeto
            "TA 1",  # ta
            "2023",  # pta
            "01",  # acao
            "Resultado 1",  # resultado
            "02"  # meta
        ))
        
        # Commit the changes
        conn.commit()
        
        # Get the ID of the inserted product
        produto_id = cursor.lastrowid
        print(f"Test product inserted with ID: {produto_id}")
        
        # Verify the inserted data
        cursor.execute("SELECT * FROM produtos_servicos WHERE id = ?", (produto_id,))
        row = cursor.fetchone()
        
        if row:
            print("\nInserted product data:")
            cursor.execute("PRAGMA table_info(produtos_servicos);")
            columns = [column[1] for column in cursor.fetchall()]
            
            for i, value in enumerate(row):
                print(f"  {columns[i]}: {value}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    insert_test_produto()
