import tkinter as tk
from tkinter import ttk
import datetime
from controllers.aditivos_controller import adicionar_aditivo as controller_adicionar_aditivo, listar_aditivos, obter_aditivos_por_contrato, editar_aditivo, excluir_aditivo
from utils.ui_utils import FormularioBase, criar_botao, mostrar_mensagem
from views.produtos_servicos_view import FormatadorCampos

def adicionar_aditivo(self):
    """Abre o formulário para adicionar um novo aditivo"""
    if not self.id_produto:
        mostrar_mensagem("Atenção", "É necessário salvar o produto/serviço primeiro para adicionar aditivos.", tipo="aviso")
        return
        
    # Criar uma janela de diálogo para o formulário de aditivo
    dialog = tk.Toplevel(self)
    dialog.title("Adicionar Aditivo")
    dialog.geometry("600x400")
    dialog.transient(self)
    dialog.grab_set()
    
    # Formulário para o aditivo
    form = FormularioBase(dialog, "Novo Aditivo de Contrato")
    form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Adicionar campos do aditivo
    form.adicionar_campo("objetivo", "Objetivo", tipo="texto_longo", padrao="", required=True)
    
    # Obter valor total atual do contrato
    valor_total_atual = float(self.produto[9]) if self.produto and self.produto[9] else 0.0
    
    # Campo: valor total atual (somente leitura) - mostrar antes do valor do aditivo para contexto
    form.adicionar_campo("valor_total_atual", "Valor Total Atual do Contrato", tipo="numero", 
                        padrao=f"R$ {valor_total_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    valor_total_atual_widget = form.campos["valor_total_atual"]["widget"]
    valor_total_atual_widget.configure(state="readonly")
    
    # Campo obrigatório: valor do aditivo
    form.adicionar_campo("valor_aditivo", "Valor do Aditivo", tipo="numero", 
                        padrao="0.00", required=True)
    # Configurar formatação para valor do aditivo
    valor_aditivo_widget = form.campos["valor_aditivo"]["widget"]
    valor_aditivo_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_valor_brl(valor_aditivo_widget, e))
    
    # Campo calculado: novo valor total (será atualizado dinamicamente)
    form.adicionar_campo("novo_valor_total", "Novo Valor Total do Contrato", tipo="numero", 
                        padrao=f"R$ {valor_total_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    novo_valor_total_widget = form.campos["novo_valor_total"]["widget"]
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
    
    # Frame para botões
    frame_botoes = ttk.Frame(dialog)
    frame_botoes.pack(fill=tk.X, padx=20, pady=10)
    
    # Função para salvar o aditivo
    def salvar_aditivo():
        # Validar o formulário
        valido, mensagem = form.validar()
        if not valido:
            mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
            return
        
        try:
            # Obter valores do formulário
            valores = form.obter_valores()
            
            # Converter valor do aditivo para float
            valor_aditivo = self.converter_valor_brl_para_float(valores["valor_aditivo"])
            
            if valor_aditivo <= 0:
                mostrar_mensagem("Erro de Validação", "O valor do aditivo deve ser maior que zero.", tipo="erro")
                return
            
            # Preparar dados para o aditivo
            dados_aditivo = {
                'id_contrato': self.id_produto,
                'tipo_contrato': 'produtos_servicos',
                'tipo_aditivo': "",  # Campo vazio
                'descricao': valores["objetivo"],
                'valor_aditivo': valor_aditivo,
                'nova_vigencia_final': "",  # Campo vazio para produtos/serviços
                'data_registro': datetime.datetime.now().strftime("%d/%m/%Y")
            }
            
            # Adicionar o aditivo
            controller_adicionar_aditivo(**dados_aditivo)
            
            mostrar_mensagem("Sucesso", f"Aditivo de R$ {valor_aditivo:,.2f} adicionado com sucesso!\nValor total do contrato atualizado automaticamente.", tipo="sucesso")
            
            # Fechar o diálogo
            dialog.destroy()
            
            # Recarregar os aditivos na tabela
            self.carregar_aditivos()
            
            # Recarregar também o formulário principal para mostrar o valor atualizado
            if hasattr(self, 'form_contrato'):
                novo_valor_total = valor_total_atual + valor_aditivo
                total_contrato_widget = self.form_contrato.campos["total_contrato"]["widget"]
                total_contrato_widget.delete(0, tk.END)
                total_contrato_widget.insert(0, f"R$ {novo_valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
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
    
    # Verificar se é o último aditivo (apenas no modo de edição)
    if not somente_leitura:
        try:
            aditivos_produto = obter_aditivos_por_contrato(self.id_produto, "produtos_servicos")
            if not aditivos_produto or aditivos_produto[-1][0] != int(id_selecao):
                mostrar_mensagem("Atenção", "Apenas o último aditivo pode ser editado. Este não é o último aditivo do contrato.", tipo="aviso")
                return
        except Exception as e:
            mostrar_mensagem("Erro", f"Erro ao verificar posição do aditivo: {str(e)}", tipo="erro")
            return
        
    # Criar uma janela de diálogo para o formulário de aditivo
    dialog = tk.Toplevel(self)
    dialog.title("Editar Aditivo" if not somente_leitura else "Visualizar Aditivo")
    dialog.geometry("600x400")
    dialog.transient(self)
    dialog.grab_set()
    
    # Formulário para o aditivo
    form = FormularioBase(dialog, "Editar Aditivo de Contrato" if not somente_leitura else "Detalhes do Aditivo")
    form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Extrair dados do aditivo
    id_aditivo = aditivo_selecionado[0]
    id_contrato = aditivo_selecionado[1]
    tipo_contrato = aditivo_selecionado[2]
    objetivo = aditivo_selecionado[4]  # descricao
    valor_aditivo = aditivo_selecionado[5]
    
    # Adicionar campos do aditivo com valores preenchidos
    form.adicionar_campo("objetivo", "Objetivo", tipo="texto_longo", padrao=objetivo, required=True)
    
    # Obter valor total atual do contrato
    valor_total_atual = float(self.produto[9]) if self.produto and self.produto[9] else 0.0
    
    # Formatar valor do aditivo para exibição
    valor_aditivo_formatado = f"R$ {float(valor_aditivo):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if valor_aditivo else "R$ 0,00"
    
    form.adicionar_campo("valor_aditivo", "Valor do Aditivo", tipo="numero", 
                        padrao=valor_aditivo_formatado, required=True)
    # Configurar formatação para valor do aditivo
    valor_aditivo_widget = form.campos["valor_aditivo"]["widget"]
    valor_aditivo_widget.bind("<KeyRelease>", lambda e: FormatadorCampos.formatar_valor_brl(valor_aditivo_widget, e))
    
    # Mostrar o valor total atual (somente leitura)
    form.adicionar_campo("valor_total_atual", "Valor Total Atual do Contrato", tipo="numero", 
                        padrao=f"R$ {valor_total_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    valor_total_atual_widget = form.campos["valor_total_atual"]["widget"]
    valor_total_atual_widget.configure(state="readonly")
    
    # Frame para botões
    frame_botoes = ttk.Frame(dialog)
    frame_botoes.pack(fill=tk.X, padx=20, pady=10)
    
    # Se for somente leitura, desabilitar todos os campos editáveis
    if somente_leitura:
        try:
            form.campos["objetivo"]["widget"].configure(state="disabled")
            valor_aditivo_widget.configure(state="disabled")
        except Exception:
            pass
    
    # Função para salvar as alterações do aditivo
    def salvar_alteracoes():
        # Validar o formulário
        valido, mensagem = form.validar()
        if not valido:
            mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
            return
        
        try:
            # Obter valores do formulário
            valores = form.obter_valores()
            
            # Converter valor do aditivo para float
            valor_aditivo_novo = self.converter_valor_brl_para_float(valores["valor_aditivo"])
            
            if valor_aditivo_novo <= 0:
                mostrar_mensagem("Erro de Validação", "O valor do aditivo deve ser maior que zero.", tipo="erro")
                return
            
            # Preparar dados para atualizar o aditivo
            dados_aditivo = {
                'id_contrato': id_contrato,
                'tipo_contrato': tipo_contrato,
                'tipo_aditivo': "",  # Campo vazio
                'descricao': valores["objetivo"],
                'valor_aditivo': valor_aditivo_novo,
                'nova_vigencia_final': "",  # Campo vazio
                'data_registro': datetime.datetime.now().strftime("%d/%m/%Y")
            }
            
            # Atualizar o aditivo
            editar_aditivo(id_aditivo, **dados_aditivo)
            
            mostrar_mensagem("Sucesso", f"Aditivo atualizado com sucesso!\nValor total do contrato recalculado automaticamente.", tipo="sucesso")
            
            # Fechar o diálogo
            dialog.destroy()
            
            # Recarregar os aditivos na tabela
            self.carregar_aditivos()
            
            # Recarregar também o formulário principal para mostrar o valor atualizado
            if hasattr(self, 'form_contrato'):
                # Calcular o novo valor total (valor atual - valor antigo + valor novo)
                novo_valor_total = valor_total_atual - float(valor_aditivo) + valor_aditivo_novo
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
        aditivos_produto = obter_aditivos_por_contrato(self.id_produto, "produtos_servicos")
        if not aditivos_produto:
            mostrar_mensagem("Erro", "Nenhum aditivo encontrado para este produto/serviço.", tipo="erro")
            return
            
        if aditivos_produto[-1][0] != int(id_selecao):
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
            # Excluir o aditivo
            excluir_aditivo(id_selecao)
            
            mostrar_mensagem("Sucesso", f"Aditivo excluído com sucesso!\nValor total do contrato atualizado automaticamente.", tipo="sucesso")
            
            # Recarregar os aditivos na tabela
            self.carregar_aditivos()
            
            # Recarregar também o formulário principal para mostrar o valor atualizado
            if hasattr(self, 'form_contrato'):
                # Obter valor total atual do contrato
                valor_total_atual = float(self.produto[9]) if self.produto and self.produto[9] else 0.0
                
                # Calcular o novo valor total (valor atual - valor do aditivo)
                novo_valor_total = valor_total_atual - valor_aditivo
                total_contrato_widget = self.form_contrato.campos["total_contrato"]["widget"]
                total_contrato_widget.delete(0, tk.END)
                total_contrato_widget.insert(0, f"R$ {novo_valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
        except ValueError as ve:
            # Tratar especificamente a exceção de regra de negócio
            mostrar_mensagem("Regra de Negócio", str(ve), tipo="aviso")
        except Exception as e:
            mostrar_mensagem("Erro", f"Erro ao excluir aditivo: {str(e)}", tipo="erro")

def carregar_aditivos(self):
    """Carrega os aditivos do contrato na tabela"""
    if not hasattr(self, 'tabela_aditivos') or not self.id_produto:
        return
        
    self.tabela_aditivos.limpar()
    
    # Obter aditivos do contrato
    aditivos = obter_aditivos_por_contrato(self.id_produto, "produtos_servicos")
    
    # Obter o valor base do contrato (valor estimado)
    valor_base = float(self.produto[8]) if self.produto and self.produto[8] else 0
    
    # Valor acumulado para calcular o valor total atualizado
    valor_acumulado = valor_base
    
    for aditivo in aditivos:
        # Extrair dados do aditivo
        id_aditivo = aditivo[0]
        objetivo = aditivo[4]  # descricao
        valor_aditivo = float(aditivo[5]) if aditivo[5] else 0
        
        # Atualizar valor acumulado
        valor_acumulado += valor_aditivo
        
        # Criar um dicionário com os valores do aditivo
        valores = {
            "id": id_aditivo,
            "objetivo": objetivo,
            "valor_aditivo": valor_aditivo,
            "valor_total_atualizado": valor_acumulado
        }
        
        # Formatar valores monetários
        valores["valor_aditivo"] = f"R$ {valores['valor_aditivo']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        valores["valor_total_atualizado"] = f"R$ {valores['valor_total_atualizado']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        self.tabela_aditivos.adicionar_linha(valores, str(id_aditivo))
