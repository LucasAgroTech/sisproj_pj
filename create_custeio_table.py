import pandas as pd
import sqlite3
import os

def create_custeio_table():
    print("Starting the process to create custeio table...")
    
    # Check if files exist
    excel_path = 'listagem_Custeio.xlsx'
    db_path = 'contrato.db'
    
    if not os.path.exists(excel_path):
        print(f"Error: Excel file not found at {excel_path}")
        return False
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return False
    
    try:
        # Read the Excel file
        print(f"Reading Excel file: {excel_path}")
        df = pd.read_excel(excel_path)
        
        # Clean column names (remove dots and standardize)
        df.columns = [col.replace('DIM_PROJETO.', '').lower() for col in df.columns]
        
        # Fill NaN values with empty strings for text columns
        df = df.fillna('')
        
        # Connect to the SQLite database
        print(f"Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='custeio';")
        if cursor.fetchone():
            print("Table 'custeio' already exists. Dropping it to recreate...")
            cursor.execute("DROP TABLE custeio;")
        
        # Create the new table
        print("Creating 'custeio' table...")
        cursor.execute('''
        CREATE TABLE custeio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instituicao_parceira TEXT,
            cod_projeto TEXT,
            cod_ta TEXT,
            resultado TEXT,
            subprojeto TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        
        # Insert data into the table
        print(f"Inserting {len(df)} rows of data...")
        for _, row in df.iterrows():
            cursor.execute('''
            INSERT INTO custeio (instituicao_parceira, cod_projeto, cod_ta, resultado, subprojeto)
            VALUES (?, ?, ?, ?, ?);
            ''', (
                row['instituicao_parceira'],
                row['cod_projeto'],
                row['cod_ta'],
                row['resultado'],
                row['subprojeto']
            ))
        
        # Create indexes for better query performance
        print("Creating indexes...")
        cursor.execute("CREATE INDEX idx_instituicao ON custeio (instituicao_parceira);")
        cursor.execute("CREATE INDEX idx_cod_projeto ON custeio (cod_projeto);")
        cursor.execute("CREATE INDEX idx_cod_ta ON custeio (cod_ta);")
        cursor.execute("CREATE INDEX idx_resultado ON custeio (resultado);")
        cursor.execute("CREATE INDEX idx_subprojeto ON custeio (subprojeto);")
        
        # Commit the changes and close the connection
        conn.commit()
        
        # Verify the data was inserted correctly
        cursor.execute("SELECT COUNT(*) FROM custeio;")
        count = cursor.fetchone()[0]
        print(f"Verification: {count} rows inserted into the custeio table.")
        
        # Show the first few rows
        cursor.execute("SELECT * FROM custeio LIMIT 5;")
        rows = cursor.fetchall()
        print("\nSample data from the custeio table:")
        for row in rows:
            print(row)
        
        conn.close()
        print("Process completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    create_custeio_table()
