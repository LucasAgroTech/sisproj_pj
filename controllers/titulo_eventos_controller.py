from models.db_manager import get_connection

def adicionar_titulo_evento(titulo, cidade, estado, data_inicio, data_fim):
    """Adiciona um novo título de evento
    
    Returns:
        int: ID do título de evento inserido
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO titulo_eventos (titulo, cidade, estado, data_inicio, data_fim)
    VALUES (?, ?, ?, ?, ?)
    """, (titulo, cidade, estado, data_inicio, data_fim))
    
    # Obter o ID do título de evento inserido
    titulo_evento_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return titulo_evento_id

def listar_titulos_eventos():
    """Retorna todos os títulos de eventos cadastrados"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM titulo_eventos ORDER BY titulo")
    titulos_eventos = cursor.fetchall()
    conn.close()
    return titulos_eventos

def buscar_titulo_evento_por_nome(titulo):
    """Busca um título de evento pelo nome
    
    Returns:
        tuple: Dados do título de evento ou None se não encontrado
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM titulo_eventos WHERE titulo = ?", (titulo,))
    titulo_evento = cursor.fetchone()
    conn.close()
    return titulo_evento

def editar_titulo_evento(id_titulo_evento, titulo, cidade, estado, data_inicio, data_fim):
    """Edita um título de evento existente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    UPDATE titulo_eventos SET 
        titulo = ?, cidade = ?, estado = ?, data_inicio = ?, data_fim = ?
    WHERE id = ?
    """, (titulo, cidade, estado, data_inicio, data_fim, id_titulo_evento))
    
    conn.commit()
    conn.close()

def excluir_titulo_evento(id_titulo_evento):
    """Exclui um título de evento pelo ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM titulo_eventos WHERE id = ?", (id_titulo_evento,))
    conn.commit()
    conn.close()
