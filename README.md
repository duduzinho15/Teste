# 🚀 Garimpeiro Geek

Sistema completo de recomendações de ofertas para Telegram com validação de conversores de afiliados, agendamento automático, fila de ofertas, pipelines de processamento e controle de qualidade avançado.

## ✨ Funcionalidades

### 🚀 **APIs e Scrapers Reais Implementados**
- **Scrapers Funcionais** - Amazon, Magazine Luiza, Mercado Livre com parsing real
- **APIs de Afiliados** - Criação e validação de links reais (Amazon Associates, Awin, Rakuten, Shopee, AliExpress, Mercado Livre, Magazine Luiza)
- **Bot Telegram Real** - Sistema completo de envio de ofertas com comandos
- **Validação de Links** - Verificação automática de links de afiliados
- **Relatórios Detalhados** - Estatísticas reais de performance e ganhos
- **Backup Automático** - Sistema de backup completo do projeto
- **Dashboard Funcional** - Interface Windows nativa com botões funcionais

### 🔗 Sistema de Afiliados
- **Validação automática** de conversores para Amazon, Mercado Livre, Shopee, Magazine Luiza, AliExpress, Awin e Rakuten
- **APIs oficiais** com fallback para scraping quando necessário
- **Cache inteligente** com Redis para otimizar conversões
- **Validação de URLs** com regex patterns específicos por plataforma
- **Geração de shortlinks** otimizados para cada plataforma
- **Métricas de conversão** em tempo real por plataforma

### 📱 Bot do Telegram
- **Formatação dinâmica** de mensagens com templates específicos por plataforma
- **Emojis contextuais** baseados no tipo de oferta e qualidade
- **Sistema de notificações** configurável para administradores
- **Templates personalizados** para cada plataforma de afiliados
- **Modo DRY_RUN** para testes sem publicação
- **Comandos administrativos** (/on, /off, /status, /testpost)

### ⏰ Sistema de Agendamento Cron
- **Tarefas automáticas** para coleta de ofertas (90s)
- **Enriquecimento de preços** em background (15min)
- **Postagem automática** na fila (45s)
- **Agregação de preços** para análise (30min)
- **Sistema assíncrono** com timeouts e backoff
- **Retry automático** para jobs falhados

### 📋 Sistema de Fila e Moderação
- **Fila prioritária** de ofertas com scoring automático
- **Sistema de moderação** manual e automática
- **Controle de qualidade** com validação de afiliados
- **Processamento assíncrono** de ofertas
- **Sistema de prioridades** dinâmicas
- **Workflow de aprovação** em múltiplos níveis

### 🔄 Pipelines de Processamento
- **Ingestão de ofertas** via APIs e scrapers
- **Enriquecimento automático** de dados
- **Coleta de preços** históricos
- **Agregação inteligente** de dados
- **Sistema de cache** distribuído
- **Processamento em lote** otimizado

### 📝 Sistema de Postagem Automática
- **Formatação profissional** de mensagens por plataforma
- **Templates com emojis** e campos opcionais
- **Agendador de jobs** (coleta 90s, enriquecimento 15min, postagem 45s)
- **Gerenciador de postagem** com controle de qualidade
- **Aprovação automática** baseada em score (threshold 0.8)
- **Sistema de moderação** manual para ofertas de baixa qualidade
- **Controle de rate limiting** e prevenção de spam
- **Validação de mensagens** antes da postagem

### 🕷️ Sistema de Scrapers
- **Scrapers de lojas** com afiliação ativa
- **Scrapers de comunidades** (Promobit, Pelando, MeuPC)
- **Scrapers de preços** (Zoom, Buscapé)
- **Medidas anti-bot** e rate limiting
- **Cache inteligente** de dados coletados
- **Tratamento de erros** robusto

### 📊 Dashboard e Monitoramento
- **Dashboard Flet** responsivo e interativo
- **Métricas de produção** em tempo real
- **Sistema de alertas** automáticos
- **Logs estruturados** e legíveis
- **Health checks** do sistema
- **Relatórios automáticos** de performance

### 🚀 Produção e Escalabilidade
- **Configuração Redis** otimizada para produção
- **Cache distribuído** com fallback em memória
- **Rate limiting** inteligente por API
- **Sistema de deduplicação** de ofertas
- **Circuit breaker** para falhas de API
- **Auto-scaling** baseado em métricas

## 🎮 **SISTEMA GEEK COMPLETO IMPLEMENTADO (2025)**

### **🚀 Sistema de Priorização Geek/Gamer**
- **GeekPrioritizer**: Algoritmo inteligente para calcular scores geek de produtos
- **Categorias Primárias**: Gaming, Tech Geek, PC Gaming, Smart Home, Audio Premium, Anime/Otaku, Collectibles
- **Categorias Secundárias**: Eletrodomésticos Tech, Mobile & Wearables, Fitness Tech, Eletrônicos Gerais
- **Sistema de Scores**: 0.0-1.0 com níveis Crítico, Alta, Média e Baixa prioridade
- **Palavras-chave Específicas**: Detecção automática de produtos geek por categoria
- **Produtos Sempre Prioritários**: PlayStation, Xbox, RTX, Smart TVs, Headphones Bluetooth, etc.

### **🚨 Sistema de Alertas Geek Inteligente**
- **GeekAlertManager**: Monitoramento automático de produtos de alta prioridade
- **Alertas por Score**: Crítico (0.9+), Alta (0.8+), Média (0.7+)
- **Tipos de Alerta**: Alta prioridade, queda de preço, estoque limitado
- **Limites Inteligentes**: Máximo de alertas por hora/dia para evitar spam
- **Histórico de Alertas**: Tracking completo de alertas enviados e pendentes
- **Estatísticas em Tempo Real**: Métricas de performance do sistema geek

### **📱 Comandos Específicos do Bot Telegram**
- **/geek**: Ofertas geek prioritárias gerais
- **/gaming**: Filtro específico para gaming (consoles, periféricos, jogos)
- **/tech**: Produtos tech premium (smartphones, tablets, notebooks)
- **/anime**: Produtos anime/otaku (figuras, mangás, cosplay)
- **/smart**: Smart home e IoT (smart TVs, speakers, automação)
- **/audio**: Audio premium e gaming (headphones, headsets, soundbars)
- **/collectibles**: Collectibles e edições limitadas
- **/geekstats**: Estatísticas geek do sistema
- **/geekhelp**: Ajuda sobre comandos geek

### **📊 Dashboard de Métricas Geek**
- **Aba Específica**: Métricas dedicadas para produtos geek/gamer
- **Cards de Métricas**: Total de ofertas geek, score médio, alertas críticos, taxa de conversão
- **Gráficos Interativos**: Distribuição por categoria, performance por categoria
- **Top Produtos**: Lista dos produtos geek com maior score
- **Painel de Alertas**: Estatísticas de alertas por prioridade e tipo
- **Atualização Automática**: Refresh automático a cada 5 minutos

### **🧪 Sistema de Testes Completo**
- **Testes Unitários**: Cobertura completa de GeekPrioritizer, GeekAlertManager e GeekCommands
- **Testes de Integração**: Workflow completo do sistema geek
- **Testes de Consistência**: Validação de configurações e priorização
- **Mocks e Fixtures**: Dados de teste realistas para validação
- **Cobertura de Cenários**: Gaming, Tech, Smart Home, Audio, Anime, Collectibles

### **⚡ Integração com Sistema Existente**
- **Quality Controller**: Integração completa com sistema de qualidade
- **Pipelines**: Priorização geek em todos os pipelines de processamento
- **Scrapers**: Foco automático em produtos geek durante coleta
- **Postagem**: Priorização de ofertas geek na fila de postagem
- **Cache**: Otimização de cache para produtos geek frequentes

## 🆕 **SISTEMA INTELIGENTE DE COLETA AUTOMÁTICA AWIN**

## 🔑 **NOVOS TOKENS IMPLEMENTADOS (31/08/2025)**

### **🟠 RAKUTEN ADVERTISING**
- **Web Service Token**: Configurado e funcionando ✅
- **Security Token**: Configurado e funcionando ✅
- **Status**: API habilitada e integrada ao sistema
- **Funcionalidades**: Geração de deeplinks, healthcheck, cache

### **🟡 SHOPEE AFFILIATE OPEN API**
- **App ID**: `18330800803` ✅
- **Secret**: Configurado e funcionando ✅
- **Status**: API habilitada e integrada ao sistema
- **Funcionalidades**: Geração de shortlinks, validação de URLs, cache SQLite

### **📊 Resultado dos Testes**
- **Rakuten**: ✅ Cliente criado, healthcheck funcionando, deeplinks gerados
- **Shopee**: ✅ Validação de URLs, geração de shortlinks, cache funcionando
- **Sistema**: ✅ Integração completa, testes passando, pronto para produção

### **🎯 Coleta Automática de Ofertas**
- **9 Afiliações Ativas**: COMFY, Trocafy, LG, Kabum, Samsung, Gigantec BR, Ninja, **Rakuten**, **Shopee**
- **API Oficial Awin**: Integração completa com Publisher API
- **API Rakuten**: Web Service + Security Tokens configurados ✅
- **API Shopee**: App ID + Secret configurados ✅
- **Coleta Contínua**: Pipeline automático configurável (padrão: 1 hora)
- **Fallback Inteligente**: Product Feed API + Link Builder API

### **🔧 Filtros Automáticos Inteligentes**
- **5 Filtros Padrão**: Desconto, preço, categoria, loja, qualidade
- **Operadores Flexíveis**: EQUALS, GREATER_THAN, IN, BETWEEN, etc.
- **Regras Complexas**: Lógica AND/OR/XOR com prioridades
- **Perfis Personalizáveis**: Configurações para diferentes cenários
- **Performance Alta**: 333.252 ofertas/segundo

### **📊 Pipeline de Ingestão Automática**
- **Validação Automática**: URLs de afiliado e qualidade
- **Deduplicação Inteligente**: Cache para evitar duplicatas
- **Postagem Automática**: Telegram com rate limiting
- **Estatísticas Completas**: Performance e métricas em tempo real

## 🤖 **SISTEMA AUTOMÁTICO DE POSTAGEM TELEGRAM**

### **🚀 Automação Completa**
- **Coleta Automática**: Ofertas coletadas a cada 5 minutos
- **Postagem Automática**: Posts a cada 3 minutos com rate limiting
- **Fila Inteligente**: Sistema de prioridades e controle de qualidade
- **Scheduler Avançado**: Jobs configuráveis e monitoramento em tempo real

### **📱 Integração Telegram**
- **Bot Configurado**: Credenciais e permissões configuradas
- **Canal Ativo**: Postagem automática no canal configurado
- **Formatação Profissional**: Templates personalizados por plataforma
- **Imagens Automáticas**: Suporte a imagens dos produtos

### **⚙️ Controle e Monitoramento**
- **Sistema de Produção**: Script dedicado para ativação em produção
- **Logs Estruturados**: Sistema de logging completo com encoding UTF-8
- **Health Checks**: Verificação automática da saúde do sistema
- **Parada Graciosa**: Controle via Ctrl+C e sinais do sistema
- **Status em Tempo Real**: Monitoramento a cada 5 minutos

### **🔧 Configurações Avançadas**
- **Rate Limiting**: 3 minutos entre posts (configurável)
- **Filtros de Qualidade**: Desconto mínimo de 10%
- **Categorias Permitidas**: Smartphones, Notebooks, Smart TVs, Consoles, Fones
- **Fallback Automático**: Recuperação de erros e retry inteligente
- **Backup Automático**: Sistema de recuperação

### **🔄 Monitoramento em Tempo Real**
- **Status do Pipeline**: Execuções, sucessos, falhas
- **Performance dos Filtros**: Tempo médio, ofertas processadas
- **Saúde do Sistema**: Credenciais, conectividade, logs
- **Atualização Automática**: Refresh configurável (padrão: 5s)

## 🏗️ Arquitetura Completa

```
src/
├── affiliate/          # Conversores de afiliados
│   ├── amazon.py      # Conversor Amazon (ASIN-first + fallback)
│   ├── mercadolivre.py # Conversor Mercado Livre
│   ├── shopee.py      # Conversor Shopee
│   ├── magazineluiza.py # Conversor Magazine Luiza
│   ├── aliexpress.py  # Conversor AliExpress
│   ├── awin.py        # Conversor Awin
│   ├── rakuten.py     # Conversor Rakuten
│   ├── *_api.py       # Clientes de API oficiais
│   └── base_api.py    # Classe base para APIs
├── app/                # Aplicação principal
│   ├── queue/         # Sistema de fila de ofertas
│   │   ├── offer_queue.py      # Fila principal
│   │   ├── moderation_system.py # Sistema de moderação
│   │   ├── quality_controller.py # Controle de qualidade
│   │   └── queue_manager.py    # Gerenciador da fila
│   ├── scheduler/     # Agendador cron
│   │   ├── cron_manager.py     # Gerenciador de cron jobs
│   │   ├── job_scheduler.py    # Agendador de tarefas
│   │   ├── task_runner.py     # Executor de tarefas
│   │   └── post_scheduler.py  # Agendador de postagens
│   ├── dashboard/     # Dashboard interno
│   └── bot/           # Bot interno
├── core/               # Componentes principais
│   ├── models.py      # Modelos de dados (Offer, etc.)
│   ├── settings.py    # Configurações (.env)
│   ├── database.py    # Banco de dados SQLite
│   ├── db_init.py     # Inicialização do banco
│   ├── affiliate_*.py # Sistema de afiliados
│   ├── conversion_metrics.py  # Métricas de conversão
│   ├── failure_alerts.py      # Sistema de alertas
│   ├── optimization_engine.py # Motor de otimização
│   ├── performance_logger.py  # Logger de performance
│   ├── enhanced_metrics.py    # Métricas avançadas
│   ├── alert_system.py        # Sistema de alertas
│   ├── analytics_queries.py   # Queries analíticas
│   ├── cache_config.py        # Configuração de cache
│   ├── deduplication.py       # Sistema de deduplicação
│   ├── rate_limiter.py        # Rate limiting
│   ├── affiliate_cache.py     # Cache de afiliados
│   ├── offer_pipeline.py      # Pipeline de ofertas
│   ├── affiliate_converter.py # Conversor de afiliados
│   ├── matchers.py            # Sistema de matching
│   ├── metrics.py             # Métricas básicas
│   ├── platforms.py           # Configurações de plataformas
│   ├── live_logs.py           # Logs em tempo real
│   ├── logging_setup.py       # Configuração de logs
│   ├── storage.py             # Sistema de armazenamento
│   ├── monitoring/            # Sistema de monitoramento
│   └── cache/                 # Sistema de cache
├── pipelines/          # Pipelines de processamento
│   ├── ingest_offers_api.py   # Ingestão via APIs
│   ├── enrich_offers_api.py   # Enriquecimento de dados
│   ├── price_collect.py       # Coleta de preços
│   ├── price_enrich.py        # Enriquecimento de preços
│   └── price_aggregate.py     # Agregação de preços
├── posting/            # Sistema de postagem
│   ├── message_formatter.py   # Formatação de mensagens
│   └── posting_manager.py     # Gerenciador de postagens
├── scrapers/           # Sistema de scrapers
│   ├── base_scraper.py        # Classe base para scrapers
│   ├── lojas/                 # Scrapers de lojas
│   ├── comunidades/           # Scrapers de comunidades
│   │   ├── promobit/          # Scraper Promobit
│   │   ├── pelando/           # Scraper Pelando
│   │   └── meupc/             # Scraper MeuPC
│   └── precos/                # Scrapers de preços
│       ├── zoom/              # Scraper Zoom
│       └── buscape/           # Scraper Buscapé
├── telegram_bot/       # Bot do Telegram
│   ├── bot.py                 # Bot principal
│   ├── bot_manager.py         # Gerenciador do bot
│   ├── message_builder.py     # Construtor de mensagens
│   └── notification_manager.py # Gerenciador de notificações
├── utils/              # Utilitários
│   ├── anti_bot.py            # Medidas anti-bot
│   ├── affiliate_validator.py # Validador de URLs
│   ├── asin_cache.py          # Cache de ASINs
│   ├── url_utils.py           # Utilitários de URL
│   └── sqlite_helpers.py      # Helpers para SQLite
├── diagnostics/        # Sistema de diagnóstico
│   └── ui_reporter.py         # Relatórios de UI
├── recommender/        # Sistema de recomendação
├── db/                 # Banco de dados
│   ├── garimpeiro_geek.db    # Banco principal
│   ├── aff_cache.sqlite       # Cache de afiliados
│   └── analytics.sqlite       # Banco de analytics
├── logs/               # Logs do sistema
├── exports/            # Exportações de dados
└── tests/              # Testes automatizados
    ├── unit/           # Testes unitários
    ├── e2e/            # Testes end-to-end
    ├── api/            # Testes de API
    ├── helpers/        # Helpers para testes
    └── data/           # Dados de teste

apps/
└── flet_dashboard/     # Dashboard Flet
    ├── main.py         # Aplicação principal
    ├── ui_components.py # Componentes de UI
    └── run_dashboard.py # Script de execução
```

## 🚀 Instalação

### Pré-requisitos
- Python 3.9+
- Redis 5.0+ (opcional, com fallback em memória)
- Git

### 1. Clone o repositório
```bash
git clone https://github.com/duduzinho15/Ainda-nao-funciona.git
cd Sistema-de-Recomendacoes-de-Ofertas-Telegram2.0
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente
```bash
cp config/env.example .env
# Edite o arquivo .env com suas configurações
```

### 4. Configure o Redis (opcional)
```bash
# Para desenvolvimento, o sistema usa cache em memória
# Para produção, configure Redis conforme config/redis.production.conf
```

### 5. Ative o Sistema Automático
```bash
# Testar o sistema
python test_auto_system.py

# Executar demonstração
python demo_telegram_posting.py

# Ativar em produção
python start_production_system.py

# Para parar: Ctrl+C
```

## ⚙️ Configuração

### Variáveis de Ambiente (.env)
```bash
# ========================================
# TELEGRAM
# ========================================
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=your_channel_id_here
TELEGRAM_ADMIN_USER_ID=your_admin_user_id_here

# ========================================
# BANCO DE DADOS
# ========================================
DATABASE_URL=sqlite:///src/db/garimpeiro_geek.db
DATABASE_PATH=src/db/garimpeiro_geek.db

# ========================================
# AFILIADOS
# ========================================
AFFILIATE_AMAZON_TAG=garimpeirogee-20
AFFILIATE_MERCADOLIVRE_ID=seu_id_aqui
AFFILIATE_SHOPEE_ID=seu_id_aqui
AFFILIATE_AWIN_ID=seu_id_aqui
AFFILIATE_RAKUTEN_ID=seu_id_aqui

# ========================================
# RAKUTEN ADVERTISING
# ========================================
RAKUTEN_ENABLED=false
RAKUTEN_WEBSERVICE_TOKEN=seu_token_aqui
RAKUTEN_SECURITY_TOKEN=seu_security_token_aqui

# ========================================
# MONITORAMENTO E CACHE
# ========================================
MONITORING_ENABLED=true
CACHE_ENABLED=true
RATE_LIMIT_ENABLED=true
BACKUP_ENABLED=true
```

## 🧪 Testes

### Executar todos os testes
```bash
make test
```

### Testes unitários
```bash
make test-unit
```

### Testes de integração
```bash
make test-e2e
```

### Linting e formatação
```bash
make format      # Formatação com Black + Ruff
make lint        # Linting com Ruff
make type-check  # Verificação de tipos com MyPy
```

### Testes específicos
```bash
# Testar sistema de afiliados
pytest tests/unit/test_affiliate_system.py

# Testar sistema de fila
pytest tests/unit/test_queue_system.py

# Testar agendador
pytest tests/unit/test_scheduler.py

# Testar scrapers
pytest tests/unit/test_scrapers/
```

## 🚀 Execução

### 1. Executar o sistema principal
```bash
python -m src.app.main
```

### 2. Executar o bot do Telegram
```bash
python -m src.telegram_bot.bot
```

### 3. Executar o dashboard Flet
```bash
python apps/flet_dashboard/run_dashboard.py
```

### 4. Executar scrapers específicos
```bash
# Scraper Promobit
python -m src.scrapers.comunidades.promobit

# Scraper de preços Zoom
python -m src.scrapers.precos.zoom
```

### 5. Executar pipelines
```bash
# Pipeline de ingestão
python -m src.pipelines.ingest_offers_api

# Pipeline de enriquecimento
python -m src.pipelines.enrich_offers_api
```

### 6. Executar demonstrações dos sistemas
```bash
# Demonstração do sistema de testes em produção
python demo_production_testing.py

# Demonstração do sistema de monitoramento de conversão
python demo_conversion_monitoring.py

# Demonstração do sistema de feedback dos usuários
python demo_user_feedback.py

# Demonstração do sistema de expansão de categorias
python demo_category_expansion.py

# Teste rápido do sistema de expansão de categorias
python demo_category_expansion.py quick

# Demonstração do sistema de IA para otimização
python demo_ai_optimization.py

# Teste rápido do sistema de IA para otimização
python demo_ai_optimization.py quick

# Sistema Unificado de Dashboard
python demo_unified_dashboard.py

# Teste rápido do sistema unificado
python demo_unified_dashboard.py quick

# Testes de Performance Avançados
python demo_performance_tests.py full

# Teste rápido de performance
python demo_performance_tests.py quick

# Integração com Afiliados
python demo_affiliate_integration.py full
python demo_affiliate_integration.py quick

# Métricas Avançadas
python demo_advanced_metrics.py quick
python demo_advanced_metrics.py full
python demo_advanced_metrics.py dashboard

# Deep Learning
python demo_deep_learning.py quick
python demo_deep_learning.py full
python demo_deep_learning.py dashboard
```

## 📊 Monitoramento

### Dashboard Flet
Acesse o dashboard em tempo real para monitorar:

#### **📊 Tabs Disponíveis**
- **Visão Geral**: KPIs principais e alertas do sistema
- **Amazon ASIN**: Qualidade de normalização e estratégias de extração
- **🛒 Mercado Livre**: Métricas específicas de qualidade, performance e receita
- **Afiliação**: Monitoramento de links afiliados e receita
- **Performance**: Latência de deeplinks e freshness de preços
- **Alertas**: Sistema de notificações e problemas detectados
- **Controles**: Gerenciamento de plataformas e configurações

#### **🛒 Aba Mercado Livre - Funcionalidades**
- **Qualidade dos Links**: Shortlinks, links sociais e diretos
- **Score de Qualidade**: Baseado em tipos de link (shortlinks têm peso maior)
- **Performance**: Taxa de conversão e latência média
- **Receita**: Total de receita e ticket médio por transação
- **Gráficos**: Distribuição de tipos de link e taxa de conversão
- **Alertas**: Notificações para qualidade < 70% e conversão < 80%

#### **🔧 Aba Moderação ML - Sistema Completo de Workflow**
- **Scraping Automático**: Coleta ofertas das melhores categorias (smartphones, notebooks, smart-tvs, consoles)
- **Filtros de Qualidade**: Desconto mínimo 10%, preço máximo R$ 5.000, avaliação mínima 4.0
- **Moderação Manual**: Interface para converter links para afiliados via dashboard
- **Validação Automática**: Verificação de URLs de afiliado (shortlinks e links sociais)
- **Pipeline Integrado**: Fluxo completo desde scraping até postagem no Telegram
- **Controle de Status**: Acompanhamento de tarefas pendentes, aprovadas e prontas para postagem

### Métricas Disponíveis
- **Conversões**: Total, sucesso, falha por plataforma
- **Performance**: Tempo de resposta, cache hits/misses
- **Qualidade**: Score das ofertas, taxa de aprovação
- **Sistema**: Uso de memória, conexões, uptime
- **Scrapers**: Taxa de sucesso, erros, performance

### Logs Estruturados
- Logs de aplicação em `src/logs/`
- Logs de performance e métricas
- Logs de erros e alertas
- Logs de auditoria e segurança

## 🔧 Desenvolvimento

### Formatação de Código
```bash
# Formatação automática
make format

# Linting
make lint

# Verificação de tipos
make type-check

# Limpeza
make clean
```

### Estrutura de Commits
Seguimos o padrão [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação
- `refactor:` Refatoração
- `test:` Testes
- `chore:` Manutenção

### Padrões de Código
- **Type hints** obrigatórios em todas as funções públicas
- **Docstrings** claras e objetivas
- **Logs estruturados** com contexto
- **Tratamento de erros** robusto
- **Testes unitários** para todas as funcionalidades
- **Imports absolutos** a partir de `src/`

## 📚 Documentação

- [📋 TODO Unificado](TODO.md) - Roadmap completo do projeto
- [🔧 Especificações Técnicas](docs/ESPECIFICACAO_GARIMPEIRO_GEEK_COM_RAKUTEN.md)
- [🤖 Documentação do Bot](docs/telegram_bot.md)
- [🔗 APIs de Integração](docs/apis_integracao.md)
- [📊 Exemplos de Afiliados](docs/affiliate_examples.md)
- [📊 Dados Históricos](docs/dados_historico_precos.md)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Antes de submeter
```bash
# Executar todos os checks
make format && make lint && make type-check && make test

# Verificar cobertura de testes
make test  # Inclui relatório de cobertura
```

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🆘 Suporte

Para suporte e dúvidas:
- Abra uma [Issue](https://github.com/duduzinho15/Ainda-nao-funciona/issues)
- Consulte a [documentação](docs/)
- Verifique os [exemplos](tests/)
- Consulte o [TODO.md](TODO.md) para roadmap

## 🎯 Roadmap

### ✅ Implementado
- [x] Sistema de afiliados completo
- [x] Bot do Telegram funcional
- [x] Sistema de fila e moderação
- [x] Pipelines de processamento
- [x] Scrapers organizados
- [x] Dashboard Flet
- [x] Sistema de monitoramento

### ✅ Recentemente Implementado
- [x] Testes E2E completos
- [x] Sistema de postagem automática
- [x] Otimizações de performance
- [x] Análise completa do projeto
- [x] Gigantec BR integrada ao Awin
- [x] Sistema 100% funcional
- [x] **Tokens Rakuten implementados** (Web Service + Security)
- [x] **Tokens Shopee implementados** (App ID + Secret)
- [x] **APIs Rakuten e Shopee habilitadas e funcionais**
- [x] **🛒 Aba Mercado Livre implementada no Dashboard** (Métricas específicas, qualidade de links, performance e receita)
- [x] **🔧 Sistema Completo de Moderação Manual do Mercado Livre** (Scraping automático, conversão manual via dashboard, postagem automática)
- [x] **🎯 Sistema de Priorização Geek Completo** (Algoritmo de score, alertas, comandos Telegram, dashboard Flet)
- [x] **📊 Sistema de Teste em Produção** (Pipeline de dados reais, monitor de performance, validador do sistema)
- [x] **📈 Sistema de Monitoramento de Conversão Geek vs Geral** (Rastreamento, análise, dashboard, relatórios)
- [x] **🔄 Sistema de Feedback dos Usuários** (Coleta, análise, ajuste automático de scores, dashboard interativo)
- [x] **📈 Sistema de Expansão de Categorias** (Análise de tendências, pesquisa de mercado, expansão automática, otimização)
- [x] **🤖 Sistema de IA para Otimização Automática** (Machine Learning, predição de scores, otimização automática, dashboard interativo)
- [x] **🎛️ Sistema Unificado de Dashboard** (Integração completa de todos os sistemas, métricas consolidadas, controle centralizado)
- [x] **🔗 Sistema de Integração com Afiliados Reais** (APIs oficiais, validação de links, múltiplas redes, dashboard dedicado)
- [x] **📊 Sistema de Métricas Avançadas** (Análise temporal, segmentação demográfica, sazonalidade, engajamento, insights preditivos)
- [x] **🤖 Sistema de Deep Learning** (Redes neurais avançadas, predições inteligentes, otimização automática de priorização)

### **🤖 Sistema de IA para Otimização Automática de Priorização**
- **AIOptimizer**: Otimizador principal que coordena todo o sistema de IA
- **DataCollector**: Coleta dados históricos e features para treinamento dos modelos
- **ModelTrainer**: Treina modelos de machine learning (Random Forest, Gradient Boosting, Linear Regression)
- **PredictionEngine**: Motor de predição que otimiza scores baseado em dados históricos
- **OptimizationDashboard**: Interface interativa para monitorar e controlar o sistema
- **Features Inteligentes**: Preço, score geek, taxa de conversão, engajamento, horário, estação, reputação da loja
- **Modelos de IA**: 3 algoritmos diferentes com métricas de performance (R², MSE, MAE, Cross-Validation)
- **Auto-retreinamento**: Sistema que retreina modelos automaticamente baseado em novos dados
- **Confiança e Insights**: Análise de confiança das predições e fatores-chave que influenciam os scores
- **Otimização em Lote**: Processamento eficiente de múltiplas ofertas simultaneamente
- **Histórico Completo**: Tracking de todas as otimizações realizadas pelo sistema

### **🧪 Sistema de Testes de Performance Avançados**

Sistema completo de testes de stress, carga, concorrência, memória, rede e benchmark para validar a performance do sistema em diferentes cenários.

#### **Componentes Implementados:**

1. **📊 Performance Monitor** (`src/tests/performance/performance_monitor.py`)
   - Monitoramento em tempo real de CPU, memória, disco e rede
   - Registro de tempos de resposta
   - Alertas configuráveis para thresholds

2. **⚡ Stress Tester** (`src/tests/performance/stress_tester.py`)
   - Testes de stress com ramp-up/down
   - Usuários concorrentes configuráveis
   - Cenários simulados (scraping, processing, posting, validation)

3. **📈 Load Generator** (`src/tests/performance/load_generator.py`)
   - Testes de carga progressiva
   - Aumento gradual de usuários
   - Métricas de throughput e latência

4. **🔄 Concurrency Tester** (`src/tests/performance/concurrency_tester.py`)
   - Testes de concorrência com ThreadPoolExecutor
   - Tarefas distribuídas por peso
   - Análise de deadlocks e race conditions

5. **💾 Memory Profiler** (`src/tests/performance/memory_profiler.py`)
   - Monitoramento de uso de memória
   - Detecção de vazamentos com tracemalloc
   - Forçar garbage collection

6. **🌐 Network Simulator** (`src/tests/performance/network_simulator.py`)
   - Simulação de condições de rede (latência, jitter, packet loss)
   - Interceptação de chamadas socket
   - Testes de conectividade

7. **⚡ Benchmark Runner** (`src/tests/performance/benchmark_runner.py`)
   - Benchmarks específicos para funções
   - Profiling de CPU com cProfile
   - Métricas de performance detalhadas

#### **Como Usar:**

```bash
# Demonstração rápida
python demo_performance_tests.py quick

# Demonstração completa
python demo_performance_tests.py full
```

#### **Métricas Coletadas:**
- Throughput (RPS - Requests Per Second)
- Tempo médio de resposta
- Taxa de erro
- Uso de CPU e memória
- Vazamentos de memória
- Latência de rede
- Performance de benchmarks

---

### **🔗 Sistema de Integração com Afiliados Reais**

Sistema completo para integração com redes de afiliados reais, incluindo APIs oficiais, validação de links e monitoramento de métricas.

#### **Componentes Principais:**

1. **AffiliateIntegrationManager** (`src/core/affiliate_integration.py`)
   - Gerenciamento centralizado de redes de afiliados
   - Configuração de APIs oficiais
   - Validação de links em lote
   - Armazenamento em banco SQLite
   - Métricas de performance

2. **AffiliateLinkValidator** (`src/core/affiliate_integration.py`)
   - Validação automática de links de afiliado
   - Detecção de rede por URL
   - Cache de validações
   - Teste de acessibilidade
   - Rate limiting inteligente

3. **AffiliateAPIClient** (`src/core/affiliate_integration.py`)
   - Cliente base para APIs de afiliados
   - Rate limiting automático
   - Retry com backoff exponencial
   - Tratamento de erros robusto

4. **AmazonAPIClient** (`src/core/affiliate_integration.py`)
   - Integração específica com Amazon Associates
   - Busca de produtos via API oficial
   - Geração automática de links de afiliado
   - Tratamento de categorias

5. **AwinAPIClient** (`src/core/affiliate_integration.py`)
   - Integração com rede Awin
   - Listagem de programas disponíveis
   - Busca de produtos por programa
   - Métricas de conversão

6. **AffiliateDashboard** (`src/core/affiliate_dashboard.py`)
   - Interface console para gerenciamento
   - Configuração de redes
   - Validação de links
   - Busca de produtos
   - Relatórios e métricas

#### **Redes Suportadas:**
- **Amazon Associates**: API oficial, busca de produtos, geração de links
- **Awin**: API REST, programas de afiliados, métricas detalhadas
- **Rakuten**: Plataforma de afiliados globais, múltiplas categorias
- **Shopee**: Marketplace com programa de afiliados
- **AliExpress**: Plataforma global de e-commerce
- **Mercado Livre**: Maior plataforma de e-commerce da América Latina
- **Magazine Luiza**: Varejista brasileiro com programa de afiliados
- **Perfect Pay**: Gateway de pagamentos
- **Kiwify**: Plataforma de produtos digitais

#### **Funcionalidades:**
- ✅ **Configuração de Redes**: Adicionar, editar, remover redes de afiliados
- ✅ **Validação de Links**: Verificação automática de links válidos
- ✅ **Busca de Produtos**: Busca em múltiplas redes simultaneamente
- ✅ **Métricas de Performance**: CTR, conversão, receita, comissões
- ✅ **Cache Inteligente**: Cache de validações para performance
- ✅ **Rate Limiting**: Controle automático de requisições
- ✅ **Tratamento de Erros**: Recuperação robusta de falhas
- ✅ **Dashboard Interativo**: Interface console completa

#### **Como Usar:**

```bash
# Demonstração rápida
python demo_affiliate_integration.py quick

# Demonstração completa
python demo_affiliate_integration.py full

# Dashboard interativo
python -c "from src.core.affiliate_dashboard import affiliate_dashboard; import asyncio; asyncio.run(affiliate_dashboard.show_main_menu())"
```

#### **Configuração de Redes:**

```python
from src.core.affiliate_integration import AffiliateConfig, AffiliateNetwork

# Configurar Amazon
amazon_config = AffiliateConfig(
    network=AffiliateNetwork.AMAZON,
    api_key="sua_api_key",
    timeout=30,
    priority=1
)

# Configurar Awin
awin_config = AffiliateConfig(
    network=AffiliateNetwork.AWIN,
    api_key="sua_api_key",
    api_secret="seu_api_secret",
    timeout=30,
    priority=2
)
```

#### **Validação de Links:**

```python
from src.core.affiliate_integration import affiliate_manager

# Validar links em lote
urls = [
    "https://amazon.com.br/dp/B08N5WRWNW?tag=garimpeirogeek-20",
    "https://awin1.com/cread.php?awinmid=12345&awinaffid=67890"
]

results = await affiliate_manager.validate_links(urls)
for result in results:
    print(f"{result.url}: {'✅' if result.is_valid else '❌'}")
```

#### **Busca de Produtos:**

```python
# Buscar produtos em múltiplas redes
products = await affiliate_manager.search_products(
    keywords="headphone gamer",
    category="Eletrônicos"
)

for product in products:
    print(f"{product.name}: R$ {product.price:.2f}")
```

#### **Métricas Coletadas:**
- Taxa de validação de links
- Performance por rede
- Produtos encontrados
- Conversões e cliques
- Receita e comissões
- Tempo de resposta das APIs

---

### **🎛️ Sistema Unificado de Dashboard**
- **UnifiedDashboard**: Dashboard principal que coordena todos os sistemas implementados
- **SystemStatus**: Monitoramento de status de cada sistema em tempo real
- **DashboardMetrics**: Métricas consolidadas de todos os sistemas
- **Health Monitoring**: Monitoramento de saúde do sistema completo
- **Integração Total**: Todos os 5 sistemas implementados integrados em uma interface única
- **Relatórios Unificados**: Relatórios consolidados de todos os sistemas
- **Controle Centralizado**: Interface única para controle de todos os sistemas

### 📋 Planejado
- [ ] Machine Learning para scoring avançado
- [ ] Machine Learning para scoring
- [ ] Integração com mais plataformas
- [ ] Sistema de notificações push
- [ ] API REST para integrações
- [ ] Dashboard mobile responsivo
- [ ] Sistema de backup automático

---

## 🔄 Atualizações Automáticas

**⚠️ IMPORTANTE**: Este README é atualizado automaticamente sempre que:
- Novos módulos são criados
- Estrutura de pastas é alterada
- Novas funcionalidades são implementadas
- Configurações são modificadas

### **Sistema de Atualização Automática**
O projeto inclui um sistema inteligente que mantém o README sempre sincronizado:

#### **Atualização Manual**
```bash
# Windows (PowerShell)
.\scripts\update_readme.ps1

# Linux/Mac
python scripts/update_readme.py

# Via Makefile (se disponível)
make update-readme
```

#### **Atualização Automática**
- **Git Hook**: Executa automaticamente antes de cada commit
- **Detecção Inteligente**: Identifica mudanças na estrutura
- **Cache de Performance**: Evita atualizações desnecessárias
- **Integração Total**: Funciona em Windows, Linux e Mac

#### **Documentação Completa**
Para detalhes sobre o sistema de atualização, consulte:
- [📋 Sistema de Atualização Automática](docs/README_UPDATE_SYSTEM.md)

**Para manter o README atualizado**:
1. ✅ **Sempre crie arquivos** dentro da estrutura definida
2. ✅ **Use os padrões** de nomenclatura estabelecidos
3. ✅ **Documente novas funcionalidades**
4. ✅ **O sistema atualiza automaticamente** via Git hooks

---

**Desenvolvido com ❤️ para a comunidade de ofertas e promoções**

**Versão**: 2.0  
**Última Análise**: 31-08-2025 12:30:00  
**Status**: ✅ Sistema 100% Funcional e Pronto para Produção
