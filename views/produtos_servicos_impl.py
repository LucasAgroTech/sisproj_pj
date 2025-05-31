import tkinter as tk
from tkinter import ttk
import re
from controllers.produtos_servicos_controller import listar_produtos_servicos, excluir_produto_servico, obter_produtos_por_demanda
from controllers.demanda_controller import listar_demandas
from controllers.fornecedores_controller import listar_fornecedores
from utils.ui_utils import FormularioBase, criar_botao, TabelaBase, mostrar_mensagem, Estilos, Cores
from utils.custeio_utils import CusteioManager

# Import the ProdutoServicoForm class from the view module
from views.produtos_servicos_view import ProdutoServicoForm

class ProdutosServicosView:
    """Tela principal de listagem e gestão de produtos/serviços"""
    
    def __init__(self, master, codigo_demanda=None):
        """
        Args:
            master: widget pai
            codigo_demanda: código da demanda para filtrar (opcional)
        """
        self.master = master
        self.codigo_demanda = codigo_demanda
        
        # Verifica se o master é uma janela principal para definir o título
        if isinstance(master, (tk.Tk, tk.Toplevel)):
            self.master.title("Gestão de Produtos e Serviços")
        
        # Configura estilos
        Estilos.configurar()
        
        # Frame principal
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de cabeçalho
        frame_cabecalho = ttk.Frame(self.frame)
        frame_cabecalho.pack(fill=tk.X, pady=(0, 10))
        
        titulo = "Gestão de Produtos e Serviços"
        if codigo_demanda:
            demandas = listar_demandas()
            for d in demandas:
                if d[0] == int(codigo_demanda):
                    titulo += f" - Demanda {codigo_demanda} ({d[2]})"
                    break
                    
        ttk.Label(frame_cabecalho, text=titulo, style="Titulo.TLabel").pack(side=tk.LEFT)
        criar_botao(frame_cabecalho, "Novo Produto/Serviço", self.adicionar, "Primario", 15).pack(side=tk.RIGHT)
        
        # Frame de pesquisa
        frame_pesquisa = ttk.Frame(self.frame)
        frame_pesquisa.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_pesquisa, text="Pesquisar:").pack(side=tk.LEFT, padx=(0, 5))
        self.pesquisa_entry = ttk.Entry(frame_pesquisa, width=40)
        self.pesquisa_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.pesquisa_entry.bind("<Return>", lambda e: self.pesquisar())
        
        criar_botao(frame_pesquisa, "Buscar", self.pesquisar, "Primario", 12).pack(side=tk.LEFT)
        criar_botao(frame_pesquisa, "Limpar", self.limpar_pesquisa, "Primario", 12).pack(side=tk.LEFT, padx=(5, 0))
        
        if not codigo_demanda:
            criar_botao(frame_pesquisa, "Ver Todos", self.ver_todos, "Primario", 12).pack(side=tk.RIGHT)
        else:
            criar_botao(frame_pesquisa, "Voltar", self.voltar, "Primario", 12).pack(side=tk.RIGHT)
        
        # Tabela de produtos/serviços
        colunas = ["id", "codigo_demanda", "fornecedor", "modalidade", "objetivo", "vigencia_final", "total_contrato"]
        titulos = {
            "id": "ID",
            "codigo_demanda": "Demanda",
            "fornecedor": "Fornecedor",
            "modalidade": "Modalidade",
            "objetivo": "Objetivo",
            "vigencia_final": "Vigência Final",
            "total_contrato": "Total (R$)"
        }
        
        self.tabela = TabelaBase(self.frame, colunas, titulos)
        self.tabela.pack(fill=tk.BOTH, expand=True)
        
        # Frame de botões de ação
        frame_acoes = ttk.Frame(self.frame)
        frame_acoes.pack(fill=tk.X, pady=(10, 0))
        
        criar_botao(frame_acoes, "Visualizar", self.visualizar, "Primario", 15).pack(side=tk.LEFT, padx=(0, 5))
        criar_botao(frame_acoes, "Editar", self.editar, "Secundario", 15).pack(side=tk.LEFT, padx=(0, 5))
        criar_botao(frame_acoes, "Excluir", self.excluir, "Perigo", 15).pack(side=tk.LEFT)
        
        # Formulário (inicialmente oculto)
        self.frame_formulario = ttk.Frame(self.master)
        
        # Carrega os dados
        self.carregar_dados()
        
    def carregar_dados(self, filtro=None):
        """Carrega os dados dos produtos/serviços na tabela"""
        self.tabela.limpar()
        
        if self.codigo_demanda:
            produtos = obter_produtos_por_demanda(self.codigo_demanda)
        else:
            produtos = listar_produtos_servicos()
        
        for produto in produtos:
            # Se tiver filtro, verifica se produto contém o texto do filtro em algum campo
            if filtro:
                texto_filtro = filtro.lower()
                texto_produto = ' '.join(str(campo).lower() for campo in produto)
                if texto_filtro not in texto_produto:
                    continue
                    
            # Criar um dicionário com os valores do produto
            valores = {
                "id": produto[0],
                "codigo_demanda": produto[1],
                "fornecedor": produto[2],
                "modalidade": produto[3],
                "objetivo": produto[4],
                "vigencia_final": produto[6],
                "total_contrato": produto[9]
            }
            
            # Formatar valor monetário
            if "total_contrato" in valores and valores["total_contrato"]:
                try:
                    valores["total_contrato"] = f"R$ {float(valores['total_contrato']):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                except ValueError:
                    # Mantém o valor original se não for possível converter para float
                    valores["total_contrato"] = f"R$ {valores['total_contrato']}"
                
            self.tabela.adicionar_linha(valores, str(produto[0]))
    
    def pesquisar(self):
        """Filtra os produtos/serviços conforme o texto de pesquisa"""
        texto = self.pesquisa_entry.get().strip()
        if texto:
            self.carregar_dados(texto)
        else:
            self.carregar_dados()
    
    def limpar_pesquisa(self):
        """Limpa o campo de pesquisa e recarrega todos os dados"""
        self.pesquisa_entry.delete(0, tk.END)
        self.carregar_dados()
        
    def ver_todos(self):
        """Remove o filtro por demanda"""
        self.codigo_demanda = None
        self.carregar_dados()
        if isinstance(self.master, (tk.Tk, tk.Toplevel)):
            self.master.title("Gestão de Produtos e Serviços")
        
    def voltar(self):
        """Volta para a tela anterior (implementar conforme necessário)"""
        pass
    
    def adicionar(self):
        """Abre o formulário para adicionar um novo produto/serviço"""
        # Oculta o frame principal
        self.frame.pack_forget()
        
        # Cria e exibe o formulário
        self.formulario = ProdutoServicoForm(
            self.frame_formulario, 
            callback_salvar=self.salvar_formulario, 
            callback_cancelar=self.cancelar_formulario,
            produto=None
        )
        self.formulario.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.frame_formulario.pack(fill=tk.BOTH, expand=True)
    
    def visualizar(self):
        """Abre o formulário para visualizar o produto/serviço selecionado (somente leitura)"""
        self.editar(somente_leitura=True)
    
    def editar(self, somente_leitura=False):
        """Abre o formulário para editar o produto/serviço selecionado"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem("Atenção", "Selecione um produto/serviço para editar.", tipo="aviso")
            return
            
        # Busca o produto/serviço selecionado
        produtos = listar_produtos_servicos()
        for produto in produtos:
            if str(produto[0]) == id_selecao:
                # Oculta o frame principal
                self.frame.pack_forget()
                
                # Cria o formulário de edição
                self.formulario = ProdutoServicoForm(
                    self.frame_formulario, 
                    callback_salvar=self.salvar_formulario if not somente_leitura else self.cancelar_formulario, 
                    callback_cancelar=self.cancelar_formulario,
                    produto=produto
                )
                
                # Exibe o formulário
                self.formulario.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                self.frame_formulario.pack(fill=tk.BOTH, expand=True)
                
                # Se for somente leitura, desabilita os campos
                if somente_leitura:
                    # Função para desabilitar os campos após um pequeno delay
                    # para garantir que todos os widgets estejam completamente criados
                    def desabilitar_campos():
                        # Primeiro, desabilita todos os campos normais
                        for form in [self.formulario.form_demanda, self.formulario.form_custeio, self.formulario.form_contrato]:
                            for campo_nome, campo_info in form.campos.items():
                                try:
                                    widget = campo_info["widget"]
                                    widget.configure(state="disabled")
                                except Exception:
                                    pass
                        
                        # Tratamento especial para os campos de texto longo
                        try:
                            # Acessa diretamente os widgets de texto
                            objetivo_widget = self.formulario.form_contrato.campos["objetivo"]["widget"]
                            observacoes_widget = self.formulario.form_contrato.campos["observacao"]["widget"]
                            
                            # Desabilita os widgets de texto
                            objetivo_widget.configure(state="disabled")
                            observacoes_widget.configure(state="disabled")
                            
                            # Adiciona binds para bloquear qualquer tentativa de edição
                            objetivo_widget.bind("<Key>", lambda e: "break")
                            observacoes_widget.bind("<Key>", lambda e: "break")
                            objetivo_widget.bind("<Button-1>", lambda e: "break")
                            observacoes_widget.bind("<Button-1>", lambda e: "break")
                        except Exception:
                            # Se falhar, tenta uma abordagem mais genérica
                            try:
                                # Procura por todos os Text widgets no formulário
                                for widget in self.formulario.winfo_children():
                                    if isinstance(widget, tk.Text):
                                        widget.configure(state="disabled")
                                        widget.bind("<Key>", lambda e: "break")
                            except:
                                pass
                    
                    # Executa a função após um pequeno delay
                    self.formulario.after(100, desabilitar_campos)
                break
    
    def excluir(self):
        """Exclui o produto/serviço selecionado"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem("Atenção", "Selecione um produto/serviço para excluir.", tipo="aviso")
            return
            
        if mostrar_mensagem("Confirmação", "Deseja realmente excluir este produto/serviço?", tipo="pergunta"):
            excluir_produto_servico(id_selecao)
            mostrar_mensagem("Sucesso", "Produto/serviço excluído com sucesso!", tipo="sucesso")
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
