# views/dashboard_view.py
import tkinter as tk
from tkinter import ttk
from utils.ui_utils import Estilos, TabelaBase, Menu, mostrar_mensagem, criar_botao
from controllers.carta_acordo_controller import listar_cartas_acordo
from controllers.eventos_controller import listar_eventos
from controllers.produtos_servicos_controller import listar_produtos_servicos
from views.carta_acordo_view import CartaAcordoView
from views.eventos_view import EventosView
from views.produtos_servicos_view import ProdutosServicosView
from views.custeio_view import CusteioView

class DashboardView:
    """Dashboard principal do sistema"""
    
    def __init__(self, master):
        self.master = master
        self.master.title("Dashboard - SISPROJ - PESSOA JURÍDICA")
        self.master.geometry("1200x700")  # Define tamanho inicial da janela
        
        # Configura estilos
        Estilos.configurar()
        
        # Frame principal
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Cria menu lateral
        self.criar_menu()
        
        # Frame de conteúdo (inicialmente mostra o dashboard)
        self.frame_conteudo = ttk.Frame(self.frame, style='CardBorda.TFrame')
        self.frame_conteudo.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Mostrar dashboard inicial
        self.mostrar_dashboard()
    
    def criar_menu(self):
        """Cria o menu lateral"""
        # Itens principais do menu com ícones
        itens_menu = [
            {'texto': 'Dashboard', 'comando': self.mostrar_dashboard, 'icone': '📊'},
            {'texto': 'Cartas de Acordo', 'comando': self.mostrar_cartas_acordo, 'icone': '📝'},
            {'texto': 'Eventos', 'comando': self.mostrar_eventos, 'icone': '📅'},
            {'texto': 'Produtos/Serviços', 'comando': self.mostrar_produtos_servicos, 'icone': '🛒'},
            {'texto': 'Relatórios', 'comando': self.mostrar_relatorios, 'icone': '📈'},
        ]
        
        # Cria o menu com os itens principais
        self.menu = Menu(self.frame, itens_menu)
        
        # Adiciona o botão Sair de forma mais discreta
        menu_container = self.menu.frame.winfo_children()[2]  # Obtém o container dos itens de menu
        ttk.Separator(menu_container).pack(fill=tk.X, padx=15, pady=(15, 15))
        
        # Cria o botão Sair com estilo secundário (mais discreto) e ícone
        frame_sair = ttk.Frame(menu_container, style='Card.TFrame')
        frame_sair.pack(fill=tk.X, pady=8, padx=15)
        self.menu.criar_botao_menu(frame_sair, 'Sair', self.sair, '🚪', 'Secundario')
    
    def limpar_conteudo(self):
        """Limpa o frame de conteúdo"""
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()
    
    def mostrar_dashboard(self):
        """Exibe o dashboard com resumo e estatísticas"""
        self.limpar_conteudo()
        
        # Frame de título
        frame_titulo = ttk.Frame(self.frame_conteudo)
        frame_titulo.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(frame_titulo, text="Dashboard", style="Titulo.TLabel").pack(anchor=tk.W)
        ttk.Separator(frame_titulo).pack(fill=tk.X, pady=(5, 0))
        
        # Frame com cards de resumo
        frame_resumo = ttk.Frame(self.frame_conteudo)
        frame_resumo.pack(fill=tk.X, pady=(0, 20))
        
        # Cria cards com estatísticas
        self.criar_card_estatistica(frame_resumo, "Cartas de Acordo", len(listar_cartas_acordo()), "#388E3C")
        self.criar_card_estatistica(frame_resumo, "Eventos", len(listar_eventos()), "#F57C00")
        self.criar_card_estatistica(frame_resumo, "Produtos/Serviços", len(listar_produtos_servicos()), "#D32F2F")
        
        # Frame com tabelas de atividade recente
        frame_atividade = ttk.Frame(self.frame_conteudo)
        frame_atividade.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Dividir em duas colunas
        frame_col1 = ttk.Frame(frame_atividade)
        frame_col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        frame_col2 = ttk.Frame(frame_atividade)
        frame_col2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Eventos recentes
        self.criar_tabela_eventos_recentes(frame_col1)
        
        # Contratos recentes
        self.criar_tabela_contratos_recentes(frame_col2)
    
    def criar_card_estatistica(self, master, titulo, valor, cor):
        """Cria um card com estatística"""
        frame = ttk.Frame(master, style='CardBorda.TFrame')
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Borda colorida superior
        borda = tk.Frame(frame, background=cor, height=5)
        borda.pack(fill=tk.X)
        
        # Conteúdo do card
        ttk.Label(frame, text=titulo, font=('Segoe UI', 12)).pack(pady=(15, 5))
        ttk.Label(frame, text=str(valor), font=('Segoe UI', 24, 'bold')).pack(pady=(5, 15))
    
    def criar_tabela_eventos_recentes(self, master):
        """Cria tabela com eventos recentes"""
        frame = ttk.Frame(master)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Eventos Recentes", style="Subtitulo.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        # Tabela de eventos
        colunas = ["id", "titulo_evento", "fornecedor", "valor_estimado"]
        titulos = {
            "id": "ID",
            "titulo_evento": "Título",
            "fornecedor": "Fornecedor",
            "valor_estimado": "Valor (R$)"
        }
        
        tabela = TabelaBase(frame, colunas, titulos)
        tabela.pack(fill=tk.BOTH, expand=True)
        
        # Carregar dados (limitado aos 5 mais recentes)
        eventos = listar_eventos()
        for i, evento in enumerate(eventos[:5] if len(eventos) >= 5 else eventos):
            # Nova estrutura após remoção do objetivo: titulo_evento(10), fornecedor(11), valor_estimado(13)
            try:
                valor_estimado = float(evento[13]) if evento[13] else 0.0  # Atualizado de [14] para [13]
                valor_formatado = f"R$ {valor_estimado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError, IndexError):
                valor_formatado = "R$ 0,00"
                
            valores = {
                "id": evento[0],
                "titulo_evento": evento[10],  
                "fornecedor": evento[11],     
                "valor_estimado": valor_formatado
            }
            tabela.adicionar_linha(valores)
            
        # Botão para ver todos
        criar_botao(frame, "Ver Todos", self.mostrar_eventos, "Secundario").pack(anchor=tk.E, pady=(5, 0))
    
    def criar_tabela_contratos_recentes(self, master):
        """Cria tabela com contratos recentes"""
        frame = ttk.Frame(master)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Contratos Recentes", style="Subtitulo.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        # Tabela de contratos
        colunas = ["id", "instituicao", "titulo_projeto", "total_contrato"]
        titulos = {
            "id": "ID",
            "instituicao": "Instituição",
            "titulo_projeto": "Título",
            "total_contrato": "Valor (R$)"
        }
        
        tabela = TabelaBase(frame, colunas, titulos)
        tabela.pack(fill=tk.BOTH, expand=True)
        
        # Carregar dados (limitado aos 5 mais recentes)
        cartas = listar_cartas_acordo()
        for i, carta in enumerate(cartas[:5] if len(cartas) >= 5 else cartas):
            valores = {
                "id": carta[0],
                "instituicao": carta[2],
                "titulo_projeto": carta[15],
                "total_contrato": f"R$ {float(carta[18]):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            }
            tabela.adicionar_linha(valores)
        
        # Botão para ver todas
        criar_botao(frame, "Ver Todos", self.mostrar_cartas_acordo, "Secundario").pack(anchor=tk.E, pady=(5, 0))
    
    def mostrar_cartas_acordo(self):
        """Abre a tela de gestão de cartas de acordo"""
        self.limpar_conteudo()
        CartaAcordoView(self.frame_conteudo)
    
    def mostrar_eventos(self):
        """Abre a tela de gestão de eventos"""
        self.limpar_conteudo()
        EventosView(self.frame_conteudo)
    
    def mostrar_produtos_servicos(self):
        """Abre a tela de gestão de produtos e serviços"""
        self.limpar_conteudo()
        ProdutosServicosView(self.frame_conteudo)
    
    def mostrar_aditivos(self):
        """Abre a tela de gestão de aditivos"""
        self.limpar_conteudo()
        mostrar_mensagem("Em desenvolvimento", "Esta funcionalidade será implementada em breve.", tipo="info")
        self.mostrar_dashboard()
    
    def mostrar_custeio(self):
        """Abre a tela de gestão de custeio"""
        self.limpar_conteudo()
        CusteioView(self.frame_conteudo)
    
    def mostrar_relatorios(self):
        """Abre a tela de relatórios"""
        self.limpar_conteudo()
        mostrar_mensagem("Em desenvolvimento", "Esta funcionalidade será implementada em breve.", tipo="info")
        self.mostrar_dashboard()
    
    def sair(self):
        """Fecha a aplicação"""
        if mostrar_mensagem("Confirmação", "Deseja realmente sair da aplicação?", tipo="pergunta"):
            self.master.destroy()
