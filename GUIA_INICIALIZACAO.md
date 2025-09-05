# 🚀 Guia de Inicialização - Garimpeiro Geek

## 📋 Pré-requisitos

### 1. Python 3.11+
```bash
# Verificar versão do Python
python --version

# Se não tiver Python 3.11+, instale via pyenv
pyenv install 3.11.7
pyenv shell 3.11.7
```

### 2. Dependências do Projeto
```bash
# Instalar dependências principais
pip install flet torch torchvision torchaudio scikit-learn pandas numpy

# Ou instalar todas as dependências do requirements.txt (se existir)
pip install -r requirements.txt
```

## 🎮 Iniciando o Dashboard

### Opção 1: Dashboard Windows Nativo (Recomendado)
```bash
# Navegar para o diretório do projeto
cd "C:\Users\Eduardo Vitorino\CascadeProjects\Sistema de Recomendações de Ofertas Telegram2.0"

# Iniciar o dashboard Windows
python windows_dashboard.py
```

### Opção 2: Dashboard Web (Flet)
```bash
# Iniciar dashboard web
python apps/flet_dashboard/main.py
```

### Opção 3: Scripts de Inicialização
```bash
# Windows PowerShell
.\start_dashboard.ps1

# Windows Batch
.\start_dashboard.bat
```

## 🧪 Testando Funcionalidades

### 1. Testes Unitários
```bash
# Executar testes unitários
python -m pytest tests/unit/ -v
```

### 2. Testes End-to-End
```bash
# Executar testes E2E
python -m pytest tests/e2e/ -v --tb=short
```

### 3. Demos dos Sistemas
```bash
# Demo do sistema unificado
python scripts/demo_unified_dashboard.py

# Demo de testes de performance
python scripts/demo_performance_tests.py

# Demo de integração de afiliados
python scripts/demo_affiliate_integration.py

# Demo de métricas avançadas
python scripts/demo_advanced_metrics.py

# Demo de deep learning
python scripts/demo_deep_learning.py
```

## 🤖 Iniciando o Bot Telegram

### 1. Configurar Credenciais
```bash
# Criar arquivo .env com suas credenciais
cp .env.example .env

# Editar .env com suas credenciais do Telegram
# TELEGRAM_BOT_TOKEN=seu_token_aqui
# TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

### 2. Iniciar Bot em Modo Dry-Run
```bash
# Testar bot sem enviar mensagens reais
python -m src.telegram_bot.bot --dry-run
```

### 3. Iniciar Bot em Produção
```bash
# Iniciar bot real
python -m src.telegram_bot.bot
```

## 📊 Monitoramento e Logs

### 1. Visualizar Logs
```bash
# Logs do sistema
tail -f logs/system.log

# Logs do bot
tail -f logs/telegram_bot.log

# Logs de afiliados
tail -f logs/affiliate.log
```

### 2. Dashboard de Métricas
- Acesse a aba **📊 Métricas** no dashboard
- Visualize estatísticas em tempo real
- Monitore performance dos sistemas

## 🔧 Configurações Importantes

### 1. Estrutura de Pastas
```
src/
├── affiliate/          # Conversores de afiliados
├── scrapers/           # Lojas com afiliação ativa
├── core/               # Núcleo do sistema
├── pipelines/          # Ingestão e processamento
├── posting/            # Validação e formatação
└── telegram_bot/       # Integração Telegram

apps/
└── flet_dashboard/     # Dashboard Flet

tests/
├── unit/               # Testes unitários
├── e2e/                # Testes end-to-end
└── helpers/            # Utilitários de teste
```

### 2. Variáveis de Ambiente
```bash
# .env
TELEGRAM_BOT_TOKEN=seu_token
TELEGRAM_CHAT_ID=seu_chat_id
DATABASE_URL=sqlite:///data/garimpeiro_geek.db
LOG_LEVEL=INFO
DEBUG_MODE=false
```

## 🚨 Solução de Problemas

### 1. Erro de Módulo Não Encontrado
```bash
# Verificar se está no diretório correto
pwd

# Adicionar ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 2. Erro de Dependências
```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt

# Limpar cache do pip
pip cache purge
```

### 3. Erro de Permissões
```bash
# Windows: Executar como administrador
# Linux/Mac: Verificar permissões de arquivo
chmod +x start_dashboard.sh
```

## 📱 Funcionalidades do Dashboard

### 🏠 Aba Início
- **Status dos Sistemas:** Monitoramento em tempo real
- **Controles Rápidos:** Iniciar/parar bot, reiniciar sistema
- **Logs Recentes:** Histórico de atividades

### 🤖 Aba Telegram
- **Status do Bot:** Estado atual do bot
- **Controles:** Iniciar/parar bot, visualizar logs
- **Configurações:** Token, chat ID, modo dry-run

### 📊 Aba Métricas
- **Estatísticas:** Cliques, conversões, receita
- **Gráficos:** Visualizações interativas
- **Tendências:** Análise temporal

### 🔗 Aba Afiliados
- **Plataformas:** Amazon, Awin, Rakuten, Shopee, AliExpress, Mercado Livre, Magazine Luiza
- **Validação:** Verificar links de afiliados
- **Relatórios:** Análise de performance

### ⚙️ Aba Configurações
- **Configurações Gerais:** Modo noturno, auto-início
- **Ações do Sistema:** Backup, atualização, logs
- **Configurações Avançadas:** Logs, debug, etc.

## 🎯 Próximos Passos

1. **Configure suas credenciais** do Telegram
2. **Teste o bot** em modo dry-run
3. **Explore o dashboard** e suas funcionalidades
4. **Execute os demos** para entender os sistemas
5. **Configure afiliados** se necessário
6. **Monitore logs** e métricas

## 📞 Suporte

- **Logs:** Verifique sempre os logs para diagnóstico
- **Dashboard:** Use o modo diagnóstico se necessário
- **Testes:** Execute testes para validar funcionalidades
- **Documentação:** Consulte README.md para detalhes

---

**🎮 Garimpeiro Geek está pronto para uso!**
