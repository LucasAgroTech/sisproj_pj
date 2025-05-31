import sqlite3
import tkinter as tk
from tkinter import ttk

def test_form_loading_no_gui():
    """
    Tests if the form is loading the custeio data correctly without requiring GUI interaction.
    """
    print("Testing form loading without GUI...")
    
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
        
        # Create a root window but don't show it
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create a frame to hold the form
        frame = ttk.Frame(root)
        
        # Import the ProdutoServicoForm class
        from views.produtos_servicos_view import ProdutoServicoForm
        
        # Create the form with the test product
        form = ProdutoServicoForm(
            frame,
            callback_salvar=lambda: None,
            callback_cancelar=lambda: None,
            produto=produto
        )
        
        # Process Tkinter events to ensure the form is fully initialized
        root.update()
        
        # Print the current values of the custeio fields
        print("\nCurrent values in the custeio form:")
        for field in ["instituicao", "instrumento", "subprojeto", "ta", "pta", "acao", "resultado", "meta"]:
            try:
                widget = form.form_custeio.campos[field]["widget"]
                value = widget.get()
                print(f"  {field}: '{value}'")
            except Exception as e:
                print(f"  Error getting {field}: {e}")
        
        # Clean up
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    test_form_loading_no_gui()
