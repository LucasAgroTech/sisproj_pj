import sqlite3
from typing import List, Dict, Any, Optional, Tuple

class CusteioManager:
    """
    Utility class to manage hierarchical selection and filtering for the custeio table.
    The hierarchy follows: instituicao_parceira -> cod_projeto -> cod_ta -> resultado -> subprojeto
    """
    
    def __init__(self, db_path: str = 'contrato.db'):
        """Initialize the CusteioManager with the database path."""
        self.db_path = db_path
    
    def _get_connection(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        """Create and return a connection to the database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        return conn, cursor
    
    def get_distinct_values(self, field: str, filters: Optional[Dict[str, str]] = None) -> List[str]:
        """
        Get distinct values for a specific field, optionally filtered by previous selections.
        
        Args:
            field: The field to get distinct values for
            filters: Dictionary of field-value pairs to filter by
            
        Returns:
            List of distinct values for the specified field
        """
        conn, cursor = self._get_connection()
        
        try:
            query = f"SELECT DISTINCT {field} FROM custeio WHERE {field} != ''"
            params = []
            
            # Add filters if provided
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    filter_conditions.append(f"{key} = ?")
                    params.append(value)
                
                if filter_conditions:
                    query += " AND " + " AND ".join(filter_conditions)
            
            query += f" ORDER BY {field}"
            cursor.execute(query, params)
            
            # Extract values from the result
            result = [row[0] for row in cursor.fetchall()]
            return result
            
        finally:
            conn.close()
    
    def get_hierarchical_options(self) -> Dict[str, List[str]]:
        """
        Get all distinct values for each level of the hierarchy.
        
        Returns:
            Dictionary with field names as keys and lists of distinct values as values
        """
        fields = ['instituicao_parceira', 'cod_projeto', 'cod_ta', 'resultado', 'subprojeto']
        result = {}
        
        for field in fields:
            result[field] = self.get_distinct_values(field)
        
        return result
    
    def filter_by_selection(self, filters: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Get filtered data based on the provided selections.
        
        Args:
            filters: Dictionary of field-value pairs to filter by
            
        Returns:
            List of dictionaries containing the filtered data
        """
        conn, cursor = self._get_connection()
        
        try:
            query = "SELECT * FROM custeio"
            params = []
            
            # Add filters if provided
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    if value:  # Only add non-empty filters
                        filter_conditions.append(f"{key} = ?")
                        params.append(value)
                
                if filter_conditions:
                    query += " WHERE " + " AND ".join(filter_conditions)
            
            cursor.execute(query, params)
            
            # Convert the result to a list of dictionaries
            columns = [column[0] for column in cursor.description]
            result = []
            
            for row in cursor.fetchall():
                result.append(dict(zip(columns, row)))
            
            return result
            
        finally:
            conn.close()
    
    def get_next_level_options(self, current_level: str, filters: Dict[str, str]) -> List[str]:
        """
        Get options for the next level in the hierarchy based on current selections.
        
        Args:
            current_level: The current level in the hierarchy
            filters: Dictionary of field-value pairs representing current selections
            
        Returns:
            List of options for the next level
        """
        hierarchy = ['instituicao_parceira', 'cod_projeto', 'cod_ta', 'resultado', 'subprojeto']
        
        # Find the current level index
        try:
            current_index = hierarchy.index(current_level)
        except ValueError:
            return []
        
        # Check if there's a next level
        if current_index >= len(hierarchy) - 1:
            return []
        
        next_level = hierarchy[current_index + 1]
        return self.get_distinct_values(next_level, filters)


# Example usage
def example_usage():
    """Demonstrate how to use the CusteioManager class."""
    manager = CusteioManager()
    
    print("Hierarchical Options:")
    options = manager.get_hierarchical_options()
    for field, values in options.items():
        print(f"{field}: {values[:5]}{'...' if len(values) > 5 else ''}")
    
    print("\nCascading Selection Example:")
    # Get all institutions
    institutions = manager.get_distinct_values('instituicao_parceira')
    print(f"Available institutions: {institutions}")
    
    # Select an institution
    selected_institution = institutions[0]
    print(f"\nSelected institution: {selected_institution}")
    
    # Get projects for the selected institution
    projects = manager.get_distinct_values('cod_projeto', {'instituicao_parceira': selected_institution})
    print(f"Available projects for {selected_institution}: {projects}")
    
    # Select a project
    if projects:
        selected_project = projects[0]
        print(f"\nSelected project: {selected_project}")
        
        # Get TAs for the selected project
        tas = manager.get_distinct_values('cod_ta', {
            'instituicao_parceira': selected_institution,
            'cod_projeto': selected_project
        })
        print(f"Available TAs for {selected_project}: {tas}")
        
        # Continue with the hierarchy...
        if tas:
            selected_ta = tas[0]
            print(f"\nSelected TA: {selected_ta}")
            
            # Get results for the selected TA
            results = manager.get_distinct_values('resultado', {
                'instituicao_parceira': selected_institution,
                'cod_projeto': selected_project,
                'cod_ta': selected_ta
            })
            print(f"Available results for {selected_ta}: {results}")
    
    print("\nFiltering Example:")
    # Filter by institution and project
    filters = {
        'instituicao_parceira': selected_institution,
        'cod_projeto': selected_project
    }
    filtered_data = manager.filter_by_selection(filters)
    print(f"Found {len(filtered_data)} records matching the filters")
    
    # Display a few records
    for i, record in enumerate(filtered_data[:3]):
        print(f"Record {i+1}: {record}")


if __name__ == "__main__":
    example_usage()
