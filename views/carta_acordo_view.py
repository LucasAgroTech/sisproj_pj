import tkinter as tk
from tkinter import ttk
import re
import datetime
from controllers.carta_acordo_controller import adicionar_carta_acordo, listar_cartas_acordo, editar_carta_acordo, excluir_carta_acordo, obter_cartas_por_demanda
from controllers.demanda_controller import adicionar_demanda, listar_demandas, editar_demanda
from controllers.aditivos_controller import adicionar_aditivo, listar_aditivos, obter_aditivos_por_contrato, editar_aditivo, excluir_aditivo
from utils.ui_utils import FormularioBase, criar_botao, TabelaBase, mostrar_mensagem, Estilos
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


class CartaAcordoForm(FormularioBase):
    """Formulário para cadastro e edição de cartas de acordo"""
    
    def __init__(self, master, callback_salvar, callback_cancelar, carta=None):
        """
        Args:
            master: widget pai
            callback_salvar: função a ser chamada quando o formulário for salvo
            callback_cancelar: função a ser chamada quando o formulário for cancelado
            carta: dados da carta para edição (opcional)
        """
        super().__init__(master, "Cadastro de Carta de Acordo" if not carta else "Edição de Carta de Acordo")
        
        self.callback_salvar = callback_salvar
        self.callback_cancelar = callback_cancelar
        self.carta = carta
        self.id_carta = carta[0] if carta else None
        self.modo_edicao = carta is not None
        
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
            codigo_demanda = carta[1]
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
        
        # Garantir que a instituição seja uma das opções válidas
        instituicao_padrao = ""
        if carta and carta[2]:
            if carta[2] in instituicoes_opcoes:
                instituicao_padrao = carta[2]
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
                                      opcoes=[""], padrao=carta[4] if carta else "")
        
        self.form_custeio.adicionar_campo("ta", "TA", tipo="opcoes",
                                      opcoes=[""], padrao=carta[5] if carta else "")
        self.form_custeio.adicionar_campo("pta", "PTA", tipo="opcoes",
                                      opcoes=[""], padrao=carta[6] if carta else "")
        self.form_custeio.adicionar_campo("acao", "Ação", tipo="opcoes",
                                       opcoes=[""], padrao=carta[7] if carta else "")
        self.form_custeio.adicionar_campo("resultado", "Resultado", tipo="opcoes",
                                       opcoes=[""], padrao=carta[8] if carta else "")
        self.form_custeio.adicionar_campo("meta", "Meta", tipo="opcoes",
                                       opcoes=[""], padrao=carta[9] if carta else "")
        
        # Inicializar os campos de custeio com base na instituição selecionada
        self.atualizar_campos_custeio()
        
        # Se estiver em modo de edição, precisamos garantir que os valores sejam carregados corretamente
        if self.modo_edicao and carta:
            # Primeiro, garantir que a instituição esteja corretamente selecionada
            instituicao_widget = self.form_custeio.campos["instituicao"]["widget"]
            if carta[2] in ["OPAS", "FIOCRUZ"]:
                instituicao_widget.set(carta[2])
            
            # Chamar novamente para garantir que os campos dependentes sejam atualizados
            self.atualizar_campos_custeio()
            
            # Configurar os valores salvos para os campos de custeio
            # Atualizar o instrumento
            if carta[3]:  # instrumento
                instrumento_widget = self.form_custeio.campos["instrumento"]["widget"]
                instrumento_widget.set(carta[3])
                
                # Atualizar o TA após definir o instrumento
                if carta[5]:  # ta
                    self.atualizar_ta()
                    ta_widget = self.form_custeio.campos["ta"]["widget"]
                    ta_widget.set(carta[5])
                    
                    # Atualizar o resultado após definir o TA
                    if carta[8]:  # resultado
                        self.atualizar_resultado()
                        resultado_widget = self.form_custeio.campos["resultado"]["widget"]
                        resultado_widget.set(carta[8])
            
            # Atualizar outros campos
            if carta[6]:  # pta
                pta_widget = self.form_custeio.campos["pta"]["widget"]
                pta_widget.set(carta[6])
            
            if carta[7]:  # acao
                acao_widget = self.form_custeio.campos["acao"]["widget"]
                acao_widget.set(carta[7])
            
            if carta[9]:  # meta
                meta_widget = self.form_custeio.campos["meta"]["widget"]
                meta_widget.set(carta[9])
            
            # Garantir que o subprojeto seja carregado corretamente
            if carta[4]:  # subprojeto
                # Criar instância do CusteioManager
                custeio_manager = CusteioManager()
                
                # Carregar subprojetos para a instituição selecionada
                filtros = {'instituicao_parceira': carta[2]}
                subprojetos = custeio_manager.get_distinct_values('subprojeto', filtros)
                
                # Garantir que temos pelo menos uma opção
                if not subprojetos:
                    subprojetos = [""]
                
                # Adicionar o subprojeto da carta se não estiver na lista
                if carta[4] not in subprojetos:
                    subprojetos.append(carta[4])
                
                # Atualizar as opções do widget
                subprojeto_widget = self.form_custeio.campos["subprojeto"]["widget"]
                subprojeto_widget["values"] = subprojetos
                subprojeto_widget.set(carta[4])
        
        # Aba de contrato (terceira aba)
        self.tab_contrato = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_contrato, text="Contrato")
        
        self.form_contrato = FormularioBase(self.tab_contrato, "")
        self.form_contrato.pack(fill=tk.BOTH, expand=True)
        
        self.form_contrato.adicionar_campo("contrato", "Contrato", 
                                       padrao=carta[10] if carta else "", required=True)
        self.form_contrato.adicionar_campo("vigencia_inicial", "Vigência Inicial", tipo="data", 
                                       padrao=carta[11] if carta else "", required=True)
        # Configurar formatação para vigência inicial
        vigencia_inicial_widget = self.form_contrato.campos["vigencia_inicial"]["widget"]
        vigencia_inicial_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_data(vigencia_inicial_widget, e))
        vigencia_inicial_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
        
        self.form_contrato.adicionar_campo("vigencia_final", "Vigência Final", tipo="data", 
                                       padrao=carta[12] if carta else "", required=True)
        # Configurar formatação para vigência final
        vigencia_final_widget = self.form_contrato.campos["vigencia_final"]["widget"]
        vigencia_final_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_data(vigencia_final_widget, e))
        vigencia_final_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
        
        self.form_contrato.adicionar_campo("instituicao_2", "Instituição", 
                                       padrao=carta[13] if carta else "")
        self.form_contrato.adicionar_campo("cnpj", "CNPJ", 
                                       padrao=carta[14] if carta else "")
        # Configurar formatação para CNPJ
        cnpj_widget = self.form_contrato.campos["cnpj"]["widget"]
        cnpj_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_cnpj(cnpj_widget, e))
        cnpj_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
        
        self.form_contrato.adicionar_campo("titulo_projeto", "Título do Projeto", 
                                          padrao=carta[15] if carta else "", required=True)
        self.form_contrato.adicionar_campo("valor_estimado", "Valor Estimado", tipo="numero", 
                                          padrao=carta[17] if carta else "0.00", required=True)
        # Configurar formatação para valor estimado
        valor_estimado_widget = self.form_contrato.campos["valor_estimado"]["widget"]
        valor_estimado_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_valor_brl(valor_estimado_widget, e))
        
        self.form_contrato.adicionar_campo("total_contrato", "Total do Contrato", tipo="numero", 
                                          padrao=carta[18] if carta else "0.00", required=True)
        # Configurar formatação para total do contrato
        total_contrato_widget = self.form_contrato.campos["total_contrato"]["widget"]
        total_contrato_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_valor_brl(total_contrato_widget, e))
        
        self.form_contrato.adicionar_campo("objetivo", "Objetivo", tipo="texto_longo", 
                                          padrao=carta[16] if carta else "", required=True)
        self.form_contrato.adicionar_campo("observacoes", "Observações", tipo="texto_longo", 
                                          padrao=carta[19] if carta else "")
        
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
            colunas = ["id", "oficio", "data_entrada", "data_protocolo", "valor_aditivo", "nova_vigencia_final", "valor_total_atualizado"]
            titulos = {
                "id": "ID",
                "oficio": "Ofício",
                "data_entrada": "Data de Entrada",
                "data_protocolo": "Data de Protocolo",
                "valor_aditivo": "Valor do Aditivo (R$)",
                "nova_vigencia_final": "Nova Vigência Final",
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
        
        # Os botões já foram criados no início do método
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
                if all(campo in valores_demanda for campo in ["data_entrada", "solicitante", "data_protocolo", "oficio", "nup_sei"]):
                    # Se tiver o campo status, incluir na atualização
                    if "status" in valores_demanda:
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
                        # Buscar o status atual da demanda
                        demandas = listar_demandas()
                        status_atual = "Novo"
                        for d in demandas:
                            if d[0] == codigo_demanda and len(d) > 6:
                                status_atual = d[6]
                                break
                                
                        editar_demanda(
                            codigo_demanda,
                            valores_demanda["data_entrada"],
                            valores_demanda["solicitante"],
                            valores_demanda["data_protocolo"],
                            valores_demanda["oficio"],
                            valores_demanda["nup_sei"],
                            status_atual
                        )
                
                # Juntar todos os valores para a carta acordo
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
                    'contrato': valores_contrato["contrato"],
                    'vigencia_inicial': valores_contrato["vigencia_inicial"],
                    'vigencia_final': valores_contrato["vigencia_final"],
                    'instituicao_2': valores_contrato["instituicao_2"],
                    'cnpj': valores_contrato["cnpj"],
                    'titulo_projeto': valores_contrato["titulo_projeto"],
                    'objetivo': valores_contrato["objetivo"],
                    'valor_estimado': self.converter_valor_brl_para_float(valores_contrato["valor_estimado"]),
                    'total_contrato': self.converter_valor_brl_para_float(valores_contrato["total_contrato"]),
                    'observacoes': valores_contrato["observacoes"]
                }
                
                editar_carta_acordo(self.id_carta, **valores)
                mostrar_mensagem("Sucesso", "Carta de Acordo atualizada com sucesso!", tipo="sucesso")
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
                
                # Obter valores da carta
                valores_custeio = self.form_custeio.obter_valores()
                valores_contrato = self.form_contrato.obter_valores()
                
                # Juntar todos os valores
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
                    'contrato': valores_contrato["contrato"],
                    'vigencia_inicial': valores_contrato["vigencia_inicial"],
                    'vigencia_final': valores_contrato["vigencia_final"],
                    'instituicao_2': valores_contrato["instituicao_2"],
                    'cnpj': valores_contrato["cnpj"],
                    'titulo_projeto': valores_contrato["titulo_projeto"],
                    'objetivo': valores_contrato["objetivo"],
                    'valor_estimado': self.converter_valor_brl_para_float(valores_contrato["valor_estimado"]),
                    'total_contrato': self.converter_valor_brl_para_float(valores_contrato["total_contrato"]),
                    'observacoes': valores_contrato["observacoes"]
                }
                
                # Adicionar carta de acordo
                adicionar_carta_acordo(**valores)
                
                mostrar_mensagem("Sucesso", "Demanda e Carta de Acordo cadastradas com sucesso!", tipo="sucesso")
            
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
        
        # Limpar os valores atuais
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
    
    def cancelar(self):
        """Cancela a operação e fecha o formulário"""
        self.callback_cancelar()
        
    def carregar_aditivos(self):
        """Carrega os aditivos do contrato na tabela"""
        if not hasattr(self, 'tabela_aditivos') or not self.id_carta:
            return
            
        self.tabela_aditivos.limpar()
        
        # Obter aditivos do contrato
        aditivos = obter_aditivos_por_contrato(self.id_carta)
        
        # Obter o valor base do contrato (valor estimado)
        valor_base = 0
        cartas = listar_cartas_acordo()
        for carta in cartas:
            if carta[0] == self.id_carta:
                valor_base = float(carta[17]) if carta[17] else 0
                break
        
        # Valor acumulado para calcular o valor total atualizado
        valor_acumulado = valor_base
        
        for aditivo in aditivos:
            # Extrair dados do aditivo
            id_aditivo = aditivo[0]
            tipo_aditivo = aditivo[3]  # Ofício
            descricao = aditivo[4]  # Pode conter data de entrada ou outras informações
            valor_aditivo = float(aditivo[5]) if aditivo[5] else 0
            nova_vigencia_final = aditivo[6]
            data_registro = aditivo[7]  # Pode ser usado como data de protocolo
            
            # Atualizar valor acumulado
            valor_acumulado += valor_aditivo
            
            # Criar um dicionário com os valores do aditivo
            valores = {
                "id": id_aditivo,
                "oficio": tipo_aditivo,
                "data_entrada": descricao,
                "data_protocolo": data_registro,
                "valor_aditivo": valor_aditivo,
                "nova_vigencia_final": nova_vigencia_final,
                "valor_total_atualizado": valor_acumulado
            }
            
            # Formatar valores monetários
            valores["valor_aditivo"] = f"R$ {valores['valor_aditivo']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            valores["valor_total_atualizado"] = f"R$ {valores['valor_total_atualizado']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            self.tabela_aditivos.adicionar_linha(valores, str(id_aditivo))
    
    def adicionar_aditivo(self):
        """Abre o formulário para adicionar um novo aditivo"""
        if not self.id_carta:
            mostrar_mensagem("Atenção", "É necessário salvar o contrato antes de adicionar aditivos.", tipo="aviso")
            return
            
        # Criar uma janela de diálogo para o formulário de aditivo
        dialog = tk.Toplevel(self)
        dialog.title("Adicionar Aditivo")
        dialog.geometry("800x600")
        dialog.transient(self)
        dialog.grab_set()
        
        # Limpar qualquer formulário anterior
        for widget in dialog.winfo_children():
            widget.destroy()
        
        # Formulário para o aditivo
        form_aditivo = FormularioBase(dialog, "Novo Aditivo de Contrato")
        form_aditivo.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Adicionar campos do aditivo
        form_aditivo.adicionar_campo("oficio", "Ofício", padrao="", required=True)
        
        form_aditivo.adicionar_campo("data_entrada", "Data de Entrada", tipo="data", padrao="", required=True)
        # Configurar formatação para data de entrada
        data_entrada_widget = form_aditivo.campos["data_entrada"]["widget"]
        data_entrada_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_data(data_entrada_widget, e))
        data_entrada_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
        
        form_aditivo.adicionar_campo("data_protocolo", "Data de Protocolo", tipo="data", padrao="")
        # Configurar formatação para data de protocolo
        data_protocolo_widget = form_aditivo.campos["data_protocolo"]["widget"]
        data_protocolo_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_data(data_protocolo_widget, e))
        data_protocolo_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
        
        # Buscar os dados de custeio do contrato
        cartas = listar_cartas_acordo()
        carta_atual = None
        for carta in cartas:
            if carta[0] == self.id_carta:
                carta_atual = carta
                break
                
        # Adicionar campos de custeio com os valores do contrato
        form_aditivo.adicionar_campo("instituicao", "Instituição", 
                                    padrao=carta_atual[2] if carta_atual else "")
        form_aditivo.adicionar_campo("instrumento", "Instrumento", 
                                    padrao=carta_atual[3] if carta_atual else "")
        form_aditivo.adicionar_campo("subprojeto", "Subprojeto", 
                                    padrao=carta_atual[4] if carta_atual else "")
        form_aditivo.adicionar_campo("ta", "TA", 
                                    padrao=carta_atual[5] if carta_atual else "")
        form_aditivo.adicionar_campo("pta", "PTA", 
                                    padrao=carta_atual[6] if carta_atual else "")
        form_aditivo.adicionar_campo("acao", "Ação", 
                                    padrao=carta_atual[7] if carta_atual else "")
        
        # Buscar a vigência final atual do contrato
        cartas = listar_cartas_acordo()
        vigencia_final_atual = ""
        for carta in cartas:
            if carta[0] == self.id_carta:
                vigencia_final_atual = carta[12]
                break
        
        form_aditivo.adicionar_campo("nova_vigencia_final", "Nova Vigência Final", tipo="data", 
                                    padrao=vigencia_final_atual, required=True)
        # Configurar formatação para nova vigência final
        nova_vigencia_widget = form_aditivo.campos["nova_vigencia_final"]["widget"]
        nova_vigencia_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_data(nova_vigencia_widget, e))
        nova_vigencia_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
        
        form_aditivo.adicionar_campo("valor_aditivo", "Valor do Aditivo", tipo="numero", 
                                    padrao="0.00", required=True)
        # Configurar formatação para valor do aditivo
        valor_aditivo_widget = form_aditivo.campos["valor_aditivo"]["widget"]
        valor_aditivo_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_valor_brl(valor_aditivo_widget, e))
        
        # Buscar o valor total atual do contrato
        valor_total_atual = 0
        for carta in cartas:
            if carta[0] == self.id_carta:
                valor_total_atual = float(carta[18]) if carta[18] else 0
                break
        
        # Mostrar o valor total atual (somente leitura)
        form_aditivo.adicionar_campo("valor_total_atual", "Valor Total Atual do Contrato", tipo="numero", 
                                    padrao=f"R$ {valor_total_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        valor_total_atual_widget = form_aditivo.campos["valor_total_atual"]["widget"]
        valor_total_atual_widget.configure(state="readonly")
        
        # Frame para botões
        frame_botoes = ttk.Frame(dialog)
        frame_botoes.pack(fill=tk.X, padx=20, pady=10)
        
        # Função para salvar o aditivo
        def salvar_aditivo():
            # Validar o formulário
            valido, mensagem = form_aditivo.validar()
            if not valido:
                mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
                return
            
            try:
                # Obter valores do formulário
                valores = form_aditivo.obter_valores()
                
                # Converter valor do aditivo para float
                valor_aditivo = self.converter_valor_brl_para_float(valores["valor_aditivo"])
                
                # Calcular novo valor total
                novo_valor_total = valor_total_atual + valor_aditivo
                
                # Preparar dados para o aditivo
                dados_aditivo = {
                    'id_contrato': self.id_carta,
                    'tipo_contrato': 'carta_acordo',
                    'tipo_aditivo': valores["oficio"],
                    'descricao': valores["data_entrada"],
                    'valor_aditivo': valor_aditivo,
                    'nova_vigencia_final': valores["nova_vigencia_final"],
                    'data_registro': valores["data_protocolo"] if valores["data_protocolo"] else datetime.datetime.now().strftime("%d/%m/%Y")
                }
                
                # Adicionar o aditivo
                adicionar_aditivo(**dados_aditivo)
                
                mostrar_mensagem("Sucesso", "Aditivo adicionado com sucesso!", tipo="sucesso")
                
                # Fechar o diálogo
                dialog.destroy()
                
                # Recarregar os aditivos na tabela
                self.carregar_aditivos()
                
            except Exception as e:
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
            
        # Criar uma janela de diálogo para o formulário de aditivo
        dialog = tk.Toplevel(self)
        dialog.title("Editar Aditivo" if not somente_leitura else "Visualizar Aditivo")
        dialog.geometry("800x600")
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
        oficio = aditivo_selecionado[3]
        data_entrada = aditivo_selecionado[4]
        valor_aditivo = aditivo_selecionado[5]
        nova_vigencia_final = aditivo_selecionado[6]
        data_protocolo = aditivo_selecionado[7]
        
        # Adicionar campos do aditivo com valores preenchidos
        form_aditivo.adicionar_campo("oficio", "Ofício", padrao=oficio, required=True)
        
        form_aditivo.adicionar_campo("data_entrada", "Data de Entrada", tipo="data", 
                                    padrao=data_entrada, required=True)
        # Configurar formatação para data de entrada
        data_entrada_widget = form_aditivo.campos["data_entrada"]["widget"]
        data_entrada_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_data(data_entrada_widget, e))
        data_entrada_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
        
        form_aditivo.adicionar_campo("data_protocolo", "Data de Protocolo", tipo="data", 
                                    padrao=data_protocolo)
        # Configurar formatação para data de protocolo
        data_protocolo_widget = form_aditivo.campos["data_protocolo"]["widget"]
        data_protocolo_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_data(data_protocolo_widget, e))
        data_protocolo_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
        
        # Buscar os dados de custeio do contrato
        cartas = listar_cartas_acordo()
        carta_atual = None
        for carta in cartas:
            if carta[0] == id_contrato:
                carta_atual = carta
                break
                
        # Adicionar campos de custeio com os valores do contrato
        form_aditivo.adicionar_campo("instituicao", "Instituição", 
                                    padrao=carta_atual[2] if carta_atual else "")
        form_aditivo.adicionar_campo("instrumento", "Instrumento", 
                                    padrao=carta_atual[3] if carta_atual else "")
        form_aditivo.adicionar_campo("subprojeto", "Subprojeto", 
                                    padrao=carta_atual[4] if carta_atual else "")
        form_aditivo.adicionar_campo("ta", "TA", 
                                    padrao=carta_atual[5] if carta_atual else "")
        form_aditivo.adicionar_campo("pta", "PTA", 
                                    padrao=carta_atual[6] if carta_atual else "")
        form_aditivo.adicionar_campo("acao", "Ação", 
                                    padrao=carta_atual[7] if carta_atual else "")
        
        form_aditivo.adicionar_campo("nova_vigencia_final", "Nova Vigência Final", tipo="data", 
                                    padrao=nova_vigencia_final, required=True)
        # Configurar formatação para nova vigência final
        nova_vigencia_widget = form_aditivo.campos["nova_vigencia_final"]["widget"]
        nova_vigencia_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_data(nova_vigencia_widget, e))
        nova_vigencia_widget.bind("<KeyPress>", FormatadorCampos.validar_numerico)
        
        # Formatar valor do aditivo para exibição
        valor_aditivo_formatado = f"R$ {float(valor_aditivo):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if valor_aditivo else "R$ 0,00"
        
        form_aditivo.adicionar_campo("valor_aditivo", "Valor do Aditivo", tipo="numero", 
                                    padrao=valor_aditivo_formatado, required=True)
        # Configurar formatação para valor do aditivo
        valor_aditivo_widget = form_aditivo.campos["valor_aditivo"]["widget"]
        valor_aditivo_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_valor_brl(valor_aditivo_widget, e))
        
        # Buscar o valor total atual do contrato
        cartas = listar_cartas_acordo()
        valor_total_atual = 0
        for carta in cartas:
            if carta[0] == id_contrato:
                valor_total_atual = float(carta[18]) if carta[18] else 0
                break
        
        # Mostrar o valor total atual (somente leitura)
        form_aditivo.adicionar_campo("valor_total_atual", "Valor Total Atual do Contrato", tipo="numero", 
                                    padrao=f"R$ {valor_total_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        valor_total_atual_widget = form_aditivo.campos["valor_total_atual"]["widget"]
        valor_total_atual_widget.configure(state="readonly")
        
        # Frame para botões
        frame_botoes = ttk.Frame(dialog)
        frame_botoes.pack(fill=tk.X, padx=20, pady=10)
        
        # Se for somente leitura, desabilitar todos os campos
        if somente_leitura:
            for campo_nome, campo_info in form_aditivo.campos.items():
                try:
                    widget = campo_info["widget"]
                    widget.configure(state="disabled")
                except Exception:
                    pass
        
        # Função para salvar as alterações do aditivo
        def salvar_alteracoes():
            # Validar o formulário
            valido, mensagem = form_aditivo.validar()
            if not valido:
                mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
                return
            
            try:
                # Obter valores do formulário
                valores = form_aditivo.obter_valores()
                
                # Converter valor do aditivo para float
                valor_aditivo_novo = self.converter_valor_brl_para_float(valores["valor_aditivo"])
                
                # Preparar dados para atualizar o aditivo
                dados_aditivo = {
                    'id_contrato': id_contrato,
                    'tipo_contrato': tipo_contrato,
                    'tipo_aditivo': valores["oficio"],
                    'descricao': valores["data_entrada"],
                    'valor_aditivo': valor_aditivo_novo,
                    'nova_vigencia_final': valores["nova_vigencia_final"],
                    'data_registro': valores["data_protocolo"] if valores["data_protocolo"] else data_protocolo
                }
                
                # Atualizar o aditivo
                editar_aditivo(id_aditivo, **dados_aditivo)
                
                mostrar_mensagem("Sucesso", "Aditivo atualizado com sucesso!", tipo="sucesso")
                
                # Fechar o diálogo
                dialog.destroy()
                
                # Recarregar os aditivos na tabela
                self.carregar_aditivos()
                
            except Exception as e:
                mostrar_mensagem("Erro", f"Erro ao atualizar aditivo: {str(e)}", tipo="erro")
        
        # Botões de ação
        if somente_leitura:
            criar_botao(frame_botoes, "Fechar", dialog.destroy, "Primario", 15).pack(side=tk.RIGHT)
        else:
            criar_botao(frame_botoes, "Cancelar", dialog.destroy, "Secundario", 15).pack(side=tk.RIGHT, padx=5)
            criar_botao(frame_botoes, "Salvar", salvar_alteracoes, "Primario", 15).pack(side=tk.RIGHT)
    
    def excluir_aditivo(self):
        """Exclui o aditivo selecionado"""
        if not hasattr(self, 'tabela_aditivos'):
            return
            
        id_selecao = self.tabela_aditivos.obter_selecao()
        if not id_selecao:
            mostrar_mensagem("Atenção", "Selecione um aditivo para excluir.", tipo="aviso")
            return
            
        if mostrar_mensagem("Confirmação", "Deseja realmente excluir este aditivo?", tipo="pergunta"):
            try:
                excluir_aditivo(id_selecao)
                mostrar_mensagem("Sucesso", "Aditivo excluído com sucesso!", tipo="sucesso")
                self.carregar_aditivos()
            except Exception as e:
                mostrar_mensagem("Erro", f"Erro ao excluir aditivo: {str(e)}", tipo="erro")


class CartaAcordoView:
    """Tela principal de listagem e gestão de cartas de acordo"""
    
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
            self.master.title("Gestão de Cartas de Acordo")
        
        # Configura estilos
        Estilos.configurar()
        
        # Frame principal
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de cabeçalho
        frame_cabecalho = ttk.Frame(self.frame)
        frame_cabecalho.pack(fill=tk.X, pady=(0, 10))
        
        titulo = "Gestão de Cartas de Acordo"
        if codigo_demanda:
            demandas = listar_demandas()
            for d in demandas:
                if d[0] == int(codigo_demanda):
                    titulo += f" - Demanda {codigo_demanda} ({d[2]})"
                    break
                    
        ttk.Label(frame_cabecalho, text=titulo, style="Titulo.TLabel").pack(side=tk.LEFT)
        criar_botao(frame_cabecalho, "Nova Carta", self.adicionar, "Primario", 15).pack(side=tk.RIGHT)
        
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
            criar_botao(frame_pesquisa, "Ver Todas", self.ver_todas, "Primario", 12).pack(side=tk.RIGHT)
        else:
            criar_botao(frame_pesquisa, "Voltar", self.voltar, "Primario", 12).pack(side=tk.RIGHT)
        
        # Tabela de cartas - mostrando apenas informações mais importantes
        colunas = ["id", "codigo_demanda", "instituicao", "titulo_projeto", "vigencia_inicial", 
                  "vigencia_final", "valor_estimado"]
        titulos = {
            "id": "ID",
            "codigo_demanda": "Demanda",
            "instituicao": "Instituição",
            "titulo_projeto": "Título do Projeto",
            "vigencia_inicial": "Início Vigência",
            "vigencia_final": "Fim Vigência",
            "valor_estimado": "Valor Estimado (R$)"
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
        """Carrega os dados das cartas na tabela"""
        self.tabela.limpar()
        
        if self.codigo_demanda:
            cartas = obter_cartas_por_demanda(self.codigo_demanda)
        else:
            cartas = listar_cartas_acordo()
        
        for carta in cartas:
            # Se tiver filtro, verifica se carta contém o texto do filtro em algum campo
            if filtro:
                texto_filtro = filtro.lower()
                texto_carta = ' '.join(str(campo).lower() for campo in carta)
                if texto_filtro not in texto_carta:
                    continue
                    
            # Criar um dicionário com os valores da carta
            # Garantir que estamos mapeando corretamente os valores para as colunas
            valores = {
                "id": carta[0],
                "codigo_demanda": carta[1],
                "instituicao": carta[2],
                "titulo_projeto": carta[15],
                "vigencia_inicial": carta[11],
                "vigencia_final": carta[12],
                "valor_estimado": carta[17]
            }
            
            # Formatar valor monetário
            if "valor_estimado" in valores:
                try:
                    valores["valor_estimado"] = f"R$ {float(valores['valor_estimado']):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                except ValueError:
                    # Mantém o valor original se não for possível converter para float
                    valores["valor_estimado"] = f"R$ {valores['valor_estimado']}"
                
            self.tabela.adicionar_linha(valores, str(carta[0]))
    
    def pesquisar(self):
        """Filtra as cartas conforme o texto de pesquisa"""
        texto = self.pesquisa_entry.get().strip()
        if texto:
            self.carregar_dados(texto)
        else:
            self.carregar_dados()
    
    def limpar_pesquisa(self):
        """Limpa o campo de pesquisa e recarrega todos os dados"""
        self.pesquisa_entry.delete(0, tk.END)
        self.carregar_dados()
        
    def ver_todas(self):
        """Remove o filtro por demanda"""
        self.codigo_demanda = None
        self.carregar_dados()
        if isinstance(self.master, (tk.Tk, tk.Toplevel)):
            self.master.title("Gestão de Cartas de Acordo")
        
    def voltar(self):
        """Volta para a tela anterior (implementar conforme necessário)"""
        pass
    
    def adicionar(self):
        """Abre o formulário para adicionar uma nova carta"""
        # Oculta o frame principal
        self.frame.pack_forget()
        
        # Cria e exibe o formulário
        self.formulario = CartaAcordoForm(
            self.frame_formulario, 
            callback_salvar=self.salvar_formulario, 
            callback_cancelar=self.cancelar_formulario
        )
        self.formulario.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.frame_formulario.pack(fill=tk.BOTH, expand=True)
    
    def visualizar(self):
        """Abre o formulário para visualizar a carta selecionada (somente leitura)"""
        self.editar(somente_leitura=True)
    
    def editar(self, somente_leitura=False):
        """Abre o formulário para editar a carta selecionada"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem("Atenção", "Selecione uma carta para editar.", tipo="aviso")
            return
            
        # Busca a carta selecionada
        cartas = listar_cartas_acordo()
        for carta in cartas:
            if str(carta[0]) == id_selecao:
                # Oculta o frame principal
                self.frame.pack_forget()
                
                # Cria o formulário de edição
                self.formulario = CartaAcordoForm(
                    self.frame_formulario, 
                    callback_salvar=self.salvar_formulario if not somente_leitura else self.cancelar_formulario, 
                    callback_cancelar=self.cancelar_formulario,
                    carta=carta
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
                            observacoes_widget = self.formulario.form_contrato.campos["observacoes"]["widget"]
                            
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
        """Exclui a carta selecionada"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem("Atenção", "Selecione uma carta para excluir.", tipo="aviso")
            return
            
        if mostrar_mensagem("Confirmação", "Deseja realmente excluir esta carta de acordo?", tipo="pergunta"):
            excluir_carta_acordo(id_selecao)
            mostrar_mensagem("Sucesso", "Carta de acordo excluída com sucesso!", tipo="sucesso")
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
