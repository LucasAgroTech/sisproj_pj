from models.aditivos_model import create_aditivo, get_all_aditivos, update_aditivo, delete_aditivo
from models.carta_acordo_model import update_carta_acordo, get_all_cartas
from utils.session import Session
from utils.logger import log_action

def adicionar_aditivo(**kwargs):
    """
    Adiciona um novo aditivo e atualiza o contrato relacionado
    
    Returns:
        int: ID do aditivo inserido
    """
    # Criar o aditivo
    create_aditivo(**kwargs)
    
    # Atualizar o contrato com a nova vigência final e valor total
    id_contrato = kwargs['id_contrato']
    tipo_contrato = kwargs.get('tipo_contrato', 'carta_acordo')
    
    if tipo_contrato == 'eventos':
        # Atualizar evento
        from controllers.eventos_controller import listar_eventos, editar_evento
        
        eventos = listar_eventos()
        evento_atual = None
        for evento in eventos:
            if evento[0] == id_contrato:
                evento_atual = evento
                break
        
        if evento_atual:
            # Calcular novo valor total do evento
            valor_atual = float(evento_atual[14]) if evento_atual[14] else 0  # total_contrato está no índice 14
            valor_aditivo = float(kwargs['valor_aditivo']) if kwargs['valor_aditivo'] else 0
            novo_valor_total = valor_atual + valor_aditivo
            
            # Atualizar o evento com o novo valor total
            editar_evento(
                id_contrato,
                codigo_demanda=evento_atual[1],
                instituicao=evento_atual[2],
                instrumento=evento_atual[3],
                subprojeto=evento_atual[4],
                ta=evento_atual[5],
                pta=evento_atual[6],
                acao=evento_atual[7],
                resultado=evento_atual[8],
                meta=evento_atual[9],
                titulo_evento=evento_atual[10],
                fornecedor=evento_atual[11],
                observacao=evento_atual[12],
                valor_estimado=evento_atual[13],
                total_contrato=novo_valor_total
            )
    else:
        # Código original para cartas de acordo
        cartas = get_all_cartas()
        carta_atual = None
        for carta in cartas:
            if carta[0] == id_contrato:
                carta_atual = carta
                break
        
        if carta_atual:
            # Atualizar a vigência final e o valor total do contrato
            valor_atual = float(carta_atual[18]) if carta_atual[18] else 0
            valor_aditivo = float(kwargs['valor_aditivo']) if kwargs['valor_aditivo'] else 0
            novo_valor_total = valor_atual + valor_aditivo
            
            # Atualizar o contrato
            update_carta_acordo(id_contrato, 
                               codigo_demanda=carta_atual[1],
                               instituicao=carta_atual[2],
                               instrumento=carta_atual[3],
                               subprojeto=carta_atual[4],
                               ta=carta_atual[5],
                               pta=carta_atual[6],
                               acao=carta_atual[7],
                               resultado=carta_atual[8],
                               meta=carta_atual[9],
                               contrato=carta_atual[10],
                               vigencia_inicial=carta_atual[11],
                               vigencia_final=kwargs['nova_vigencia_final'],
                               instituicao_2=carta_atual[13],
                               cnpj=carta_atual[14],
                               titulo_projeto=carta_atual[15],
                               objetivo=carta_atual[16],
                               valor_estimado=carta_atual[17],
                               total_contrato=novo_valor_total,
                               observacoes=carta_atual[19])
    
    usuario = Session.get_user()[1] if Session.get_user() else 'desconhecido'
    log_action(usuario, f"Cadastro de Aditivo para Contrato {id_contrato}")

def listar_aditivos():
    """
    Lista todos os aditivos
    
    Returns:
        list: Lista de aditivos
    """
    return get_all_aditivos()

def obter_aditivos_por_contrato(id_contrato, tipo_contrato="carta_acordo"):
    """
    Obtém todos os aditivos de um contrato específico
    
    Args:
        id_contrato: ID do contrato
        tipo_contrato: Tipo do contrato (padrão: carta_acordo)
        
    Returns:
        list: Lista de aditivos do contrato
    """
    aditivos = listar_aditivos()
    return [aditivo for aditivo in aditivos if aditivo[1] == id_contrato and aditivo[2] == tipo_contrato]

def editar_aditivo(id_aditivo, **kwargs):
    """
    Edita um aditivo existente e atualiza o contrato relacionado
    
    Args:
        id_aditivo: ID do aditivo a ser editado
        **kwargs: Dados do aditivo
    """
    # Verificar se é o último aditivo (somente o último pode ser editado)
    id_contrato = kwargs['id_contrato']
    tipo_contrato = kwargs.get('tipo_contrato', 'carta_acordo')
    aditivos_contrato = obter_aditivos_por_contrato(id_contrato, tipo_contrato)
    if aditivos_contrato and aditivos_contrato[-1][0] != id_aditivo:
        raise ValueError("Somente o último aditivo pode ser editado.")
        
    update_aditivo(id_aditivo, **kwargs)
    
    # Atualizar o contrato com a nova vigência final e recalcular o valor total
    
    if tipo_contrato == 'eventos':
        # Atualizar evento
        from controllers.eventos_controller import listar_eventos, editar_evento
        
        eventos = listar_eventos()
        evento_atual = None
        for evento in eventos:
            if evento[0] == id_contrato:
                evento_atual = evento
                break
        
        if evento_atual:
            # Buscar todos os aditivos do evento para recalcular o valor total
            aditivos = obter_aditivos_por_contrato(id_contrato, tipo_contrato)
            
            # Valor base do evento (valor estimado)
            valor_base = float(evento_atual[13]) if evento_atual[13] else 0
            
            # Somar todos os valores dos aditivos
            valor_total_aditivos = sum(float(aditivo[5]) if aditivo[5] else 0 for aditivo in aditivos)
            
            # Novo valor total
            novo_valor_total = valor_base + valor_total_aditivos
            
            # Atualizar o evento
            editar_evento(
                id_contrato,
                codigo_demanda=evento_atual[1],
                instituicao=evento_atual[2],
                instrumento=evento_atual[3],
                subprojeto=evento_atual[4],
                ta=evento_atual[5],
                pta=evento_atual[6],
                acao=evento_atual[7],
                resultado=evento_atual[8],
                meta=evento_atual[9],
                titulo_evento=evento_atual[10],
                fornecedor=evento_atual[11],
                observacao=evento_atual[12],
                valor_estimado=evento_atual[13],
                total_contrato=novo_valor_total
            )
    else:
        # Código original para cartas de acordo
        cartas = get_all_cartas()
        carta_atual = None
        for carta in cartas:
            if carta[0] == id_contrato:
                carta_atual = carta
                break
        
        if carta_atual:
            # Buscar todos os aditivos do contrato para recalcular o valor total
            aditivos = obter_aditivos_por_contrato(id_contrato)
            
            # Valor base do contrato (valor estimado)
            valor_base = float(carta_atual[17]) if carta_atual[17] else 0
            
            # Somar todos os valores dos aditivos
            valor_total_aditivos = sum(float(aditivo[5]) if aditivo[5] else 0 for aditivo in aditivos)
            
            # Novo valor total
            novo_valor_total = valor_base + valor_total_aditivos
            
            # Encontrar a data de vigência final mais recente entre os aditivos
            nova_vigencia_final = carta_atual[12]  # Valor padrão
            for aditivo in aditivos:
                if aditivo[6] and aditivo[6] > nova_vigencia_final:
                    nova_vigencia_final = aditivo[6]
            
            # Atualizar o contrato
            update_carta_acordo(id_contrato, 
                               codigo_demanda=carta_atual[1],
                               instituicao=carta_atual[2],
                               instrumento=carta_atual[3],
                               subprojeto=carta_atual[4],
                               ta=carta_atual[5],
                               pta=carta_atual[6],
                               acao=carta_atual[7],
                               resultado=carta_atual[8],
                               meta=carta_atual[9],
                               contrato=carta_atual[10],
                               vigencia_inicial=carta_atual[11],
                               vigencia_final=nova_vigencia_final,
                               instituicao_2=carta_atual[13],
                               cnpj=carta_atual[14],
                               titulo_projeto=carta_atual[15],
                               objetivo=carta_atual[16],
                               valor_estimado=carta_atual[17],
                               total_contrato=novo_valor_total,
                               observacoes=carta_atual[19])
    
    usuario = Session.get_user()[1] if Session.get_user() else 'desconhecido'
    log_action(usuario, f"Edição de Aditivo {id_aditivo}")

def excluir_aditivo(id_aditivo):
    """
    Exclui um aditivo e atualiza o contrato relacionado
    
    Args:
        id_aditivo: ID do aditivo a ser excluído
    """
    # Buscar o aditivo antes de excluir para obter o id_contrato
    aditivos = listar_aditivos()
    aditivo_excluir = None
    for aditivo in aditivos:
        if aditivo[0] == id_aditivo:
            aditivo_excluir = aditivo
            break
    
    if not aditivo_excluir:
        return
    
    # Verificar se é o último aditivo (somente o último pode ser excluído)
    id_contrato = aditivo_excluir[1]
    tipo_contrato = aditivo_excluir[2]
    aditivos_contrato = obter_aditivos_por_contrato(id_contrato, tipo_contrato)
    if aditivos_contrato and aditivos_contrato[-1][0] != id_aditivo:
        raise ValueError("Somente o último aditivo pode ser excluído.")
    
    # Excluir o aditivo
    delete_aditivo(id_aditivo)
    
    # Atualizar o contrato
    
    if tipo_contrato == 'eventos':
        # Atualizar evento
        from controllers.eventos_controller import listar_eventos, editar_evento
        
        eventos = listar_eventos()
        evento_atual = None
        for evento in eventos:
            if evento[0] == id_contrato:
                evento_atual = evento
                break
        
        if evento_atual:
            # Buscar todos os aditivos restantes do evento para recalcular o valor total
            aditivos_restantes = obter_aditivos_por_contrato(id_contrato, tipo_contrato)
            
            # Valor base do evento (valor estimado)
            valor_base = float(evento_atual[13]) if evento_atual[13] else 0
            
            # Somar todos os valores dos aditivos restantes
            valor_total_aditivos = sum(float(aditivo[5]) if aditivo[5] else 0 for aditivo in aditivos_restantes)
            
            # Novo valor total
            novo_valor_total = valor_base + valor_total_aditivos
            
            # Atualizar o evento
            editar_evento(
                id_contrato,
                codigo_demanda=evento_atual[1],
                instituicao=evento_atual[2],
                instrumento=evento_atual[3],
                subprojeto=evento_atual[4],
                ta=evento_atual[5],
                pta=evento_atual[6],
                acao=evento_atual[7],
                resultado=evento_atual[8],
                meta=evento_atual[9],
                titulo_evento=evento_atual[10],
                fornecedor=evento_atual[11],
                observacao=evento_atual[12],
                valor_estimado=evento_atual[13],
                total_contrato=novo_valor_total
            )
    else:
        # Código original para cartas de acordo
        cartas = get_all_cartas()
        carta_atual = None
        for carta in cartas:
            if carta[0] == id_contrato:
                carta_atual = carta
                break
        
        if carta_atual:
            # Buscar todos os aditivos restantes do contrato para recalcular o valor total
            aditivos_restantes = obter_aditivos_por_contrato(id_contrato)
            
            # Valor base do contrato (valor estimado)
            valor_base = float(carta_atual[17]) if carta_atual[17] else 0
            
            # Somar todos os valores dos aditivos restantes
            valor_total_aditivos = sum(float(aditivo[5]) if aditivo[5] else 0 for aditivo in aditivos_restantes)
            
            # Novo valor total
            novo_valor_total = valor_base + valor_total_aditivos
            
            # Encontrar a data de vigência final mais recente entre os aditivos restantes
            if aditivos_restantes:
                # Se ainda houver aditivos, usar a vigência final do último
                nova_vigencia_final = aditivos_restantes[-1][6]  # Nova vigência final do último aditivo restante
            else:
                # Se não houver mais aditivos, voltar para a vigência final original do contrato
                # Aqui estamos usando o valor atual, mas idealmente deveria ser o valor original antes de qualquer aditivo
                nova_vigencia_final = carta_atual[12]
            
            # Atualizar o contrato
            update_carta_acordo(id_contrato, 
                               codigo_demanda=carta_atual[1],
                               instituicao=carta_atual[2],
                               instrumento=carta_atual[3],
                               subprojeto=carta_atual[4],
                               ta=carta_atual[5],
                               pta=carta_atual[6],
                               acao=carta_atual[7],
                               resultado=carta_atual[8],
                               meta=carta_atual[9],
                               contrato=carta_atual[10],
                               vigencia_inicial=carta_atual[11],
                               vigencia_final=nova_vigencia_final,
                               instituicao_2=carta_atual[13],
                               cnpj=carta_atual[14],
                               titulo_projeto=carta_atual[15],
                               objetivo=carta_atual[16],
                               valor_estimado=carta_atual[17],
                               total_contrato=novo_valor_total,
                               observacoes=carta_atual[19])
    
    usuario = Session.get_user()[1] if Session.get_user() else 'desconhecido'
    log_action(usuario, f"Exclusão de Aditivo {id_aditivo}")
