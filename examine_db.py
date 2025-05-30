import sqlite3

def examine_db():
    conn = sqlite3.connect('contrato.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("Tables in database:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Get structure of each table
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print(f"\nTable {table[0]} structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    examine_db()
