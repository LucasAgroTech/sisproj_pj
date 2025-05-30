import sqlite3

def migrar_eventos():
    conn = sqlite3.connect('contrato.db')
    cursor = conn.cursor()
    
    try:
        print("Iniciando migração de eventos...")
        
        # 1. Verificar se a tabela eventos atual tem os novos campos
        cursor.execute("PRAGMA table_info(eventos)")
        colunas_eventos = [col[1] for col in cursor.fetchall()]
        
        # Verificar se os campos de custeio já existem
        campos_custeio = ['instituicao', 'instrumento', 'subprojeto', 'ta', 'pta', 'acao', 'resultado', 'meta']
        tem_campos_custeio = all(campo in colunas_eventos for campo in campos_custeio)
        
        if not tem_campos_custeio:
            print("Adicionando colunas de custeio à tabela eventos...")
            
            # Adicionar colunas de custeio à tabela eventos
            for campo in campos_custeio:
                try:
                    cursor.execute(f"ALTER TABLE eventos ADD COLUMN {campo} TEXT")
                    print(f"- Coluna {campo} adicionada")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e):
                        raise e
                    print(f"- Coluna {campo} já existe")
        
        # 2. Verificar se existe tabela evento_custeio
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='evento_custeio'")
        tabela_existe = cursor.fetchone()
        
        if tabela_existe:
            print("Migrando dados da tabela evento_custeio...")
            
            # Buscar todos os dados de evento_custeio
            cursor.execute("SELECT * FROM evento_custeio")
            dados_custeio = cursor.fetchall()
            
            print(f"Encontrados {len(dados_custeio)} registros de custeio para migrar")
            
            # Para cada registro de custeio, atualizar o evento correspondente
            for custeio in dados_custeio:
                id_custeio, id_evento, instituicao, instrumento, subprojeto, ta, pta, acao, resultado, meta = custeio
                
                # Atualizar o evento com os dados de custeio
                cursor.execute("""
                    UPDATE eventos SET 
                        instituicao = ?, instrumento = ?, subprojeto = ?, ta = ?, 
                        pta = ?, acao = ?, resultado = ?, meta = ?
                    WHERE id = ?
                """, (instituicao, instrumento, subprojeto, ta, pta, acao, resultado, meta, id_evento))
                
                print(f"- Evento {id_evento} atualizado com dados de custeio")
            
            # 3. Excluir a tabela evento_custeio
            print("Excluindo tabela evento_custeio...")
            cursor.execute("DROP TABLE evento_custeio")
            print("- Tabela evento_custeio excluída")
        
        conn.commit()
        print("Migração concluída com sucesso!")
        
        # Verificar resultado
        cursor.execute("SELECT id, codigo_demanda, instituicao, instrumento, titulo_evento, fornecedor FROM eventos WHERE instituicao IS NOT NULL")
        eventos_migrados = cursor.fetchall()
        print(f"Total de eventos com dados de custeio: {len(eventos_migrados)}")
        for evento in eventos_migrados:
            print(f"- Evento {evento[0]} (Demanda {evento[1]}): {evento[2]} - {evento[3]} | {evento[4]} | {evento[5]}")
        
    except Exception as e:
        print(f"Erro durante a migração: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    migrar_eventos() 