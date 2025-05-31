import sqlite3

def check_produto_structure():
    """
    Checks the structure of a product in the produtos_servicos table.
    """
    print("Checking produto structure...")
    
    # Connect to the database
    conn = sqlite3.connect('contrato.db')
    cursor = conn.cursor()
    
    try:
        # Get column names
        cursor.execute("PRAGMA table_info(produtos_servicos);")
        columns = [column[1] for column in cursor.fetchall()]
        print("Columns:", columns)
        
        # Get a record
        cursor.execute("SELECT * FROM produtos_servicos LIMIT 1;")
        row = cursor.fetchone()
        
        if row:
            print("\nProduct tuple structure:")
            print(f"Length of tuple: {len(row)}")
            for i, value in enumerate(row):
                print(f"  Index {i}: {value} (Column: {columns[i] if i < len(columns) else 'Unknown'})")
        else:
            print("No products found in the database.")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    check_produto_structure()
