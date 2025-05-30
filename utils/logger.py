# utils/logger.py
from models.db_manager import get_connection

def log_action(usuario, acao):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (usuario, acao) VALUES (?, ?)", (usuario, acao))
    conn.commit()
    conn.close()
