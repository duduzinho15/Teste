.PHONY: test test-unit test-e2e test-all lint typecheck

# Comandos de teste
test-unit:
	python -m pytest tests/unit -v

test-e2e:
	python -m pytest tests/e2e -v

test-all:
	python -m pytest tests -v

# Linting e type checking
lint:
	ruff check src tests

format:
	ruff format src tests

typecheck:
	mypy src tests

# Comando para instalar dependências
install:
	pip install -r requirements.txt

# Comando para rodar todos os checks
check: lint typecheck test-all
