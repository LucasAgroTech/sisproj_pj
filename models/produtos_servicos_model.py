# models/produtos_servicos_model.py
from .db_manager import get_connection

def create_produto_servico(**kwargs):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO produtos_servicos (
            codigo_demanda, fornecedor, modalidade, objetivo, vigencia_inicial, vigencia_final,
            observacao, valor_estimado, total_contrato, instituicao, instrumento, subprojeto,
            ta, pta, acao, resultado, meta
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        kwargs['codigo_demanda'], kwargs['fornecedor'], kwargs['modalidade'], kwargs['objetivo'],
        kwargs['vigencia_inicial'], kwargs['vigencia_final'], kwargs['observacao'],
        kwargs['valor_estimado'], kwargs['total_contrato'], kwargs.get('instituicao', ''),
        kwargs.get('instrumento', ''), kwargs.get('subprojeto', ''), kwargs.get('ta', ''),
        kwargs.get('pta', ''), kwargs.get('acao', ''), kwargs.get('resultado', ''),
        kwargs.get('meta', '')
    ))
    conn.commit()
    conn.close()

def get_all_produtos_servicos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos_servicos")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_produto_servico(id_prod, **kwargs):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE produtos_servicos SET
            codigo_demanda=?, fornecedor=?, modalidade=?, objetivo=?, vigencia_inicial=?,
            vigencia_final=?, observacao=?, valor_estimado=?, total_contrato=?, instituicao=?,
            instrumento=?, subprojeto=?, ta=?, pta=?, acao=?, resultado=?, meta=?
        WHERE id=?
    """, (
        kwargs['codigo_demanda'], kwargs['fornecedor'], kwargs['modalidade'], kwargs['objetivo'],
        kwargs['vigencia_inicial'], kwargs['vigencia_final'], kwargs['observacao'],
        kwargs['valor_estimado'], kwargs['total_contrato'], kwargs.get('instituicao', ''),
        kwargs.get('instrumento', ''), kwargs.get('subprojeto', ''), kwargs.get('ta', ''),
        kwargs.get('pta', ''), kwargs.get('acao', ''), kwargs.get('resultado', ''),
        kwargs.get('meta', ''), id_prod
    ))
    conn.commit()
    conn.close()

def delete_produto_servico(id_prod):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos_servicos WHERE id=?", (id_prod,))
    conn.commit()
    conn.close()
