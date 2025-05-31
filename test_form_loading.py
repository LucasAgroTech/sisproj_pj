import tkinter as tk
from tkinter import ttk
import sqlite3

def test_form_loading():
    """
    Tests if the form is loading the custeio data correctly.
    """
    print("Testing form loading...")
    
    # Connect to the database
    conn = sqlite3.connect('contrato.db')
    cursor = conn.cursor()
    
    try:
        # Get the test product we inserted
        cursor.execute("SELECT * FROM produtos_servicos WHERE id = 3;")
        produto = cursor.fetchone()
        
        if not produto:
            print("Test product not found. Please run insert_test_produto.py first.")
            return False
        
        print("\nProduct data from database:")
        cursor.execute("PRAGMA table_info(produtos_servicos);")
        columns = [column[1] for column in cursor.fetchall()]
        
        for i, value in enumerate(produto):
            print(f"  {columns[i]}: {value}")
        
        # Create a simple Tkinter window to test the form
        root = tk.Tk()
        root.title("Test Form Loading")
        root.geometry("800x600")
        
        # Create a frame to hold the form
        frame = ttk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Import the ProdutoServicoForm class
        from views.produtos_servicos_view import ProdutoServicoForm
        
        # Create the form with the test product
        form = ProdutoServicoForm(
            frame,
            callback_salvar=lambda: print("Save callback called"),
            callback_cancelar=lambda: print("Cancel callback called"),
            produto=produto
        )
        form.pack(fill=tk.BOTH, expand=True)
        
        # Add a button to print the current values of the custeio fields
        def print_custeio_values():
            print("\nCurrent values in the custeio form:")
            for field in ["instituicao", "instrumento", "subprojeto", "ta", "pta", "acao", "resultado", "meta"]:
                try:
                    widget = form.form_custeio.campos[field]["widget"]
                    value = widget.get()
                    print(f"  {field}: '{value}'")
                except Exception as e:
                    print(f"  Error getting {field}: {e}")
        
        ttk.Button(root, text="Print Custeio Values", command=print_custeio_values).pack(pady=10)
        
        # Add a button to close the window
        ttk.Button(root, text="Close", command=root.destroy).pack(pady=10)
        
        # Run the Tkinter main loop
        print("\nOpening test form window. Click 'Print Custeio Values' to see the current values.")
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    test_form_loading()
