# models/carta_acordo_model.py
from .db_manager import get_connection

def create_carta_acordo(**kwargs):
    """
    Cria uma nova carta acordo
    
    Returns:
        int: ID da carta acordo inserida
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO carta_acordo (
            codigo_demanda, instituicao, instrumento, subprojeto, ta, pta, acao, resultado, meta,
            contrato, vigencia_inicial, vigencia_final, instituicao_2, cnpj, titulo_projeto, objetivo,
            valor_estimado, total_contrato, observacoes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        kwargs['codigo_demanda'], kwargs['instituicao'], kwargs['instrumento'], kwargs['subprojeto'],
        kwargs['ta'], kwargs['pta'], kwargs['acao'], kwargs['resultado'], kwargs['meta'], kwargs['contrato'],
        kwargs['vigencia_inicial'], kwargs['vigencia_final'], kwargs['instituicao_2'], kwargs['cnpj'],
        kwargs['titulo_projeto'], kwargs['objetivo'], kwargs['valor_estimado'], kwargs['total_contrato'],
        kwargs['observacoes']
    ))
    
    # Obter o ID da carta acordo inserida
    carta_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return carta_id

def get_all_cartas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM carta_acordo")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_carta_acordo(id_carta, **kwargs):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE carta_acordo SET
            codigo_demanda=?, instituicao=?, instrumento=?, subprojeto=?, ta=?, pta=?, acao=?, resultado=?, meta=?,
            contrato=?, vigencia_inicial=?, vigencia_final=?, instituicao_2=?, cnpj=?, titulo_projeto=?, objetivo=?,
            valor_estimado=?, total_contrato=?, observacoes=?
        WHERE id=?
    """, (
        kwargs['codigo_demanda'], kwargs['instituicao'], kwargs['instrumento'], kwargs['subprojeto'],
        kwargs['ta'], kwargs['pta'], kwargs['acao'], kwargs['resultado'], kwargs['meta'], kwargs['contrato'],
        kwargs['vigencia_inicial'], kwargs['vigencia_final'], kwargs['instituicao_2'], kwargs['cnpj'],
        kwargs['titulo_projeto'], kwargs['objetivo'], kwargs['valor_estimado'], kwargs['total_contrato'],
        kwargs['observacoes'], id_carta
    ))
    conn.commit()
    conn.close()

def delete_carta_acordo(id_carta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carta_acordo WHERE id=?", (id_carta,))
    conn.commit()
    conn.close()
