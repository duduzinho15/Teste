# Makefile para Garimpeiro Geek
# Sistema de Recomendações de Ofertas Telegram

.PHONY: help install test lint format clean docker-build docker-run docker-stop docs update-readme

# Default target
help:
	@echo "🚀 Garimpeiro Geek - Comandos disponíveis:"
	@echo ""
	@echo "📦 Desenvolvimento:"
	@echo "  install          - Instalar dependências"
	@echo "  test             - Executar todos os testes"
	@echo "  test-unit        - Executar testes unitários"
	@echo "  test-e2e         - Executar testes de integração"
	@echo "  lint             - Executar linting (ruff)"
	@echo "  format           - Formatar código (black + ruff)"
	@echo "  type-check       - Verificar tipos (mypy)"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  docker-build     - Construir imagens Docker"
	@echo "  docker-run       - Executar serviços com Docker Compose"
	@echo "  docker-stop      - Parar serviços Docker"
	@echo "  docker-logs      - Ver logs dos serviços"
	@echo "  docker-clean     - Limpar containers e volumes"
	@echo ""
	@echo "🔧 Utilitários:"
	@echo "  clean            - Limpar arquivos temporários"
	@echo "  docs             - Gerar documentação e atualizar README"
	@echo "  update-readme    - Atualizar README.md automaticamente"
	@echo "  release          - Criar nova release"

# Desenvolvimento
install:
	@echo "📦 Instalando dependências..."
	pip install -r requirements.txt
	pip install -e .

test:
	@echo "🧪 Executando todos os testes..."
	pytest tests/ -v --cov=src --cov-report=html

test-unit:
	@echo "🧪 Executando testes unitários..."
	pytest tests/unit/ -v

test-e2e:
	@echo "🧪 Executando testes de integração..."
	pytest tests/e2e/ -v

lint:
	@echo "🔍 Executando linting..."
	ruff check src/ tests/

format:
	@echo "🎨 Formatando código..."
	black src/ tests/
	ruff check --fix src/ tests/

type-check:
	@echo "🔍 Verificando tipos..."
	mypy src/

# Docker
docker-build:
	@echo "🐳 Construindo imagens Docker..."
	docker-compose build

docker-run:
	@echo "🐳 Iniciando serviços..."
	docker-compose up -d

docker-stop:
	@echo "🐳 Parando serviços..."
	docker-compose down

docker-logs:
	@echo "📋 Mostrando logs dos serviços..."
	docker-compose logs -f

docker-clean:
	@echo "🧹 Limpando Docker..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Utilitários
clean:
	@echo "🧹 Limpando arquivos temporários..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -rf build/ dist/ *.egg-info/

docs:
	@echo "📚 Gerando documentação..."
	@echo "📝 Atualizando README.md..."
	python scripts/update_readme.py

update-readme:
	@echo "📝 Atualizando README.md automaticamente..."
	python scripts/update_readme.py

release:
	@echo "🚀 Criando nova release..."
	@read -p "Digite a versão (ex: 1.0.0): " version; \
	git tag -a v$$version -m "Release v$$version"; \
	git push origin v$$version

# Comandos de desenvolvimento rápido
dev: install
	@echo "🚀 Ambiente de desenvolvimento configurado!"

quick-test: lint type-check test-unit
	@echo "✅ Verificações rápidas concluídas!"

# Comandos de produção
prod: docker-build docker-run
	@echo "🚀 Sistema de produção iniciado!"

# Comandos de monitoramento
monitor:
	@echo "📊 Monitorando sistema..."
	docker-compose ps
	docker-compose logs --tail=50

# Comandos de backup
backup:
	@echo "💾 Criando backup..."
	docker exec garimpeiro_redis redis-cli BGSAVE
	@echo "✅ Backup do Redis criado!"

# Comandos de manutenção
maintenance:
	@echo "🔧 Executando manutenção..."
	docker-compose exec redis redis-cli FLUSHDB
	@echo "✅ Cache limpo!"

