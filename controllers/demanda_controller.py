# controllers/demanda_controller.py
from models.demanda_model import create_demanda, get_all_demandas, update_demanda, delete_demanda
from utils.session import Session
from utils.logger import log_action

def adicionar_demanda(*args, **kwargs):
    create_demanda(*args, **kwargs)
    usuario = Session.get_user()[1] if Session.get_user() else 'desconhecido'
    log_action(usuario, "Cadastro de Demanda")

def listar_demandas():
    return get_all_demandas()

def editar_demanda(codigo, *args, **kwargs):
    update_demanda(codigo, *args, **kwargs)
    usuario = Session.get_user()[1] if Session.get_user() else 'desconhecido'
    log_action(usuario, f"Edição de Demanda {codigo}")

def excluir_demanda(codigo):
    delete_demanda(codigo)
    usuario = Session.get_user()[1] if Session.get_user() else 'desconhecido'
    log_action(usuario, f"Exclusão de Demanda {codigo}")
