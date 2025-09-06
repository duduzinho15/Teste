# Regras de Validação de Afiliados

Este documento descreve as regras de validação para cada plataforma de afiliado suportada.

## 📦 Amazon

### ✅ URLs Válidas
- Deve conter um ASIN válido (B seguido de 9 caracteres alfanuméricos)
- Deve incluir a tag de afiliado: `tag=garimpeirogee-20`
- Exemplo: `https://www.amazon.com.br/dp/B07YFF3JCN/?tag=garimpeirogee-20`

### ❌ URLs Inválidas
- Sem ASIN
- Sem tag de afiliado
- Tag de afiliado incorreta

## 🔗 Awin

### ✅ URLs Válidas
- Deve usar o domínio: `awin1.com/cread.php`
- MID deve estar na lista permitida: `23377, 51277, 33061, 17729, 106765, 25539`
- AFFID deve estar na lista permitida: `2370719, 2510157`
- Exemplo: `https://www.awin1.com/cread.php?awinmid=23377&awinaffid=2370719&ued=...`

### ❌ URLs Inválidas
- MID ou AFFID não permitidos
- Parâmetros ausentes
- Domínio incorreto

## 🛍️ Shopee

### ✅ URLs Válidas
- Deve usar shortlink: `s.shopee.com.br`
- Exemplo: `https://s.shopee.com.br/example`

### ❌ URLs Inválidas
- URLs completas (shopee.com.br)
- Categorias não permitidas
- URLs de vitrine/coleção

## 🌏 AliExpress

### ✅ URLs Válidas
- Deve usar shortlink: `s.click.aliexpress.com/e/`
- Deve incluir: `tracking_id=telegram`
- Exemplo: `https://s.click.aliexpress.com/e/_example?tracking_id=telegram`

### ❌ URLs Inválidas
- URLs diretas (pt.aliexpress.com/item/...)
- Sem tracking_id
- tracking_id incorreto

## 📱 Mercado Livre

### ✅ URLs Válidas
- Shortlinks: `mercadolivre.com.br/sec/...`
- URLs sociais: `mercadolivre.com.br/social/garimpeirogeek/...`
- Exemplo: `https://www.mercadolivre.com.br/sec/example`

### ❌ URLs Inválidas
- URLs de produto diretas
- URLs sem validação de afiliado

## 🏪 Magazine Luiza

### ✅ URLs Válidas
- Apenas vitrine: `magazinevoce.com.br/magazinegarimpeirogeek/...`
- Exemplo: `https://www.magazinevoce.com.br/magazinegarimpeirogeek/p/123`

### ❌ URLs Inválidas
- Domínio principal (`magazineluiza.com.br`)
- URLs fora da vitrine autorizada

## 🔒 Regras Gerais

1. **Validação Estrita**: Todas as URLs são validadas contra padrões específicos
2. **Bloqueio Automático**: URLs inválidas são bloqueadas com mensagem de erro descritiva
3. **Logs Detalhados**: Todas as validações são registradas para auditoria
4. **Testes Automatizados**: Cobertura completa de testes para todas as regras

## 🧪 Testes

Para executar os testes de validação:

```bash
# Testes unitários
make test-unit

# Testes E2E
make test-e2e

# Todos os testes
make test-all
```

## 🔄 Atualizações

- **2025-09-06**: Versão inicial do documento
- **2025-09-06**: Adicionadas regras para todas as plataformas suportadas
