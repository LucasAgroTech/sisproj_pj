# models/aditivos_model.py
from .db_manager import get_connection

def create_aditivo(**kwargs):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO aditivos (
            id_contrato, tipo_contrato, tipo_aditivo, descricao,
            valor_aditivo, nova_vigencia_final, data_registro
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        kwargs['id_contrato'], kwargs['tipo_contrato'], kwargs['tipo_aditivo'], kwargs['descricao'],
        kwargs['valor_aditivo'], kwargs['nova_vigencia_final'], kwargs['data_registro']
    ))
    conn.commit()
    conn.close()

def get_all_aditivos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM aditivos")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_aditivo(id_aditivo, **kwargs):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE aditivos SET
            id_contrato=?, tipo_contrato=?, tipo_aditivo=?, descricao=?,
            valor_aditivo=?, nova_vigencia_final=?, data_registro=?
        WHERE id=?
    """, (
        kwargs['id_contrato'], kwargs['tipo_contrato'], kwargs['tipo_aditivo'], kwargs['descricao'],
        kwargs['valor_aditivo'], kwargs['nova_vigencia_final'], kwargs['data_registro'], id_aditivo
    ))
    conn.commit()
    conn.close()

def delete_aditivo(id_aditivo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM aditivos WHERE id=?", (id_aditivo,))
    conn.commit()
    conn.close()
