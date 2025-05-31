import sqlite3

def check_produtos_servicos():
    """
    Checks the data in the produtos_servicos table.
    """
    print("Checking produtos_servicos table data...")
    
    # Connect to the database
    conn = sqlite3.connect('contrato.db')
    cursor = conn.cursor()
    
    try:
        # Get column names
        cursor.execute("PRAGMA table_info(produtos_servicos);")
        columns = [column[1] for column in cursor.fetchall()]
        print("Columns:", columns)
        
        # Get all records
        cursor.execute("SELECT * FROM produtos_servicos;")
        rows = cursor.fetchall()
        
        print(f"Number of rows: {len(rows)}")
        
        # Print each row
        for i, row in enumerate(rows):
            print(f"\nRow {i+1}:")
            for j, value in enumerate(row):
                print(f"  {columns[j]}: {value}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    check_produtos_servicos()
