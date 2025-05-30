from models.carta_acordo_model import create_carta_acordo, get_all_cartas, update_carta_acordo, delete_carta_acordo
from utils.session import Session
from utils.logger import log_action

def adicionar_carta_acordo(**kwargs):
    """
    Adiciona uma nova carta acordo
    
    Returns:
        int: ID da carta acordo inserida
    """
    carta_id = create_carta_acordo(**kwargs)
    usuario = Session.get_user()[1] if Session.get_user() else 'desconhecido'
    log_action(usuario, "Cadastro de Carta Acordo")
    return carta_id

def listar_cartas_acordo():
    return get_all_cartas()

def editar_carta_acordo(id_carta, **kwargs):
    update_carta_acordo(id_carta, **kwargs)
    usuario = Session.get_user()[1] if Session.get_user() else 'desconhecido'
    log_action(usuario, f"Edição de Carta Acordo {id_carta}")

def excluir_carta_acordo(id_carta):
    delete_carta_acordo(id_carta)
    usuario = Session.get_user()[1] if Session.get_user() else 'desconhecido'
    log_action(usuario, f"Exclusão de Carta Acordo {id_carta}")

def obter_cartas_por_demanda(codigo_demanda):
    cartas = listar_cartas_acordo()
    return [carta for carta in cartas if carta[1] == int(codigo_demanda)]
