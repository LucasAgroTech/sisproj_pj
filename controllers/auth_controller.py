# controllers/auth_controller.py
from models.user_model import authenticate
from utils.session import Session
from utils.logger import log_action
from tkinter import messagebox

def login(username, password, on_success, on_failure):
    user = authenticate(username, password)
    if user:
        Session.login(user)
        log_action(username, "Login realizado")
        on_success()
    else:
        messagebox.showerror("Erro de Login", "Usuário ou senha incorretos.")
        on_failure()
