.PHONY: install test deploy clean lint format help

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	python3 -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .

install-dev: ## Install dependencies including dev tools
	python3 -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint: ## Run linting
	mypy src/
	ruff check src/

format: ## Format code
	black src/ tests/
	ruff check --fix src/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

deploy: ## Deploy infrastructure with CDK
	cd infra/cdk && cdk deploy --all --require-approval never

destroy: ## Destroy infrastructure
	cd infra/cdk && cdk destroy --all --force

synth: ## Synthesize CDK stack
	cd infra/cdk && cdk synth

logs: ## Tail CloudWatch logs (requires AWS CLI)
	aws logs tail /aws/lambda/job-connector-hr-lookup --follow

demo: ## Run demo with mock data
	python -m src.cli.main --mock demo

web: ## Launch web UI
	streamlit run src/web/app.py --server.port 8501 --server.address localhost

run-single: ## Run single job posting example
	python -m src.cli.main process --company "Anthropic" --title "AI Safety Researcher"

run-batch: ## Run batch example
	python -m src.cli.main batch --input examples/input_batch.json --output results.json

setup-venv: ## Create virtual environment
	python3.11 -m venv .venv
	@echo "Virtual environment created. Run 'source .venv/bin/activate' to activate it."

bootstrap-cdk: ## Bootstrap CDK (first time only)
	cd infra/cdk && cdk bootstrap
