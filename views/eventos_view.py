import tkinter as tk
from tkinter import ttk
import re
import datetime
from controllers.eventos_controller import adicionar_evento, listar_eventos, editar_evento, excluir_evento, obter_eventos_por_demanda, obter_valor_total_contrato
from controllers.demanda_controller import adicionar_demanda, listar_demandas, editar_demanda
from controllers.contrato_controller import adicionar_contrato
from controllers.aditivos_controller import adicionar_aditivo, listar_aditivos, obter_aditivos_por_contrato, editar_aditivo as editar_aditivo_controller, excluir_aditivo
from controllers.titulo_eventos_controller import adicionar_titulo_evento, listar_titulos_eventos, buscar_titulo_evento_por_nome
from controllers.fornecedores_controller import adicionar_fornecedor, listar_fornecedores, buscar_fornecedor_por_nome
from utils.ui_utils import FormularioBase, criar_botao, TabelaBase, mostrar_mensagem, Estilos, Cores
from utils.custeio_utils import CusteioManager

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

class EventoForm(FormularioBase):
    """Formulário para cadastro e edição de eventos"""
    
    def __init__(self, master, callback_salvar, callback_cancelar, evento=None):
        """
        Args:
            master: widget pai
            callback_salvar: função a ser chamada quando o formulário for salvo
            callback_cancelar: função a ser chamada quando o formulário for cancelado
            evento: dados do evento para edição (opcional)
        """
        super().__init__(master, "Cadastro de Evento" if not evento else "Edição de Evento")
        
        self.callback_salvar = callback_salvar
        self.callback_cancelar = callback_cancelar
        self.evento = evento
        self.id_evento = evento[0] if evento else None
        self.modo_edicao = evento is not None
        
        # Frame principal para organizar o layout
        self.frame_principal = ttk.Frame(self)
        self.frame_principal.pack(fill=tk.BOTH, expand=True, pady=(0, 60))  # Deixa espaço para os botões
        
        # Notebook para organizar os campos em abas
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
            data_entrada_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_data(data_entrada_widget, e))
            data_entrada_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
            
            self.form_demanda.adicionar_campo("data_protocolo", "Data de Protocolo", tipo="data", 
                                 padrao="")
            # Configurar formatação para data de protocolo
            data_protocolo_widget = self.form_demanda.campos["data_protocolo"]["widget"]
            data_protocolo_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_data(data_protocolo_widget, e))
            data_protocolo_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
            
            self.form_demanda.adicionar_campo("nup_sei", "NUP/SEI", 
                                 padrao="")
            # Configurar formatação para NUP/SEI
            nup_sei_widget = self.form_demanda.campos["nup_sei"]["widget"]
            nup_sei_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_nup_sei(nup_sei_widget, e))
            nup_sei_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
            
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
            codigo_demanda = evento[1]
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
            data_entrada_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_data(data_entrada_widget, e))
            data_entrada_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
            
            data_protocolo_valor = demanda_encontrada[3] if demanda_encontrada else ""
            self.form_demanda.adicionar_campo("data_protocolo", "Data de Protocolo", tipo="data", 
                                 padrao=data_protocolo_valor)
            # Configurar formatação para data de protocolo
            data_protocolo_widget = self.form_demanda.campos["data_protocolo"]["widget"]
            data_protocolo_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_data(data_protocolo_widget, e))
            data_protocolo_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
            
            nup_sei_valor = demanda_encontrada[5] if demanda_encontrada else ""
            self.form_demanda.adicionar_campo("nup_sei", "NUP/SEI", 
                                 padrao=nup_sei_valor)
            # Configurar formatação para NUP/SEI
            nup_sei_widget = self.form_demanda.campos["nup_sei"]["widget"]
            nup_sei_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_nup_sei(nup_sei_widget, e))
            nup_sei_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
            
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
        
        # Definir valores padrão para os campos de custeio
        if evento:
            # No modo de edição, usar os dados do evento (índices 2-9 correspondem aos campos de custeio)
            instituicao_padrao = evento[2] if len(evento) > 2 and evento[2] is not None else instituicoes_opcoes[0]
            instrumento_padrao = evento[3] if len(evento) > 3 and evento[3] is not None else ""
            subprojeto_padrao = evento[4] if len(evento) > 4 and evento[4] is not None else ""
            ta_padrao = evento[5] if len(evento) > 5 and evento[5] is not None else ""
            pta_padrao = evento[6] if len(evento) > 6 and evento[6] is not None else ""
            acao_padrao = evento[7] if len(evento) > 7 and evento[7] is not None else ""
            resultado_padrao = evento[8] if len(evento) > 8 and evento[8] is not None else ""
            meta_padrao = evento[9] if len(evento) > 9 and evento[9] is not None else ""
        else:
            # No modo de criação, usar valores padrão
            instituicao_padrao = instituicoes_opcoes[0]
            instrumento_padrao = ""
            subprojeto_padrao = ""
            ta_padrao = ""
            pta_padrao = ""
            acao_padrao = ""
            resultado_padrao = ""
            meta_padrao = ""
        
        self.form_custeio.adicionar_campo("instituicao", "Instituição", tipo="opcoes",
                                      opcoes=instituicoes_opcoes, padrao=instituicao_padrao, required=True)
        
        # Configurar evento para quando a instituição for alterada
        instituicao_widget = self.form_custeio.campos["instituicao"]["widget"]
        instituicao_widget.bind("<<ComboboxSelected>>", self.atualizar_campos_custeio)
        
        # Garantir que o valor padrão foi definido corretamente ANTES de configurar os outros campos
        if self.modo_edicao and instituicao_padrao:
            instituicao_widget.set(instituicao_padrao)
        
        # Adicionar campos de custeio com valores padrão
        self.form_custeio.adicionar_campo("instrumento", "Instrumento", tipo="opcoes",
                                      opcoes=[""], padrao=instrumento_padrao)
        
        self.form_custeio.adicionar_campo("subprojeto", "Subprojeto", tipo="opcoes",
                                      opcoes=[""], padrao=subprojeto_padrao)
        
        self.form_custeio.adicionar_campo("ta", "TA", tipo="opcoes",
                                      opcoes=[""], padrao=ta_padrao)
        self.form_custeio.adicionar_campo("pta", "PTA", tipo="opcoes",
                                      opcoes=[""], padrao=pta_padrao)
        self.form_custeio.adicionar_campo("acao", "Ação", tipo="opcoes",
                                       opcoes=[""], padrao=acao_padrao)
        self.form_custeio.adicionar_campo("resultado", "Resultado", tipo="opcoes",
                                       opcoes=[""], padrao=resultado_padrao)
        self.form_custeio.adicionar_campo("meta", "Meta", tipo="opcoes",
                                       opcoes=[""], padrao=meta_padrao)
        
        # Inicializar os campos de custeio com base na instituição selecionada
        self.atualizar_campos_custeio()
        
        # Se estiver no modo de edição, definir os valores corretos após a inicialização
        if self.modo_edicao and evento:
            # Aguardar um momento para que os campos sejam inicializados
            self.after(100, lambda: self.definir_valores_custeio_edicao(evento))
        
        # Aba de contrato (terceira aba - juntando informações básicas, financeiro e contrato)
        self.tab_contrato = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_contrato, text="Contrato")
        
        self.form_contrato = FormularioBase(self.tab_contrato, "")
        self.form_contrato.pack(fill=tk.BOTH, expand=True)
        
        # Configurar estilo especial para a aba de aditivos (cor diferente)
        style = ttk.Style()
        style.map("TNotebook.Tab", background=[("selected", "#f0e68c")])
        
        # Se estiver no modo de edição, mostrar o código da demanda
        if self.modo_edicao:
            self.form_contrato.adicionar_campo("codigo_demanda", "Código da Demanda", 
                                          padrao=str(evento[1]))
            # Configurar o campo como somente leitura após criá-lo
            codigo_demanda_widget = self.form_contrato.campos["codigo_demanda"]["widget"]
            codigo_demanda_widget.configure(state="readonly")
        
        # Adicionar campo de título do evento com combobox e botão para adicionar novo
        frame_titulo_evento = ttk.Frame(self.form_contrato)
        frame_titulo_evento.pack(fill=tk.X, pady=5)
        
        # Label do campo
        ttk.Label(frame_titulo_evento, text="Título do Evento*:", width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        # Frame para conter o combobox e o botão
        frame_combo_titulo = ttk.Frame(frame_titulo_evento)
        frame_combo_titulo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Combobox para título do evento
        self.titulo_evento_combobox = ttk.Combobox(frame_combo_titulo, width=40)
        self.titulo_evento_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botão para adicionar novo título de evento (mais discreto, apenas um "+")
        btn_novo_titulo = tk.Button(frame_combo_titulo, text="+", command=self.abrir_dialogo_novo_titulo,
                                  bg=Cores.BACKGROUND, fg=Cores.PRIMARIA,
                                  font=('Segoe UI', 10, 'bold'), width=2, height=1,
                                  relief='flat', cursor='hand2')
        btn_novo_titulo.pack(side=tk.RIGHT, padx=(2, 0))
        
        # Carregar títulos de eventos existentes ANTES de definir o valor
        self.carregar_titulos_eventos()
        
        # Agora definir o valor após carregar as opções
        if evento:
            self.titulo_evento_combobox.set(evento[10])
        
        # Armazenar referência ao campo
        self.form_contrato.campos["titulo_evento"] = {
            "widget": self.titulo_evento_combobox,
            "tipo": "customizado",
            "required": True
        }
        
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
        if evento:
            self.fornecedor_combobox.set(evento[11])
        
        # Armazenar referência ao campo
        self.form_contrato.campos["fornecedor"] = {
            "widget": self.fornecedor_combobox,
            "tipo": "customizado",
            "required": True
        }
        
        self.form_contrato.adicionar_campo("valor_estimado", "Valor Estimado", tipo="numero", 
                                      padrao=evento[13] if evento else "0.00", required=True)
        # Configurar formatação para valor estimado
        valor_estimado_widget = self.form_contrato.campos["valor_estimado"]["widget"]
        valor_estimado_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_valor_brl(valor_estimado_widget, e))
        
        self.form_contrato.adicionar_campo("total_contrato", "Total do Contrato", tipo="numero", 
                                      padrao=evento[14] if evento else "0.00", required=True)
        # Configurar formatação para total do contrato
        total_contrato_widget = self.form_contrato.campos["total_contrato"]["widget"]
        total_contrato_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_valor_brl(total_contrato_widget, e))
        
        # Adicionar campos de observações no final
        self.form_contrato.adicionar_campo("observacao", "Observações", tipo="texto_longo", 
                                      padrao=evento[12] if evento else "")
        
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
            colunas = ["id", "valor_aditivo", "valor_total_atualizado"]
            titulos = {
                "id": "ID",
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
        
    def salvar(self):
        """Salva os dados do formulário"""
        # Validar todos os formulários
        formularios = [self.form_contrato, self.form_custeio]
        
        # Adicionar formulário de demanda se não estiver em modo de edição
        if not self.modo_edicao:
            formularios.append(self.form_demanda)
            
        for form in formularios:
            valido, mensagem = form.validar()
            if not valido:
                mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
                return
        
        try:
            if self.modo_edicao:
                # Obter valores
                valores_contrato = self.form_contrato.obter_valores()
                valores_custeio = self.form_custeio.obter_valores()
                
                # Atualizar a demanda se os campos estiverem presentes
                valores_demanda = self.form_demanda.obter_valores()
                if "codigo_demanda" in valores_demanda:
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
                else:
                    codigo_demanda = int(valores_contrato["codigo_demanda"])
                
                # Obter título do evento e fornecedor dos comboboxes
                titulo_evento = self.titulo_evento_combobox.get()
                fornecedor = self.fornecedor_combobox.get()
                
                # Verificar se o título do evento existe, se não, criar
                titulo_evento_obj = buscar_titulo_evento_por_nome(titulo_evento)
                if not titulo_evento_obj:
                    # Criar um novo título de evento com valores padrão
                    adicionar_titulo_evento(
                        titulo_evento,
                        "Não informado",  # cidade
                        "DF",  # estado (padrão: Distrito Federal)
                        "01/01/2024",  # data_inicio padrão
                        "31/12/2024"   # data_fim padrão
                    )
                
                # Verificar se o fornecedor existe, se não, criar
                fornecedor_obj = buscar_fornecedor_por_nome(fornecedor)
                if not fornecedor_obj:
                    # Criar um novo fornecedor com valores padrão
                    adicionar_fornecedor(
                        fornecedor,
                        "",  # CNPJ (não obrigatório)
                        "Cadastrado automaticamente"  # observação
                    )
                
                # Juntar todos os valores para o evento (incluindo custeio)
                valores = {
                    'codigo_demanda': codigo_demanda,
                    'instituicao': valores_custeio["instituicao"],
                    'instrumento': valores_custeio["instrumento"],
                    'subprojeto': valores_custeio["subprojeto"],
                    'ta': valores_custeio["ta"],
                    'pta': valores_custeio["pta"],
                    'acao': valores_custeio["acao"],
                    'resultado': valores_custeio["resultado"],
                    'meta': valores_custeio["meta"],
                    'titulo_evento': titulo_evento,
                    'fornecedor': fornecedor,
                    'observacao': valores_contrato["observacao"],
                    'valor_estimado': self.converter_valor_brl_para_float(valores_contrato["valor_estimado"]),
                    'total_contrato': self.converter_valor_brl_para_float(valores_contrato["total_contrato"])
                }
                
                editar_evento(self.id_evento, **valores)
                mostrar_mensagem("Sucesso", "Evento atualizado com sucesso!", tipo="sucesso")
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
                
                # Obter valores do evento
                valores_contrato = self.form_contrato.obter_valores()
                valores_custeio = self.form_custeio.obter_valores()
                
                # Obter título do evento e fornecedor dos comboboxes
                titulo_evento = self.titulo_evento_combobox.get()
                fornecedor = self.fornecedor_combobox.get()
                
                # Verificar se o título do evento existe, se não, criar
                titulo_evento_obj = buscar_titulo_evento_por_nome(titulo_evento)
                if not titulo_evento_obj:
                    # Criar um novo título de evento com valores padrão
                    adicionar_titulo_evento(
                        titulo_evento,
                        "Não informado",  # cidade
                        "DF",  # estado (padrão: Distrito Federal)
                        "01/01/2024",  # data_inicio padrão
                        "31/12/2024"   # data_fim padrão
                    )
                
                # Verificar se o fornecedor existe, se não, criar
                fornecedor_obj = buscar_fornecedor_por_nome(fornecedor)
                if not fornecedor_obj:
                    # Criar um novo fornecedor com valores padrão
                    adicionar_fornecedor(
                        fornecedor,
                        "",  # CNPJ (não obrigatório)
                        "Cadastrado automaticamente"  # observação
                    )
                
                # Juntar todos os valores para o evento (incluindo custeio)
                valores = {
                    'codigo_demanda': codigo_demanda,
                    'instituicao': valores_custeio["instituicao"],
                    'instrumento': valores_custeio["instrumento"],
                    'subprojeto': valores_custeio["subprojeto"],
                    'ta': valores_custeio["ta"],
                    'pta': valores_custeio["pta"],
                    'acao': valores_custeio["acao"],
                    'resultado': valores_custeio["resultado"],
                    'meta': valores_custeio["meta"],
                    'titulo_evento': titulo_evento,
                    'fornecedor': fornecedor,
                    'observacao': valores_contrato["observacao"],
                    'valor_estimado': self.converter_valor_brl_para_float(valores_contrato["valor_estimado"]),
                    'total_contrato': self.converter_valor_brl_para_float(valores_contrato["total_contrato"])
                }
                
                # Adicionar evento
                evento_id = adicionar_evento(**valores)
                
                # Criar o contrato associado ao evento (sem número de contrato e data de assinatura)
                adicionar_contrato(
                    tipo_contrato='eventos',
                    id_referencia=evento_id,
                    numero_contrato="",
                    data_assinatura="",
                    observacoes=valores_contrato["observacao"]
                )
                
                mostrar_mensagem("Sucesso", "Demanda, Evento e Contrato cadastrados com sucesso!", tipo="sucesso")
                
            self.callback_salvar()
        except Exception as e:
            mostrar_mensagem("Erro", f"Erro ao salvar: {str(e)}", tipo="erro")
        
    def atualizar_campos_custeio(self, event=None):
        """Atualiza os campos de custeio com base na instituição selecionada"""
        # Obter a instituição selecionada
        instituicao = self.form_custeio.campos["instituicao"]["widget"].get()
        
        # Obter referências aos widgets
        instrumento_widget = self.form_custeio.campos["instrumento"]["widget"]
        subprojeto_widget = self.form_custeio.campos["subprojeto"]["widget"]
        ta_widget = self.form_custeio.campos["ta"]["widget"]
        pta_widget = self.form_custeio.campos["pta"]["widget"]
        acao_widget = self.form_custeio.campos["acao"]["widget"]
        resultado_widget = self.form_custeio.campos["resultado"]["widget"]
        meta_widget = self.form_custeio.campos["meta"]["widget"]
        
        # Salvar valores atuais para preservar no modo de edição
        valores_atuais = {}
        if self.modo_edicao:
            valores_atuais = {
                'instrumento': instrumento_widget.get(),
                'subprojeto': subprojeto_widget.get(),
                'ta': ta_widget.get(),
                'pta': pta_widget.get(),
                'acao': acao_widget.get(),
                'resultado': resultado_widget.get(),
                'meta': meta_widget.get()
            }
        
        # Limpar os valores atuais apenas se não estiver em modo de edição ou se for um evento manual
        if not self.modo_edicao or event is not None:
            instrumento_widget.set("")
            subprojeto_widget.set("")
            ta_widget.set("")
            pta_widget.set("")
            acao_widget.set("")
            resultado_widget.set("")
            meta_widget.set("")
        
        # Criar instância do CusteioManager
        custeio_manager = CusteioManager()
        
        # Configurar os campos com base na instituição
        if instituicao == "OPAS":
            # Carregar projetos para OPAS
            filtros = {'instituicao_parceira': 'OPAS'}
            projetos = custeio_manager.get_distinct_values('cod_projeto', filtros)
            
            # Garantir que temos pelo menos uma opção
            if not projetos:
                projetos = [""]
                
            instrumento_widget["values"] = projetos
            
            # Configurar evento para quando o instrumento for alterado
            instrumento_widget.bind("<<ComboboxSelected>>", self.atualizar_ta)
            
            # Carregar lista de ações (01 até 35)
            acoes = [f"{i:02d}" for i in range(1, 36)]
            acao_widget["values"] = acoes
            
            # Carregar lista de metas (01 até 35)
            metas = [f"{i:02d}" for i in range(1, 36)]
            meta_widget["values"] = metas
            
            # Carregar lista de anos para PTA (2020 até 2025)
            anos_pta = [str(ano) for ano in range(2020, 2026)]
            pta_widget["values"] = anos_pta
            
            # Habilitar campos de filtros dinâmicos
            ta_widget.configure(state="readonly")
            pta_widget.configure(state="normal")
            acao_widget.configure(state="readonly")
            resultado_widget.configure(state="normal")
            meta_widget.configure(state="readonly")
            
            # Desabilitar subprojeto
            subprojeto_widget.configure(state="disabled")
            
        elif instituicao == "FIOCRUZ":
            # Carregar projetos para FIOCRUZ
            filtros = {'instituicao_parceira': 'FIOCRUZ'}
            projetos = custeio_manager.get_distinct_values('cod_projeto', filtros)
            
            # Garantir que temos pelo menos uma opção
            if not projetos:
                projetos = [""]
                
            instrumento_widget["values"] = projetos
            
            # Carregar subprojetos para FIOCRUZ
            subprojetos = custeio_manager.get_distinct_values('subprojeto', filtros)
            
            # Garantir que temos pelo menos uma opção
            if not subprojetos:
                subprojetos = [""]
                
            subprojeto_widget["values"] = subprojetos
            
            # Habilitar apenas os campos necessários
            subprojeto_widget.configure(state="readonly")
            
            # Desabilitar os outros campos
            ta_widget.configure(state="disabled")
            pta_widget.configure(state="disabled")
            acao_widget.configure(state="disabled")
            resultado_widget.configure(state="disabled")
            meta_widget.configure(state="disabled")
        
        # Configurar o estado do instrumento
        instrumento_widget.configure(state="readonly")
        
        # Restaurar valores no modo de edição se foram preservados
        if self.modo_edicao and valores_atuais and event is None:
            # Usar o método after para garantir que os valores sejam definidos após a configuração
            self.after(50, lambda: self.restaurar_valores_custeio(valores_atuais))
    
    def atualizar_ta(self, event=None):
        """Atualiza o campo TA com base no instrumento selecionado"""
        # Obter a instituição e o instrumento selecionados
        instituicao = self.form_custeio.campos["instituicao"]["widget"].get()
        instrumento = self.form_custeio.campos["instrumento"]["widget"].get()
        
        # Obter referência ao widget TA
        ta_widget = self.form_custeio.campos["ta"]["widget"]
        resultado_widget = self.form_custeio.campos["resultado"]["widget"]
        
        # Limpar o valor atual
        ta_widget.set("")
        resultado_widget.set("")
        
        # Se não tiver instrumento selecionado, não faz nada
        if not instrumento:
            ta_widget["values"] = [""]
            return
        
        # Criar instância do CusteioManager
        custeio_manager = CusteioManager()
        
        # Carregar TAs para o instrumento selecionado
        filtros = {
            'instituicao_parceira': instituicao,
            'cod_projeto': instrumento
        }
        tas = custeio_manager.get_distinct_values('cod_ta', filtros)
        
        # Garantir que temos pelo menos uma opção
        if not tas:
            tas = [""]
            
        ta_widget["values"] = tas
        
        # Configurar evento para quando o TA for alterado
        ta_widget.bind("<<ComboboxSelected>>", self.atualizar_resultado)
    
    def atualizar_resultado(self, event=None):
        """Atualiza o campo Resultado com base no TA selecionado"""
        # Obter a instituição, o instrumento e o TA selecionados
        instituicao = self.form_custeio.campos["instituicao"]["widget"].get()
        instrumento = self.form_custeio.campos["instrumento"]["widget"].get()
        ta = self.form_custeio.campos["ta"]["widget"].get()
        
        # Obter referência ao widget Resultado
        resultado_widget = self.form_custeio.campos["resultado"]["widget"]
        
        # Limpar o valor atual
        resultado_widget.set("")
        
        # Se não tiver TA selecionado, não faz nada
        if not ta:
            resultado_widget["values"] = [""]
            return
        
        # Criar instância do CusteioManager
        custeio_manager = CusteioManager()
        
        # Carregar Resultados para o TA selecionado
        filtros = {
            'instituicao_parceira': instituicao,
            'cod_projeto': instrumento,
            'cod_ta': ta
        }
        resultados = custeio_manager.get_distinct_values('resultado', filtros)
        
        # Garantir que temos pelo menos uma opção
        if not resultados:
            resultados = [""]
            
        resultado_widget["values"] = resultados
    
    def converter_valor_brl_para_float(self, valor_str):
        """Converte um valor em formato de moeda brasileira (R$ 1.234,56) para float (1234.56)"""
        if not valor_str:
            return 0.0
            
        # Se for um número, retorna diretamente
        if isinstance(valor_str, (int, float)):
            return float(valor_str)
            
        # Remove o símbolo de moeda e espaços
        valor_str = str(valor_str).replace("R$", "").strip()
        
        # Remove pontos de milhar e substitui vírgula por ponto
        valor_str = valor_str.replace(".", "").replace(",", ".")
        
        # Remove caracteres não numéricos, exceto ponto decimal
        valor_str = re.sub(r'[^\d.]', '', valor_str)
        
        try:
            return float(valor_str)
        except ValueError:
            return 0.0
    
    def carregar_aditivos(self):
        """Carrega os aditivos do contrato na tabela"""
        if not hasattr(self, 'tabela_aditivos') or not self.id_evento:
            return
            
        self.tabela_aditivos.limpar()
        
        # Obter aditivos do contrato (passando o tipo correto para eventos)
        aditivos = obter_aditivos_por_contrato(self.id_evento, "eventos")
        
        # Debug: imprimir quantidade de aditivos encontrados
        print(f"Debug: Encontrados {len(aditivos)} aditivos para evento {self.id_evento}")
        
        # Obter o valor base do contrato usando a nova função
        valor_base = obter_valor_total_contrato(self.id_evento)
        
        # Buscar o valor estimado original (antes dos aditivos)
        eventos = listar_eventos()
        valor_estimado_original = 0
        for evento in eventos:
            if evento[0] == self.id_evento:
                valor_estimado_original = float(evento[13]) if evento[13] else 0
                break
        
        print(f"Debug: Valor estimado original do evento: R$ {valor_estimado_original}")
        print(f"Debug: Valor base atual do evento: R$ {valor_base}")
        
        # Valor acumulado para calcular o valor total atualizado progressivamente
        valor_acumulado = valor_estimado_original
        
        # Ordenar aditivos por ID para garantir ordem cronológica
        aditivos_ordenados = sorted(aditivos, key=lambda x: x[0])
        
        for i, aditivo in enumerate(aditivos_ordenados):
            # Extrair dados do aditivo
            id_aditivo = aditivo[0]
            valor_aditivo = float(aditivo[5]) if aditivo[5] else 0
            
            print(f"Debug: Processando aditivo {id_aditivo} com valor R$ {valor_aditivo}")
            
            # Atualizar valor acumulado
            valor_acumulado += valor_aditivo
            
            # Criar um dicionário com os valores do aditivo
            valores = {
                "id": id_aditivo,
                "valor_aditivo": valor_aditivo,
                "valor_total_atualizado": valor_acumulado
            }
            
            # Formatar valores monetários
            valores["valor_aditivo"] = f"R$ {valores['valor_aditivo']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            valores["valor_total_atualizado"] = f"R$ {valores['valor_total_atualizado']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            self.tabela_aditivos.adicionar_linha(valores, str(id_aditivo))
        
        print(f"Debug: Carregamento de aditivos concluído. Total de linhas na tabela: {len(aditivos_ordenados)}")
        
        # Verificar se há aditivos e destacar o último (que pode ser editado/excluído)
        if aditivos_ordenados:
            ultimo_aditivo_id = str(aditivos_ordenados[-1][0])
            print(f"Debug: Último aditivo (editável/excluível): {ultimo_aditivo_id}")
            
            # Aqui poderia adicionar lógica para destacar visualmente o último aditivo
            # Por exemplo, mudando a cor da linha na tabela
    
    def adicionar_aditivo(self):
        """Abre o formulário para adicionar um novo aditivo"""
        if not self.id_evento:
            mostrar_mensagem("Atenção", "É necessário salvar o evento antes de adicionar aditivos.", tipo="aviso")
            return
            
        # Criar uma janela de diálogo para o formulário de aditivo
        dialog = tk.Toplevel(self)
        dialog.title("Adicionar Aditivo")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Limpar qualquer formulário anterior
        for widget in dialog.winfo_children():
            widget.destroy()
        
        # Formulário para o aditivo
        form_aditivo = FormularioBase(dialog, "Novo Aditivo de Contrato")
        form_aditivo.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Obter valor total atual do evento usando a nova função
        valor_total_atual = obter_valor_total_contrato(self.id_evento)
        
        # Campo: valor total atual (somente leitura) - mostrar antes do valor do aditivo para contexto
        form_aditivo.adicionar_campo("valor_total_atual", "Valor Total Atual do Contrato", tipo="numero", 
                                    padrao=f"R$ {valor_total_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        valor_total_atual_widget = form_aditivo.campos["valor_total_atual"]["widget"]
        valor_total_atual_widget.configure(state="readonly")
        
        # Campo obrigatório: valor do aditivo
        form_aditivo.adicionar_campo("valor_aditivo", "Valor do Aditivo", tipo="numero", 
                                    padrao="0.00", required=True)
        # Configurar formatação para valor do aditivo
        valor_aditivo_widget = form_aditivo.campos["valor_aditivo"]["widget"]
        valor_aditivo_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_valor_brl(valor_aditivo_widget, e))
        
        # Campo calculado: novo valor total (será atualizado dinamicamente)
        form_aditivo.adicionar_campo("novo_valor_total", "Novo Valor Total do Contrato", tipo="numero", 
                                    padrao=f"R$ {valor_total_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        novo_valor_total_widget = form_aditivo.campos["novo_valor_total"]["widget"]
        novo_valor_total_widget.configure(state="readonly")
        
        # Função para atualizar o valor total em tempo real
        def atualizar_valor_total(event=None):
            try:
                valor_aditivo_texto = valor_aditivo_widget.get()
                valor_aditivo = self.converter_valor_brl_para_float(valor_aditivo_texto)
                novo_total = valor_total_atual + valor_aditivo
                
                # Formatar e atualizar o campo
                novo_total_formatado = f"R$ {novo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                novo_valor_total_widget.configure(state="normal")
                novo_valor_total_widget.delete(0, tk.END)
                novo_valor_total_widget.insert(0, novo_total_formatado)
                novo_valor_total_widget.configure(state="readonly")
            except:
                pass
        
        # Vincular a atualização ao campo valor do aditivo
        valor_aditivo_widget.bind("<KeyRelease>", atualizar_valor_total)
        
        # Adicionar informação sobre as regras
        info_frame = ttk.Frame(form_aditivo)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_text = "ℹ️ Este aditivo será automaticamente somado ao valor total do contrato.\n" \
                   "⚠️ Apenas o último aditivo pode ser editado ou excluído."
        
        info_label = ttk.Label(info_frame, text=info_text, foreground="blue", 
                              font=('Segoe UI', 9), wraplength=400)
        info_label.pack(pady=5)
        
        # Frame para botões
        frame_botoes = ttk.Frame(dialog)
        frame_botoes.pack(fill=tk.X, padx=20, pady=10)
        
        # Função para salvar o aditivo
        def salvar_aditivo():
            # Validar apenas os campos obrigatórios
            valor_aditivo_texto = form_aditivo.campos["valor_aditivo"]["widget"].get()
            if not valor_aditivo_texto or valor_aditivo_texto.strip() in ["", "R$ 0,00", "0,00"]:
                mostrar_mensagem("Erro de Validação", "O campo 'Valor do Aditivo' é obrigatório e deve ser maior que zero.", tipo="erro")
                return
            
            try:
                # Obter valores do formulário
                valores = form_aditivo.obter_valores()
                
                # Converter valor do aditivo para float
                valor_aditivo = self.converter_valor_brl_para_float(valores["valor_aditivo"])
                
                if valor_aditivo <= 0:
                    mostrar_mensagem("Erro de Validação", "O valor do aditivo deve ser maior que zero.", tipo="erro")
                    return
                
                # Preparar dados para o aditivo (apenas campos essenciais)
                dados_aditivo = {
                    'id_contrato': self.id_evento,
                    'tipo_contrato': 'eventos',
                    'tipo_aditivo': "",  # Campo vazio
                    'descricao': f"Aditivo de valor - R$ {valor_aditivo:,.2f}",
                    'valor_aditivo': valor_aditivo,
                    'nova_vigencia_final': "",  # Campo vazio para eventos
                    'data_registro': datetime.datetime.now().strftime("%d/%m/%Y")
                }
                
                print(f"Debug: Salvando aditivo com dados: {dados_aditivo}")
                
                # Adicionar o aditivo (o controller já vai atualizar o valor total automaticamente)
                adicionar_aditivo(**dados_aditivo)
                
                print(f"Debug: Aditivo salvo com sucesso para evento {self.id_evento}")
                
                mostrar_mensagem("Sucesso", f"Aditivo de R$ {valor_aditivo:,.2f} adicionado com sucesso!\nValor total do contrato atualizado automaticamente.", tipo="sucesso")
                
                # Fechar o diálogo
                dialog.destroy()
                
                # Recarregar os aditivos na tabela
                self.carregar_aditivos()
                
                # Recarregar também o formulário principal para mostrar o valor atualizado
                if hasattr(self, 'form_contrato'):
                    novo_valor_total = obter_valor_total_contrato(self.id_evento)
                    total_contrato_widget = self.form_contrato.campos["total_contrato"]["widget"]
                    total_contrato_widget.delete(0, tk.END)
                    total_contrato_widget.insert(0, f"R$ {novo_valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                
            except Exception as e:
                print(f"Debug: Erro ao salvar aditivo: {str(e)}")
                mostrar_mensagem("Erro", f"Erro ao salvar aditivo: {str(e)}", tipo="erro")
        
        # Botões de ação
        criar_botao(frame_botoes, "Cancelar", dialog.destroy, "Secundario", 15).pack(side=tk.RIGHT, padx=5)
        criar_botao(frame_botoes, "Salvar", salvar_aditivo, "Primario", 15).pack(side=tk.RIGHT)
    
    def visualizar_aditivo(self):
        """Visualiza os detalhes de um aditivo (somente leitura)"""
        self.editar_aditivo(somente_leitura=True)
    
    def editar_aditivo(self, somente_leitura=False):
        """Abre o formulário para editar um aditivo"""
        if not hasattr(self, 'tabela_aditivos'):
            return
            
        id_selecao = self.tabela_aditivos.obter_selecao()
        if not id_selecao:
            mostrar_mensagem("Atenção", "Selecione um aditivo para editar.", tipo="aviso")
            return
            
        # Buscar o aditivo selecionado
        aditivos = listar_aditivos()
        aditivo_selecionado = None
        for aditivo in aditivos:
            if str(aditivo[0]) == id_selecao:
                aditivo_selecionado = aditivo
                break
                
        if not aditivo_selecionado:
            mostrar_mensagem("Erro", "Aditivo não encontrado.", tipo="erro")
            return
        
        # Verificar se é o último aditivo (apenas no modo de edição)
        if not somente_leitura:
            try:
                aditivos_evento = obter_aditivos_por_contrato(self.id_evento, "eventos")
                if not aditivos_evento or aditivos_evento[-1][0] != int(id_selecao):
                    mostrar_mensagem("Atenção", "Apenas o último aditivo pode ser editado. Este não é o último aditivo do contrato.", tipo="aviso")
                    return
            except Exception as e:
                mostrar_mensagem("Erro", f"Erro ao verificar posição do aditivo: {str(e)}", tipo="erro")
                return
            
        # Criar uma janela de diálogo para o formulário de aditivo
        dialog = tk.Toplevel(self)
        dialog.title("Editar Aditivo" if not somente_leitura else "Visualizar Aditivo")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Limpar qualquer formulário anterior
        for widget in dialog.winfo_children():
            widget.destroy()
        
        # Formulário para o aditivo
        form_aditivo = FormularioBase(dialog, "Editar Aditivo de Contrato" if not somente_leitura else "Detalhes do Aditivo")
        form_aditivo.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Extrair dados do aditivo
        id_aditivo = aditivo_selecionado[0]
        id_contrato = aditivo_selecionado[1]
        tipo_contrato = aditivo_selecionado[2]
        valor_aditivo = aditivo_selecionado[5]
        
        # Formatar valor do aditivo para exibição
        valor_aditivo_formatado = f"R$ {float(valor_aditivo):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if valor_aditivo else "R$ 0,00"
        
        # Obter valor total atual do evento
        valor_total_atual = obter_valor_total_contrato(id_contrato)
        
        # Campo: valor total atual (somente leitura)
        form_aditivo.adicionar_campo("valor_total_atual", "Valor Total Atual do Contrato", tipo="numero", 
                                    padrao=f"R$ {valor_total_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        valor_total_atual_widget = form_aditivo.campos["valor_total_atual"]["widget"]
        valor_total_atual_widget.configure(state="readonly")
        
        # Campo obrigatório: valor do aditivo
        form_aditivo.adicionar_campo("valor_aditivo", "Valor do Aditivo", tipo="numero", 
                                    padrao=valor_aditivo_formatado, required=True)
        # Configurar formatação para valor do aditivo
        valor_aditivo_widget = form_aditivo.campos["valor_aditivo"]["widget"]
        valor_aditivo_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_valor_brl(valor_aditivo_widget, e))
        
        # Frame para botões
        frame_botoes = ttk.Frame(dialog)
        frame_botoes.pack(fill=tk.X, padx=20, pady=10)
        
        # Se for somente leitura, desabilitar todos os campos editáveis
        if somente_leitura:
            try:
                valor_aditivo_widget.configure(state="disabled")
            except Exception:
                pass
        
        # Função para salvar as alterações do aditivo
        def salvar_alteracoes():
            # Validar apenas os campos obrigatórios
            valor_aditivo_texto = form_aditivo.campos["valor_aditivo"]["widget"].get()
            if not valor_aditivo_texto or valor_aditivo_texto.strip() in ["", "R$ 0,00", "0,00"]:
                mostrar_mensagem("Erro de Validação", "O campo 'Valor do Aditivo' é obrigatório e deve ser maior que zero.", tipo="erro")
                return
            
            try:
                # Obter valores do formulário
                valores = form_aditivo.obter_valores()
                
                # Converter valor do aditivo para float
                valor_aditivo_novo = self.converter_valor_brl_para_float(valores["valor_aditivo"])
                
                if valor_aditivo_novo <= 0:
                    mostrar_mensagem("Erro de Validação", "O valor do aditivo deve ser maior que zero.", tipo="erro")
                    return
                
                # Preparar dados para atualizar o aditivo (apenas campos essenciais)
                dados_aditivo = {
                    'id_contrato': id_contrato,
                    'tipo_contrato': tipo_contrato,
                    'tipo_aditivo': "",  # Campo vazio
                    'descricao': f"Aditivo de valor - R$ {valor_aditivo_novo:,.2f}",
                    'valor_aditivo': valor_aditivo_novo,
                    'nova_vigencia_final': "",  # Campo vazio
                    'data_registro': datetime.datetime.now().strftime("%d/%m/%Y")
                }
                
                # Atualizar o aditivo (o controller já vai recalcular o valor total automaticamente)
                editar_aditivo_controller(id_aditivo, **dados_aditivo)
                
                mostrar_mensagem("Sucesso", f"Aditivo atualizado com sucesso!\nValor total do contrato recalculado automaticamente.", tipo="sucesso")
                
                # Fechar o diálogo
                dialog.destroy()
                
                # Recarregar os aditivos na tabela
                self.carregar_aditivos()
                
                # Recarregar também o formulário principal para mostrar o valor atualizado
                if hasattr(self, 'form_contrato'):
                    novo_valor_total = obter_valor_total_contrato(self.id_evento)
                    total_contrato_widget = self.form_contrato.campos["total_contrato"]["widget"]
                    total_contrato_widget.delete(0, tk.END)
                    total_contrato_widget.insert(0, f"R$ {novo_valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                
            except ValueError as ve:
                # Tratar especificamente a exceção de regra de negócio
                mostrar_mensagem("Regra de Negócio", str(ve), tipo="aviso")
            except Exception as e:
                mostrar_mensagem("Erro", f"Erro ao atualizar aditivo: {str(e)}", tipo="erro")
        
        # Botões de ação
        if somente_leitura:
            criar_botao(frame_botoes, "Fechar", dialog.destroy, "Primario", 15).pack(side=tk.RIGHT)
        else:
            criar_botao(frame_botoes, "Cancelar", dialog.destroy, "Secundario", 15).pack(side=tk.RIGHT, padx=5)
            criar_botao(frame_botoes, "Salvar", salvar_alteracoes, "Primario", 15).pack(side=tk.RIGHT)
    
    def excluir_aditivo(self):
        """Exclui o aditivo selecionado (apenas o último)"""
        if not hasattr(self, 'tabela_aditivos'):
            return
            
        id_selecao = self.tabela_aditivos.obter_selecao()
        if not id_selecao:
            mostrar_mensagem("Atenção", "Selecione um aditivo para excluir.", tipo="aviso")
            return
        
        # Verificar se é o último aditivo
        try:
            aditivos_evento = obter_aditivos_por_contrato(self.id_evento, "eventos")
            if not aditivos_evento:
                mostrar_mensagem("Erro", "Nenhum aditivo encontrado para este evento.", tipo="erro")
                return
                
            if aditivos_evento[-1][0] != int(id_selecao):
                mostrar_mensagem("Regra de Negócio", 
                               "Apenas o último aditivo pode ser excluído.\n\n" +
                               "Para excluir este aditivo, primeiro você deve excluir " +
                               "todos os aditivos posteriores, um por vez, começando pelo mais recente.", 
                               tipo="aviso")
                return
                
        except Exception as e:
            mostrar_mensagem("Erro", f"Erro ao verificar posição do aditivo: {str(e)}", tipo="erro")
            return
        
        # Obter o valor do aditivo para mostrar na confirmação
        valor_aditivo = 0
        try:
            aditivos = listar_aditivos()
            for aditivo in aditivos:
                if aditivo[0] == int(id_selecao):
                    valor_aditivo = float(aditivo[5]) if aditivo[5] else 0
                    break
        except:
            pass
        
        mensagem_confirmacao = f"Deseja realmente excluir o último aditivo?\n\n" \
                             f"Valor do aditivo: R$ {valor_aditivo:,.2f}\n" \
                             f"O valor total do contrato será reduzido automaticamente."
        
        if mostrar_mensagem("Confirmação", mensagem_confirmacao, tipo="pergunta"):
            try:
                # Excluir o aditivo (o controller já vai recalcular o valor total automaticamente)
                excluir_aditivo(id_selecao)
                
                mostrar_mensagem("Sucesso", f"Aditivo excluído com sucesso!\nValor total do contrato atualizado automaticamente.", tipo="sucesso")
                
                # Recarregar os aditivos na tabela
                self.carregar_aditivos()
                
                # Recarregar também o formulário principal para mostrar o valor atualizado
                if hasattr(self, 'form_contrato'):
                    from controllers.eventos_controller import obter_valor_total_contrato
                    novo_valor_total = obter_valor_total_contrato(self.id_evento)
                    total_contrato_widget = self.form_contrato.campos["total_contrato"]["widget"]
                    total_contrato_widget.delete(0, tk.END)
                    total_contrato_widget.insert(0, f"R$ {novo_valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                
            except ValueError as ve:
                # Tratar especificamente a exceção de regra de negócio
                mostrar_mensagem("Regra de Negócio", str(ve), tipo="aviso")
            except Exception as e:
                mostrar_mensagem("Erro", f"Erro ao excluir aditivo: {str(e)}", tipo="erro")
    
    def carregar_titulos_eventos(self):
        """Carrega os títulos de eventos existentes no combobox"""
        try:
            titulos = listar_titulos_eventos()
            titulos_texto = [titulo[1] for titulo in titulos]  # Pega apenas o campo 'titulo'
            self.titulo_evento_combobox['values'] = titulos_texto
        except Exception as e:
            print(f"Erro ao carregar títulos de eventos: {e}")
    
    def carregar_fornecedores(self):
        """Carrega os fornecedores existentes no combobox"""
        try:
            fornecedores = listar_fornecedores()
            fornecedores_texto = [fornecedor[1] for fornecedor in fornecedores]  # Pega apenas o campo 'razao_social'
            self.fornecedor_combobox['values'] = fornecedores_texto
        except Exception as e:
            print(f"Erro ao carregar fornecedores: {e}")
    
    def abrir_dialogo_novo_titulo(self):
        """Abre o diálogo para adicionar um novo título de evento"""
        dialog = tk.Toplevel(self)
        dialog.title("Novo Título de Evento")
        dialog.geometry("600x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Formulário para o novo título de evento
        form = FormularioBase(dialog, "Cadastro de Título de Evento")
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Adicionar campos
        form.adicionar_campo("titulo", "Título", padrao="", required=True)
        
        # Lista de estados brasileiros
        estados = [
            "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
            "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
        ]
        form.adicionar_campo("estado", "Estado", tipo="opcoes", opcoes=estados, padrao=estados[0], required=True)
        
        form.adicionar_campo("cidade", "Cidade", padrao="", required=True)
        
        form.adicionar_campo("data_inicio", "Data de Início", tipo="data", padrao="", required=True)
        # Configurar formatação para data de início
        data_inicio_widget = form.campos["data_inicio"]["widget"]
        data_inicio_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_data(data_inicio_widget, e))
        data_inicio_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
        
        form.adicionar_campo("data_fim", "Data de Fim", tipo="data", padrao="", required=True)
        # Configurar formatação para data de fim
        data_fim_widget = form.campos["data_fim"]["widget"]
        data_fim_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_data(data_fim_widget, e))
        data_fim_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
        
        # Frame para botões
        frame_botoes = ttk.Frame(dialog)
        frame_botoes.pack(fill=tk.X, padx=20, pady=10)
        
        # Função para salvar o título de evento
        def salvar_titulo():
            # Validar o formulário
            valido, mensagem = form.validar()
            if not valido:
                mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
                return
            
            try:
                # Obter valores do formulário
                valores = form.obter_valores()
                
                # Adicionar o título de evento
                adicionar_titulo_evento(
                    valores["titulo"],
                    valores["cidade"],
                    valores["estado"],
                    valores["data_inicio"],
                    valores["data_fim"]
                )
                
                mostrar_mensagem("Sucesso", "Título de evento adicionado com sucesso!", tipo="sucesso")
                
                # Atualizar o combobox com o novo título
                self.carregar_titulos_eventos()
                self.titulo_evento_combobox.set(valores["titulo"])
                
                # Fechar o diálogo
                dialog.destroy()
                
            except Exception as e:
                mostrar_mensagem("Erro", f"Erro ao salvar título de evento: {str(e)}", tipo="erro")
        
        # Botões de ação
        criar_botao(frame_botoes, "Cancelar", dialog.destroy, "Secundario", 15).pack(side=tk.RIGHT, padx=5)
        criar_botao(frame_botoes, "Salvar", salvar_titulo, "Primario", 15).pack(side=tk.RIGHT)
    
    def abrir_dialogo_novo_fornecedor(self):
        """Abre o diálogo para adicionar um novo fornecedor"""
        dialog = tk.Toplevel(self)
        dialog.title("Novo Fornecedor")
        dialog.geometry("600x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Formulário para o novo fornecedor
        form = FormularioBase(dialog, "Cadastro de Fornecedor")
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Adicionar campos
        form.adicionar_campo("razao_social", "Razão Social", padrao="", required=True)
        
        form.adicionar_campo("cnpj", "CNPJ", padrao="")
        # Configurar formatação para CNPJ
        cnpj_widget = form.campos["cnpj"]["widget"]
        cnpj_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_cnpj(cnpj_widget, e))
        cnpj_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
        
        form.adicionar_campo("observacao", "Observação", tipo="texto_longo", padrao="")
        
        # Frame para botões
        frame_botoes = ttk.Frame(dialog)
        frame_botoes.pack(fill=tk.X, padx=20, pady=10)
        
        # Função para salvar o fornecedor
        def salvar_fornecedor():
            # Validar o formulário
            valido, mensagem = form.validar()
            if not valido:
                mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
                return
            
            try:
                # Obter valores do formulário
                valores = form.obter_valores()
                
                # Adicionar o fornecedor
                adicionar_fornecedor(
                    valores["razao_social"],
                    valores["cnpj"],
                    valores["observacao"]
                )
                
                mostrar_mensagem("Sucesso", "Fornecedor adicionado com sucesso!", tipo="sucesso")
                
                # Atualizar o combobox com o novo fornecedor
                self.carregar_fornecedores()
                self.fornecedor_combobox.set(valores["razao_social"])
                
                # Fechar o diálogo
                dialog.destroy()
                
            except Exception as e:
                mostrar_mensagem("Erro", f"Erro ao salvar fornecedor: {str(e)}", tipo="erro")
        
        # Botões de ação
        criar_botao(frame_botoes, "Cancelar", dialog.destroy, "Secundario", 15).pack(side=tk.RIGHT, padx=5)
        criar_botao(frame_botoes, "Salvar", salvar_fornecedor, "Primario", 15).pack(side=tk.RIGHT)
    
    def cancelar(self):
        """Cancela a operação e fecha o formulário"""
        self.callback_cancelar()
    
    def definir_valores_custeio_edicao(self, evento):
        """Define os valores de custeio corretos no modo de edição após a inicialização dos campos"""
        if not evento or len(evento) <= 2:
            return
            
        try:
            # Obter os widgets dos campos
            instrumento_widget = self.form_custeio.campos["instrumento"]["widget"]
            subprojeto_widget = self.form_custeio.campos["subprojeto"]["widget"]
            ta_widget = self.form_custeio.campos["ta"]["widget"]
            pta_widget = self.form_custeio.campos["pta"]["widget"]
            acao_widget = self.form_custeio.campos["acao"]["widget"]
            resultado_widget = self.form_custeio.campos["resultado"]["widget"]
            meta_widget = self.form_custeio.campos["meta"]["widget"]
            
            # Definir os valores dos campos de custeio (índices 3-9)
            if len(evento) > 3 and evento[3] is not None:
                instrumento_widget.set(evento[3])
            if len(evento) > 4 and evento[4] is not None:
                subprojeto_widget.set(evento[4])
            if len(evento) > 5 and evento[5] is not None:
                ta_widget.set(evento[5])
            if len(evento) > 6 and evento[6] is not None:
                pta_widget.set(evento[6])
            if len(evento) > 7 and evento[7] is not None:
                acao_widget.set(evento[7])
            if len(evento) > 8 and evento[8] is not None:
                resultado_widget.set(evento[8])
            if len(evento) > 9 and evento[9] is not None:
                meta_widget.set(evento[9])
                
        except Exception as e:
            print(f"Erro ao definir valores de custeio na edição: {e}")
    
    def restaurar_valores_custeio(self, valores_atuais):
        """Restaura os valores dos campos de custeio após a configuração"""
        try:
            instrumento_widget = self.form_custeio.campos["instrumento"]["widget"]
            subprojeto_widget = self.form_custeio.campos["subprojeto"]["widget"]
            ta_widget = self.form_custeio.campos["ta"]["widget"]
            pta_widget = self.form_custeio.campos["pta"]["widget"]
            acao_widget = self.form_custeio.campos["acao"]["widget"]
            resultado_widget = self.form_custeio.campos["resultado"]["widget"]
            meta_widget = self.form_custeio.campos["meta"]["widget"]
            
            # Restaurar valores se não estiverem vazios
            if valores_atuais.get('instrumento'):
                instrumento_widget.set(valores_atuais['instrumento'])
            if valores_atuais.get('subprojeto'):
                subprojeto_widget.set(valores_atuais['subprojeto'])
            if valores_atuais.get('ta'):
                ta_widget.set(valores_atuais['ta'])
            if valores_atuais.get('pta'):
                pta_widget.set(valores_atuais['pta'])
            if valores_atuais.get('acao'):
                acao_widget.set(valores_atuais['acao'])
            if valores_atuais.get('resultado'):
                resultado_widget.set(valores_atuais['resultado'])
            if valores_atuais.get('meta'):
                meta_widget.set(valores_atuais['meta'])
                
        except Exception as e:
            print(f"Erro ao restaurar valores de custeio: {e}")


class EventosView:
    """Tela principal de listagem e gestão de eventos"""
    
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
            self.master.title("Gestão de Eventos")
        
        # Configura estilos
        Estilos.configurar()
        
        # Frame principal
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de cabeçalho
        frame_cabecalho = ttk.Frame(self.frame)
        frame_cabecalho.pack(fill=tk.X, pady=(0, 10))
        
        titulo = "Gestão de Eventos"
        if codigo_demanda:
            demandas = listar_demandas()
            for d in demandas:
                if d[0] == int(codigo_demanda):
                    titulo += f" - Demanda {codigo_demanda} ({d[2]})"
                    break
                    
        ttk.Label(frame_cabecalho, text=titulo, style="Titulo.TLabel").pack(side=tk.LEFT)
        criar_botao(frame_cabecalho, "Novo Evento", self.adicionar, "Primario", 15).pack(side=tk.RIGHT)
        
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
        
        # Tabela de eventos
        colunas = ["id", "codigo_demanda", "titulo_evento", "fornecedor", "total_contrato"]
        titulos = {
            "id": "ID",
            "codigo_demanda": "Demanda",
            "titulo_evento": "Título do Evento",
            "fornecedor": "Fornecedor",
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
        """Carrega os dados dos eventos na tabela"""
        self.tabela.limpar()
        
        try:
            if self.codigo_demanda:
                eventos = obter_eventos_por_demanda(self.codigo_demanda)
            else:
                eventos = listar_eventos()
            
            for evento in eventos:
                try:
                    # Se tiver filtro, verifica se evento contém o texto do filtro em algum campo
                    if filtro:
                        texto_filtro = filtro.lower()
                        texto_evento = ' '.join(str(campo).lower() for campo in evento)
                        if texto_filtro not in texto_evento:
                            continue
                    
                    # Mapear explicitamente cada coluna para garantir que estamos usando os valores corretos
                    # Nova estrutura da tabela eventos após remoção do objetivo: id(0), codigo_demanda(1), instituicao(2), instrumento(3), 
                    # subprojeto(4), ta(5), pta(6), acao(7), resultado(8), meta(9), titulo_evento(10), 
                    # fornecedor(11), observacao(12), valor_estimado(13), total_contrato(14)
                    valores = {
                        "id": evento[0],
                        "codigo_demanda": evento[1],
                        "titulo_evento": evento[10],
                        "fornecedor": evento[11],
                        "total_contrato": evento[14]  # Atualizado de evento[15] para evento[14]
                    }
                    
                    # Formatar valor monetário
                    if valores["total_contrato"] is not None:
                        try:
                            # Tentar converter para float e formatar como moeda
                            valor = float(valores['total_contrato'])
                            valores["total_contrato"] = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        except (ValueError, TypeError):
                            # Se não for possível converter para float, usar um valor padrão
                            valores["total_contrato"] = "R$ 0,00"
                    else:
                        valores["total_contrato"] = "R$ 0,00"
                    
                    # Adicionar a linha à tabela
                    self.tabela.adicionar_linha(valores, str(evento[0]))
                except Exception as e:
                    print(f"Erro ao processar evento: {e}")
                    continue
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            mostrar_mensagem("Erro", f"Erro ao carregar dados: {str(e)}", tipo="erro")
    
    def pesquisar(self):
        """Filtra os eventos conforme o texto de pesquisa"""
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
            self.master.title("Gestão de Eventos")
        
    def voltar(self):
        """Volta para a tela anterior (implementar conforme necessário)"""
        pass
    
    def adicionar(self):
        """Abre o formulário para adicionar um novo evento"""
        # Oculta o frame principal
        self.frame.pack_forget()
        
        # Cria e exibe o formulário
        self.formulario = EventoForm(
            self.frame_formulario, 
            callback_salvar=self.salvar_formulario, 
            callback_cancelar=self.cancelar_formulario
        )
        self.formulario.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.frame_formulario.pack(fill=tk.BOTH, expand=True)
    
    def visualizar(self):
        """Abre o formulário para visualizar o evento selecionado (somente leitura)"""
        self.editar(somente_leitura=True)
    
    def editar(self, somente_leitura=False):
        """Abre o formulário para editar o evento selecionado"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem("Atenção", "Selecione um evento para editar.", tipo="aviso")
            return
            
        # Busca o evento selecionado
        eventos = listar_eventos()
        for evento in eventos:
            if str(evento[0]) == id_selecao:
                # Oculta o frame principal
                self.frame.pack_forget()
                
                # Cria e exibe o formulário de edição
                self.formulario = EventoForm(
                    self.frame_formulario, 
                    callback_salvar=self.salvar_formulario if not somente_leitura else self.cancelar_formulario, 
                    callback_cancelar=self.cancelar_formulario,
                    evento=evento
                )
                
                # Se for somente leitura, desabilita os campos
                if somente_leitura:
                    # Função para desabilitar os campos após um pequeno delay
                    # para garantir que todos os widgets estejam completamente criados
                    def desabilitar_campos():
                        # Desabilitar campos nas abas
                        for form in [self.formulario.form_demanda, self.formulario.form_custeio, self.formulario.form_contrato]:
                            for campo_nome, campo_info in form.campos.items():
                                try:
                                    widget = campo_info["widget"]
                                    widget.configure(state="disabled")
                                except Exception:
                                    pass
                        
                        # Desabilitar os comboboxes customizados
                        try:
                            self.formulario.titulo_evento_combobox.configure(state="disabled")
                            self.formulario.fornecedor_combobox.configure(state="disabled")
                        except Exception:
                            pass
                        
                        # Tratamento especial para os campos de texto longo na aba de contrato
                        try:
                            # Acessa diretamente os widgets de texto da aba de contrato
                            observacao_widget = self.formulario.form_contrato.campos["observacao"]["widget"]
                            
                            # Desabilita os widgets de texto
                            observacao_widget.configure(state="disabled")
                            
                            # Adiciona binds para bloquear qualquer tentativa de edição
                            observacao_widget.bind("<Key>", lambda e: "break")
                            observacao_widget.bind("<Button-1>", lambda e: "break")
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
                
                self.formulario.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                self.frame_formulario.pack(fill=tk.BOTH, expand=True)
                break
    
    def excluir(self):
        """Exclui o evento selecionado"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem("Atenção", "Selecione um evento para excluir.", tipo="aviso")
            return
            
        if mostrar_mensagem("Confirmação", "Deseja realmente excluir este evento?", tipo="pergunta"):
            excluir_evento(id_selecao)
            mostrar_mensagem("Sucesso", "Evento excluído com sucesso!", tipo="sucesso")
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
        