from models.db_manager import get_connection

def adicionar_produto_servico(codigo_demanda, fornecedor, modalidade, objetivo, 
                           vigencia_inicial, vigencia_final, observacao, valor_estimado, total_contrato,
                           instituicao=None, instrumento=None, subprojeto=None, ta=None, pta=None, 
                           acao=None, resultado=None, meta=None):
    """Adiciona um novo produto/serviço
    
    Returns:
        int: ID do produto/serviço inserido
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO produtos_servicos (codigo_demanda, fornecedor, modalidade, objetivo,
                               vigencia_inicial, vigencia_final, observacao, valor_estimado, total_contrato,
                               instituicao, instrumento, subprojeto, ta, pta, acao, resultado, meta)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (codigo_demanda, fornecedor, modalidade, objetivo, 
         vigencia_inicial, vigencia_final, observacao, valor_estimado, total_contrato,
         instituicao, instrumento, subprojeto, ta, pta, acao, resultado, meta))
    
    # Obter o ID do produto/serviço inserido
    produto_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return produto_id

def listar_produtos_servicos():
    """Retorna todos os produtos/serviços cadastrados"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos_servicos ORDER BY id DESC")
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def obter_produtos_por_demanda(codigo_demanda):
    """Retorna todos os produtos/serviços de uma demanda específica"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos_servicos WHERE codigo_demanda = ? ORDER BY id DESC", (codigo_demanda,))
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def editar_produto_servico(id_produto, codigo_demanda, fornecedor, modalidade, objetivo, 
                        vigencia_inicial, vigencia_final, observacao, valor_estimado, total_contrato,
                        instituicao=None, instrumento=None, subprojeto=None, ta=None, pta=None, 
                        acao=None, resultado=None, meta=None):
    """Edita um produto/serviço existente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    UPDATE produtos_servicos SET 
        codigo_demanda = ?, fornecedor = ?, modalidade = ?, objetivo = ?,
        vigencia_inicial = ?, vigencia_final = ?, observacao = ?, valor_estimado = ?, total_contrato = ?,
        instituicao = ?, instrumento = ?, subprojeto = ?, ta = ?, pta = ?, acao = ?, resultado = ?, meta = ?
    WHERE id = ?
    """, (codigo_demanda, fornecedor, modalidade, objetivo, 
         vigencia_inicial, vigencia_final, observacao, valor_estimado, total_contrato,
         instituicao, instrumento, subprojeto, ta, pta, acao, resultado, meta, id_produto))
    
    conn.commit()
    conn.close()

def excluir_produto_servico(id_produto):
    """Exclui um produto/serviço pelo ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos_servicos WHERE id = ?", (id_produto,))
    conn.commit()
    conn.close()
