# DENTEFIER - Sistema Odontolegal

![Logo Dentefier](logo_dentefier.png)

## Visão Geral
O DENTEFIER é um sistema completo para gerenciamento de casos odontolegais que combina um frontend visual com um backend inteligente. O sistema permite o registro, análise e visualização de casos odontológicos com recursos de machine learning para identificar padrões e fatores determinantes.

## Frontend (Interface do Usuário)

### Recursos Principais
1. **Dashboard Analítico**:
   - Gráfico de rosca interativo para distribuição de casos
   - Histograma de distribuição de idade das vítimas
   - Visualização de fatores determinantes nos tipos de caso
   
2. **Filtros Avançados**:
   - Seleção por período (data inicial e final)
   - Escolha de variáveis para análise (tipo de caso, localização, etnia)
   
3. **Recursos de Acessibilidade**:
   - Controles de contraste
   - Ajuste de tamanho de fonte
   - Design responsivo

4. **Navegação Intuitiva**:
   - Gerenciamento de casos
   - Controle de usuários (para administradores)
   - Painéis de visualização de dados

### Tecnologias Utilizadas
- HTML5, CSS3 (com design responsivo)
- Chart.js para visualizações gráficas
- JavaScript Vanilla (ES6+)
- Layout moderno com Flexbox e Grid

## Backend (Sistema de Gerenciamento)

### Recursos Principais
1. **Gestão de Casos**:
   - CRUD completo de casos odontolegais
   - Validação de dados estruturados
   - Geração de dados iniciais para demonstração

2. **Modelo Preditivo**:
   - Classificação de tipos de caso usando XGBoost
   - Pré-processamento de dados com OneHotEncoder
   - Pipeline completo de machine learning

3. **Análise de Dados**:
   - Endpoint para coeficientes do modelo
   - Cálculo de importância de características
   - Suporte para análise estatística

4. **Integração com MongoDB**:
   - Conexão segura com tratamento de erros
   - Operações otimizadas para consultas
   - Estrutura de dados documental flexível

### Tecnologias Utilizadas
- Python 3.9+
- Flask (framework web)
- MongoDB (banco de dados)
- XGBoost (modelo de machine learning)
- Scikit-learn (pré-processamento)
- Pickle (serialização de modelos)

## Integração Frontend-Backend

### Fluxo de Dados

![Fluxo Dados](mermaid-fluxo.png)

### Endpoints Utilizados
| Endpoint                  | Método | Função                                | Uso no Frontend               |
|---------------------------|--------|---------------------------------------|-------------------------------|
| `/api/casos`              | GET    | Listar todos os casos                 | Gráficos de rosca e idade     |
| `/api/modelo/coeficientes`| GET    | Obter coeficientes do modelo          | Gráfico de fatores determinantes |
| `/api/casos`              | POST   | Criar novo caso                       | Formulário de novo caso       |
| `/api/casos/<data>`       | GET    | Buscar caso por data                  | Detalhes de caso específico   |
| `/api/casos/<data>`       | DELETE | Excluir caso                          | Gerenciamento de casos        |

## Configuração do Ambiente

### Pré-requisitos
- Python 3.9+
- MongoDB (local ou Atlas)
- Node.js (para desenvolvimento frontend opcional)

### Passos de Instalação
1. **Configurar variáveis de ambiente**:
   ```bash
   cp .env.example .env
   # Editar .env com suas credenciais do MongoDB
   ```

2. **Instalar dependências Python**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Treinar o modelo inicial**:
   ```bash
   python train_model.py
   ```

4. **Iniciar o servidor backend**:
   ```bash
   python app.py
   ```

5. **Configurar frontend**:
   - O frontend está pronto para uso nos arquivos HTML/CSS/JS
   - Pode ser servido por qualquer servidor web estático

### Variáveis de Ambiente
| Variável    | Descrição                           | Exemplo                     |
|-------------|-------------------------------------|-----------------------------|
| `MONGO_URI` | URI de conexão com o MongoDB        | `mongodb+srv://user:pass@cluster` |
| `PORT`      | Porta para o servidor Flask         | `5000`                      |

## Estrutura de Dados

### Modelo de Caso
```javascript
{
  "data_do_caso": "2025-01-15",
  "tipo_do_caso": "Maloclusão",
  "localizacao": "São Paulo",
  "vitima": {
    "etnia": "Branca",
    "idade": 35
  }
}
```

### Modelo de Treinamento
O pipeline de machine learning consiste em:
1. Pré-processamento:
   - OneHotEncoder para variáveis categóricas (etnia, localização)
   - Manutenção de variáveis numéricas (idade)
2. Classificador XGBoost com parâmetros otimizados

## Executando o Sistema

### Iniciando Backend
```bash
python app.py
```

## Recursos Adicionais

### Geração de Dados Iniciais
O backend gera automaticamente 20 casos de exemplo se o banco estiver vazio.

### Recursos de Acessibilidade
O frontend inclui:
- Botão de alto contraste
- Controles para aumentar/diminuir fonte
- Design responsivo para dispositivos móveis

### Monitoramento
O endpoint `/` fornece status do sistema:
```json
{
  "status": "online",
  "database": "connected",
  "model_loaded": true
}
```

## Solução de Problemas Comuns

### Problema: Conexão com MongoDB falha
**Solução**:
1. Verifique a `MONGO_URI` no .env
2. Teste a conexão com o cliente MongoDB
3. Verifique permissões de rede/firewall

### Problema: Modelo não carrega
**Solução**:
1. Execute `train_model.py` para gerar model.pkl
2. Verifique permissões de arquivo
3. Confira dependências do scikit-learn e XGBoost

### Problema: Gráficos não carregam
**Solução**:
1. Verifique console do navegador por erros CORS
2. Confira se o backend está rodando e acessível
3. Atualize as dependências do Chart.js

## Contribuição
Contribuições são bem-vindas! Siga o fluxo:
1. Fork do repositório
2. Crie um branch para sua feature (`git checkout -b feature/foo`)
3. Commit suas mudanças (`git commit -am 'Add some foo'`)
4. Push para o branch (`git push origin feature/foo`)
5. Crie um novo Pull Request

## Licença
Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.