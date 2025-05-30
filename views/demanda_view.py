# views/demanda_view.py
import tkinter as tk
from tkinter import ttk
from controllers.demanda_controller import adicionar_demanda, listar_demandas, editar_demanda, excluir_demanda
from utils.ui_utils import FormularioBase, criar_botao, TabelaBase, mostrar_mensagem, Estilos

class DemandaForm(FormularioBase):
    """Formulário para cadastro e edição de demandas"""
    
    def __init__(self, master, callback_salvar, callback_cancelar, demanda=None):
        """
        Args:
            master: widget pai
            callback_salvar: função a ser chamada quando o formulário for salvo
            callback_cancelar: função a ser chamada quando o formulário for cancelado
            demanda: dados da demanda para edição (opcional)
        """
        super().__init__(master, "Cadastro de Demanda" if not demanda else "Edição de Demanda")
        
        self.callback_salvar = callback_salvar
        self.callback_cancelar = callback_cancelar
        self.demanda = demanda
        self.codigo = demanda[0] if demanda else None
        
        # Criar campos do formulário
        self.adicionar_campo("data_entrada", "Data de Entrada", tipo="data", 
                          padrao=demanda[1] if demanda else "", required=True)
        self.adicionar_campo("solicitante", "Solicitante", 
                          padrao=demanda[2] if demanda else "", required=True)
        self.adicionar_campo("data_protocolo", "Data de Protocolo", tipo="data", 
                          padrao=demanda[3] if demanda else "")
        self.adicionar_campo("oficio", "Ofício", 
                          padrao=demanda[4] if demanda else "")
        self.adicionar_campo("nup_sei", "NUP/SEI", 
                          padrao=demanda[5] if demanda else "")
        
        status_opcoes = ["Novo", "Em Análise", "Aprovado", "Reprovado", "Concluído", "Cancelado"]
        self.adicionar_campo("status", "Status", tipo="opcoes", opcoes=status_opcoes, 
                          padrao=demanda[6] if demanda else "Novo", required=True)
        
        # Botões de ação
        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        criar_botao(frame_botoes, "Cancelar", self.cancelar, "Secundario", 15).pack(side=tk.RIGHT, padx=5)
        criar_botao(frame_botoes, "Salvar", self.salvar, "Primario", 15).pack(side=tk.RIGHT)
        
    def salvar(self):
        """Salva os dados do formulário"""
        valido, mensagem = self.validar()
        if not valido:
            mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
            return
            
        valores = self.obter_valores()
        
        if self.demanda:  # Edição
            editar_demanda(self.codigo, 
                         valores["data_entrada"], 
                         valores["solicitante"], 
                         valores["data_protocolo"], 
                         valores["oficio"], 
                         valores["nup_sei"], 
                         valores["status"])
            mostrar_mensagem("Sucesso", "Demanda atualizada com sucesso!", tipo="sucesso")
        else:  # Novo cadastro
            adicionar_demanda(
                valores["data_entrada"], 
                valores["solicitante"], 
                valores["data_protocolo"], 
                valores["oficio"], 
                valores["nup_sei"], 
                valores["status"]
            )
            mostrar_mensagem("Sucesso", "Demanda cadastrada com sucesso!", tipo="sucesso")
            
        self.callback_salvar()
        
    def cancelar(self):
        """Cancela a operação e fecha o formulário"""
        self.callback_cancelar()


class DemandaView:
    """Tela principal de listagem e gestão de demandas"""
    
    def __init__(self, master):
        self.master = master
        
        # Verifica se o master é uma janela principal para definir o título
        if isinstance(master, (tk.Tk, tk.Toplevel)):
            self.master.title("Gestão de Demandas")
        
        # Configura estilos
        Estilos.configurar()
        
        # Frame principal
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de cabeçalho
        frame_cabecalho = ttk.Frame(self.frame)
        frame_cabecalho.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_cabecalho, text="Gestão de Demandas", style="Titulo.TLabel").pack(side=tk.LEFT)
        criar_botao(frame_cabecalho, "Nova Demanda", self.adicionar, "Primario", 15).pack(side=tk.RIGHT)
        
        # Frame de pesquisa
        frame_pesquisa = ttk.Frame(self.frame)
        frame_pesquisa.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_pesquisa, text="Pesquisar:").pack(side=tk.LEFT, padx=(0, 5))
        self.pesquisa_entry = ttk.Entry(frame_pesquisa, width=40)
        self.pesquisa_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.pesquisa_entry.bind("<Return>", lambda e: self.pesquisar())
        
        criar_botao(frame_pesquisa, "Buscar", self.pesquisar, "Primario", 12).pack(side=tk.LEFT)
        criar_botao(frame_pesquisa, "Limpar", self.limpar_pesquisa, "Primario", 12).pack(side=tk.LEFT, padx=(5, 0))
        
        # Tabela de demandas
        colunas = ["codigo", "data_entrada", "solicitante", "data_protocolo", "oficio", "nup_sei", "status"]
        titulos = {
            "codigo": "Código",
            "data_entrada": "Data de Entrada",
            "solicitante": "Solicitante",
            "data_protocolo": "Data de Protocolo",
            "oficio": "Ofício",
            "nup_sei": "NUP/SEI",
            "status": "Status"
        }
        
        self.tabela = TabelaBase(self.frame, colunas, titulos)
        self.tabela.pack(fill=tk.BOTH, expand=True)
        
        # Frame de botões de ação
        frame_acoes = ttk.Frame(self.frame)
        frame_acoes.pack(fill=tk.X, pady=(10, 0))
        
        criar_botao(frame_acoes, "Editar", self.editar, "Secundario", 15).pack(side=tk.LEFT, padx=(0, 5))
        criar_botao(frame_acoes, "Excluir", self.excluir, "Perigo", 15).pack(side=tk.LEFT)
        
        # Formulário (inicialmente oculto)
        self.frame_formulario = ttk.Frame(self.master)
        
        # Carrega os dados
        self.carregar_dados()
        
    def carregar_dados(self, filtro=None):
        """Carrega os dados das demandas na tabela"""
        self.tabela.limpar()
        
        for demanda in listar_demandas():
            # Se tiver filtro, verifica se demanda contém o texto do filtro em algum campo
            if filtro:
                texto_filtro = filtro.lower()
                texto_demanda = ' '.join(str(campo).lower() for campo in demanda)
                if texto_filtro not in texto_demanda:
                    continue
                    
            self.tabela.adicionar_linha(dict(zip(self.tabela.colunas, demanda)), str(demanda[0]))
    
    def pesquisar(self):
        """Filtra as demandas conforme o texto de pesquisa"""
        texto = self.pesquisa_entry.get().strip()
        if texto:
            self.carregar_dados(texto)
        else:
            self.carregar_dados()
    
    def limpar_pesquisa(self):
        """Limpa o campo de pesquisa e recarrega todos os dados"""
        self.pesquisa_entry.delete(0, tk.END)
        self.carregar_dados()
    
    def adicionar(self):
        """Abre o formulário para adicionar uma nova demanda"""
        # Oculta o frame principal
        self.frame.pack_forget()
        
        # Cria e exibe o formulário
        self.formulario = DemandaForm(
            self.frame_formulario, 
            callback_salvar=self.salvar_formulario, 
            callback_cancelar=self.cancelar_formulario
        )
        self.formulario.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.frame_formulario.pack(fill=tk.BOTH, expand=True)
    
    def editar(self):
        """Abre o formulário para editar a demanda selecionada"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem("Atenção", "Selecione uma demanda para editar.", tipo="aviso")
            return
            
        # Busca a demanda selecionada
        for demanda in listar_demandas():
            if str(demanda[0]) == id_selecao:
                # Oculta o frame principal
                self.frame.pack_forget()
                
                # Cria e exibe o formulário de edição
                self.formulario = DemandaForm(
                    self.frame_formulario, 
                    callback_salvar=self.salvar_formulario, 
                    callback_cancelar=self.cancelar_formulario,
                    demanda=demanda
                )
                self.formulario.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                self.frame_formulario.pack(fill=tk.BOTH, expand=True)
                break
    
    def excluir(self):
        """Exclui a demanda selecionada"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem("Atenção", "Selecione uma demanda para excluir.", tipo="aviso")
            return
            
        if mostrar_mensagem("Confirmação", "Deseja realmente excluir esta demanda?", tipo="pergunta"):
            excluir_demanda(id_selecao)
            mostrar_mensagem("Sucesso", "Demanda excluída com sucesso!", tipo="sucesso")
            self.carregar_dados()
    
    def salvar_formulario(self):
        """Callback quando o formulário é salvo"""
        self.cancelar_formulario()
        self.carregar_dados()
    
    def cancelar_formulario(self):
        """Fecha o formulário e volta para a listagem"""
        # Remove o formulário
        if hasattr(self, 'formulario'):
            self.formulario.destroy()
        self.frame_formulario.pack_forget()
        
        # Exibe novamente o frame principal
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
