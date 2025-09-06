# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Unreleased]

## [1.0.0] - 2025-09-06

### Added
- **Fase 1: Testes E2E e Validações de Bloqueio**
  - Testes E2E completos para todas as plataformas de afiliados
  - Validação rigorosa de URLs por plataforma
  - Sistema de bloqueio para URLs inválidas
  - Modo DRY_RUN para testes sem publicação
  - Fixtures para bloquear acesso à rede durante testes
  - Documentação detalhada das regras de validação
  - Suporte a testes de falha e resiliência
  - Sistema de deduplicação de ofertas
  - Verificação de tipos estáticos com mypy
  - Linting automatizado com ruff

### Changed
- Melhor tratamento de erros nas validações
- Mensagens de erro mais descritivas
- Otimização no processamento de URLs

### Fixed
- Correção de falsos positivos na validação
- Ajustes na detecção de ofertas duplicadas
- Melhorias na cobertura de testes

### Removed
- Removida a integração com a Hotmart, que estava fora do escopo do projeto
- Removidas referências a redes não utilizadas (PerfectPay, Kiwify)

### Added
- Sistema completo de validação de conversores de afiliados
- Formatação dinâmica de mensagens para Telegram
- Agendador cron para tarefas automáticas
- Sistema de fila de ofertas com moderação
- Controle de qualidade automático
- Configuração de produção otimizada
- Sistema de monitoramento em tempo real
- Motor de otimização automático
- Cache distribuído com Redis
- Sistema de alertas de falhas
- Dashboard de métricas de conversão

### Changed
- Reestruturação completa da arquitetura do projeto
- Migração para estrutura `src/` padrão Python
- Atualização de todas as dependências
- Melhoria na organização dos testes

### Fixed
- Correções de bugs em conversores de afiliados
- Melhorias na validação de URLs
- Otimizações de performance

## [1.0.0] - 2024-12-01

### Added
- Sistema básico de scraping de ofertas
- Bot do Telegram para notificações
- Dashboard básico para monitoramento
- Sistema de métricas simples
- Backup automático de dados
- Testes unitários básicos

### Changed
- Estrutura inicial do projeto
- Configurações básicas de ambiente

### Fixed
- Bugs iniciais de configuração

---

## Tipos de Mudanças

- **Added** para novas funcionalidades
- **Changed** para mudanças em funcionalidades existentes
- **Deprecated** para funcionalidades que serão removidas em breve
- **Removed** para funcionalidades removidas
- **Fixed** para correções de bugs
- **Security** para correções de vulnerabilidades
