import sqlite3
from datetime import datetime

def adicionar_contrato(tipo_contrato, id_referencia, numero_contrato, data_assinatura, observacoes=""):
    """
    Adiciona um novo contrato associado a uma carta acordo, produto/serviço ou evento
    
    Args:
        tipo_contrato: tipo do contrato ('carta_acordo', 'produtos_servicos', 'eventos')
        id_referencia: ID da carta acordo, produto/serviço ou evento
        numero_contrato: número do contrato
        data_assinatura: data de assinatura do contrato
        observacoes: observações sobre o contrato
        
    Returns:
        ID do contrato adicionado
    """
    conn = sqlite3.connect("contrato.db")
    cursor = conn.cursor()
    
    # Criação da tabela de contratos, se não existir
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contratos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_contrato TEXT, -- ('carta_acordo', 'produtos_servicos', 'eventos')
        id_referencia INTEGER, -- ID da carta acordo, produto/serviço ou evento
        numero_contrato TEXT,
        data_assinatura TEXT,
        data_registro TEXT,
        observacoes TEXT
    )
    ''')
    
    # Registrar o contrato
    data_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
    INSERT INTO contratos (tipo_contrato, id_referencia, numero_contrato, data_assinatura, data_registro, observacoes)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (tipo_contrato, id_referencia, numero_contrato, data_assinatura, data_registro, observacoes))
    
    id_contrato = cursor.lastrowid
    
    # Registrar na tabela de logs
    cursor.execute('''
    INSERT INTO logs (usuario, acao, data_hora)
    VALUES (?, ?, ?)
    ''', ("admin", f"Cadastro de Contrato {numero_contrato}", data_registro))
    
    conn.commit()
    conn.close()
    
    return id_contrato

def listar_contratos(tipo_contrato=None, id_referencia=None):
    """
    Lista todos os contratos ou filtra por tipo e/ou referência
    
    Args:
        tipo_contrato: filtrar por tipo de contrato (opcional)
        id_referencia: filtrar por ID de referência (opcional)
        
    Returns:
        Lista de contratos
    """
    conn = sqlite3.connect("contrato.db")
    cursor = conn.cursor()
    
    # Verificar se a tabela existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contratos'")
    if not cursor.fetchone():
        conn.close()
        return []
    
    # Montar a consulta
    sql = "SELECT * FROM contratos"
    params = []
    
    if tipo_contrato or id_referencia:
        sql += " WHERE"
        
        if tipo_contrato:
            sql += " tipo_contrato = ?"
            params.append(tipo_contrato)
            
        if tipo_contrato and id_referencia:
            sql += " AND"
            
        if id_referencia:
            sql += " id_referencia = ?"
            params.append(id_referencia)
    
    cursor.execute(sql, params)
    contratos = cursor.fetchall()
    
    conn.close()
    return contratos

def obter_contrato_por_referencia(tipo_contrato, id_referencia):
    """
    Obtém o contrato associado a uma carta acordo, produto/serviço ou evento
    
    Args:
        tipo_contrato: tipo do contrato ('carta_acordo', 'produtos_servicos', 'eventos')
        id_referencia: ID da carta acordo, produto/serviço ou evento
        
    Returns:
        Contrato ou None se não encontrado
    """
    conn = sqlite3.connect("contrato.db")
    cursor = conn.cursor()
    
    # Verificar se a tabela existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contratos'")
    if not cursor.fetchone():
        conn.close()
        return None
    
    cursor.execute('''
    SELECT * FROM contratos 
    WHERE tipo_contrato = ? AND id_referencia = ?
    ''', (tipo_contrato, id_referencia))
    
    contrato = cursor.fetchone()
    
    conn.close()
    return contrato

def editar_contrato(id_contrato, numero_contrato=None, data_assinatura=None, observacoes=None):
    """
    Edita um contrato existente
    
    Args:
        id_contrato: ID do contrato
        numero_contrato: novo número do contrato (opcional)
        data_assinatura: nova data de assinatura (opcional)
        observacoes: novas observações (opcional)
        
    Returns:
        True se a edição foi bem-sucedida, False caso contrário
    """
    conn = sqlite3.connect("contrato.db")
    cursor = conn.cursor()
    
    # Verificar se o contrato existe
    cursor.execute("SELECT id FROM contratos WHERE id = ?", (id_contrato,))
    if not cursor.fetchone():
        conn.close()
        return False
    
    # Coletar os campos a serem atualizados
    campos = []
    valores = []
    
    if numero_contrato is not None:
        campos.append("numero_contrato = ?")
        valores.append(numero_contrato)
        
    if data_assinatura is not None:
        campos.append("data_assinatura = ?")
        valores.append(data_assinatura)
        
    if observacoes is not None:
        campos.append("observacoes = ?")
        valores.append(observacoes)
    
    if not campos:
        conn.close()
        return False
    
    # Adicionar o ID do contrato aos valores
    valores.append(id_contrato)
    
    # Atualizar o contrato
    sql = f"UPDATE contratos SET {', '.join(campos)} WHERE id = ?"
    cursor.execute(sql, valores)
    
    # Registrar na tabela de logs
    data_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
    INSERT INTO logs (usuario, acao, data_hora)
    VALUES (?, ?, ?)
    ''', ("admin", f"Edição de Contrato ID {id_contrato}", data_registro))
    
    conn.commit()
    conn.close()
    
    return True

def excluir_contrato(id_contrato):
    """
    Exclui um contrato
    
    Args:
        id_contrato: ID do contrato
        
    Returns:
        True se a exclusão foi bem-sucedida, False caso contrário
    """
    conn = sqlite3.connect("contrato.db")
    cursor = conn.cursor()
    
    # Verificar se o contrato existe
    cursor.execute("SELECT id FROM contratos WHERE id = ?", (id_contrato,))
    if not cursor.fetchone():
        conn.close()
        return False
    
    # Excluir o contrato
    cursor.execute("DELETE FROM contratos WHERE id = ?", (id_contrato,))
    
    # Registrar na tabela de logs
    data_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
    INSERT INTO logs (usuario, acao, data_hora)
    VALUES (?, ?, ?)
    ''', ("admin", f"Exclusão de Contrato ID {id_contrato}", data_registro))
    
    conn.commit()
    conn.close()
    
    return True 