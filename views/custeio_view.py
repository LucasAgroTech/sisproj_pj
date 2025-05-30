import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any, Optional, Callable

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controllers.custeio_controller import CusteioController
from utils.ui_utils import Estilos, Cores, criar_botao


class CusteioView:
    """
    View class for the Custeio module.
    Provides a UI for hierarchical selection and filtering of custeio data.
    """
    
    def __init__(self, root=None):
        """
        Initialize the CusteioView.
        
        Args:
            root: The root Tkinter window (optional)
        """
        self.controller = CusteioController()
        
        # Create a new window if root is not provided
        if root is None:
            self.root = tk.Tk()
            self.root.title("Custeio - Seleção Hierárquica")
            self.root.geometry("800x600")
            # Center window
            window_width = 800
            window_height = 600
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x_cordinate = int((screen_width/2) - (window_width/2))
            y_cordinate = int((screen_height/2) - (window_height/2))
            self.root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")
        else:
            self.root = root
            
        self.create_widgets()
        self.load_initial_data()
    
    def create_widgets(self):
        """Create the UI widgets."""
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Seleção Hierárquica de Custeio", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Selection frame
        selection_frame = ttk.LabelFrame(self.main_frame, text="Filtros", padding="10")
        selection_frame.pack(fill=tk.X, pady=10)
        
        # Create comboboxes for each level of the hierarchy
        self.create_selection_widgets(selection_frame)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.main_frame, text="Resultados", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create a treeview for displaying results
        self.create_results_treeview(results_frame)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Apply filter button
        apply_button = ttk.Button(buttons_frame, text="Aplicar Filtros", command=self.apply_filters)
        apply_button.pack(side=tk.RIGHT, padx=5)
        
        # Clear filters button
        clear_button = ttk.Button(buttons_frame, text="Limpar Filtros", command=self.clear_filters)
        clear_button.pack(side=tk.RIGHT, padx=5)
    
    def create_selection_widgets(self, parent):
        """
        Create the selection widgets for each level of the hierarchy.
        
        Args:
            parent: The parent widget
        """
        # Create a frame with a grid layout
        grid_frame = ttk.Frame(parent)
        grid_frame.pack(fill=tk.X, pady=5)
        
        # Institution selection
        ttk.Label(grid_frame, text="Instituição:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.institution_var = tk.StringVar()
        self.institution_combo = ttk.Combobox(grid_frame, textvariable=self.institution_var, state="readonly", width=30)
        self.institution_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.institution_combo.bind("<<ComboboxSelected>>", self.on_institution_selected)
        
        # Project selection
        ttk.Label(grid_frame, text="Projeto:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.project_var = tk.StringVar()
        self.project_combo = ttk.Combobox(grid_frame, textvariable=self.project_var, state="readonly", width=30)
        self.project_combo.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        self.project_combo.bind("<<ComboboxSelected>>", self.on_project_selected)
        
        # TA selection
        ttk.Label(grid_frame, text="TA:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.ta_var = tk.StringVar()
        self.ta_combo = ttk.Combobox(grid_frame, textvariable=self.ta_var, state="readonly", width=30)
        self.ta_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.ta_combo.bind("<<ComboboxSelected>>", self.on_ta_selected)
        
        # Result selection
        ttk.Label(grid_frame, text="Resultado:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.result_var = tk.StringVar()
        self.result_combo = ttk.Combobox(grid_frame, textvariable=self.result_var, state="readonly", width=30)
        self.result_combo.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        self.result_combo.bind("<<ComboboxSelected>>", self.on_result_selected)
        
        # Subproject selection
        ttk.Label(grid_frame, text="Subprojeto:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.subproject_var = tk.StringVar()
        self.subproject_combo = ttk.Combobox(grid_frame, textvariable=self.subproject_var, state="readonly", width=30)
        self.subproject_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
    
    def create_results_treeview(self, parent):
        """
        Create a treeview for displaying results.
        
        Args:
            parent: The parent widget
        """
        # Create a frame with a scrollbar
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("id", "instituicao_parceira", "cod_projeto", "cod_ta", "resultado", "subprojeto")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        
        # Configure scrollbar
        scrollbar.config(command=self.tree.yview)
        
        # Configure column headings
        self.tree.heading("id", text="ID")
        self.tree.heading("instituicao_parceira", text="Instituição")
        self.tree.heading("cod_projeto", text="Projeto")
        self.tree.heading("cod_ta", text="TA")
        self.tree.heading("resultado", text="Resultado")
        self.tree.heading("subprojeto", text="Subprojeto")
        
        # Configure column widths
        self.tree.column("id", width=50)
        self.tree.column("instituicao_parceira", width=150)
        self.tree.column("cod_projeto", width=150)
        self.tree.column("cod_ta", width=100)
        self.tree.column("resultado", width=150)
        self.tree.column("subprojeto", width=150)
        
        # Pack the treeview
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def load_initial_data(self):
        """Load the initial data for the comboboxes."""
        # Load institutions
        institutions = self.controller.get_institutions()
        self.institution_combo["values"] = [""] + institutions
        
        # Load projects
        projects = self.controller.get_projects()
        self.project_combo["values"] = [""] + projects
        
        # Load TAs
        tas = self.controller.get_tas()
        self.ta_combo["values"] = [""] + tas
        
        # Load results
        results = self.controller.get_results()
        self.result_combo["values"] = [""] + results
        
        # Load subprojects
        subprojects = self.controller.get_subprojects()
        self.subproject_combo["values"] = [""] + subprojects
    
    def on_institution_selected(self, event=None):
        """Handle institution selection event."""
        institution = self.institution_var.get()
        
        # Update projects
        projects = self.controller.get_projects(institution if institution else None)
        self.project_combo["values"] = [""] + projects
        self.project_var.set("")
        
        # Update TAs
        self.on_project_selected()
    
    def on_project_selected(self, event=None):
        """Handle project selection event."""
        institution = self.institution_var.get()
        project = self.project_var.get()
        
        # Update TAs
        tas = self.controller.get_tas(
            institution if institution else None,
            project if project else None
        )
        self.ta_combo["values"] = [""] + tas
        self.ta_var.set("")
        
        # Update results
        self.on_ta_selected()
    
    def on_ta_selected(self, event=None):
        """Handle TA selection event."""
        institution = self.institution_var.get()
        project = self.project_var.get()
        ta = self.ta_var.get()
        
        # Update results
        results = self.controller.get_results(
            institution if institution else None,
            project if project else None,
            ta if ta else None
        )
        self.result_combo["values"] = [""] + results
        self.result_var.set("")
        
        # Update subprojects
        self.on_result_selected()
    
    def on_result_selected(self, event=None):
        """Handle result selection event."""
        institution = self.institution_var.get()
        project = self.project_var.get()
        ta = self.ta_var.get()
        result = self.result_var.get()
        
        # Update subprojects
        subprojects = self.controller.get_subprojects(
            institution if institution else None,
            project if project else None,
            ta if ta else None,
            result if result else None
        )
        self.subproject_combo["values"] = [""] + subprojects
        self.subproject_var.set("")
    
    def apply_filters(self):
        """Apply the selected filters and update the results."""
        # Get the selected values
        filters = {
            "instituicao_parceira": self.institution_var.get(),
            "cod_projeto": self.project_var.get(),
            "cod_ta": self.ta_var.get(),
            "resultado": self.result_var.get(),
            "subprojeto": self.subproject_var.get()
        }
        
        # Filter the data
        filtered_data = self.controller.filter_custeio(filters)
        
        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Populate the treeview with the filtered data
        for record in filtered_data:
            self.tree.insert("", tk.END, values=(
                record["id"],
                record["instituicao_parceira"],
                record["cod_projeto"],
                record["cod_ta"],
                record["resultado"],
                record["subprojeto"]
            ))
        
        # Show a message if no records were found
        if not filtered_data:
            messagebox.showinfo("Informação", "Nenhum registro encontrado com os filtros selecionados.")
    
    def clear_filters(self):
        """Clear all filters."""
        self.institution_var.set("")
        self.project_var.set("")
        self.ta_var.set("")
        self.result_var.set("")
        self.subproject_var.set("")
        
        # Reset combobox values
        self.load_initial_data()
        
        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


# Example usage
if __name__ == "__main__":
    view = CusteioView()
    view.run()
