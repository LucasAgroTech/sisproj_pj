import sqlite3

def migrate_produtos_servicos():
    """
    Migrates the produtos_servicos table to add custeio and contrato fields.
    """
    print("Starting migration of produtos_servicos table...")
    
    # Connect to the database
    conn = sqlite3.connect('contrato.db')
    cursor = conn.cursor()
    
    try:
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='produtos_servicos';")
        if not cursor.fetchone():
            print("Error: produtos_servicos table does not exist.")
            return False
        
        # Get the current columns in the table
        cursor.execute("PRAGMA table_info(produtos_servicos);")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add custeio fields if they don't exist
        custeio_fields = [
            ("instituicao", "TEXT"),
            ("instrumento", "TEXT"),
            ("subprojeto", "TEXT"),
            ("ta", "TEXT"),
            ("pta", "TEXT"),
            ("acao", "TEXT"),
            ("resultado", "TEXT"),
            ("meta", "TEXT")
        ]
        
        for field_name, field_type in custeio_fields:
            if field_name not in columns:
                print(f"Adding {field_name} column to produtos_servicos table...")
                cursor.execute(f"ALTER TABLE produtos_servicos ADD COLUMN {field_name} {field_type};")
        
        # Commit the changes
        conn.commit()
        print("Migration completed successfully!")
        
        # Show the updated table structure
        cursor.execute("PRAGMA table_info(produtos_servicos);")
        updated_columns = cursor.fetchall()
        print("\nUpdated produtos_servicos table structure:")
        for column in updated_columns:
            print(f"  - {column[1]} ({column[2]})")
        
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_produtos_servicos()
