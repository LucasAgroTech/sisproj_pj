import tkinter as tk
from tkinter import ttk
from controllers.produtos_servicos_controller import adicionar_produto_servico, listar_produtos_servicos, editar_produto_servico, excluir_produto_servico, obter_produtos_por_demanda
from controllers.demanda_controller import adicionar_demanda, listar_demandas
from utils.ui_utils import FormularioBase, TabelaBase, mostrar_mensagem, Estilos, criar_botao

class ProdutoServicoForm(FormularioBase):
    """Formulário para cadastro e edição de produtos e serviços"""
    
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
        
        # Notebook para organizar os campos em abas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Aba de demanda (apenas para novos cadastros)
        if not self.modo_edicao:
            self.tab_demanda = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_demanda, text="Demanda")
            
            # Configurar campos na aba de demanda
            self.form_demanda = FormularioBase(self.tab_demanda, "")
            self.form_demanda.pack(fill=tk.BOTH, expand=True)
            
            self.form_demanda.adicionar_campo("data_entrada", "Data de Entrada", tipo="data", 
                                 padrao="", required=True)
            self.form_demanda.adicionar_campo("solicitante", "Solicitante", 
                                 padrao="", required=True)
            self.form_demanda.adicionar_campo("data_protocolo", "Data de Protocolo", tipo="data", 
                                 padrao="")
            self.form_demanda.adicionar_campo("oficio", "Ofício", 
                                 padrao="")
            self.form_demanda.adicionar_campo("nup_sei", "NUP/SEI", 
                                 padrao="")
            
            status_opcoes = ["Novo", "Em Análise", "Aprovado", "Reprovado", "Concluído", "Cancelado"]
            self.form_demanda.adicionar_campo("status", "Status", tipo="opcoes", opcoes=status_opcoes, 
                                 padrao="Novo", required=True)
        
        # Aba de informações básicas
        self.tab_basico = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_basico, text="Informações Básicas")
        
        # Aba de detalhes financeiros
        self.tab_financeiro = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_financeiro, text="Financeiro")
        
        # Configurar campos na aba básica
        self.form_basico = FormularioBase(self.tab_basico, "")
        self.form_basico.pack(fill=tk.BOTH, expand=True)
        
        # Se estiver no modo de edição, mostrar o código da demanda
        if self.modo_edicao:
            self.form_basico.adicionar_campo("codigo_demanda", "Código da Demanda", 
                                          padrao=str(produto[1]), readonly=True)
        
        self.form_basico.adicionar_campo("fornecedor", "Fornecedor", 
                                      padrao=produto[2] if produto else "", required=True)
        self.form_basico.adicionar_campo("modalidade", "Modalidade", 
                                      padrao=produto[3] if produto else "")
        self.form_basico.adicionar_campo("objetivo", "Objetivo", tipo="texto_longo", 
                                      padrao=produto[4] if produto else "", required=True)
        self.form_basico.adicionar_campo("vigencia_inicial", "Vigência Inicial", tipo="data", 
                                      padrao=produto[5] if produto else "", required=True)
        self.form_basico.adicionar_campo("vigencia_final", "Vigência Final", tipo="data", 
                                      padrao=produto[6] if produto else "", required=True)
        
        # Configurar campos na aba financeiro
        self.form_financeiro = FormularioBase(self.tab_financeiro, "")
        self.form_financeiro.pack(fill=tk.BOTH, expand=True)
        
        self.form_financeiro.adicionar_campo("observacao", "Observações", tipo="texto_longo", 
                                          padrao=produto[7] if produto else "")
        self.form_financeiro.adicionar_campo("valor_estimado", "Valor Estimado", tipo="numero", 
                                          padrao=produto[8] if produto else "0.00", required=True)
        self.form_financeiro.adicionar_campo("total_contrato", "Total do Contrato", tipo="numero", 
                                          padrao=produto[9] if produto else "0.00", required=True)
        
        # Aba de contrato (para implementação futura)
        if not self.modo_edicao:
            self.tab_contrato = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_contrato, text="Contrato")
            
            self.form_contrato = FormularioBase(self.tab_contrato, "")
            self.form_contrato.pack(fill=tk.BOTH, expand=True)
            
            self.form_contrato.adicionar_campo("numero_contrato", "Número do Contrato", 
                                         padrao="", required=True)
            self.form_contrato.adicionar_campo("data_assinatura", "Data de Assinatura", tipo="data", 
                                         padrao="", required=True)
            self.form_contrato.adicionar_campo("observacoes_contrato", "Observações", tipo="texto_longo", 
                                         padrao="")
        
        # Botões de ação
        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        criar_botao(frame_botoes, "Cancelar", self.cancelar, "Secundario", 15).pack(side=tk.RIGHT, padx=5)
        criar_botao(frame_botoes, "Salvar", self.salvar, "Primario", 15).pack(side=tk.RIGHT)
        
    def salvar(self):
        """Salva os dados do formulário"""
        # Validar todos os formulários
        formularios = [self.form_basico, self.form_financeiro]
        
        # Adicionar formulários adicionais se não estiver em modo de edição
        if not self.modo_edicao:
            formularios.extend([self.form_demanda, self.form_contrato])
            
        for form in formularios:
            valido, mensagem = form.validar()
            if not valido:
                mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
                return
        
        try:
            if self.modo_edicao:
                # Obter valores
                valores_basico = self.form_basico.obter_valores()
                valores_financeiro = self.form_financeiro.obter_valores()
                
                # Juntar todos os valores
                valores = {
                    'codigo_demanda': int(valores_basico["codigo_demanda"]),
                    'fornecedor': valores_basico["fornecedor"],
                    'modalidade': valores_basico["modalidade"],
                    'objetivo': valores_basico["objetivo"],
                    'vigencia_inicial': valores_basico["vigencia_inicial"],
                    'vigencia_final': valores_basico["vigencia_final"],
                    'observacao': valores_financeiro["observacao"],
                    'valor_estimado': float(valores_financeiro["valor_estimado"] or 0),
                    'total_contrato': float(valores_financeiro["total_contrato"] or 0)
                }
                
                # Atualizar produto/serviço
                editar_produto_servico(self.id_produto, **valores)
                mostrar_mensagem("Sucesso", "Produto/Serviço atualizado com sucesso!", tipo="sucesso")
            else:
                # Cadastrar nova demanda
                valores_demanda = self.form_demanda.obter_valores()
                
                # Criar a demanda
                adicionar_demanda(
                    valores_demanda["data_entrada"],
                    valores_demanda["solicitante"],
                    valores_demanda["data_protocolo"],
                    valores_demanda["oficio"],
                    valores_demanda["nup_sei"],
                    valores_demanda["status"]
                )
                
                # Obter o código da nova demanda (última demanda inserida)
                demandas = listar_demandas()
                codigo_demanda = demandas[-1][0] if demandas else 1
                
                # Obter valores do produto/serviço
                valores_basico = self.form_basico.obter_valores()
                valores_financeiro = self.form_financeiro.obter_valores()
                
                # Juntar todos os valores
                valores = {
                    'codigo_demanda': codigo_demanda,
                    'fornecedor': valores_basico["fornecedor"],
                    'modalidade': valores_basico["modalidade"],
                    'objetivo': valores_basico["objetivo"],
                    'vigencia_inicial': valores_basico["vigencia_inicial"],
                    'vigencia_final': valores_basico["vigencia_final"],
                    'observacao': valores_financeiro["observacao"],
                    'valor_estimado': float(valores_financeiro["valor_estimado"] or 0),
                    'total_contrato': float(valores_financeiro["total_contrato"] or 0)
                }
                
                # Adicionar produto/serviço
                adicionar_produto_servico(**valores)
                
                # Aqui você adicionaria o código para salvar o contrato
                valores_contrato = self.form_contrato.obter_valores()
                # TODO: Implementar a criação do contrato com base nos valores_contrato
                
                mostrar_mensagem("Sucesso", "Demanda, Produto/Serviço e Contrato cadastrados com sucesso!", tipo="sucesso")
                
            self.callback_salvar()
        except Exception as e:
            mostrar_mensagem("Erro", f"Erro ao salvar: {str(e)}", tipo="erro")
        
    def cancelar(self):
        """Cancela a operação e fecha o formulário"""
        self.callback_cancelar()


class ProdutosServicosView:
    """Tela principal de listagem e gestão de produtos e serviços"""
    
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
        criar_botao(frame_cabecalho, "Novo Produto/Serviço", self.adicionar, "Primario", 20).pack(side=tk.RIGHT)
        
        # Frame de pesquisa
        frame_pesquisa = ttk.Frame(self.frame)
        frame_pesquisa.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_pesquisa, text="Pesquisar:").pack(side=tk.LEFT, padx=(0, 5))
        self.pesquisa_entry = ttk.Entry(frame_pesquisa, width=40)
        self.pesquisa_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.pesquisa_entry.bind("<Return>", lambda e: self.pesquisar())
        
        criar_botao(frame_pesquisa, "Buscar", self.pesquisar, "Primario", 10).pack(side=tk.LEFT)
        criar_botao(frame_pesquisa, "Limpar", self.limpar_pesquisa, "Secundario", 10).pack(side=tk.LEFT, padx=(5, 0))
        
        if not codigo_demanda:
            criar_botao(frame_pesquisa, "Ver Todos", self.ver_todos, "Primario", 12).pack(side=tk.RIGHT)
        else:
            criar_botao(frame_pesquisa, "Voltar", self.voltar, "Secundario", 10).pack(side=tk.RIGHT)
        
        # Tabela de produtos e serviços
        colunas = ["id", "codigo_demanda", "fornecedor", "modalidade", "vigencia_inicial", 
                  "vigencia_final", "total_contrato"]
        titulos = {
            "id": "ID",
            "codigo_demanda": "Demanda",
            "fornecedor": "Fornecedor",
            "modalidade": "Modalidade",
            "vigencia_inicial": "Início Vigência",
            "vigencia_final": "Fim Vigência",
            "total_contrato": "Total (R$)"
        }
        
        self.tabela = TabelaBase(self.frame, colunas, titulos)
        self.tabela.pack(fill=tk.BOTH, expand=True)
        
        # Frame de botões de ação
        frame_acoes = ttk.Frame(self.frame)
        frame_acoes.pack(fill=tk.X, pady=(10, 0))
        
        criar_botao(frame_acoes, "Visualizar", self.visualizar, "Primario", 12).pack(side=tk.LEFT, padx=(0, 5))
        criar_botao(frame_acoes, "Editar", self.editar, "Secundario", 12).pack(side=tk.LEFT, padx=(0, 5))
        criar_botao(frame_acoes, "Excluir", self.excluir, "Perigo", 12).pack(side=tk.LEFT)
        
        # Formulário (inicialmente oculto)
        self.frame_formulario = ttk.Frame(self.master)
        
        # Carrega os dados
        self.carregar_dados()
        
    def carregar_dados(self, filtro=None):
        """Carrega os dados dos produtos na tabela"""
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
                    
            # Formatar valor monetário
            valores = dict(zip(self.tabela.colunas, produto))
            if "total_contrato" in valores:
                valores["total_contrato"] = f"R$ {float(valores['total_contrato']):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                
            self.tabela.adicionar_linha(valores, str(produto[0]))
    
    def pesquisar(self):
        """Filtra os produtos conforme o texto de pesquisa"""
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
            callback_cancelar=self.cancelar_formulario
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
            
        # Busca o produto selecionado
        produtos = listar_produtos_servicos()
        for produto in produtos:
            if str(produto[0]) == id_selecao:
                # Oculta o frame principal
                self.frame.pack_forget()
                
                # Cria e exibe o formulário de edição
                self.formulario = ProdutoServicoForm(
                    self.frame_formulario, 
                    callback_salvar=self.salvar_formulario if not somente_leitura else self.cancelar_formulario, 
                    callback_cancelar=self.cancelar_formulario,
                    produto=produto
                )
                
                # Se for somente leitura, desabilita os campos
                if somente_leitura:
                    for form in [self.formulario.form_basico, self.formulario.form_financeiro]:
                        for campo_info in form.campos.values():
                            campo_info["widget"].configure(state="disabled")
                
                self.formulario.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                self.frame_formulario.pack(fill=tk.BOTH, expand=True)
                break
    
    def excluir(self):
        """Exclui o produto/serviço selecionado"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem("Atenção", "Selecione um produto/serviço para excluir.", tipo="aviso")
            return
            
        if mostrar_mensagem("Confirmação", "Deseja realmente excluir este produto/serviço?", tipo="pergunta"):
            excluir_produto_servico(id_selecao)
            mostrar_mensagem("Sucesso", "Produto/Serviço excluído com sucesso!", tipo="sucesso")
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
