import pandas as pd
import sqlite3
import os

# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Check if the Excel file exists
excel_path = 'listagem_Custeio.xlsx'
if os.path.exists(excel_path):
    print(f"Excel file found: {excel_path}")
else:
    print(f"Excel file not found at: {excel_path}")

# Read the Excel file
try:
    df = pd.read_excel(excel_path)
    
    # Display basic information about the dataframe
    print("\nDataFrame Info:")
    print(f"Number of rows: {len(df)}")
    print(f"Number of columns: {len(df.columns)}")
    
    # Display column names
    print("\nColumn Names:")
    for col in df.columns:
        print(f"- {col}")
    
    # Display data types
    print("\nData Types:")
    print(df.dtypes)
    
    # Display first few rows
    print("\nFirst 5 rows:")
    print(df.head())
    
    # Check for null values
    print("\nNull Values Count:")
    print(df.isnull().sum())
    
except Exception as e:
    print(f"Error reading Excel file: {e}")

# Check if the database file exists
db_path = 'contrato.db'
if os.path.exists(db_path):
    print(f"\nDatabase file found: {db_path}")
    
    # Connect to the database and list tables
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\nExisting tables in the database:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table[0]});")
            columns = cursor.fetchall()
            print(f"  Schema for {table[0]}:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
    except Exception as e:
        print(f"Error connecting to database: {e}")
else:
    print(f"\nDatabase file not found at: {db_path}")
