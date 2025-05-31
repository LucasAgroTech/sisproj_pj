import tkinter as tk
from tkinter import ttk
import re
import datetime
from controllers.produtos_servicos_controller import adicionar_produto_servico, listar_produtos_servicos, editar_produto_servico, excluir_produto_servico, obter_produtos_por_demanda
from controllers.demanda_controller import adicionar_demanda, listar_demandas, editar_demanda
from controllers.aditivos_controller import adicionar_aditivo, listar_aditivos, obter_aditivos_por_contrato, editar_aditivo, excluir_aditivo
from controllers.fornecedores_controller import adicionar_fornecedor, listar_fornecedores, buscar_fornecedor_por_nome
from utils.ui_utils import FormularioBase, criar_botao, TabelaBase, mostrar_mensagem, Estilos, Cores
from utils.custeio_utils import CusteioManager

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
        
        # Frame principal para organizar o layout
        self.frame_principal = ttk.Frame(self)
        self.frame_principal.pack(fill=tk.BOTH, expand=True, pady=(0, 60))  # Deixa espaço para os botões
        
        # Notebook para organizar os campos em abas (com altura limitada)
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Botões de ação (criados por último para garantir que fiquem visíveis)
        self.frame_botoes = ttk.Frame(self)
        self.frame_botoes.pack(fill=tk.X, pady=10, side=tk.BOTTOM, anchor=tk.S)
        
        self.btn_cancelar = criar_botao(self.frame_botoes, "Cancelar", self.cancelar, "Secundario", 15)
        self.btn_cancelar.pack(side=tk.RIGHT, padx=5)
        
        self.btn_salvar = criar_botao(self.frame_botoes, "Salvar", self.salvar, "Primario", 15)
        self.btn_salvar.pack(side=tk.RIGHT)
        
        # Aba de demanda (primeira aba)
        self.tab_demanda = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_demanda, text="Demanda")
        
        # Configurar campos na aba de demanda
        self.form_demanda = FormularioBase(self.tab_demanda, "")
        self.form_demanda.pack(fill=tk.BOTH, expand=True)
        
        if not self.modo_edicao:
            # Para novos cadastros, não mostramos o código (será automático)
            self.form_demanda.adicionar_campo("data_entrada", "Data de Entrada", tipo="data", 
                                 padrao="", required=True)
            # Configurar formatação para data de entrada
            data_entrada_widget = self.form_demanda.campos["data_entrada"]["widget"]
            data_entrada_widget.bind("<KeyRelease>", lambda e: self.formatar_data(data_entrada_widget, e))
            data_entrada_widget.bind("<KeyPress>", self.validar_numerico)
            
            self.form_demanda.adicionar_campo("data_protocolo", "Data de Protocolo", tipo="data", 
                                 padrao="")
            # Configurar formatação para data de protocolo
            data_protocolo_widget = self.form_demanda.campos["data_protocolo"]["widget"]
            data_protocolo_widget.bind("<KeyRelease>", lambda e: self.formatar_data(data_protocolo_widget, e))
            data_protocolo_widget.bind("<KeyPress>", self.validar_numerico)
            
            self.form_demanda.adicionar_campo("nup_sei", "NUP/SEI", 
                                 padrao="")
            # Configurar formatação para NUP/SEI
            nup_sei_widget = self.form_demanda.campos["nup_sei"]["widget"]
            nup_sei_widget.bind("<KeyRelease>", lambda e: self.formatar_nup_sei(nup_sei_widget, e))
            nup_sei_widget.bind("<KeyPress>", self.validar_numerico)
            self.form_demanda.adicionar_campo("oficio", "Ofício", 
                                 padrao="")
            # Lista de solicitantes
            solicitantes_opcoes = [
                "AECI/MS",
                "AISA/MS",
                "APSD/MS",
                "ASCOM/MS",
                "ASPAR/MS",
                "AUDSUS/MS",
                "CGARTI/SECTICS/MS",
                "CGOEX/SECTICS/MS",
                "CGPO/SECTICS/MS",
                "CGPROJ/SECTICS/MS",
                "CMED/ANVISA",
                "CONJUR/MS",
                "CORREGEDORIA/MS",
                "DAF/SECTICS/MS",
                "DECEIIS/SECTICS/MS",
                "DECIT/SECTICS/MS",
                "DESID/SECTICS/MS",
                "DGITS/SECTICS/MS",
                "GABINETE/SECTICS/MS",
                "GM/MS",
                "OUVSUS/MS",
                "SAES/MS",
                "SAPS/MS",
                "SE/MS",
                "SEIDIGI/MS",
                "SESAI/MS",
                "SGTES/MS",
                "SVSA/MS"
            ]
            self.form_demanda.adicionar_campo("solicitante", "Solicitante", tipo="opcoes",
                                 opcoes=solicitantes_opcoes, padrao=solicitantes_opcoes[0] if solicitantes_opcoes else "", required=True)
            
            status_opcoes = ["Novo", "Em Análise", "Aprovado", "Reprovado", "Concluído", "Cancelado"]
            self.form_demanda.adicionar_campo("status", "Status", tipo="opcoes", opcoes=status_opcoes, 
                                 padrao="Novo", required=True)
        else:
            # Para edição, buscamos os dados da demanda pelo código
            codigo_demanda = produto[1]
            demanda_encontrada = None
            
            # Buscar a demanda pelo código
            demandas = listar_demandas()
            for d in demandas:
                if d[0] == codigo_demanda:
                    demanda_encontrada = d
                    break
            
            # Para edição, mostramos o código da demanda
            self.form_demanda.adicionar_campo("codigo_demanda", "Código da Demanda", 
                                          padrao=str(codigo_demanda), required=False)
            
            # Adicionar campos com os dados da demanda encontrada
            data_entrada_valor = demanda_encontrada[1] if demanda_encontrada else ""
            self.form_demanda.adicionar_campo("data_entrada", "Data de Entrada", tipo="data", 
                                 padrao=data_entrada_valor, required=True)
            # Configurar formatação para data de entrada
            data_entrada_widget = self.form_demanda.campos["data_entrada"]["widget"]
            data_entrada_widget.bind("<KeyRelease>", lambda e: self.formatar_data(data_entrada_widget, e))
            data_entrada_widget.bind("<KeyPress>", self.validar_numerico)
            
            data_protocolo_valor = demanda_encontrada[3] if demanda_encontrada else ""
            self.form_demanda.adicionar_campo("data_protocolo", "Data de Protocolo", tipo="data", 
                                 padrao=data_protocolo_valor)
            # Configurar formatação para data de protocolo
            data_protocolo_widget = self.form_demanda.campos["data_protocolo"]["widget"]
            data_protocolo_widget.bind("<KeyRelease>", lambda e: self.formatar_data(data_protocolo_widget, e))
            data_protocolo_widget.bind("<KeyPress>", self.validar_numerico)
            
            nup_sei_valor = demanda_encontrada[5] if demanda_encontrada else ""
            self.form_demanda.adicionar_campo("nup_sei", "NUP/SEI", 
                                 padrao=nup_sei_valor)
            # Configurar formatação para NUP/SEI
            nup_sei_widget = self.form_demanda.campos["nup_sei"]["widget"]
            nup_sei_widget.bind("<KeyRelease>", lambda e: self.formatar_nup_sei(nup_sei_widget, e))
            nup_sei_widget.bind("<KeyPress>", self.validar_numerico)
            
            oficio_valor = demanda_encontrada[4] if demanda_encontrada else ""
            self.form_demanda.adicionar_campo("oficio", "Ofício", 
                                 padrao=oficio_valor)
            
            # Lista de solicitantes
            solicitantes_opcoes = [
                "AECI/MS",
                "AISA/MS",
                "APSD/MS",
                "ASCOM/MS",
                "ASPAR/MS",
                "AUDSUS/MS",
                "CGARTI/SECTICS/MS",
                "CGOEX/SECTICS/MS",
                "CGPO/SECTICS/MS",
                "CGPROJ/SECTICS/MS",
                "CMED/ANVISA",
                "CONJUR/MS",
                "CORREGEDORIA/MS",
                "DAF/SECTICS/MS",
                "DECEIIS/SECTICS/MS",
                "DECIT/SECTICS/MS",
                "DESID/SECTICS/MS",
                "DGITS/SECTICS/MS",
                "GABINETE/SECTICS/MS",
                "GM/MS",
                "OUVSUS/MS",
                "SAES/MS",
                "SAPS/MS",
                "SE/MS",
                "SEIDIGI/MS",
                "SESAI/MS",
                "SGTES/MS",
                "SVSA/MS"
            ]
            
            # Adicionar campo de solicitante com valor padrão temporário
            self.form_demanda.adicionar_campo("solicitante", "Solicitante", tipo="opcoes",
                                 opcoes=solicitantes_opcoes, padrao=solicitantes_opcoes[0], required=True)
            
            # Obter o widget do combobox para solicitante
            solicitante_widget = self.form_demanda.campos["solicitante"]["widget"]
            
            # Definir o valor correto após a criação do widget
            if demanda_encontrada and demanda_encontrada[2]:
                # Tentar encontrar o valor exato na lista
                if demanda_encontrada[2] in solicitantes_opcoes:
                    solicitante_widget.set(demanda_encontrada[2])
                else:
                    # Se não encontrar, usar o primeiro valor
                    solicitante_widget.set(solicitantes_opcoes[0])
            
            # Adicionar campo de status
            status_opcoes = ["Novo", "Em Análise", "Aprovado", "Reprovado", "Concluído", "Cancelado"]
            
            # Adicionar campo de status com valor padrão temporário
            self.form_demanda.adicionar_campo("status", "Status", tipo="opcoes", 
                                 opcoes=status_opcoes, padrao=status_opcoes[0], required=True)
            
            # Obter o widget do combobox para status
            status_widget = self.form_demanda.campos["status"]["widget"]
            
            # Definir o valor correto após a criação do widget
            if demanda_encontrada and len(demanda_encontrada) > 6 and demanda_encontrada[6]:
                # Tentar encontrar o valor exato na lista
                if demanda_encontrada[6] in status_opcoes:
                    status_widget.set(demanda_encontrada[6])
                else:
                    # Se não encontrar, usar "Novo" como padrão
                    status_widget.set("Novo")
            else:
                status_widget.set("Novo")
        
        # Aba de custeio (segunda aba)
        self.tab_custeio = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_custeio, text="Custeio")
        
        # Configurar campos na aba de custeio
        self.form_custeio = FormularioBase(self.tab_custeio, "")
        self.form_custeio.pack(fill=tk.BOTH, expand=True)
        
        # Opções para instituição
        instituicoes_opcoes = ["OPAS", "FIOCRUZ"]
        
        # Garantir que a instituição seja uma das opções válidas
        instituicao_padrao = ""
        if produto and produto[2]:
            if produto[2] in instituicoes_opcoes:
                instituicao_padrao = produto[2]
            else:
                instituicao_padrao = instituicoes_opcoes[0]
        else:
            instituicao_padrao = instituicoes_opcoes[0]
        
        self.form_custeio.adicionar_campo("instituicao", "Instituição", tipo="opcoes",
                                      opcoes=instituicoes_opcoes, padrao=instituicao_padrao, required=True)
        
        # Configurar evento para quando a instituição for alterada
        instituicao_widget = self.form_custeio.campos["instituicao"]["widget"]
        instituicao_widget.bind("<<ComboboxSelected>>", self.atualizar_campos_custeio)
        
        # Inicialmente, adicionamos opções vazias para evitar erro
        self.form_custeio.adicionar_campo("instrumento", "Instrumento", tipo="opcoes",
                                      opcoes=[""], padrao="")
        
        self.form_custeio.adicionar_campo("subprojeto", "Subprojeto", tipo="opcoes",
                                      opcoes=[""], padrao=produto[4] if produto else "")
        
        self.form_custeio.adicionar_campo("ta", "TA", tipo="opcoes",
                                      opcoes=[""], padrao=produto[5] if produto else "")
        self.form_custeio.adicionar_campo("pta", "PTA", tipo="opcoes",
                                      opcoes=[""], padrao=produto[6] if produto else "")
        self.form_custeio.adicionar_campo("acao", "Ação", tipo="opcoes",
                                       opcoes=[""], padrao=produto[7] if produto else "")
        self.form_custeio.adicionar_campo("resultado", "Resultado", tipo="opcoes",
                                       opcoes=[""], padrao=produto[8] if produto else "")
        self.form_custeio.adicionar_campo("meta", "Meta", tipo="opcoes",
                                       opcoes=[""], padrao=produto[9] if produto else "")
        
        # Inicializar os campos de custeio com base na instituição selecionada
        self.atualizar_campos_custeio()
        
        # Se estiver em modo de edição, precisamos garantir que os valores sejam carregados corretamente
        if self.modo_edicao and produto:
            # Primeiro, garantir que a instituição esteja corretamente selecionada
            instituicao_widget = self.form_custeio.campos["instituicao"]["widget"]
            if produto[2] in ["OPAS", "FIOCRUZ"]:
                instituicao_widget.set(produto[2])
            
            # Chamar novamente para garantir que os campos dependentes sejam atualizados
            self.atualizar_campos_custeio()
            
            # Configurar os valores salvos para os campos de custeio
            # Atualizar o instrumento
            if produto[3]:  # instrumento
                instrumento_widget = self.form_custeio.campos["instrumento"]["widget"]
                instrumento_widget.set(produto[3])
                
                # Atualizar o TA após definir o instrumento
                if produto[5]:  # ta
                    self.atualizar_ta()
                    ta_widget = self.form_custeio.campos["ta"]["widget"]
                    ta_widget.set(produto[5])
                    
                    # Atualizar o resultado após definir o TA
                    if produto[8]:  # resultado
                        self.atualizar_resultado()
                        resultado_widget = self.form_custeio.campos["resultado"]["widget"]
                        resultado_widget.set(produto[8])
            
            # Atualizar outros campos
            if produto[6]:  # pta
                pta_widget = self.form_custeio.campos["pta"]["widget"]
                pta_widget.set(produto[6])
            
            if produto[7]:  # acao
                acao_widget = self.form_custeio.campos["acao"]["widget"]
                acao_widget.set(produto[7])
            
            if produto[9]:  # meta
                meta_widget = self.form_custeio.campos["meta"]["widget"]
                meta_widget.set(produto[9])
            
            # Garantir que o subprojeto seja carregado corretamente
            if produto[4]:  # subprojeto
                # Criar instância do CusteioManager
                custeio_manager = CusteioManager()
                
                # Carregar subprojetos para a instituição selecionada
                filtros = {'instituicao_parceira': produto[2]}
                subprojetos = custeio_manager.get_distinct_values('subprojeto', filtros)
                
                # Garantir que temos pelo menos uma opção
                if not subprojetos:
                    subprojetos = [""]
                
                # Adicionar o subprojeto do produto se não estiver na lista
                if produto[4] not in subprojetos:
                    subprojetos.append(produto[4])
                
                # Atualizar as opções do widget
                subprojeto_widget = self.form_custeio.campos["subprojeto"]["widget"]
                subprojeto_widget["values"] = subprojetos
                subprojeto_widget.set(produto[4])
        
        # Aba de contrato (terceira aba)
        self.tab_contrato = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_contrato, text="Contrato")
        
        self.form_contrato = FormularioBase(self.tab_contrato, "")
        self.form_contrato.pack(fill=tk.BOTH, expand=True)
        
        # Adicionar campo de fornecedor com combobox e botão para adicionar novo
        frame_fornecedor = ttk.Frame(self.form_contrato)
        frame_fornecedor.pack(fill=tk.X, pady=5)
        
        # Label do campo
        ttk.Label(frame_fornecedor, text="Fornecedor*:", width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        # Frame para conter o combobox e o botão
        frame_combo_fornecedor = ttk.Frame(frame_fornecedor)
        frame_combo_fornecedor.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Combobox para fornecedor
        self.fornecedor_combobox = ttk.Combobox(frame_combo_fornecedor, width=40)
        self.fornecedor_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botão para adicionar novo fornecedor (mais discreto, apenas um "+")
        btn_novo_fornecedor = tk.Button(frame_combo_fornecedor, text="+", command=self.abrir_dialogo_novo_fornecedor,
                                      bg=Cores.BACKGROUND, fg=Cores.PRIMARIA,
                                      font=('Segoe UI', 10, 'bold'), width=2, height=1,
                                      relief='flat', cursor='hand2')
        btn_novo_fornecedor.pack(side=tk.RIGHT, padx=(2, 0))
        
        # Carregar fornecedores existentes ANTES de definir o valor
        self.carregar_fornecedores()
        
        # Agora definir o valor após carregar as opções
        if produto:
            self.fornecedor_combobox.set(produto[2])
        
        # Armazenar referência ao campo
        self.form_contrato.campos["fornecedor"] = {
            "widget": self.fornecedor_combobox,
            "tipo": "customizado",
            "required": True
        }
        
        # Adicionar campo para modalidade
        modalidades_opcoes = ["Contrato", "Carta Acordo", "Termo de Execução Descentralizada", "Outro"]
        self.form_contrato.adicionar_campo("modalidade", "Modalidade", tipo="opcoes",
                                      opcoes=modalidades_opcoes, padrao=produto[3] if produto else modalidades_opcoes[0], required=True)
        
        self.form_contrato.adicionar_campo("objetivo", "Objetivo", tipo="texto_longo", 
                                      padrao=produto[4] if produto else "", required=True)
        
        self.form_contrato.adicionar_campo("vigencia_inicial", "Vigência Inicial", tipo="data", 
                                       padrao=produto[5] if produto else "", required=True)
        # Configurar formatação para vigência inicial
        vigencia_inicial_widget = self.form_contrato.campos["vigencia_inicial"]["widget"]
        vigencia_inicial_widget.bind("<KeyRelease>", lambda e: self.formatar_data(vigencia_inicial_widget, e))
        vigencia_inicial_widget.bind("<KeyPress>", self.validar_numerico)
        
        self.form_contrato.adicionar_campo("vigencia_final", "Vigência Final", tipo="data", 
                                       padrao=produto[6] if produto else "", required=True)
        # Configurar formatação para vigência final
        vigencia_final_widget = self.form_contrato.campos["vigencia_final"]["widget"]
        vigencia_final_widget.bind("<KeyRelease>", lambda e: self.formatar_data(vigencia_final_widget, e))
        vigencia_final_widget.bind("<KeyPress>", self.validar_numerico)
        
        self.form_contrato.adicionar_campo("valor_estimado", "Valor Estimado", tipo="numero", 
                                          padrao=produto[8] if produto else "0.00", required=True)
        # Configurar formatação para valor estimado
        valor_estimado_widget = self.form_contrato.campos["valor_estimado"]["widget"]
        valor_estimado_widget.bind("<KeyRelease>", lambda e: self.formatar_valor_brl(valor_estimado_widget, e))
        
        self.form_contrato.adicionar_campo("total_contrato", "Total do Contrato", tipo="numero", 
                                          padrao=produto[9] if produto else "0.00", required=True)
        # Configurar formatação para total do contrato
        total_contrato_widget = self.form_contrato.campos["total_contrato"]["widget"]
        total_contrato_widget.bind("<KeyRelease>", lambda e: self.formatar_valor_brl(total_contrato_widget, e))
        
        self.form_contrato.adicionar_campo("observacao", "Observações", tipo="texto_longo", 
                                          padrao=produto[7] if produto else "")
        
        # Configurar estilo especial para a aba de aditivos (cor diferente)
        style = ttk.Style()
        style.map("TNotebook.Tab", background=[("selected", "#f0e68c")])
        
        # Aba de aditivos (quarta aba)
        self.tab_aditivos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_aditivos, text="Aditivos")
        
        # Frame para a tabela de aditivos
        self.frame_tabela_aditivos = ttk.Frame(self.tab_aditivos)
        self.frame_tabela_aditivos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título e botão para adicionar aditivo
        frame_cabecalho_aditivos = ttk.Frame(self.frame_tabela_aditivos)
        frame_cabecalho_aditivos.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_cabecalho_aditivos, text="Aditivos do Contrato", style="Titulo.TLabel").pack(side=tk.LEFT)
        
        # Botão de adicionar aditivo (só habilitado em modo de edição)
        self.btn_adicionar_aditivo = criar_botao(frame_cabecalho_aditivos, "Adicionar Aditivo", self.adicionar_aditivo, "Primario", 15)
        self.btn_adicionar_aditivo.pack(side=tk.RIGHT)
        
        if not self.modo_edicao:
            # Desabilitar o botão - precisamos acessar o botão dentro do frame
            for widget in self.btn_adicionar_aditivo.winfo_children():
                if isinstance(widget, tk.Button):
                    widget.configure(state="disabled")
            
            ttk.Label(self.frame_tabela_aditivos, text="Salve o contrato primeiro para adicionar aditivos.", 
                     style="Info.TLabel").pack(pady=20)
        else:
            # Tabela de aditivos
            colunas = ["id", "objetivo", "valor_aditivo", "valor_total_atualizado"]
            titulos = {
                "id": "ID",
                "objetivo": "Objetivo",
                "valor_aditivo": "Valor do Aditivo (R$)",
                "valor_total_atualizado": "Valor Total Atualizado (R$)"
            }
            
            self.tabela_aditivos = TabelaBase(self.frame_tabela_aditivos, colunas, titulos)
            self.tabela_aditivos.pack(fill=tk.BOTH, expand=True)
            
            # Frame de botões de ação para aditivos
            frame_acoes_aditivos = ttk.Frame(self.frame_tabela_aditivos)
            frame_acoes_aditivos.pack(fill=tk.X, pady=(10, 0))
            
            criar_botao(frame_acoes_aditivos, "Visualizar", self.visualizar_aditivo, "Primario", 15).pack(side=tk.LEFT, padx=(0, 5))
            criar_botao(frame_acoes_aditivos, "Editar", self.editar_aditivo, "Secundario", 15).pack(side=tk.LEFT, padx=(0, 5))
            criar_botao(frame_acoes_aditivos, "Excluir", self.excluir_aditivo, "Perigo", 15).pack(side=tk.LEFT)
            
            # Carregar aditivos existentes
            self.carregar_aditivos()
    
    # Métodos de formatação
    def formatar_data(self, entry, event=None):
        return FormatadorCampos.formatar_data(entry, event)
    
    def formatar_nup_sei(self, entry, event=None):
        return FormatadorCampos.formatar_nup_sei(entry, event)
    
    def formatar_cnpj(self, entry, event=None):
        return FormatadorCampos.formatar_cnpj(entry, event)
    
    def formatar_valor_brl(self, entry, event=None):
        return FormatadorCampos.formatar_valor_brl(entry, event)
    
    def validar_numerico(self, event):
        return FormatadorCampos.validar_numerico(event)
    
    def salvar(self):
        """Salva os dados do formulário"""
        # Validar todos os formulários
        formularios = [self.form_demanda, self.form_custeio, self.form_contrato]
            
        for form in formularios:
            valido, mensagem = form.validar()
            if not valido:
                mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
                return
        
        try:
            if self.modo_edicao:
                # Obter valores
                valores_demanda = self.form_demanda.obter_valores()
                valores_custeio = self.form_custeio.obter_valores()
                valores_contrato = self.form_contrato.obter_valores()
                
                # Atualizar a demanda se os campos estiverem presentes
                codigo_demanda = int(valores_demanda["codigo_demanda"])
                
                # Verificar se temos os campos necessários para atualizar a demanda
                if all(campo in valores_demanda for campo in ["data_entrada", "solicitante", "data_protocolo", "oficio", "nup_sei", "status"]):
                    editar_demanda(
                        codigo_demanda,
                        valores_demanda["data_entrada"],
                        valores_demanda["solicitante"],
                        valores_demanda["data_protocolo"],
                        valores_demanda["oficio"],
                        valores_demanda["nup_sei"],
                        valores_demanda["status"]
                    )
                
                # Obter fornecedor do combobox
                fornecedor = self.fornecedor_combobox.get()
                
                # Verificar se o fornecedor existe, se não, criar
                fornecedor_obj = buscar_fornecedor_por_nome(fornecedor)
                if not fornecedor_obj:
                    # Criar
