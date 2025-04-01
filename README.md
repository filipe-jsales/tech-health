# Tech Health - Technical Due Diligence Tool

Tech Health é um MVP que audita a base de código de startups e gera um apêndice de "Saúde Tecnológica" para pitch decks, ajudando startups a demonstrarem robustez técnica para investidores.

## 🚀 Visão Geral

O Tech Health resolve um problema crítico enfrentado por startups em fase inicial: como demonstrar de forma convincente a robustez técnica e gerenciar riscos tecnológicos em seus pitch decks para investidores.

### Proposta de Valor Única

Transforma fraquezas técnicas em pontos fortes estratégicos através de insights claros e orientados por dados que ressoam fortemente com investidores, melhorando significativamente o potencial de captação de recursos de uma startup.

## ✨ Funcionalidades Principais

- **Integração com GitHub/CI-CD** - Conecta-se com repositórios e sistemas de CI/CD para analisar o código-fonte
- **Análise Abrangente** - Avalia qualidade de código, frequência de deploy e dívida técnica
- **Geração Automatizada de Relatórios** - Cria um apêndice de Saúde Tecnológica visualmente atraente
- **Benchmark com Pares** - Compara métricas com benchmarks do setor
- **Recomendações Acionáveis** - Fornece um roteiro de otimização para melhorias técnicas

## 🏗️ Arquitetura do Sistema

O Tech Health é dividido em três componentes principais:

1. **API de Integração** - Conecta-se ao GitHub e sistemas CI/CD para extrair dados
2. **Motor de Análise** - Processa e analisa os dados extraídos
3. **Gerador de Relatório** - Cria um apêndice de Saúde Tecnológica visualmente atraente


## 🛠️ Stack Tecnológico

### Backend
- **Framework**: FastAPI (Python)
- **Integração GitHub**: PyGithub
- **Análise de Código**: radon, pylint
- **Geração de Relatórios**: Jinja2, WeasyPrint

### Frontend
- **Framework**: React
- **Componentes UI**: Chakra UI
- **Visualização de Dados**: Chart.js
- **Estilos**: CSS/SCSS

## 📊 Métricas Analisadas

O Tech Health analisa diversas métricas para fornecer uma visão holística da saúde tecnológica:

### Qualidade de Código
- Complexidade ciclomática
- Índice de manutenibilidade
- Proporção de comentários
- Cobertura de testes

### Atividade de Desenvolvimento
- Frequência de commits
- Distribuição de commits por autor
- Tendências de desenvolvimento

### Dívida Técnica
- Proporção de dívida
- Arquivos críticos
- Dívida por categoria

## 🚦 Como Executar

### Requisitos
- Python 3.8+
- Node.js 14+
- Conta GitHub (para integração)

### Instalação e Configuração

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/tech-health.git
   cd tech-health
   ```

2. Configure o ambiente backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure o ambiente frontend:
   ```bash
   cd frontend
   npm install
   ```

4. Configure as variáveis de ambiente:
   ```
   # Crie um arquivo .env na raiz do projeto
   GITHUB_APP_ID=seu_app_id
   GITHUB_APP_SECRET=seu_app_secret
   ```

5. Execute o backend:
   ```bash
   cd backend
   uvicorn app:app --reload
   ```

6. Execute o frontend:
   ```bash
   cd frontend
   npm start
   ```

7. Acesse o aplicativo em `http://localhost:3000`

## 🔒 Segurança e Privacidade

O Tech Health trata a segurança e privacidade como prioridades máximas:

- **Acesso Somente Leitura** - O sistema utiliza apenas acesso de leitura aos repositórios
- **Armazenamento Seguro** - Armazenamento seguro de tokens e dados sensíveis
- **Confidencialidade** - Garantia de que o código-fonte nunca é compartilhado com terceiros
- **Relatórios Locais** - Os relatórios são gerados localmente, sem enviar dados para serviços externos

## 🧪 Exemplo de Relatório

Os relatórios do Tech Health são projetados para serem facilmente compreendidos por investidores não-técnicos, fornecendo insights claros e acionáveis sobre a saúde tecnológica de uma startup.


## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia o guia de contribuição antes de enviar pull requests.

## 📜 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

## 📬 Contato

Para perguntas ou feedback, por favor abra uma issue no repositório ou entre em contato via email.

