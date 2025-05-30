from models.db_manager import get_connection

def adicionar_evento(codigo_demanda, instituicao, instrumento, subprojeto, ta, pta, acao, resultado, meta,
                   titulo_evento, fornecedor, observacao, valor_estimado, total_contrato):
    """Adiciona um novo evento
    
    Returns:
        int: ID do evento inserido
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO eventos (codigo_demanda, instituicao, instrumento, subprojeto, ta, pta, acao, resultado, meta,
                       titulo_evento, fornecedor, observacao, valor_estimado, total_contrato)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (codigo_demanda, instituicao, instrumento, subprojeto, ta, pta, acao, resultado, meta,
          titulo_evento, fornecedor, observacao, valor_estimado, total_contrato))
    
    # Obter o ID do evento inserido
    evento_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return evento_id

def listar_eventos():
    """Retorna todos os eventos cadastrados"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eventos ORDER BY id DESC")
    eventos = cursor.fetchall()
    conn.close()
    return eventos

def obter_eventos_por_demanda(codigo_demanda):
    """Retorna todos os eventos de uma demanda específica"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eventos WHERE codigo_demanda = ? ORDER BY id DESC", (codigo_demanda,))
    eventos = cursor.fetchall()
    conn.close()
    return eventos

def editar_evento(id_evento, codigo_demanda, instituicao, instrumento, subprojeto, ta, pta, acao, resultado, meta,
                titulo_evento, fornecedor, observacao, valor_estimado, total_contrato):
    """Edita um evento existente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    UPDATE eventos SET 
        codigo_demanda = ?, instituicao = ?, instrumento = ?, subprojeto = ?, ta = ?, pta = ?, acao = ?, resultado = ?, meta = ?,
        titulo_evento = ?, fornecedor = ?, observacao = ?, valor_estimado = ?, total_contrato = ?
    WHERE id = ?
    """, (codigo_demanda, instituicao, instrumento, subprojeto, ta, pta, acao, resultado, meta,
          titulo_evento, fornecedor, observacao, valor_estimado, total_contrato, id_evento))
    
    conn.commit()
    conn.close()

def atualizar_valor_total_contrato(id_evento, novo_valor_total):
    """Atualiza apenas o valor total do contrato de um evento específico"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    UPDATE eventos SET total_contrato = ? WHERE id = ?
    """, (novo_valor_total, id_evento))
    
    conn.commit()
    conn.close()

def obter_valor_total_contrato(id_evento):
    """Obtém o valor total atual do contrato de um evento específico"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT total_contrato FROM eventos WHERE id = ?", (id_evento,))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return float(resultado[0]) if resultado[0] else 0.0
    return 0.0

def excluir_evento(id_evento):
    """Exclui um evento pelo ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM eventos WHERE id = ?", (id_evento,))
    conn.commit()
    conn.close()
