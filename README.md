# SISPROJ - PESSOA JURÍDICA

Sistema de gerenciamento de projetos e contratos para pessoa jurídica, desenvolvido para o setor de saúde.

## Alterações Recentes

- Atualização do nome do sistema para "SISPROJ - PESSOA JURÍDICA"
- Novo esquema de cores com foco na área da saúde:
  - Verde-azulado (teal) como cor principal
  - Verde médio como cor secundária
  - Interface clara e amigável
  - Melhor contraste visual (texto escuro em fundo claro, texto claro em fundo escuro)

## Recursos

- Gestão de demandas
- Controle de cartas de acordo
- Gerenciamento de eventos
- Registro de produtos e serviços
- Geração de relatórios
- Interface intuitiva

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual Python:
   ```
   python -m venv venv
   ```
3. Ative o ambiente virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
5. Execute a aplicação:
   ```
   python main.py
   ```

## Estrutura do Projeto

- `main.py` - Ponto de entrada da aplicação
- `models/` - Modelos de dados e interação com banco de dados
- `views/` - Interfaces de usuário
- `controllers/` - Lógica de negócios
- `utils/` - Utilidades e ferramentas comuns

## Cores do Sistema

- **Cor primária**: Verde-azulado (#00796B)
- **Cor secundária**: Verde médio (#4CAF50)
- **Alerta**: Âmbar (#FFA000)
- **Perigo**: Vermelho (#D32F2F)
- **Fundo**: Branco (#FFFFFF)
- **Texto principal**: Quase preto (#212121)
- **Detalhes**: Verde-azulado médio (#26A69A)

## Funcionalidades Implementadas

### Demandas
- Listagem de todas as demandas
- Cadastro de novas demandas
- Edição e exclusão de demandas existentes
- Visualização detalhada

### Cartas de Acordo
- Listagem de todas as cartas de acordo
- Cadastro de novas cartas de acordo
- Edição e exclusão de cartas existentes
- Visualização detalhada
- Filtro por demanda

### Eventos
- Listagem de todos os eventos
- Cadastro de novos eventos
- Edição e exclusão de eventos existentes
- Visualização detalhada
- Filtro por demanda

### Produtos e Serviços
- Listagem de todos os produtos/serviços
- Cadastro de novos produtos/serviços
- Edição e exclusão de produtos/serviços existentes
- Visualização detalhada
- Filtro por demanda

## Módulos do Sistema

- **Dashboard**: Visão geral com estatísticas e dados recentes
- **Gestão de Demandas**: Controle de todas as demandas recebidas
- **Cartas de Acordo**: Gestão de contratos do tipo carta acordo
- **Eventos**: Gestão de contratos do tipo evento
- **Produtos/Serviços**: Gestão de contratos do tipo produto ou serviço
- **Aditivos**: Gestão de aditivos contratuais (em desenvolvimento)
- **Relatórios**: Geração de relatórios (em desenvolvimento)

## Como Executar

1. Certifique-se de ter o Python 3.x instalado
2. Execute o arquivo principal:
   ```
   python main.py
   ```
3. Faça login usando as credenciais padrão:
   - Usuário: admin
   - Senha: admin

## Estrutura do Projeto

- **models/**: Modelos e conexão com banco de dados
- **views/**: Interfaces gráficas do sistema
- **controllers/**: Lógica de negócio e operações
- **utils/**: Funções e classes utilitárias

# Alterações no Sistema de Gestão de Demandas e Contratos

## Principais Mudanças Implementadas

1. **Remoção da Tela de Demandas Independente**
   - A tela de Demandas foi removida do menu lateral
   - O card de estatísticas de Demandas foi removido do Dashboard
   - A tabela de Demandas Recentes foi substituída por Eventos Recentes

2. **Integração do Cadastro de Demanda nas Telas Principais**
   - Cada tela (Carta Acordo, Produtos e Serviços, Eventos) agora inclui diretamente um formulário de Demanda
   - O cadastro é feito em uma aba específica "Demanda" nos formulários

3. **Implementação de Contratos Vinculados**
   - Foi criado um novo controller para gerenciar contratos
   - Cada tela principal agora inclui uma aba para cadastro de contrato
   - Os contratos são automaticamente vinculados à entidade principal (Carta Acordo, Produto/Serviço ou Evento)

4. **Alterações nas Interfaces**
   - Todos os formulários foram atualizados para usar o novo fluxo de cadastro
   - O Dashboard foi atualizado para refletir as novas estruturas

## Nova Estrutura de Dados

Foi adicionada uma nova tabela `contratos` que possui os seguintes campos:
- `id`: Identificador único do contrato
- `tipo_contrato`: Tipo da entidade relacionada ('carta_acordo', 'produtos_servicos', 'eventos')
- `id_referencia`: ID da entidade relacionada
- `numero_contrato`: Número do contrato
- `data_assinatura`: Data de assinatura do contrato
- `data_registro`: Data de registro do contrato no sistema
- `observacoes`: Observações adicionais sobre o contrato

## Novo Fluxo de Cadastro

1. O usuário escolhe qual tipo de documento deseja cadastrar (Carta Acordo, Produto/Serviço ou Evento)
2. No formulário, preenche os dados da Demanda (primeira aba)
3. Preenche os dados específicos da entidade escolhida
4. Preenche os dados do Contrato vinculado
5. Ao salvar, o sistema cria automaticamente:
   - Uma nova Demanda
   - A entidade escolhida, vinculada à Demanda
   - Um Contrato, vinculado à entidade 