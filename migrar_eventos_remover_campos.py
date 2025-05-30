#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para migrar a tabela eventos, removendo campos desnecessários:
- modalidade
- vigencia_inicial  
- vigencia_final
"""

import sqlite3
import os

def migrar_tabela_eventos():
    """Remove campos desnecessários da tabela eventos"""
    
    # Caminho do banco de dados
    db_path = 'contrato.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return
    
    # Fazer backup
    backup_path = 'contrato_backup_remover_campos.db'
    os.system(f'copy "{db_path}" "{backup_path}"')
    print(f"✅ Backup criado: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔄 Iniciando migração da tabela eventos...")
        
        # 1. Verificar se a tabela eventos existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eventos'")
        if not cursor.fetchone():
            print("❌ Tabela eventos não encontrada!")
            return
        
        # 2. Verificar colunas atuais
        cursor.execute("PRAGMA table_info(eventos)")
        colunas_atuais = [col[1] for col in cursor.fetchall()]
        print(f"📋 Colunas atuais: {colunas_atuais}")
        
        # 3. Criar nova tabela eventos sem os campos removidos
        cursor.execute("""
            CREATE TABLE eventos_nova (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_demanda INTEGER,
                instituicao TEXT, 
                instrumento TEXT, 
                subprojeto TEXT, 
                ta TEXT, 
                pta TEXT, 
                acao TEXT,
                resultado TEXT, 
                meta TEXT,
                titulo_evento TEXT, 
                fornecedor TEXT, 
                objetivo TEXT,
                observacao TEXT, 
                valor_estimado REAL, 
                total_contrato REAL,
                FOREIGN KEY (codigo_demanda) REFERENCES demanda(codigo)
            )
        """)
        print("✅ Nova tabela criada")
        
        # 4. Copiar dados da tabela antiga para a nova (excluindo campos removidos)
        cursor.execute("""
            INSERT INTO eventos_nova (
                id, codigo_demanda, instituicao, instrumento, subprojeto, ta, pta, acao,
                resultado, meta, titulo_evento, fornecedor, objetivo, observacao, 
                valor_estimado, total_contrato
            )
            SELECT 
                id, codigo_demanda, instituicao, instrumento, subprojeto, ta, pta, acao,
                resultado, meta, titulo_evento, fornecedor, objetivo, observacao, 
                valor_estimado, total_contrato
            FROM eventos
        """)
        
        registros_copiados = cursor.rowcount
        print(f"✅ {registros_copiados} registros copiados")
        
        # 5. Renomear tabelas
        cursor.execute("DROP TABLE eventos")
        cursor.execute("ALTER TABLE eventos_nova RENAME TO eventos")
        print("✅ Tabela renomeada")
        
        # 6. Verificar resultado
        cursor.execute("PRAGMA table_info(eventos)")
        novas_colunas = [col[1] for col in cursor.fetchall()]
        print(f"📋 Novas colunas: {novas_colunas}")
        
        cursor.execute("SELECT COUNT(*) FROM eventos")
        total_registros = cursor.fetchone()[0]
        print(f"📊 Total de registros na nova tabela: {total_registros}")
        
        conn.commit()
        print("✅ Migração concluída com sucesso!")
        
        # Listar campos removidos
        campos_removidos = ['modalidade', 'vigencia_inicial', 'vigencia_final']
        print(f"🗑️  Campos removidos: {campos_removidos}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro durante a migração: {e}")
        print("🔄 Restaurando backup...")
        conn.close()
        os.system(f'copy "{backup_path}" "{db_path}"')
        print("✅ Backup restaurado")
        return
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Script de Migração - Remoção de Campos da Tabela Eventos")
    print("=" * 60)
    
    resposta = input("⚠️  Continuar com a migração? (s/n): ").lower()
    if resposta == 's':
        migrar_tabela_eventos()
    else:
        print("❌ Migração cancelada pelo usuário") 