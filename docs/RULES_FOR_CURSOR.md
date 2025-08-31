# 🛡️ Regras para o Cursor - Garimpeiro Geek

## 📁 **ESTRUTURA DE PASTAS (IMUTÁVEL)**

### **Organização Oficial:**
```
src/
├── affiliate/          # Conversores de link (Awin, Amazon, ML, Magalu, etc.)
├── scrapers/           # Scrapers de lojas e comunidades
│   ├── lojas/         # Apenas lojas com afiliação ativa
│   ├── comunidades/   # Promobit, Pelando, MeuPC
│   └── precos/        # Zoom, Buscapé (histórico de preços)
├── core/              # DB, settings, models, matchers, métricas/alertas, logging
├── pipelines/         # Ingestão, enrich, agregações
├── posting/           # Message formatter, posting manager
├── telegram_bot/      # Bot e handlers
├── utils/             # Utilitários (anti-bot, cache, etc.)
└── app/               # Entradas do app/bot
```

### **Pastas de Apoio:**
```
tests/                 # Unit, api, e2e, helpers, data
scripts/               # Scripts de automação
apps/flet_dashboard/   # Dashboard Flet
config/                # Configurações (.env.example, etc.)
docs/                  # Documentação
```

## 🔒 **REGRAS OBRIGATÓRIAS (NUNCA VIOLAR)**

### **1. Organização de Arquivos:**
- **NUNCA** criar/modificar arquivos fora das pastas oficiais
- **SEMPRE** usar imports absolutos a partir de `src/`
- **NUNCA** duplicar arquivos (se já existir, alterar o existente)
- **NUNCA** commitar credenciais (ler de `.env` via `src/core/settings.py`)

### **2. Convenções de Código:**
- **Type hints obrigatórios** em todas as funções públicas
- **Docstrings** em todas as classes e métodos
- **Nomenclatura**: `snake_case.py` para arquivos, `PascalCase` para classes
- **Logs estruturados** com contexto e tratamento de erros

### **3. Padrão de Saída dos Scrapers:**
```python
@dataclass
class Offer:
    title: str
    price: Decimal
    original_price: Optional[Decimal]
    url: str                    # URL canônica não-afiliada
    store: str
    category: Optional[str]
    affiliate_url: Optional[str] # URL convertida para afiliado
    # ... outros campos
```

## 🔗 **REGRAS ESPECÍFICAS DE AFILIADOS**

### **Awin (Comfy, Trocafy, LG, KaBuM!, Samsung, Ninja):**
- ✅ **PODE**: Deeplinks com validação rígida de MIDs e AFFIDs
- ✅ **PODE**: MIDs configuráveis por loja
- ❌ **NÃO PODE**: URLs inválidas ou sem parâmetros obrigatórios

### **Amazon (ASIN-first):**
- ✅ **PODE**: Normalização automática com tag `garimpeirogee-20`
- ✅ **PODE**: Extração ASIN: URL → HTML → Playwright (fallback)
- ❌ **NÃO PODE**: Ofertas sem ASIN válido

### **Mercado Livre:**
- ✅ **PODE**: Etiqueta `garimpeirogeek` obrigatória
- ✅ **PODE**: Shortlinks `mercadolivre.com/sec/*`
- ❌ **NÃO PODE**: Produtos brutos sem etiqueta

### **Shopee (Shortlink via painel + cache):**
- ✅ **PODE**: Geração via painel/portal Shopee
- ✅ **PODE**: Cache local em `aff_cache.sqlite`
- ❌ **NÃO PODE**: Categorias proibidas

### **AliExpress (Shortlink via painel + cache):**
- ✅ **PODE**: Geração via painel/portal AliExpress
- ✅ **PODE**: Tracking ID configurável (`telegram`)
- ❌ **NÃO PODE**: Produtos brutos

### **Magazine Luiza:**
- ✅ **PODE**: Vitrine `magazinegarimpeirogeek` obrigatória
- ✅ **PODE**: Conversão automática de domínios
- ❌ **NÃO PODE**: Domínios fora da vitrine

### **Rakuten Advertising (Habilitável):**
- ✅ **PODE**: Feature flag `RAKUTEN_ENABLED=false` por padrão
- ✅ **PODE**: Tokens configuráveis para Hype Games e Nuuvem
- ❌ **NÃO PODE**: Parâmetros inválidos

## 🕷️ **POLÍTICA DE SCRAPING vs API**

### **Prioridade 1: APIs Oficiais**
- **AliExpress Open Platform**: Quando `USE_API_ALIEXPRESS=true`
- **Shopee Affiliate Open API**: Quando `USE_API_SHOPEE=true`
- **Awin Publisher API**: Quando `USE_API_AWIN=true`
- **Rakuten Advertising**: Quando `USE_API_RAKUTEN=true`

### **Prioridade 2: Scraping (Fallback)**
- **Rate limiting**: Respeitar delays configuráveis
- **Anti-bot**: Usar rotação de User-Agents e proxies
- **Retry exponencial**: Para falhas temporárias
- **Cache inteligente**: Evitar requisições desnecessárias

## 🚫 **O QUE NUNCA FAZER**

1. **Criar arquivos fora das pastas oficiais**
2. **Comitar credenciais ou tokens**
3. **Ignorar validação de afiliados**
4. **Postar links sem conversão para afiliados**
5. **Violar rate limits das APIs**
6. **Criar duplicatas de funcionalidades**
7. **Usar imports relativos**
8. **Ignorar type hints**
9. **Postar no Telegram sem modo DRY_RUN primeiro**
10. **Ignorar logs e métricas**

## ✅ **CRITÉRIOS DE ACEITE**

### **Antes de qualquer PR:**
1. `make fmt` - Formatação com black/isort
2. `make lint` - Linting com ruff
3. `make type` - Type checking com mypy
4. `make test` - Testes unitários
5. `make test-e2e` - Testes E2E

### **Critério de aceite automático:**
- **FALHAR** se qualquer arquivo novo for criado fora das pastas listadas
- **FALHAR** se não houver type hints
- **FALHAR** se não houver docstrings
- **FALHAR** se não houver testes

## 🔧 **EXEMPLOS DE "PODE/NÃO PODE"**

### **✅ PODE:**
```python
# ✅ Import correto
from src.scrapers.lojas.amazon import AmazonScraper

# ✅ Type hints
def validate_affiliate_url(url: str) -> ValidationResult:

# ✅ Docstring
def scrape_offers(self, max_offers: int = 10) -> List[Offer]:
    """Coleta ofertas da loja."""
```

### **❌ NÃO PODE:**
```python
# ❌ Import relativo
from ..core.models import Offer

# ❌ Sem type hints
def validate_url(url):

# ❌ Sem docstring
def scrape():
```

## 📚 **REFERÊNCIAS**

- **Especificação Funcional**: `docs/ESPECIFICACAO_GARIMPEIRO_GEEK.md`
- **Regras Awin**: `docs/awin_rules.md`
- **Exemplos de Afiliados**: `docs/affiliate_examples.md`
- **Integração Rakuten**: `docs/integracao_rakuten.md`
