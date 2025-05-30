from models.db_manager import get_connection

def adicionar_fornecedor(razao_social, cnpj, observacao):
    """Adiciona um novo fornecedor
    
    Returns:
        int: ID do fornecedor inserido
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO fornecedores (razao_social, cnpj, observacao)
    VALUES (?, ?, ?)
    """, (razao_social, cnpj, observacao))
    
    # Obter o ID do fornecedor inserido
    fornecedor_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return fornecedor_id

def listar_fornecedores():
    """Retorna todos os fornecedores cadastrados"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fornecedores ORDER BY razao_social")
    fornecedores = cursor.fetchall()
    conn.close()
    return fornecedores

def buscar_fornecedor_por_nome(razao_social):
    """Busca um fornecedor pelo nome
    
    Returns:
        tuple: Dados do fornecedor ou None se não encontrado
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fornecedores WHERE razao_social = ?", (razao_social,))
    fornecedor = cursor.fetchone()
    conn.close()
    return fornecedor

def editar_fornecedor(id_fornecedor, razao_social, cnpj, observacao):
    """Edita um fornecedor existente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    UPDATE fornecedores SET 
        razao_social = ?, cnpj = ?, observacao = ?
    WHERE id = ?
    """, (razao_social, cnpj, observacao, id_fornecedor))
    
    conn.commit()
    conn.close()

def excluir_fornecedor(id_fornecedor):
    """Exclui um fornecedor pelo ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fornecedores WHERE id = ?", (id_fornecedor,))
    conn.commit()
    conn.close()
