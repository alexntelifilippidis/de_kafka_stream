.PHONY: help install sync update clean test lint format produce consume run docker-up docker-down docker-logs init dev

# Detect container runtime (prefer docker, fallback to podman)
CONTAINER_RUNTIME := $(shell command -v docker 2>/dev/null || command -v podman 2>/dev/null)
COMPOSE_CMD := $(shell command -v docker-compose 2>/dev/null || (command -v docker 2>/dev/null && echo "docker compose") || (command -v podman-compose 2>/dev/null) || echo "podman-compose")

# Default target - show help
help:
	@echo "🚀 Kafka Stream Project - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make init                        - Initialize project (install UV if needed, sync dependencies)"
	@echo "  make install                     - Install/sync all dependencies with UV"
	@echo "  make sync                        - Sync dependencies from lock file"
	@echo "  make sync-dev                    - Sync dev dependencies"
	@echo "  make sync-risingwave             - Sync RisingWave dependencies"
	@echo "  make sync-all                    - Sync all dependency groups"
	@echo "  make update                      - Update dependencies and lock file"
	@echo "  make add PKG=name                - Add a dependency"
	@echo "  make add-dev PKG=name            - Add a dev dependency"
	@echo "  make add-env PKG=name ENV=risingwave  - Add dependency to environment group"
	@echo ""
	@echo "Development:"
	@echo "  make dev                         - Start development environment (Kafka + app)"
	@echo "  make produce                     - Run Kafka producer (default: development)"
	@echo "  make produce ENV=risingwave      - Run producer with RisingWave dependencies"
	@echo "  make produce NUM_MESSAGES=10     - Send 10 random employee messages"
	@echo "  make produce NUM_MESSAGES=100    - Send 100 random employee messages"
	@echo "  make consume                     - Run Kafka consumer (default: development)"
	@echo "  make consume ENV=risingwave      - Run consumer with RisingWave dependencies"
	@echo "  make consume MAX_MESSAGES=10     - Consume up to 10 messages then stop"
	@echo "  make consume GROUP=my-group      - Consume with custom consumer group"
	@echo "  make test                        - Run tests"
	@echo "  make lint                        - Run linting checks"
	@echo "  make format                      - Format code"
	@echo ""
	@echo "Docker/Kafka:"
	@echo "  make docker-up                   - Start Kafka cluster"
	@echo "  make docker-down                 - Stop Kafka cluster"
	@echo "  make docker-logs                 - View Kafka logs"
	@echo "  make docker-clean                - Stop and remove all containers/volumes"
	@echo "  make risingwave-reset            - Reset RisingWave with clean state (fixes corruption)"
	@echo ""
	@echo "Web UIs (after make docker-up):"
	@echo "  Kafka UI:           http://localhost:8080"
	@echo "  RisingWave Console: http://localhost:8020"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                       - Clean up cache files and temp directories"
	@echo "  make clean-all                   - Deep clean (cache + venv + docker)"

# Initialize project - first time setup
init:
	@echo "🔧 Initializing project..."
	@command -v uv >/dev/null 2>&1 || { echo "Installing UV..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	@echo "📦 Syncing dependencies..."
	uv sync
	@echo "✅ Project initialized successfully!"

# Install/sync dependencies
install:
	@echo "📦 Installing dependencies..."
	uv sync

sync:
	@echo "🔄 Syncing dependencies from lock file..."
	uv sync

# Sync specific dependency groups
sync-dev:
	@echo "🔄 Syncing dev dependencies..."
	uv sync --group dev

sync-risingwave:
	@echo "🔄 Syncing RisingWave dependencies..."
	uv sync --group risingwave

sync-all:
	@echo "🔄 Syncing all dependency groups..."
	uv sync --group dev --group risingwave

# Update dependencies
update:
	@echo "⬆️  Updating dependencies..."
	uv lock --upgrade
	uv sync

# Add a new dependency (use: make add PKG=package-name)
add:
	@if [ -z "$(PKG)" ]; then \
		echo "❌ Please specify package: make add PKG=package-name"; \
		exit 1; \
	fi
	@echo "➕ Adding $(PKG)..."
	uv add $(PKG)

# Add a development dependency (use: make add-dev PKG=package-name)
add-dev:
	@if [ -z "$(PKG)" ]; then \
		echo "❌ Please specify package: make add-dev PKG=package-name"; \
		exit 1; \
	fi
	@echo "➕ Adding $(PKG) as dev dependency..."
	uv add --dev $(PKG)

# Add dependency to specific environment group (use: make add-env PKG=package-name ENV=risingwave)
add-env:
	@if [ -z "$(PKG)" ]; then \
		echo "❌ Please specify package: make add-env PKG=package-name ENV=risingwave"; \
		exit 1; \
	fi
	@if [ -z "$(ENV)" ]; then \
		echo "❌ Please specify environment: make add-env PKG=package-name ENV=risingwave"; \
		exit 1; \
	fi
	@echo "➕ Adding $(PKG) to $(ENV) dependency group..."
	uv add --group $(ENV) $(PKG)

# Run Kafka producer (use: make produce ENV=risingwave NUM_MESSAGES=10)
produce:
	@echo "📤 Starting Kafka Producer..."
	@if [ -n "$(ENV)" ]; then \
		echo "🌍 Environment: $(ENV)"; \
		echo "📦 Syncing dependencies for $(ENV)..."; \
		uv sync --group $(ENV); \
		if [ -n "$(NUM_MESSAGES)" ]; then \
			echo "📊 Number of messages: $(NUM_MESSAGES)"; \
			NUM_MESSAGES=$(NUM_MESSAGES) ENV=$(ENV) uv run python -m app.producer; \
		else \
			ENV=$(ENV) uv run python -m app.producer; \
		fi \
	else \
		echo "🌍 Environment: development (default)"; \
		if [ -n "$(NUM_MESSAGES)" ]; then \
			echo "📊 Number of messages: $(NUM_MESSAGES)"; \
			NUM_MESSAGES=$(NUM_MESSAGES) uv run python -m app.producer; \
		else \
			uv run python -m app.producer; \
		fi \
	fi

# Alias for backward compatibility
run: produce

# Run Kafka consumer (use: make consume ENV=risingwave MAX_MESSAGES=10 GROUP=my-group)
consume:
	@echo "📥 Starting Kafka Consumer..."
	@if [ -n "$(ENV)" ]; then \
		echo "🌍 Environment: $(ENV)"; \
		echo "📦 Syncing dependencies for $(ENV)..."; \
		uv sync --group $(ENV); \
		if [ -n "$(MAX_MESSAGES)" ]; then \
			echo "📊 Max messages: $(MAX_MESSAGES)"; \
		fi; \
		if [ -n "$(GROUP)" ]; then \
			echo "👥 Consumer group: $(GROUP)"; \
			KAFKA_CONSUMER_GROUP_ID=$(GROUP) MAX_MESSAGES=$(MAX_MESSAGES) ENV=$(ENV) uv run python -m app.consumer; \
		else \
			MAX_MESSAGES=$(MAX_MESSAGES) ENV=$(ENV) uv run python -m app.consumer; \
		fi \
	else \
		echo "🌍 Environment: development (default)"; \
		if [ -n "$(MAX_MESSAGES)" ]; then \
			echo "📊 Max messages: $(MAX_MESSAGES)"; \
		fi; \
		if [ -n "$(GROUP)" ]; then \
			echo "👥 Consumer group: $(GROUP)"; \
			KAFKA_CONSUMER_GROUP_ID=$(GROUP) MAX_MESSAGES=$(MAX_MESSAGES) uv run python -m app.consumer; \
		else \
			MAX_MESSAGES=$(MAX_MESSAGES) uv run python -m app.consumer; \
		fi \
	fi

# Start development environment
dev: docker-up
	@echo "🔥 Starting development environment..."
	@sleep 3
	@make produce

# Run tests
test:
	@echo "🧪 Running tests..."
	uv run pytest tests/ -v

# Run linting
lint:
	@echo "🔍 Running linting checks..."
	uv run ruff check .
	uv run mypy app/

# Format code
format:
	@echo "✨ Formatting code..."
	uv run ruff format .
	uv run ruff check --fix .

# Docker commands for Kafka
docker-up:
	@echo "🐳 Starting Kafka cluster..."
	@if [ -z "$(CONTAINER_RUNTIME)" ]; then \
		echo "❌ Neither docker nor podman found. Please install one."; \
		exit 1; \
	fi
	@if [ ! -f docker-compose.yml ]; then \
		echo "⚠️  docker-compose.yml not found. Please create it first."; \
		exit 1; \
	fi
	@echo "Using: $(COMPOSE_CMD)"
	$(COMPOSE_CMD) up -d
	@echo "✅ Kafka cluster started!"

docker-down:
	@echo "🛑 Stopping Kafka cluster..."
	@if [ -z "$(CONTAINER_RUNTIME)" ]; then \
		echo "❌ Neither docker nor podman found."; \
		exit 1; \
	fi
	$(COMPOSE_CMD) down

docker-logs:
	@echo "📋 Viewing Kafka logs..."
	@if [ -z "$(CONTAINER_RUNTIME)" ]; then \
		echo "❌ Neither docker nor podman found."; \
		exit 1; \
	fi
	$(COMPOSE_CMD) logs -f

docker-clean:
	@echo "🧹 Cleaning Docker resources..."
	@if [ -z "$(CONTAINER_RUNTIME)" ]; then \
		echo "❌ Neither docker nor podman found."; \
		exit 1; \
	fi
	$(COMPOSE_CMD) down -v --remove-orphans

# Reset RisingWave with clean state
risingwave-reset:
	@echo "🔄 Resetting RisingWave with clean state..."
	@if [ -z "$(CONTAINER_RUNTIME)" ]; then \
		echo "❌ Neither docker nor podman found."; \
		exit 1; \
	fi
	@echo "Stopping services..."
	$(COMPOSE_CMD) down
	@echo "Removing RisingWave volume..."
	$(CONTAINER_RUNTIME) volume rm de_kafka_stream_risingwave-data 2>/dev/null || true
	@echo "Starting services..."
	$(COMPOSE_CMD) up -d
	@echo "⏳ Waiting 20 seconds for RisingWave to initialize..."
	@sleep 20
	@echo "✅ RisingWave reset complete!"
	@echo "Check status with: make docker-logs"

# Clean cache and temporary files
clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cache cleaned!"

# Deep clean - including venv and docker
clean-all: clean docker-clean
	@echo "🧹 Deep cleaning project..."
	rm -rf .venv
	@echo "✅ Deep clean complete!"

# Show project info
info:
	@echo "📊 Project Information"
	@echo ""
	@echo "Python version:"
	@python3 --version
	@echo ""
	@echo "UV version:"
	@uv --version || echo "UV not installed"
	@echo ""
	@echo "Container Runtime:"
	@docker --version 2>/dev/null || echo "Docker not installed"
	@podman --version 2>/dev/null || echo "Podman not installed"
	@echo ""
	@echo "Active runtime: $(CONTAINER_RUNTIME)"
	@echo "Compose command: $(COMPOSE_CMD)"
	@echo ""
	@echo "Installed packages:"
	@uv pip list 2>/dev/null || echo "No packages installed yet"

