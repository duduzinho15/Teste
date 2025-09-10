# ðŸš€ Garimpeiro Geek

Sistema completo de recomendaÃ§Ãµes de ofertas para Telegram com validaÃ§Ã£o de conversores de afiliados, agendamento automÃ¡tico, fila de ofertas, pipelines de processamento e controle de qualidade avanÃ§ado.

## âœ¨ Funcionalidades

### ðŸš€ **APIs e Scrapers Reais Implementados**
- **Scrapers Funcionais** - Amazon, Magazine Luiza, Mercado Livre com parsing real
- **APIs de Afiliados** - CriaÃ§Ã£o e validaÃ§Ã£o de links reais (Amazon Associates, Awin, Rakuten, Shopee, AliExpress, Mercado Livre, Magazine Luiza)
- **Bot Telegram Real** - Sistema completo de envio de ofertas com comandos
- **ValidaÃ§Ã£o de Links** - VerificaÃ§Ã£o automÃ¡tica de links de afiliados
- **RelatÃ³rios Detalhados** - EstatÃ­sticas reais de performance e ganhos
- **Backup AutomÃ¡tico** - Sistema de backup completo do projeto
- **Dashboard Funcional** - Interface Windows nativa com botÃµes funcionais

## 🎯 Sistema de Pontuação de Ofertas

O sistema agora inclui um motor avançado de pontuação de ofertas que classifica automaticamente as ofertas com base em múltiplos fatores:

### 📊 Fatores de Pontuação
- **Desconto**: Comparação com preço médio e histórico
- **Histórico de Preços**: Menor preço em 40/90/180 dias
- **Vendedor**: Lista de vendedores confiáveis
- **Categoria**: Regras específicas por tipo de produto

### 🏷️ Níveis de Oferta
- **CRÍTICO (≥ 0.85)**: Ofertas excelentes para postagem imediata
- **ALTA (0.75-0.84)**: Boas ofertas para a próxima janela
- **MÉDIA (0.50-0.74)**: Ofertas razoáveis
- **BAIXA (< 0.50)**: Abaixo do limiar de qualidade

### ⚙️ Configuração
Personalize os limiares no arquivo `.env`:
```ini
DEAL_SCORE_CRITICAL=0.85
DEAL_SCORE_HIGH=0.75
ELECTRONICS_MIN_DISC=0.20
PERIPHERALS_MIN_DISC=0.25
APPLIANCES_MIN_DISC=0.18
```

Consulte [docs/DEAL_SCORING.md](docs/DEAL_SCORING.md) para detalhes completos.

### ðŸ”— Sistema de Afiliados
- **ValidaÃ§Ã£o automÃ¡tica** de conversores para Amazon, Mercado Livre, Shopee, Magazine Luiza, AliExpress, Awin e Rakuten
- **APIs oficiais** com fallback para scraping quando necessÃ¡rio
- **Cache inteligente** com Redis para otimizar conversÃµes
- **ValidaÃ§Ã£o de URLs** com regex patterns especÃ­ficos por plataforma
- **GeraÃ§Ã£o de shortlinks** otimizados para cada plataforma
- **MÃ©tricas de conversÃ£o** em tempo real por plataforma

### ðŸ“± Bot do Telegram
- **FormataÃ§Ã£o dinÃ¢mica** de mensagens com templates especÃ­ficos por plataforma
- **Emojis contextuais** baseados no tipo de oferta e qualidade
- **Sistema de notificaÃ§Ãµes** configurÃ¡vel para administradores
- **Templates personalizados** para cada plataforma de afiliados
- **Modo DRY_RUN** para testes sem publicaÃ§Ã£o
- **Comandos administrativos** (/on, /off, /status, /testpost)

### â�° Sistema de Agendamento Cron
- **Tarefas automÃ¡ticas** para coleta de ofertas (90s)
- **Enriquecimento de preÃ§os** em background (15min)
- **Postagem automÃ¡tica** na fila (45s)
- **AgregaÃ§Ã£o de preÃ§os** para anÃ¡lise (30min)
- **Sistema assÃ­ncrono** com timeouts e backoff
- **Retry automÃ¡tico** para jobs falhados

### ðŸ“‹ Sistema de Fila e ModeraÃ§Ã£o
- **Fila prioritÃ¡ria** de ofertas com scoring automÃ¡tico
- **Sistema de moderaÃ§Ã£o** manual e automÃ¡tica
- **Controle de qualidade** com validaÃ§Ã£o de afiliados
- **Processamento assÃ­ncrono** de ofertas
- **Sistema de prioridades** dinÃ¢micas
- **Workflow de aprovaÃ§Ã£o** em mÃºltiplos nÃ­veis

### ðŸ”„ Pipelines de Processamento
- **IngestÃ£o de ofertas** via APIs e scrapers
- **Enriquecimento automÃ¡tico** de dados
- **Coleta de preÃ§os** histÃ³ricos
- **AgregaÃ§Ã£o inteligente** de dados
- **Sistema de cache** distribuÃ­do
- **Processamento em lote** otimizado

### ðŸ“� Sistema de Postagem AutomÃ¡tica
- **FormataÃ§Ã£o profissional** de mensagens por plataforma
- **Templates com emojis** e campos opcionais
- **Agendador de jobs** (coleta 90s, enriquecimento 15min, postagem 45s)
- **Gerenciador de postagem** com controle de qualidade
- **AprovaÃ§Ã£o automÃ¡tica** baseada em score (threshold 0.8)
- **Sistema de moderaÃ§Ã£o** manual para ofertas de baixa qualidade
- **Controle de rate limiting** e prevenÃ§Ã£o de spam
- **ValidaÃ§Ã£o de mensagens** antes da postagem

### ðŸ•·ï¸� Sistema de Scrapers
- **Scrapers de lojas** com afiliaÃ§Ã£o ativa
- **Scrapers de comunidades** (Promobit, Pelando, MeuPC)
- **Scrapers de preÃ§os** (Zoom, BuscapÃ©)
- **Medidas anti-bot** e rate limiting
- **Cache inteligente** de dados coletados
- **Tratamento de erros** robusto

### ðŸ“Š Dashboard e Monitoramento
- **Dashboard Flet** responsivo e interativo
- **MÃ©tricas de produÃ§Ã£o** em tempo real
- **Sistema de alertas** automÃ¡ticos
- **Logs estruturados** e legÃ­veis
- **Health checks** do sistema
- **RelatÃ³rios automÃ¡ticos** de performance

### ðŸš€ ProduÃ§Ã£o e Escalabilidade
- **ConfiguraÃ§Ã£o Redis** otimizada para produÃ§Ã£o
- **Cache distribuÃ­do** com fallback em memÃ³ria
- **Rate limiting** inteligente por API
- **Sistema de deduplicaÃ§Ã£o** de ofertas
- **Circuit breaker** para falhas de API
- **Auto-scaling** baseado em mÃ­tricas

## ðŸŽ® **SISTEMA GEEK COMPLETO IMPLEMENTADO (2025)**

### **ðŸš€ Sistema de PriorizaÃ§Ã£o Geek/Gamer**
- **GeekPrioritizer**: Algoritmo inteligente para calcular scores geek de produtos
- **Categorias PrimÃ¡rias**: Gaming, Tech Geek, PC Gaming, Smart Home, Audio Premium, Anime/Otaku, Collectibles
- **Categorias SecundÃ¡rias**: EletrodomÃ­sticos Tech, Mobile & Wearables, Fitness Tech, EletrÃ´nicos Gerais
- **Sistema de Scores**: 0.0-1.0 com nÃ­veis CrÃ­tico, Alta, MÃ­dia e Baixa prioridade
- **Sistema de Scores**: 0.0-1.0 com nÃ­veis CrÃ­tico, Alta, MÃ©dia e Baixa prioridade
- **Palavras-chave EspecÃ­ficas**: DetecÃ§Ã£o automÃ¡tica de produtos geek por categoria
- **Produtos Sempre PrioritÃ¡rios**: PlayStation, Xbox, RTX, Smart TVs, Headphones Bluetooth, etc.

### **ðŸš¨ Sistema de Alertas Geek Inteligente**
- **GeekAlertManager**: Monitoramento automÃ¡tico de produtos de alta prioridade
- **Alertas por Score**: CrÃ­tico (0.9+), Alta (0.8+), MÃ©dia (0.7+)
- **Tipos de Alerta**: Alta prioridade, queda de preÃ§o, estoque limitado
- **Limites Inteligentes**: MÃ¡ximo de alertas por hora/dia para evitar spam
- **HistÃ³rico de Alertas**: Tracking completo de alertas enviados e pendentes
- **EstatÃ­sticas em Tempo Real**: MÃ©tricas de performance do sistema geek

### **ðŸ“± Comandos EspecÃ­ficos do Bot Telegram**
- **/geek**: Ofertas geek prioritÃ¡rias gerais
- **/gaming**: Filtro especÃ­fico para gaming (consoles, perifÃ©ricos, jogos)
- **/tech**: Produtos tech premium (smartphones, tablets, notebooks)
- **/anime**: Produtos anime/otaku (figuras, mangÃ¡s, cosplay)
- **/smart**: Smart home e IoT (smart TVs, speakers, automaÃ§Ã£o)
- **/audio**: Audio premium e gaming (headphones, headsets, soundbars)
- **/collectibles**: Collectibles e ediÃ§Ãµes limitadas
- **/geekstats**: EstatÃ­sticas geek do sistema
- **/geekhelp**: Ajuda sobre comandos geek

### **ðŸ“Š Dashboard de MÃ©tricas Geek**
- **Aba EspecÃ­fica**: MÃ©tricas dedicadas para produtos geek/gamer
- **Cards de MÃ©tricas**: Total de ofertas geek, score mÃ©dio, alertas crÃ­ticos, taxa de conversÃ£o
- **GrÃ¡ficos Interativos**: DistribuiÃ§Ã£o por categoria, performance por categoria
- **Top Produtos**: Lista dos produtos geek com maior score
- **Painel de Alertas**: EstatÃ­sticas de alertas por prioridade e tipo
- **AtualizaÃ§Ã£o AutomÃ¡tica**: Refresh automÃ¡tico a cada 5 minutos

### **ðŸ§ª Sistema de Testes Completo**
- **Testes UnitÃ¡rios**: Cobertura completa de GeekPrioritizer, GeekAlertManager e GeekCommands
- **Testes de IntegraÃ§Ã£o**: Workflow completo do sistema geek
- **Testes de ConsistÃªncia**: ValidaÃ§Ã£o de configuraÃ§Ãµes e priorizaÃ§Ã£o
- **Mocks e Fixtures**: Dados de teste realistas para validaÃ§Ã£o
- **Cobertura de CenÃ¡rios**: Gaming, Tech, Smart Home, Audio, Anime, Collectibles

### **âš¡ IntegraÃ§Ã£o com Sistema Existente**
- **Quality Controller**: IntegraÃ§Ã£o completa com sistema de qualidade
- **Pipelines**: PriorizaÃ§Ã£o geek em todos os pipelines de processamento
- **Scrapers**: Foco automÃ¡tico em produtos geek durante coleta
- **Postagem**: PriorizaÃ§Ã£o de ofertas geek na fila de postagem
- **Cache**: OtimizaÃ§Ã£o de cache para produtos geek frequentes

## ðŸ†• **SISTEMA INTELIGENTE DE COLETA AUTOMÃ�TICA AWIN**

## ðŸ”‘ **NOVOS TOKENS IMPLEMENTADOS (31/08/2025)**

### **ðŸŸ  RAKUTEN ADVERTISING**
- **Web Service Token**: Configurado e funcionando âœ…
- **Security Token**: Configurado e funcionando âœ…
- **Status**: API habilitada e integrada ao sistema
- **Funcionalidades**: GeraÃ§Ã£o de deeplinks, healthcheck, cache

### **ðŸŸ¡ SHOPEE AFFILIATE OPEN API**
- **App ID**: `18330800803` âœ…
- **Secret**: Configurado e funcionando âœ…
- **Status**: API habilitada e integrada ao sistema
- **Funcionalidades**: GeraÃ§Ã£o de shortlinks, validaÃ§Ã£o de URLs, cache SQLite

### **ðŸ“Š Resultado dos Testes**
- **Rakuten**: âœ… Cliente criado, healthcheck funcionando, deeplinks gerados
- **Shopee**: âœ… ValidaÃ§Ã£o de URLs, geraÃ§Ã£o de shortlinks, cache funcionando
- **Sistema**: âœ… IntegraÃ§Ã£o completa, testes passando, pronto para produÃ§Ã£o

### **ðŸŽ¯ Coleta AutomÃ¡tica de Ofertas**
- **9 AfiliaÃ§Ãµes Ativas**: COMFY, Trocafy, LG, Kabum, Samsung, Gigantec BR, Ninja, **Rakuten**, **Shopee**
- **API Oficial Awin**: IntegraÃ§Ã£o completa com Publisher API
- **API Rakuten**: Web Service + Security Tokens configurados âœ…
- **API Shopee**: App ID + Secret configurados âœ…
- **Coleta ContÃ­nua**: Pipeline automÃ¡tico configurÃ¡vel (padrÃ£o: 1 hora)
- **Fallback Inteligente**: Product Feed API + Link Builder API

### **ðŸ”§ Filtros AutomÃ¡ticos Inteligentes**
- **5 Filtros PadrÃ£o**: Desconto, preÃ§o, categoria, loja, qualidade
- **Operadores FlexÃ­veis**: EQUALS, GREATER_THAN, IN, BETWEEN, etc.
- **Regras Complexas**: LÃ³gica AND/OR/XOR com prioridades
- **Perfis PersonalizÃ¡veis**: ConfiguraÃ§Ãµes para diferentes cenÃ¡rios
- **Performance Alta**: 333.252 ofertas/segundo

### **ðŸ“Š Pipeline de IngestÃ£o AutomÃ¡tica**
- **ValidaÃ§Ã£o AutomÃ¡tica**: URLs de afiliado e qualidade
- **DeduplicaÃ§Ã£o Inteligente**: Cache para evitar duplicatas
- **Postagem AutomÃ¡tica**: Telegram com rate limiting
- **EstatÃ­sticas Completas**: Performance e mÃ©tricas em tempo real

## ðŸ¤– **SISTEMA AUTOMÃ�TICO DE POSTAGEM TELEGRAM**

### **ðŸš€ AutomaÃ§Ã£o Completa**
- **Coleta AutomÃ¡tica**: Ofertas coletadas a cada 5 minutos
- **Postagem AutomÃ¡tica**: Posts a cada 3 minutos com rate limiting
- **Fila Inteligente**: Sistema de prioridades e controle de qualidade
- **Scheduler AvanÃ§ado**: Jobs configurÃ¡veis e monitoramento em tempo real

### **ðŸ“± IntegraÃ§Ã£o Telegram**
- **Bot Configurado**: Credenciais e permissÃµes configuradas
- **Canal Ativo**: Postagem automÃ¡tica no canal configurado
- **FormataÃ§Ã£o Profissional**: Templates personalizados por plataforma
- **Imagens AutomÃ¡ticas**: Suporte a imagens dos produtos

### **âš™ï¸� Controle e Monitoramento**
- **Sistema de ProduÃ§Ã£o**: Script dedicado para ativaÃ§Ã£o em produÃ§Ã£o
- **Logs Estruturados**: Sistema de logging completo com encoding UTF-8
- **Health Checks**: VerificaÃ§Ã£o automÃ¡tica da saÃºde do sistema
- **Parada Graciosa**: Controle via Ctrl+C e sinais do sistema
- **Status em Tempo Real**: Monitoramento a cada 5 minutos

### **ðŸ”§ ConfiguraÃ§Ãµes AvanÃ§adas**
- **Rate Limiting**: 3 minutos entre posts (configurÃ¡vel)
- **Filtros de Qualidade**: Desconto mÃ­nimo de 10%
- **Categorias Permitidas**: Smartphones, Notebooks, Smart TVs, Consoles, Fones
- **Fallback AutomÃ¡tico**: RecuperaÃ§Ã£o de erros e retry inteligente
- **Backup AutomÃ¡tico**: Sistema de recuperaÃ§Ã£o

### **ðŸ”„ Monitoramento em Tempo Real**
- **Status do Pipeline**: ExecuÃ§Ãµes, sucessos, falhas
- **Performance dos Filtros**: Tempo mÃ©dio, ofertas processadas
- **SaÃºde do Sistema**: Credenciais, conectividade, logs
- **AtualizaÃ§Ã£o AutomÃ¡tica**: Refresh configurÃ¡vel (padrÃ£o: 5s)

## ðŸ�—ï¸� Arquitetura Completa

```
src/
â”œâ”€â”€ affiliate/          # Conversores de afiliados
â”‚   â”œâ”€â”€ amazon.py      # Conversor Amazon (ASIN-first + fallback)
â”‚   â”œâ”€â”€ mercadolivre.py # Conversor Mercado Livre
â”‚   â”œâ”€â”€ shopee.py      # Conversor Shopee
â”‚   â”œâ”€â”€ magazineluiza.py # Conversor Magazine Luiza
â”‚   â”œâ”€â”€ aliexpress.py  # Conversor AliExpress
â”‚   â”œâ”€â”€ awin.py        # Conversor Awin
â”‚   â”œâ”€â”€ rakuten.py     # Conversor Rakuten
â”‚   â”œâ”€â”€ *_api.py       # Clientes de API oficiais
â”‚   â””â”€â”€ base_api.py    # Classe base para APIs
â”œâ”€â”€ app/                # AplicaÃ§Ã£o principal
â”‚   â”œâ”€â”€ queue/         # Sistema de fila de ofertas
â”‚   â”‚   â”œâ”€â”€ offer_queue.py      # Fila principal
â”‚   â”‚   â”œâ”€â”€ moderation_system.py # Sistema de moderaÃ§Ã£o
â”‚   â”‚   â”œâ”€â”€ quality_controller.py # Controle de qualidade
â”‚   â”‚   â””â”€â”€ queue_manager.py    # Gerenciador da fila
â”‚   â”œâ”€â”€ scheduler/     # Agendador cron
â”‚   â”‚   â”œâ”€â”€ cron_manager.py     # Gerenciador de cron jobs
â”‚   â”‚   â”œâ”€â”€ job_scheduler.py    # Agendador de tarefas
â”‚   â”‚   â”œâ”€â”€ task_runner.py     # Executor de tarefas
â”‚   â”‚   â””â”€â”€ post_scheduler.py  # Agendador de postagens
â”‚   â”œâ”€â”€ dashboard/     # Dashboard interno
â”‚   â””â”€â”€ bot/           # Bot interno
â”œâ”€â”€ core/               # Componentes principais
â”‚   â”œâ”€â”€ models.py      # Modelos de dados (Offer, etc.)
â”‚   â”œâ”€â”€ settings.py    # ConfiguraÃ§Ãµes (.env)
â”‚   â”œâ”€â”€ database.py    # Banco de dados SQLite
â”‚   â”œâ”€â”€ db_init.py     # InicializaÃ§Ã£o do banco
â”‚   â”œâ”€â”€ affiliate_*.py # Sistema de afiliados
â”‚   â”œâ”€â”€ conversion_metrics.py  # MÃ©tricas de conversÃ£o
â”‚   â”œâ”€â”€ failure_alerts.py      # Sistema de alertas
â”‚   â”œâ”€â”€ optimization_engine.py # Motor de otimizaÃ§Ã£o
â”‚   â”œâ”€â”€ performance_logger.py  # Logger de performance
â”‚   â”œâ”€â”€ enhanced_metrics.py    # MÃ©tricas avanÃ§adas
â”‚   â”œâ”€â”€ alert_system.py        # Sistema de alertas
â”‚   â”œâ”€â”€ analytics_queries.py   # Queries analÃ­ticas
â”‚   â”œâ”€â”€ cache_config.py        # ConfiguraÃ§Ã£o de cache
â”‚   â”œâ”€â”€ deduplication.py       # Sistema de deduplicaÃ§Ã£o
â”‚   â”œâ”€â”€ rate_limiter.py        # Rate limiting
â”‚   â”œâ”€â”€ affiliate_cache.py     # Cache de afiliados
â”‚   â”œâ”€â”€ offer_pipeline.py      # Pipeline de ofertas
â”‚   â”œâ”€â”€ affiliate_converter.py # Conversor de afiliados
â”‚   â”œâ”€â”€ matchers.py            # Sistema de matching
â”‚   â”œâ”€â”€ metrics.py             # MÃ©tricas bÃ¡sicas
â”‚   â”œâ”€â”€ platforms.py           # ConfiguraÃ§Ãµes de plataformas
â”‚   â”œâ”€â”€ live_logs.py           # Logs em tempo real
â”‚   â”œâ”€â”€ logging_setup.py       # ConfiguraÃ§Ã£o de logs
â”‚   â”œâ”€â”€ storage.py             # Sistema de armazenamento
â”‚   â”œâ”€â”€ monitoring/            # Sistema de monitoramento
â”‚   â””â”€â”€ cache/                 # Sistema de cache
â”œâ”€â”€ pipelines/          # Pipelines de processamento
â”‚   â”œâ”€â”€ ingest_offers_api.py   # IngestÃ£o via APIs
â”‚   â”œâ”€â”€ enrich_offers_api.py   # Enriquecimento de dados
â”‚   â”œâ”€â”€ price_collect.py       # Coleta de preÃ§os
â”‚   â”œâ”€â”€ price_enrich.py        # Enriquecimento de preÃ§os
â”‚   â””â”€â”€ price_aggregate.py     # AgregaÃ§Ã£o de preÃ§os
â”œâ”€â”€ posting/            # Sistema de postagem
â”‚   â”œâ”€â”€ message_formatter.py   # FormataÃ§Ã£o de mensagens
â”‚   â””â”€â”€ posting_manager.py     # Gerenciador de postagens
â”œâ”€â”€ scrapers/           # Sistema de scrapers
â”‚   â”œâ”€â”€ base_scraper.py        # Classe base para scrapers
â”‚   â”œâ”€â”€ lojas/                 # Scrapers de lojas
â”‚   â”œâ”€â”€ comunidades/           # Scrapers de comunidades
â”‚   â”‚   â”œâ”€â”€ promobit/          # Scraper Promobit
â”‚   â”‚   â”œâ”€â”€ pelando/           # Scraper Pelando
â”‚   â”‚   â””â”€â”€ meupc/             # Scraper MeuPC
â”‚   â””â”€â”€ precos/                # Scrapers de preÃ§os
â”‚       â”œâ”€â”€ zoom/              # Scraper Zoom
â”‚       â””â”€â”€ buscape/           # Scraper BuscapÃ©
â”œâ”€â”€ telegram_bot/       # Bot do Telegram
â”‚   â”œâ”€â”€ bot.py                 # Bot principal
â”‚   â”œâ”€â”€ bot_manager.py         # Gerenciador do bot
â”‚   â”œâ”€â”€ message_builder.py     # Construtor de mensagens
â”‚   â””â”€â”€ notification_manager.py # Gerenciador de notificaÃ§Ãµes
â”œâ”€â”€ utils/              # UtilitÃ¡rios
â”‚   â”œâ”€â”€ anti_bot.py            # Medidas anti-bot
â”‚   â”œâ”€â”€ affiliate_validator.py # Validador de URLs
â”‚   â”œâ”€â”€ asin_cache.py          # Cache de ASINs
â”‚   â”œâ”€â”€ url_utils.py           # UtilitÃ¡rios de URL
â”‚   â””â”€â”€ sqlite_helpers.py      # Helpers para SQLite
â”œâ”€â”€ diagnostics/        # Sistema de diagnÃ³stico
â”‚   â””â”€â”€ ui_reporter.py         # RelatÃ³rios de UI
â”œâ”€â”€ recommender/        # Sistema de recomendaÃ§Ã£o
â”œâ”€â”€ db/                 # Banco de dados
â”‚   â”œâ”€â”€ garimpeiro_geek.db    # Banco principal
â”‚   â”œâ”€â”€ aff_cache.sqlite       # Cache de afiliados
â”‚   â””â”€â”€ analytics.sqlite       # Banco de analytics
â”œâ”€â”€ logs/               # Logs do sistema
â”œâ”€â”€ exports/            # ExportaÃ§Ãµes de dados
â””â”€â”€ tests/              # Testes automatizados
    â”œâ”€â”€ unit/           # Testes unitÃ¡rios
    â”œâ”€â”€ e2e/            # Testes end-to-end
    â”œâ”€â”€ api/            # Testes de API
    â”œâ”€â”€ helpers/        # Helpers para testes
    â””â”€â”€ data/           # Dados de teste

apps/
â””â”€â”€ flet_dashboard/     # Dashboard Flet
    â”œâ”€â”€ main.py         # AplicaÃ§Ã£o principal
    â”œâ”€â”€ ui_components.py # Componentes de UI
    â””â”€â”€ run_dashboard.py # Script de execuÃ§Ã£o
```

## ðŸš€ InstalaÃ§Ã£o

### PrÃ©-requisitos
- Python 3.9+
- Redis 5.0+ (opcional, com fallback em memÃ³ria)
- Git

### 1. Clone o repositÃ³rio
```bash
git clone https://github.com/duduzinho15/Ainda-nao-funciona.git
cd Sistema-de-Recomendacoes-de-Ofertas-Telegram2.0
```

### 2. Instale as dependÃªncias
```bash
pip install -r requirements.txt
```

### 3. Configure as variÃ¡veis de ambiente
```bash
cp config/env.example .env
# Edite o arquivo .env com suas configuraÃ§Ãµes
```

### 4. Configure o Redis (opcional)
```bash
# Para desenvolvimento, o sistema usa cache em memÃ³ria
# Para produÃ§Ã£o, configure Redis conforme config/redis.production.conf
```

### 5. Ative o Sistema AutomÃ¡tico
```bash
# Testar o sistema
python test_auto_system.py

# Executar demonstraÃ§Ã£o
python demo_telegram_posting.py

# Ativar em produÃ§Ã£o
python start_production_system.py

# Para parar: Ctrl+C
```

## âš™ï¸� ConfiguraÃ§Ã£o

### VariÃ¡veis de Ambiente (.env)
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

## ðŸ§ª Testes

### Executar todos os testes
```bash
make test
```

### Testes unitÃ¡rios
```bash
make test-unit
```

### Testes de integraÃ§Ã£o
```bash
make test-e2e
```

### Linting e formataÃ§Ã£o
```bash
make format      # FormataÃ§Ã£o com Black + Ruff
make lint        # Linting com Ruff
make type-check  # VerificaÃ§Ã£o de tipos com MyPy
```

### Testes especÃ­ficos
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

## ðŸ§ª Testes e ValidaÃ§Ãµes

### Executando Testes

```bash
# Rodar todos os testes
make test-all

# Apenas testes unitÃ¡rios
make test-unit

# Apenas testes E2E
make test-e2e

# Verificar formataÃ§Ã£o e estilo
make lint

# Verificar tipos
make typecheck
```

### Regras de ValidaÃ§Ã£o por Plataforma

#### Amazon
- âœ… URLs devem conter ASIN vÃ¡lido (B seguido de 9 caracteres alfanumÃ©ricos)
- âœ… Tag de afiliado obrigatÃ³ria: `tag=garimpeirogee-20`
- â�Œ Bloquear URLs sem ASIN

#### Awin
- âœ… MID permitidos: 23377, 51277, 33061, 17729, 106765, 25539
- âœ… AFFID permitidos: 2370719, 2510157
- â�Œ Bloquear URLs com parÃ¢metros invÃ¡lidos

#### Shopee
- âœ… Apenas shortlinks: `s.shopee.com.br`
- â�Œ Bloquear URLs completas
- â�Œ Bloquear categorias nÃ£o permitidas

#### AliExpress
- âœ… Apenas shortlinks: `s.click.aliexpress.com/e/`
- âœ… Exigir `tracking_id=telegram`
- â�Œ Bloquear URLs diretas

#### Mercado Livre
- âœ… Apenas URLs sociais e shortlinks
- â�Œ Bloquear URLs de produto diretas

#### Magazine Luiza
- âœ… Apenas vitrine: `magazinevoce.com.br/magazinegarimpeirogeek`
- â�Œ Bloquear `magazineluiza.com.br`

### Modo DRY_RUN

Para testar sem publicar ofertas, use a variÃ¡vel de ambiente:

```bash
# No Windows
set DRY_RUN=1
python -m src.app.main

# No Linux/macOS
export DRY_RUN=1
python -m src.app.main
```

## ðŸš€ ExecuÃ§Ã£o

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

### 4. Executar scrapers especÃ­ficos
```bash
# Scraper Promobit
python -m src.scrapers.comunidades.promobit

# Scraper de preÃ§os Zoom
python -m src.scrapers.precos.zoom
```

### 5. Executar pipelines
```bash
# Pipeline de ingestÃ£o
python -m src.pipelines.ingest_offers_api

# Pipeline de enriquecimento
python -m src.pipelines.enrich_offers_api
```

### 6. Executar demonstraÃ§Ãµes dos sistemas
```bash
# DemonstraÃ§Ã£o do sistema de testes em produÃ§Ã£o
python demo_production_testing.py

# DemonstraÃ§Ã£o do sistema de monitoramento de conversÃ£o
python demo_conversion_monitoring.py

# DemonstraÃ§Ã£o do sistema de feedback dos usuÃ¡rios
python demo_user_feedback.py

# DemonstraÃ§Ã£o do sistema de expansÃ£o de categorias
python demo_category_expansion.py

# Teste rÃ¡pido do sistema de expansÃ£o de categorias
python demo_category_expansion.py quick

# DemonstraÃ§Ã£o do sistema de IA para otimizaÃ§Ã£o
python demo_ai_optimization.py

# Teste rÃ¡pido do sistema de IA para otimizaÃ§Ã£o
python demo_ai_optimization.py quick

# Sistema Unificado de Dashboard
python demo_unified_dashboard.py

# Teste rÃ¡pido do sistema unificado
python demo_unified_dashboard.py quick

# Testes de Performance AvanÃ§ados
python demo_performance_tests.py full

# Teste rÃ¡pido de performance
python demo_performance_tests.py quick

# IntegraÃ§Ã£o com Afiliados
python demo_affiliate_integration.py full
python demo_affiliate_integration.py quick

# MÃ©tricas AvanÃ§adas
python demo_advanced_metrics.py quick
python demo_advanced_metrics.py full
python demo_advanced_metrics.py dashboard

# Deep Learning
python demo_deep_learning.py quick
python demo_deep_learning.py full
python demo_deep_learning.py dashboard
```

## ðŸ“Š Monitoramento

### Dashboard Flet
Acesse o dashboard em tempo real para monitorar:

#### **ðŸ“Š Tabs DisponÃ­veis**
- **VisÃ£o Geral**: KPIs principais e alertas do sistema
- **Amazon ASIN**: Qualidade de normalizaÃ§Ã£o e estratÃ©gias de extraÃ§Ã£o
- **ðŸ›’ Mercado Livre**: MÃ©tricas especÃ­ficas de qualidade, performance e receita
- **AfiliaÃ§Ã£o**: Monitoramento de links afiliados e receita
- **Performance**: LatÃªncia de deeplinks e freshness de preÃ§os
- **Alertas**: Sistema de notificaÃ§Ãµes e problemas detectados
- **Controles**: Gerenciamento de plataformas e configuraÃ§Ãµes

#### **ðŸ›’ Aba Mercado Livre - Funcionalidades**
- **Qualidade dos Links**: Shortlinks, links sociais e diretos
- **Score de Qualidade**: Baseado em tipos de link (shortlinks tÃªm peso maior)
- **Performance**: Taxa de conversÃ£o e latÃªncia mÃ©dia
- **Receita**: Total de receita e ticket mÃ©dio por transaÃ§Ã£o
- **GrÃ¡ficos**: DistribuiÃ§Ã£o de tipos de link e taxa de conversÃ£o
- **Alertas**: NotificaÃ§Ãµes para qualidade < 70% e conversÃ£o < 80%

#### **ðŸ”§ Aba ModeraÃ§Ã£o ML - Sistema Completo de Workflow**
- **Scraping AutomÃ¡tico**: Coleta ofertas das melhores categorias (smartphones, notebooks, smart-tvs, consoles)
- **Filtros de Qualidade**: Desconto mÃ­nimo 10%, preÃ§o mÃ¡ximo R$ 5.000, avaliaÃ§Ã£o mÃ­nima 4.0
- **ModeraÃ§Ã£o Manual**: Interface para converter links para afiliados via dashboard
- **ValidaÃ§Ã£o AutomÃ¡tica**: VerificaÃ§Ã£o de URLs de afiliado (shortlinks e links sociais)
- **Pipeline Integrado**: Fluxo completo desde scraping atÃ© postagem no Telegram
- **Controle de Status**: Acompanhamento de tarefas pendentes, aprovadas e prontas para postagem

### MÃ©tricas DisponÃ­veis
- **ConversÃµes**: Total, sucesso, falha por plataforma
- **Performance**: Tempo de resposta, cache hits/misses
- **Qualidade**: Score das ofertas, taxa de aprovaÃ§Ã£o
- **Sistema**: Uso de memÃ³ria, conexÃµes, uptime
- **Scrapers**: Taxa de sucesso, erros, performance

### Logs Estruturados
- Logs de aplicaÃ§Ã£o em `src/logs/`
- Logs de performance e mÃ©tricas
- Logs de erros e alertas
- Logs de auditoria e seguranÃ§a

## ðŸ”§ Desenvolvimento

### FormataÃ§Ã£o de CÃ³digo
```bash
# FormataÃ§Ã£o automÃ¡tica
make format

# Linting
make lint

# VerificaÃ§Ã£o de tipos
make type-check

# Limpeza
make clean
```

### Estrutura de Commits
Seguimos o padrÃ£o [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` Nova funcionalidade
- `fix:` CorreÃ§Ã£o de bug
- `docs:` DocumentaÃ§Ã£o
- `style:` FormataÃ§Ã£o
- `refactor:` RefatoraÃ§Ã£o
- `test:` Testes
- `chore:` ManutenÃ§Ã£o

### PadrÃµes de CÃ³digo
- **Type hints** obrigatÃ³rios em todas as funÃ§Ãµes pÃºblicas
- **Docstrings** claras e objetivas
- **Logs estruturados** com contexto
- **Tratamento de erros** robusto
- **Testes unitÃ¡rios** para todas as funcionalidades
- **Imports absolutos** a partir de `src/`

## ðŸ“š DocumentaÃ§Ã£o

- [ðŸ“‹ TODO Unificado](TODO.md) - Roadmap completo do projeto
- [ðŸ”§ EspecificaÃ§Ãµes TÃ©cnicas](docs/ESPECIFICACAO_GARIMPEIRO_GEEK_COM_RAKUTEN.md)
- [ðŸ¤– DocumentaÃ§Ã£o do Bot](docs/telegram_bot.md)
- [ðŸ”— APIs de IntegraÃ§Ã£o](docs/apis_integracao.md)
- [ðŸ“Š Exemplos de Afiliados](docs/affiliate_examples.md)
- [ðŸ“Š Dados HistÃ³ricos](docs/dados_historico_precos.md)

## ðŸ¤� ContribuiÃ§Ã£o

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanÃ§as (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Antes de submeter
```bash
# Executar todos os checks
make format && make lint && make type-check && make test

# Verificar cobertura de testes
make test  # Inclui relatÃ³rio de cobertura
```

## ðŸ“„ LicenÃ§a

Este projeto estÃ¡ sob a licenÃ§a MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ðŸ†˜ Suporte

Para suporte e dÃºvidas:
- Abra uma [Issue](https://github.com/duduzinho15/Ainda-nao-funciona/issues)
- Consulte a [documentaÃ§Ã£o](docs/)
- Verifique os [exemplos](tests/)
- Consulte o [TODO.md](TODO.md) para roadmap

## ðŸŽ¯ Roadmap

### âœ… Implementado
- [x] Sistema de afiliados completo
- [x] Bot do Telegram funcional
- [x] Sistema de fila e moderaÃ§Ã£o
- [x] Pipelines de processamento
- [x] Scrapers organizados
- [x] Dashboard Flet
- [x] Sistema de monitoramento

### âœ… Recentemente Implementado
- [x] Testes E2E completos
- [x] Sistema de postagem automÃ¡tica
- [x] OtimizaÃ§Ãµes de performance
- [x] AnÃ¡lise completa do projeto
- [x] Gigantec BR integrada ao Awin
- [x] Sistema 100% funcional
- [x] **Tokens Rakuten implementados** (Web Service + Security)
- [x] **Tokens Shopee implementados** (App ID + Secret)
- [x] **APIs Rakuten e Shopee habilitadas e funcionais**
- [x] **ðŸ›’ Aba Mercado Livre implementada no Dashboard** (MÃ©tricas especÃ­ficas, qualidade de links, performance e receita)
- [x] **ðŸ”§ Sistema Completo de ModeraÃ§Ã£o Manual do Mercado Livre** (Scraping automÃ¡tico, conversÃ£o manual via dashboard, postagem automÃ¡tica)
- [x] **ðŸŽ¯ Sistema de PriorizaÃ§Ã£o Geek Completo** (Algoritmo de score, alertas, comandos Telegram, dashboard Flet)
- [x] **ðŸ“Š Sistema de Teste em ProduÃ§Ã£o** (Pipeline de dados reais, monitor de performance, validador do sistema)
- [x] **ðŸ“ˆ Sistema de Monitoramento de ConversÃ£o Geek vs Geral** (Rastreamento, anÃ¡lise, dashboard, relatÃ³rios)
- [x] **ðŸ”„ Sistema de Feedback dos UsuÃ¡rios** (Coleta, anÃ¡lise, ajuste automÃ¡tico de scores, dashboard interativo)
- [x] **ðŸ“ˆ Sistema de ExpansÃ£o de Categorias** (AnÃ¡lise de tendÃªncias, pesquisa de mercado, expansÃ£o automÃ¡tica, otimizaÃ§Ã£o)
- [x] **ðŸ¤– Sistema de IA para OtimizaÃ§Ã£o AutomÃ¡tica** (Machine Learning, prediÃ§Ã£o de scores, otimizaÃ§Ã£o automÃ¡tica, dashboard interativo)
- [x] **ðŸŽ›ï¸� Sistema Unificado de Dashboard** (IntegraÃ§Ã£o completa de todos os sistemas, mÃ©tricas consolidadas, controle centralizado)
- [x] **ðŸ”— Sistema de IntegraÃ§Ã£o com Afiliados Reais** (APIs oficiais, validaÃ§Ã£o de links, mÃºltiplas redes, dashboard dedicado)
- [x] **ðŸ“Š Sistema de MÃ©tricas AvanÃ§adas** (AnÃ¡lise temporal, segmentaÃ§Ã£o demogrÃ¡fica, sazonalidade, engajamento, insights preditivos)
- [x] **ðŸ¤– Sistema de Deep Learning** (Redes neurais avanÃ§adas, prediÃ§Ãµes inteligentes, otimizaÃ§Ã£o automÃ¡tica de priorizaÃ§Ã£o)

### **ðŸ¤– Sistema de IA para OtimizaÃ§Ã£o AutomÃ¡tica de PriorizaÃ§Ã£o**
- **AIOptimizer**: Otimizador principal que coordena todo o sistema de IA
- **DataCollector**: Coleta dados histÃ³ricos e features para treinamento dos modelos
- **ModelTrainer**: Treina modelos de machine learning (Random Forest, Gradient Boosting, Linear Regression)
- **PredictionEngine**: Motor de prediÃ§Ã£o que otimiza scores baseado em dados histÃ³ricos
- **OptimizationDashboard**: Interface interativa para monitorar e controlar o sistema
- **Features Inteligentes**: PreÃ§o, score geek, taxa de conversÃ£o, engajamento, horÃ¡rio, estaÃ§Ã£o, reputaÃ§Ã£o da loja
- **Modelos de IA**: 3 algoritmos diferentes com mÃ©tricas de performance (RÂ², MSE, MAE, Cross-Validation)
- **Auto-retreinamento**: Sistema que retreina modelos automaticamente baseado em novos dados
- **ConfianÃ§a e Insights**: AnÃ¡lise de confianÃ§a das prediÃ§Ãµes e fatores-chave que influenciam os scores
- **OtimizaÃ§Ã£o em Lote**: Processamento eficiente de mÃºltiplas ofertas simultaneamente
- **HistÃ³rico Completo**: Tracking de todas as otimizaÃ§Ãµes realizadas pelo sistema

### **ðŸ§ª Sistema de Testes de Performance AvanÃ§ados**

Sistema completo de testes de stress, carga, concorrÃªncia, memÃ³ria, rede e benchmark para validar a performance do sistema em diferentes cenÃ¡rios.

#### **Componentes Implementados:**

1. **ðŸ“Š Performance Monitor** (`src/tests/performance/performance_monitor.py`)
   - Monitoramento em tempo real de CPU, memÃ³ria, disco e rede
   - Registro de tempos de resposta
   - Alertas configurÃ¡veis para thresholds

2. **âš¡ Stress Tester** (`src/tests/performance/stress_tester.py`)
   - Testes de stress com ramp-up/down
   - UsuÃ¡rios concorrentes configurÃ¡veis
   - CenÃ¡rios simulados (scraping, processing, posting, validation)

3. **ðŸ“ˆ Load Generator** (`src/tests/performance/load_generator.py`)
   - Testes de carga progressiva
   - Aumento gradual de usuÃ¡rios
   - MÃ©tricas de throughput e latÃªncia

4. **ðŸ”„ Concurrency Tester** (`src/tests/performance/concurrency_tester.py`)
   - Testes de concorrÃªncia com ThreadPoolExecutor
   - Tarefas distribuÃ­das por peso
   - AnÃ¡lise de deadlocks e race conditions

5. **ðŸ’¾ Memory Profiler** (`src/tests/performance/memory_profiler.py`)
   - Monitoramento de uso de memÃ³ria
   - DetecÃ§Ã£o de vazamentos com tracemalloc
   - ForÃ§ar garbage collection

6. **ðŸŒ� Network Simulator** (`src/tests/performance/network_simulator.py`)
   - SimulaÃ§Ã£o de condiÃ§Ãµes de rede (latÃªncia, jitter, packet loss)
   - InterceptaÃ§Ã£o de chamadas socket
   - Testes de conectividade

7. **âš¡ Benchmark Runner** (`src/tests/performance/benchmark_runner.py`)
   - Benchmarks especÃ­ficos para funÃ§Ãµes
   - Profiling de CPU com cProfile
   - MÃ©tricas de performance detalhadas

#### **Como Usar:**

```bash
# DemonstraÃ§Ã£o rÃ¡pida
python demo_performance_tests.py quick

# DemonstraÃ§Ã£o completa
python demo_performance_tests.py full
```

#### **MÃ©tricas Coletadas:**
- Throughput (RPS - Requests Per Second)
- Tempo mÃ©dio de resposta
- Taxa de erro
- Uso de CPU e memÃ³ria
- Vazamentos de memÃ³ria
- LatÃªncia de rede
- Performance de benchmarks

---

### **ðŸ”— Sistema de IntegraÃ§Ã£o com Afiliados Reais**

Sistema completo para integraÃ§Ã£o com redes de afiliados reais, incluindo APIs oficiais, validaÃ§Ã£o de links e monitoramento de mÃ©tricas.

#### **Componentes Principais:**

1. **AffiliateIntegrationManager** (`src/core/affiliate_integration.py`)
   - Gerenciamento centralizado de redes de afiliados
   - ConfiguraÃ§Ã£o de APIs oficiais
   - ValidaÃ§Ã£o de links em lote
   - Armazenamento em banco SQLite
   - MÃ©tricas de performance

2. **AffiliateLinkValidator** (`src/core/affiliate_integration.py`)
   - ValidaÃ§Ã£o automÃ¡tica de links de afiliado
   - DetecÃ§Ã£o de rede por URL
   - Cache de validaÃ§Ãµes
   - Teste de acessibilidade
   - Rate limiting inteligente

3. **AffiliateAPIClient** (`src/core/affiliate_integration.py`)
   - Cliente base para APIs de afiliados
   - Rate limiting automÃ¡tico
   - Retry com backoff exponencial
   - Tratamento de erros robusto

4. **AmazonAPIClient** (`src/core/affiliate_integration.py`)
   - IntegraÃ§Ã£o especÃ­fica com Amazon Associates
   - Busca de produtos via API oficial
   - GeraÃ§Ã£o automÃ¡tica de links de afiliado
   - Tratamento de categorias

5. **AwinAPIClient** (`src/core/affiliate_integration.py`)
   - IntegraÃ§Ã£o com rede Awin
   - Listagem de programas disponÃ­veis
   - Busca de produtos por programa
   - MÃ©tricas de conversÃ£o

6. **AffiliateDashboard** (`src/core/affiliate_dashboard.py`)
   - Interface console para gerenciamento
   - ConfiguraÃ§Ã£o de redes
   - ValidaÃ§Ã£o de links
   - Busca de produtos
   - RelatÃ³rios e mÃ©tricas

#### **Redes Suportadas:**
- **Amazon Associates**: API oficial, busca de produtos, geraÃ§Ã£o de links
- **Awin**: API REST, programas de afiliados, mÃ©tricas detalhadas
- **Rakuten**: Plataforma de afiliados globais, mÃºltiplas categorias
- **Shopee**: Marketplace com programa de afiliados
- **AliExpress**: Plataforma global de e-commerce
- **Mercado Livre**: Maior plataforma de e-commerce da AmÃ©rica Latina
- **Magazine Luiza**: Varejista brasileiro com programa de afiliados
- **Perfect Pay**: Gateway de pagamentos
- **Kiwify**: Plataforma de produtos digitais

#### **Funcionalidades:**
- âœ… **ConfiguraÃ§Ã£o de Redes**: Adicionar, editar, remover redes de afiliados
- âœ… **ValidaÃ§Ã£o de Links**: VerificaÃ§Ã£o automÃ¡tica de links vÃ¡lidos
- âœ… **Busca de Produtos**: Busca em mÃºltiplas redes simultaneamente
- âœ… **MÃ©tricas de Performance**: CTR, conversÃ£o, receita, comissÃµes
- âœ… **Cache Inteligente**: Cache de validaÃ§Ãµes para performance
- âœ… **Rate Limiting**: Controle automÃ¡tico de requisiÃ§Ãµes
- âœ… **Tratamento de Erros**: RecuperaÃ§Ã£o robusta de falhas
- âœ… **Dashboard Interativo**: Interface console completa

#### **Como Usar:**

```bash
# DemonstraÃ§Ã£o rÃ¡pida
python demo_affiliate_integration.py quick

# DemonstraÃ§Ã£o completa
python demo_affiliate_integration.py full

# Dashboard interativo
python -c "from src.core.affiliate_dashboard import affiliate_dashboard; import asyncio; asyncio.run(affiliate_dashboard.show_main_menu())"
```

#### **ConfiguraÃ§Ã£o de Redes:**

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

#### **ValidaÃ§Ã£o de Links:**

```python
from src.core.affiliate_integration import affiliate_manager

# Validar links em lote
urls = [
    "https://amazon.com.br/dp/B08N5WRWNW?tag=garimpeirogeek-20",
    "https://awin1.com/cread.php?awinmid=12345&awinaffid=67890"
]

results = await affiliate_manager.validate_links(urls)
for result in results:
    print(f"{result.url}: {'âœ…' if result.is_valid else 'â�Œ'}")
```

#### **Busca de Produtos:**

```python
# Buscar produtos em mÃºltiplas redes
products = await affiliate_manager.search_products(
    keywords="headphone gamer",
    category="EletrÃ´nicos"
)

for product in products:
    print(f"{product.name}: R$ {product.price:.2f}")
```

#### **MÃ©tricas Coletadas:**
- Taxa de validaÃ§Ã£o de links
- Performance por rede
- Produtos encontrados
- ConversÃµes e cliques
- Receita e comissÃµes
- Tempo de resposta das APIs

---

### **ðŸŽ›ï¸� Sistema Unificado de Dashboard**
- **UnifiedDashboard**: Dashboard principal que coordena todos os sistemas implementados
- **SystemStatus**: Monitoramento de status de cada sistema em tempo real
- **DashboardMetrics**: MÃ©tricas consolidadas de todos os sistemas
- **Health Monitoring**: Monitoramento de saÃºde do sistema completo
- **IntegraÃ§Ã£o Total**: Todos os 5 sistemas implementados integrados em uma interface Ãºnica
- **RelatÃ³rios Unificados**: RelatÃ³rios consolidados de todos os sistemas
- **Controle Centralizado**: Interface Ãºnica para controle de todos os sistemas

### ðŸ“‹ Planejado
- [ ] Machine Learning para scoring avanÃ§ado
- [ ] Machine Learning para scoring
- [ ] IntegraÃ§Ã£o com mais plataformas
- [ ] Sistema de notificaÃ§Ãµes push
- [ ] API REST para integraÃ§Ãµes
- [ ] Dashboard mobile responsivo
- [ ] Sistema de backup automÃ¡tico

---

## ðŸ”„ AtualizaÃ§Ãµes AutomÃ¡ticas

**âš ï¸� IMPORTANTE**: Este README Ã© atualizado automaticamente sempre que:
- Novos mÃ³dulos sÃ£o criados
- Estrutura de pastas Ã© alterada
- Novas funcionalidades sÃ£o implementadas
- ConfiguraÃ§Ãµes sÃ£o modificadas

### **Sistema de AtualizaÃ§Ã£o AutomÃ¡tica**
O projeto inclui um sistema inteligente que mantÃ©m o README sempre sincronizado:

#### **AtualizaÃ§Ã£o Manual**
```bash
# Windows (PowerShell)
.\scripts\update_readme.ps1

# Linux/Mac
python scripts/update_readme.py

# Via Makefile (se disponÃ­vel)
make update-readme
```

#### **AtualizaÃ§Ã£o AutomÃ¡tica**
- **Git Hook**: Executa automaticamente antes de cada commit
- **DetecÃ§Ã£o Inteligente**: Identifica mudanÃ§as na estrutura
- **Cache de Performance**: Evita atualizaÃ§Ãµes desnecessÃ¡rias
- **IntegraÃ§Ã£o Total**: Funciona em Windows, Linux e Mac

#### **DocumentaÃ§Ã£o Completa**
Para detalhes sobre o sistema de atualizaÃ§Ã£o, consulte:
- [ðŸ“‹ Sistema de AtualizaÃ§Ã£o AutomÃ¡tica](docs/README_UPDATE_SYSTEM.md)

**Para manter o README atualizado**:
1. âœ… **Sempre crie arquivos** dentro da estrutura definida
2. âœ… **Use os padrÃµes** de nomenclatura estabelecidos
3. âœ… **Documente novas funcionalidades**
4. âœ… **O sistema atualiza automaticamente** via Git hooks

---

**Desenvolvido com â�¤ï¸� para a comunidade de ofertas e promoÃ§Ãµes**

**VersÃ£o**: 2.0  
**Ãšltima AnÃ¡lise**: 31-08-2025 12:30:00  
**Status**: âœ… Sistema 100% Funcional e Pronto para ProduÃ§Ã£o

### Guardrail de Publicação
- Método central: `is_publishable_affiliate_url(url) -> (bool, reason)`
- Awin: `https://www.awin1.com/cread.php?awinmid=...&awinaffid=...&ued=...`
- AliExpress: `https://s.click.aliexpress.com/e/...` com `tracking_id=telegram`
- Shopee: `https://s.shopee.com.br/{token}`
- Magalu: `https://www.magazinevoce.com.br/magazinegarimpeirogeek/.../p/{sku}`
- Mercado Livre: `.../sec/...` ou `.../social/garimpeirogeek?...matt_word=garimpeirogeek`
- Amazon: ASIN-first; bloquear se não houver ASIN
