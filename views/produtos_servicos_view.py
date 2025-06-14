import tkinter as tk
from tkinter import ttk
import re
from controllers.produtos_servicos_controller import listar_produtos_servicos, excluir_produto_servico, obter_produtos_por_demanda
from controllers.demanda_controller import listar_demandas
from controllers.fornecedores_controller import listar_fornecedores
from utils.ui_utils import FormularioBase, criar_botao, TabelaBase, mostrar_mensagem, Estilos
from views.produtos_servicos_methods import (
    salvar_produto_servico, 
    converter_valor_brl_para_float, 
    abrir_dialogo_novo_fornecedor, 
    carregar_fornecedores,
    atualizar_campos_custeio,
    atualizar_ta,
    atualizar_resultado
)

class FormatadorCampos:
    """Classe para formatar campos de entrada"""
    
    @staticmethod
    def formatar_data(entry, event=None):
        """Formata o campo para data no padrão brasileiro (DD/MM/AAAA)"""
        texto = entry.get().replace("/", "")
        # Remove caracteres não numéricos
        texto = re.sub(r'[^\d]', '', texto)
        
        # Limita a 8 dígitos
        if len(texto) > 8:
            texto = texto[:8]
            
        # Formata conforme a quantidade de dígitos
        if len(texto) > 4:
            texto = f"{texto[:2]}/{texto[2:4]}/{texto[4:]}"
        elif len(texto) > 2:
            texto = f"{texto[:2]}/{texto[2:]}"
            
        # Atualiza o campo
        entry.delete(0, tk.END)
        entry.insert(0, texto)
        
        # Valida a data
        if len(texto) == 10:  # Formato completo DD/MM/AAAA
            try:
                dia, mes, ano = map(int, texto.split('/'))
                # Validação básica
                if not (1 <= dia <= 31 and 1 <= mes <= 12 and 1000 <= ano <= 9999):
                    entry.config(foreground="red")
                else:
                    entry.config(foreground="black")
            except:
                entry.config(foreground="red")
        
        return True
    
    @staticmethod
    def formatar_nup_sei(entry, event=None):
        """Formata o campo NUP/SEI no padrão 00000.000000/0000-00"""
        texto = entry.get().replace(".", "").replace("/", "").replace("-", "")
        # Remove caracteres não numéricos
        texto = re.sub(r'[^\d]', '', texto)
        
        # Limita a 17 dígitos
        if len(texto) > 17:
            texto = texto[:17]
            
        # Formata conforme a quantidade de dígitos
        if len(texto) > 13:
            texto = f"{texto[:5]}.{texto[5:11]}/{texto[11:15]}-{texto[15:]}"
        elif len(texto) > 11:
            texto = f"{texto[:5]}.{texto[5:11]}/{texto[11:]}"
        elif len(texto) > 5:
            texto = f"{texto[:5]}.{texto[5:]}"
            
        # Atualiza o campo
        entry.delete(0, tk.END)
        entry.insert(0, texto)
        return True
    
    @staticmethod
    def formatar_cnpj(entry, event=None):
        """Formata o campo CNPJ no padrão 00.000.000/0000-00"""
        texto = entry.get().replace(".", "").replace("/", "").replace("-", "")
        # Remove caracteres não numéricos
        texto = re.sub(r'[^\d]', '', texto)
        
        # Limita a 14 dígitos
        if len(texto) > 14:
            texto = texto[:14]
            
        # Formata conforme a quantidade de dígitos
        if len(texto) > 12:
            texto = f"{texto[:2]}.{texto[2:5]}.{texto[5:8]}/{texto[8:12]}-{texto[12:]}"
        elif len(texto) > 8:
            texto = f"{texto[:2]}.{texto[2:5]}.{texto[5:8]}/{texto[8:]}"
        elif len(texto) > 5:
            texto = f"{texto[:2]}.{texto[2:5]}.{texto[5:]}"
        elif len(texto) > 2:
            texto = f"{texto[:2]}.{texto[2:]}"
            
        # Atualiza o campo
        entry.delete(0, tk.END)
        entry.insert(0, texto)
        return True
    
    @staticmethod
    def formatar_valor_brl(entry, event=None):
        """Formata o campo para valor monetário no padrão brasileiro (R$ 0.000,00)"""
        texto = entry.get().replace("R$", "").replace(".", "").replace(",", "").strip()
        # Remove caracteres não numéricos
        texto = re.sub(r'[^\d]', '', texto)
        
        if not texto:
            texto = "0"
            
        # Converte para float (centavos)
        valor = float(texto) / 100
        
        # Formata como moeda brasileira
        texto_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
        # Atualiza o campo
        entry.delete(0, tk.END)
        entry.insert(0, texto_formatado)
        return True
    
    @staticmethod
    def validar_numerico(event):
        """Permite apenas entrada de caracteres numéricos"""
        if event.char.isdigit() or event.keysym in ('BackSpace', 'Delete', 'Left', 'Right'):
            return True
        return False


class ProdutoServicoForm(FormularioBase):
    """Formulário para cadastro e edição de produtos/serviços"""
    
    def __init__(self, master, callback_salvar, callback_cancelar, produto=None):
        """
        Args:
            master: widget pai
            callback_salvar: função a ser chamada quando o formulário for salvo
            callback_cancelar: função a ser chamada quando o formulário for cancelado
            produto: dados do produto/serviço para edição (opcional)
        """
        super().__init__(master, "Cadastro de Produto/Serviço" if not produto else "Edição de Produto/Serviço")
        
        self.callback_salvar = callback_salvar
        self.callback_cancelar = callback_cancelar
        self.produto = produto
        self.id_produto = produto[0] if produto else None
        self.modo_edicao = produto is not None
        
        # Inicialização do formulário
        self.inicializar_formulario()
    
    def inicializar_formulario(self):
        """Inicializa o formulário com todos os campos e abas"""
        from views.produtos_servicos_form_init import inicializar_formulario
        inicializar_formulario(self)
        
    # Métodos importados de produtos_servicos_aditivos.py
    from views.produtos_servicos_aditivos import (
        adicionar_aditivo,
        visualizar_aditivo,
        editar_aditivo,
        excluir_aditivo,
        carregar_aditivos
    )
    
    # Métodos importados de produtos_servicos_methods.py
    salvar = salvar_produto_servico
    converter_valor_brl_para_float = converter_valor_brl_para_float
    abrir_dialogo_novo_fornecedor = abrir_dialogo_novo_fornecedor
    carregar_fornecedores = carregar_fornecedores
    atualizar_campos_custeio = atualizar_campos_custeio
    atualizar_ta = atualizar_ta
    atualizar_resultado = atualizar_resultado
    
    def cancelar(self):
        """Cancela a operação e fecha o formulário"""
        self.callback_cancelar()


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
