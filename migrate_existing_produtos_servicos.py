import sqlite3

def migrate_existing_produtos_servicos():
    """
    Migrates existing data in the produtos_servicos table to populate the new custeio fields.
    """
    print("Starting migration of existing produtos_servicos data...")
    
    # Connect to the database
    conn = sqlite3.connect('contrato.db')
    cursor = conn.cursor()
    
    try:
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='produtos_servicos';")
        if not cursor.fetchone():
            print("Error: produtos_servicos table does not exist.")
            return False
        
        # Get all existing records
        cursor.execute("SELECT id FROM produtos_servicos;")
        records = cursor.fetchall()
        
        if not records:
            print("No existing records found in produtos_servicos table.")
            return True
        
        print(f"Found {len(records)} records to update.")
        
        # Update each record with default values for the new fields
        for record in records:
            id_produto = record[0]
            
            # Check if the record already has values for the new fields
            cursor.execute("""
                SELECT instituicao, instrumento, subprojeto, ta, pta, acao, resultado, meta
                FROM produtos_servicos WHERE id = ?
            """, (id_produto,))
            
            values = cursor.fetchone()
            
            # If any of the fields are NULL, update them with empty strings
            if values and any(v is None for v in values):
                print(f"Updating record with ID {id_produto}...")
                cursor.execute("""
                    UPDATE produtos_servicos SET
                        instituicao = COALESCE(instituicao, ''),
                        instrumento = COALESCE(instrumento, ''),
                        subprojeto = COALESCE(subprojeto, ''),
                        ta = COALESCE(ta, ''),
                        pta = COALESCE(pta, ''),
                        acao = COALESCE(acao, ''),
                        resultado = COALESCE(resultado, ''),
                        meta = COALESCE(meta, '')
                    WHERE id = ?
                """, (id_produto,))
        
        # Commit the changes
        conn.commit()
        print("Migration of existing data completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error during migration of existing data: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_existing_produtos_servicos()
