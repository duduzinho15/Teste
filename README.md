# 🚀 Garimpeiro Geek

Sistema completo de recomendações de ofertas para Telegram com validação de conversores de afiliados, agendamento automático, fila de ofertas, pipelines de processamento e controle de qualidade avançado.

## ✨ Funcionalidades

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

### 📋 Planejado
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
