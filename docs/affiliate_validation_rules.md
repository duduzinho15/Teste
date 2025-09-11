# Regras de ValidaÃ§Ã£o de Afiliados

Este documento descreve as regras de validaÃ§Ã£o para cada plataforma de afiliado suportada.

## ð¦ Amazon

### â URLs VÃ¡lidas
- Deve conter um ASIN vÃ¡lido (B seguido de 9 caracteres alfanumÃ©ricos)
- Deve incluir a tag de afiliado: `tag=garimpeirogee-20`
- Exemplo: `https://www.amazon.com.br/dp/B07YFF3JCN/?tag=garimpeirogee-20`

### â URLs InvÃ¡lidas
- Sem ASIN
- Sem tag de afiliado
- Tag de afiliado incorreta

## ð Awin

### â URLs VÃ¡lidas
- Deve usar o domÃ­nio: `awin1.com/cread.php`
- MID deve estar na lista permitida: `23377, 51277, 33061, 17729, 106765, 25539`
- AFFID deve estar na lista permitida: `2370719, 2510157`
- Exemplo: `https://www.awin1.com/cread.php?awinmid=23377&awinaffid=2370719&ued=...`

### â URLs InvÃ¡lidas
- MID ou AFFID nÃ£o permitidos
- ParÃ¢metros ausentes
- DomÃ­nio incorreto

## ðï¸ Shopee

### â URLs VÃ¡lidas
- Deve usar shortlink: `s.shopee.com.br`
- Exemplo: `https://s.shopee.com.br/example`

### â URLs InvÃ¡lidas
- URLs completas (shopee.com.br)
- Categorias nÃ£o permitidas
- URLs de vitrine/coleÃ§Ã£o

## ð AliExpress

### â URLs VÃ¡lidas
- Deve usar shortlink: `s.click.aliexpress.com/e/`
- Deve incluir: `tracking_id=telegram`
- Exemplo: `https://s.click.aliexpress.com/e/_example?tracking_id=telegram`

### â URLs InvÃ¡lidas
- URLs diretas (pt.aliexpress.com/item/...)
- Sem tracking_id
- tracking_id incorreto

## ð± Mercado Livre

### â URLs VÃ¡lidas
- Shortlinks: `mercadolivre.com.br/sec/...`
- URLs sociais: `mercadolivre.com.br/social/garimpeirogeek/...`
- Exemplo: `https://www.mercadolivre.com.br/sec/example`

### â URLs InvÃ¡lidas
- URLs de produto diretas
- URLs sem validaÃ§Ã£o de afiliado

## ðª Magazine Luiza

### â URLs VÃ¡lidas
- Apenas vitrine: `magazinevoce.com.br/magazinegarimpeirogeek/...`
- Exemplo: `https://www.magazinevoce.com.br/magazinegarimpeirogeek/p/123`

### â URLs InvÃ¡lidas
- DomÃ­nio principal (`magazineluiza.com.br`)
- URLs fora da vitrine autorizada

## ð Regras Gerais

1. **ValidaÃ§Ã£o Estrita**: Todas as URLs sÃ£o validadas contra padrÃµes especÃ­ficos
2. **Bloqueio AutomÃ¡tico**: URLs invÃ¡lidas sÃ£o bloqueadas com mensagem de erro descritiva
3. **Logs Detalhados**: Todas as validaÃ§Ãµes sÃ£o registradas para auditoria
4. **Testes Automatizados**: Cobertura completa de testes para todas as regras

## ð§ª Testes

Para executar os testes de validaÃ§Ã£o:

```bash
# Testes unitÃ¡rios
make test-unit

# Testes E2E
make test-e2e

# Todos os testes
make test-all
```

## ð AtualizaÃ§Ãµes

- **2025-09-06**: VersÃ£o inicial do documento
- **2025-09-06**: Adicionadas regras para todas as plataformas suportadas

## Guardrail (Publicação)

- Função: `is_publishable_affiliate_url(url) -> (bool, reason)`
- Awin: domain == `www.awin1.com`, path == `/cread.php`, exige `awinmid`, `awinaffid`, `ued` (URL destino codificada)
- AliExpress: somente `https://s.click.aliexpress.com/e/...` com `tracking_id=telegram`
- Shopee: somente `https://s.shopee.com.br/{token}`
- Magazine Luiza: somente `https://www.magazinevoce.com.br/magazinegarimpeirogeek/.../p/{sku}`
- Mercado Livre: somente `.../sec/...` OU `.../social/garimpeirogeek?...matt_word=garimpeirogeek`
- Amazon: ASIN-first; inválido se não houver ASIN válido

Exemplos:
- Awin válido: `https://www.awin1.com/cread.php?awinmid=23377&awinaffid=2370719&ued=https%3A%2F%2Fexample.com%2Fp%2F123`
- AliExpress válido: `https://s.click.aliexpress.com/e/abc123?tracking_id=telegram`

## 🔥 Filtro de Ofertas

Parâmetros utilizados para identificar ofertas quentes:

- `discount >= 30%`
- `price <= 0.8 * price_90d` (preço médio dos últimos 90 dias)
