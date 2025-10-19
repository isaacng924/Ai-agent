.PHONY: install test deploy clean lint format help docker-build docker-run install-cdk

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	python3 -m pip install --upgrade pip
	pip3 install -r requirements.txt
	pip3 install -e .

install-dev: ## Install dependencies including dev tools
	python3 -m pip install --upgrade pip
	pip3 install -r requirements.txt
	pip3 install -e ".[dev]"

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

install-cdk: ## Install CDK dependencies
	cd infra/cdk && pip3 install -r requirements.txt

docker-build: ## Build Docker image locally
	docker build -t ai-job-connector:latest .

docker-run: ## Run Docker container locally
	docker run -p 8501:8501 \
		--env-file .env \
		-v ${HOME}/.aws:/root/.aws:ro \
		-e AWS_PROFILE=${AWS_PROFILE} \
		ai-job-connector:latest

docker-test: ## Build and test Docker container locally
	docker build -t ai-job-connector:latest .
	docker run -p 8501:8501 \
		--env-file .env \
		-v ${HOME}/.aws:/root/.aws:ro \
		-e AWS_PROFILE=${AWS_PROFILE} \
		ai-job-connector:latest

deploy-full: install-cdk ## Full deployment (install CDK deps + deploy)
	@echo "Checking prerequisites..."
	@which cdk > /dev/null || (echo "ERROR: AWS CDK CLI not found. Install it with: npm install -g aws-cdk" && exit 1)
	@echo "Setting environment variables from .env file..."
	@if [ ! -f .env ]; then echo "ERROR: .env file not found. Copy .env.example to .env and fill in values."; exit 1; fi
	@export $$(cat .env | grep -v '^#' | xargs) && cd infra/cdk && cdk deploy --all --require-approval never

get-url: ## Get the deployed App Runner URL
	@aws cloudformation describe-stacks --stack-name AIJobConnectorStack \
		--query 'Stacks[0].Outputs[?ExportName==`AIJobConnectorURL`].OutputValue' \
		--output text 2>/dev/null || echo "Stack not deployed yet. Run 'make deploy' first."

status: ## Check deployment status
	@echo "Checking App Runner service status..."
	@aws apprunner list-services --query 'ServiceSummaryList[?ServiceName==`ai-job-connector-web`].[ServiceName,Status,ServiceUrl]' \
		--output table 2>/dev/null || echo "No services found or AWS CLI not configured."
