.PHONY: help install dev test lint format clean docker-build docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation
install: ## Install all dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

# Development
dev: ## Start development servers
	docker-compose up

dev-backend: ## Start backend development server
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend development server
	cd frontend && npm run dev

# Testing
test: ## Run all tests
	cd backend && pytest
	cd frontend && npm test || true

test-backend: ## Run backend tests
	cd backend && pytest -v

test-frontend: ## Run frontend tests
	cd frontend && npm test

test-coverage: ## Run tests with coverage
	cd backend && pytest --cov=. --cov-report=html --cov-report=term

# Linting and Formatting
lint: ## Run all linters
	cd backend && flake8 . && black --check . && isort --check .
	cd frontend && npm run lint

lint-backend: ## Lint backend code
	cd backend && flake8 . && black --check . && isort --check .

lint-frontend: ## Lint frontend code
	cd frontend && npm run lint

format: ## Format all code
	cd backend && black . && isort .
	cd frontend && npm run format

format-backend: ## Format backend code
	cd backend && black . && isort .

format-frontend: ## Format frontend code
	cd frontend && npm run format

# Docker
docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-clean: ## Remove Docker containers and volumes
	docker-compose down -v

# Database
db-migrate: ## Run database migrations (if using Alembic)
	cd backend && alembic upgrade head

db-reset: ## Reset database (WARNING: deletes all data)
	docker-compose down -v
	docker-compose up -d postgres
	sleep 5
	cd backend && python -c "from models.database import init_db; init_db()"

# Cleanup
clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf backend/.pytest_cache
	rm -rf backend/.coverage
	rm -rf backend/htmlcov
	rm -rf frontend/dist
	rm -rf frontend/node_modules/.cache

clean-all: clean docker-clean ## Remove everything including Docker volumes

# CI/CD helpers
ci-backend: ## Run backend CI checks
	cd backend && \
	flake8 . && \
	black --check . && \
	isort --check . && \
	pytest --cov=. --cov-report=xml

ci-frontend: ## Run frontend CI checks
	cd frontend && \
	npm ci && \
	npm run lint && \
	npm run format:check && \
	npm run build

# Documentation
docs: ## Generate documentation (if using Sphinx/MkDocs)
	@echo "Documentation generation not yet configured"

# Security
security-check: ## Run security checks
	cd backend && pip install safety && safety check
	cd frontend && npm audit

# Environment setup
setup-env: ## Create .env file from example
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo ".env file created from .env.example"; \
		echo "Please update .env with your actual values"; \
	else \
		echo ".env file already exists"; \
	fi
