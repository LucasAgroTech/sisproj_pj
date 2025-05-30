# models/demanda_model.py
from .db_manager import get_connection

def create_demanda(data_entrada, solicitante, data_protocolo, oficio, nup_sei, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO demanda (data_entrada, solicitante, data_protocolo, oficio, nup_sei, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data_entrada, solicitante, data_protocolo, oficio, nup_sei, status))
    conn.commit()
    conn.close()

def get_all_demandas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM demanda")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_demanda(codigo, data_entrada, solicitante, data_protocolo, oficio, nup_sei, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE demanda SET data_entrada=?, solicitante=?, data_protocolo=?, oficio=?, nup_sei=?, status=?
        WHERE codigo=?
    """, (data_entrada, solicitante, data_protocolo, oficio, nup_sei, status, codigo))
    conn.commit()
    conn.close()

def delete_demanda(codigo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM demanda WHERE codigo=?", (codigo,))
    conn.commit()
    conn.close()
