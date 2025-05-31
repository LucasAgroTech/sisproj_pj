import tkinter as tk
from tkinter import ttk
import re
import datetime
from controllers.produtos_servicos_controller import adicionar_produto_servico, listar_produtos_servicos, editar_produto_servico
from controllers.demanda_controller import adicionar_demanda, listar_demandas, editar_demanda
from controllers.fornecedores_controller import adicionar_fornecedor, buscar_fornecedor_por_nome, listar_fornecedores
from utils.ui_utils import mostrar_mensagem

def salvar_produto_servico(self):
    """Salva os dados do formulário de produto/serviço"""
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
                # Criar um novo fornecedor com valores padrão
                adicionar_fornecedor(
                    fornecedor,
                    "",  # CNPJ (não obrigatório)
                    "Cadastrado automaticamente"  # observação
                )
            
            # Obter valores de custeio
            valores_custeio = self.form_custeio.obter_valores()
            
            # Juntar todos os valores para o produto/serviço
            valores = {
                'codigo_demanda': codigo_demanda,
                'fornecedor': fornecedor,
                'modalidade': valores_contrato["modalidade"],
                'objetivo': valores_contrato["objetivo"],
                'vigencia_inicial': valores_contrato["vigencia_inicial"],
                'vigencia_final': valores_contrato["vigencia_final"],
                'observacao': valores_contrato["observacao"],
                'valor_estimado': self.converter_valor_brl_para_float(valores_contrato["valor_estimado"]),
                'total_contrato': self.converter_valor_brl_para_float(valores_contrato["total_contrato"]),
                'instituicao': valores_custeio.get("instituicao", ""),
                'instrumento': valores_custeio.get("instrumento", ""),
                'subprojeto': valores_custeio.get("subprojeto", ""),
                'ta': valores_custeio.get("ta", ""),
                'pta': valores_custeio.get("pta", ""),
                'acao': valores_custeio.get("acao", ""),
                'resultado': valores_custeio.get("resultado", ""),
                'meta': valores_custeio.get("meta", "")
            }
            
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
            valores_contrato = self.form_contrato.obter_valores()
            
            # Obter fornecedor do combobox
            fornecedor = self.fornecedor_combobox.get()
            
            # Verificar se o fornecedor existe, se não, criar
            fornecedor_obj = buscar_fornecedor_por_nome(fornecedor)
            if not fornecedor_obj:
                # Criar um novo fornecedor com valores padrão
                adicionar_fornecedor(
                    fornecedor,
                    "",  # CNPJ (não obrigatório)
                    "Cadastrado automaticamente"  # observação
                )
            
            # Obter valores de custeio
            valores_custeio = self.form_custeio.obter_valores()
            
            # Juntar todos os valores para o produto/serviço
            valores = {
                'codigo_demanda': codigo_demanda,
                'fornecedor': fornecedor,
                'modalidade': valores_contrato["modalidade"],
                'objetivo': valores_contrato["objetivo"],
                'vigencia_inicial': valores_contrato["vigencia_inicial"],
                'vigencia_final': valores_contrato["vigencia_final"],
                'observacao': valores_contrato["observacao"],
                'valor_estimado': self.converter_valor_brl_para_float(valores_contrato["valor_estimado"]),
                'total_contrato': self.converter_valor_brl_para_float(valores_contrato["total_contrato"]),
                'instituicao': valores_custeio.get("instituicao", ""),
                'instrumento': valores_custeio.get("instrumento", ""),
                'subprojeto': valores_custeio.get("subprojeto", ""),
                'ta': valores_custeio.get("ta", ""),
                'pta': valores_custeio.get("pta", ""),
                'acao': valores_custeio.get("acao", ""),
                'resultado': valores_custeio.get("resultado", ""),
                'meta': valores_custeio.get("meta", "")
            }
            
            # Adicionar produto/serviço
            adicionar_produto_servico(**valores)
            
            mostrar_mensagem("Sucesso", "Demanda e Produto/Serviço cadastrados com sucesso!", tipo="sucesso")
        
        self.callback_salvar()
    except Exception as e:
        mostrar_mensagem("Erro", f"Erro ao salvar: {str(e)}", tipo="erro")

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

def abrir_dialogo_novo_fornecedor(self):
    """Abre o diálogo para adicionar um novo fornecedor"""
    dialog = tk.Toplevel(self)
    dialog.title("Novo Fornecedor")
    dialog.geometry("600x400")
    dialog.transient(self)
    dialog.grab_set()
    
    # Formulário para o novo fornecedor
    from utils.ui_utils import FormularioBase, criar_botao
    form = FormularioBase(dialog, "Cadastro de Fornecedor")
    form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Adicionar campos
    form.adicionar_campo("razao_social", "Razão Social", padrao="", required=True)
    
    form.adicionar_campo("cnpj", "CNPJ", padrao="")
    # Configurar formatação para CNPJ
    from views.produtos_servicos_view import FormatadorCampos
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

def carregar_fornecedores(self):
    """Carrega os fornecedores existentes no combobox"""
    try:
        fornecedores = listar_fornecedores()
        fornecedores_texto = [fornecedor[1] for fornecedor in fornecedores]  # Pega apenas o campo 'razao_social'
        self.fornecedor_combobox['values'] = fornecedores_texto
    except Exception as e:
        print(f"Erro ao carregar fornecedores: {e}")

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
    from utils.custeio_utils import CusteioManager
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
    from utils.custeio_utils import CusteioManager
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
    from utils.custeio_utils import CusteioManager
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
