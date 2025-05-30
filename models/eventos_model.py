# models/eventos_model.py
from .db_manager import get_connection

def create_evento(**kwargs):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO eventos (
            codigo_demanda, instituicao, instrumento, subprojeto, ta, pta, acao, resultado, meta,
            titulo_evento, fornecedor, observacao, valor_estimado, total_contrato
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        kwargs['codigo_demanda'], kwargs['instituicao'], kwargs['instrumento'], kwargs['subprojeto'],
        kwargs['ta'], kwargs['pta'], kwargs['acao'], kwargs['resultado'], kwargs['meta'],
        kwargs['titulo_evento'], kwargs['fornecedor'], kwargs['observacao'],
        kwargs['valor_estimado'], kwargs['total_contrato']
    ))
    conn.commit()
    conn.close()

def get_all_eventos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eventos")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_evento(id_evento, **kwargs):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE eventos SET
            codigo_demanda=?, instituicao=?, instrumento=?, subprojeto=?, ta=?, pta=?, acao=?, resultado=?, meta=?,
            titulo_evento=?, fornecedor=?, observacao=?, valor_estimado=?, total_contrato=?
        WHERE id=?
    """, (
        kwargs['codigo_demanda'], kwargs['instituicao'], kwargs['instrumento'], kwargs['subprojeto'],
        kwargs['ta'], kwargs['pta'], kwargs['acao'], kwargs['resultado'], kwargs['meta'],
        kwargs['titulo_evento'], kwargs['fornecedor'], kwargs['observacao'],
        kwargs['valor_estimado'], kwargs['total_contrato'], id_evento
    ))
    conn.commit()
    conn.close()

def delete_evento(id_evento):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM eventos WHERE id=?", (id_evento,))
    conn.commit()
    conn.close()
