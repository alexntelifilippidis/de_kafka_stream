.PHONY: help install sync update clean test lint format produce consume consume-batch run docker-up docker-down docker-logs init dev kafka-alter-partitions

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
	@echo "  make produce PARTITION=0         - Send all messages to partition 0"
	@echo "  make produce PARTITION=1         - Send all messages to partition 1"
	@echo "  make produce PARTITION=2         - Send all messages to partition 2"
	@echo "  make produce PARTITION=-1        - Send messages to random partitions (default)"
	@echo "  make produce NUM_PARTITIONS=3    - Number of partitions in the topic (default: 3)"
	@echo "  make produce SKEW_RATIO=80          - 80% of messages use HOT_KEY (fills one partition)"
	@echo "  make produce SKEW_RATIO=90 HOT_KEY=EMP-HOT-999 NUM_MESSAGES=30  - custom hot key"
	@echo "  make consume                     - Run Kafka consumer (default: development)"
	@echo "  make consume ENV=risingwave      - Run consumer with RisingWave dependencies"
	@echo "  make consume MAX_MESSAGES=10     - Consume up to 10 messages then stop"
	@echo "  make consume GROUP=my-group      - Consume with custom consumer group"
	@echo "  make consume-batch               - Run consumer in BATCH mode (poll-based)"
	@echo "  make consume-batch BATCH_SIZE=50 - Batch of up to 50 records per poll"
	@echo "  make consume-batch BATCH_TIMEOUT_MS=5000 - Wait 5 s per poll"
	@echo "  make consume-batch MAX_BATCHES=3 - Stop after 3 non-empty batches"
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
	@echo "  make kafka-alter-partitions TOPIC=codehub NUM_PARTITIONS=6  - Increase partitions → forces consumer rebalance"
	@echo ""
	@echo "Web UIs (after make docker-up):"
	@echo "  Kafka UI:           http://localhost:8080"
	@echo "  RisingWave Console: http://localhost:8020"
	@echo ""
	@echo "RisingWave Table:"
	@echo "  make rw-create-table             - Create the employees streaming table"
	@echo "  make rw-query-table              - Query the employees table"
	@echo "  make rw-drop-table               - Drop the employees table"
	@echo "  make rw-delete-data              - Delete all records from employees table"
	@echo "  make rw-delete-data ID=<id>      - Delete a specific employee record by ID"
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

# Run Kafka producer (use: make produce ENV=risingwave NUM_MESSAGES=10 PARTITION=0 SKEW_RATIO=80)
produce:
	@echo "📤 Starting Kafka Producer..."
	@if [ -n "$(ENV)" ]; then \
		echo "🌍 Environment: $(ENV)"; \
		echo "📦 Syncing dependencies for $(ENV)..."; \
		uv sync --group $(ENV); \
		NUM_MESSAGES=$(NUM_MESSAGES) \
		PARTITION=$(or $(PARTITION),-1) \
		NUM_PARTITIONS=$(or $(NUM_PARTITIONS),3) \
		SKEW_RATIO=$(or $(SKEW_RATIO),0) \
		HOT_KEY=$(or $(HOT_KEY),EMP-HOT-000) \
		ENV=$(ENV) uv run python -m app.producer; \
	else \
		echo "🌍 Environment: development (default)"; \
		NUM_MESSAGES=$(NUM_MESSAGES) \
		PARTITION=$(or $(PARTITION),-1) \
		NUM_PARTITIONS=$(or $(NUM_PARTITIONS),3) \
		SKEW_RATIO=$(or $(SKEW_RATIO),0) \
		HOT_KEY=$(or $(HOT_KEY),EMP-HOT-000) \
		uv run python -m app.producer; \
	fi

# Alias for backward compatibility
run: produce

# Run Kafka consumer in BATCH mode
# Usage: make consume-batch [BATCH_SIZE=100] [BATCH_TIMEOUT_MS=3000] [MAX_BATCHES=5] [GROUP=my-group] [ENV=dev]
consume-batch:
	@echo "📦 Starting Kafka Consumer in BATCH mode..."
	@if [ -n "$(ENV)" ]; then \
		echo "🌍 Environment: $(ENV)"; \
		echo "📦 Syncing dependencies for $(ENV)..."; \
		uv sync --group $(ENV); \
		if [ -n "$(GROUP)" ]; then \
			BATCH_MODE=true \
			BATCH_SIZE=$(or $(BATCH_SIZE),100) \
			BATCH_TIMEOUT_MS=$(or $(BATCH_TIMEOUT_MS),3000) \
			MAX_BATCHES=$(MAX_BATCHES) \
			KAFKA_CONSUMER_GROUP_ID=$(GROUP) \
			ENV=$(ENV) uv run python -m app.consumer; \
		else \
			BATCH_MODE=true \
			BATCH_SIZE=$(or $(BATCH_SIZE),100) \
			BATCH_TIMEOUT_MS=$(or $(BATCH_TIMEOUT_MS),3000) \
			MAX_BATCHES=$(MAX_BATCHES) \
			ENV=$(ENV) uv run python -m app.consumer; \
		fi \
	else \
		echo "🌍 Environment: development (default)"; \
		if [ -n "$(GROUP)" ]; then \
			BATCH_MODE=true \
			BATCH_SIZE=$(or $(BATCH_SIZE),100) \
			BATCH_TIMEOUT_MS=$(or $(BATCH_TIMEOUT_MS),3000) \
			MAX_BATCHES=$(MAX_BATCHES) \
			KAFKA_CONSUMER_GROUP_ID=$(GROUP) \
			uv run python -m app.consumer; \
		else \
			BATCH_MODE=true \
			BATCH_SIZE=$(or $(BATCH_SIZE),100) \
			BATCH_TIMEOUT_MS=$(or $(BATCH_TIMEOUT_MS),3000) \
			MAX_BATCHES=$(MAX_BATCHES) \
			uv run python -m app.consumer; \
		fi \
	fi

# ── Increase topic partitions at runtime → forces consumer group rebalance ──
# NOTE: Kafka only allows INCREASING the partition count, never decreasing.
# After this runs, every consumer in the group will trigger a rebalance and
# re-assign partitions on the next poll.
# Usage: make kafka-alter-partitions TOPIC=codehub NUM_PARTITIONS=6
kafka-alter-partitions:
	@if [ -z "$(TOPIC)" ]; then \
		echo "❌ Please specify TOPIC=<name>  e.g. make kafka-alter-partitions TOPIC=codehub NUM_PARTITIONS=6"; \
		exit 1; \
	fi
	@if [ -z "$(NUM_PARTITIONS)" ]; then \
		echo "❌ Please specify NUM_PARTITIONS=<n>  e.g. make kafka-alter-partitions TOPIC=codehub NUM_PARTITIONS=6"; \
		exit 1; \
	fi
	@echo "⚙️  Altering topic '$(TOPIC)' → $(NUM_PARTITIONS) partition(s)..."
	@echo "   (consumers in the group will rebalance on next poll)"
	$(CONTAINER_RUNTIME) exec kafka kafka-topics.sh \
		--alter \
		--bootstrap-server localhost:9092 \
		--topic $(TOPIC) \
		--partitions $(NUM_PARTITIONS)
	@echo "✅ Done! Describe result:"
	$(CONTAINER_RUNTIME) exec kafka kafka-topics.sh \
		--describe \
		--bootstrap-server localhost:9092 \
		--topic $(TOPIC)

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

# RisingWave table management
rw-create-table:
	@echo "📋 Creating RisingWave employees streaming table..."
	uv run --group risingwave python -c "from app.rising_wave import create_kafka_streaming_table; create_kafka_streaming_table()"

rw-query-table:
	@echo "🔍 Querying RisingWave employees table..."
	uv run --group risingwave python -c "from app.rising_wave import query_streaming_table; query_streaming_table(limit=20)"

rw-drop-table:
	@echo "🗑️  Dropping RisingWave employees table..."
	uv run --group risingwave python -c "from app.rising_wave import drop_streaming_table; drop_streaming_table()"
	@echo "✅ Table dropped!"

rw-delete-data:
	@echo "🧹 Deleting data from RisingWave employees table..."
	@if [ -n "$(ID)" ]; then \
		echo "Deleting employee with ID: $(ID)"; \
		uv run --group risingwave python -c "from app.rising_wave import delete_table_data; delete_table_data('$(ID)')"; \
	else \
		echo "Deleting ALL records from employees table"; \
		uv run --group risingwave python -c "from app.rising_wave import delete_table_data; delete_table_data()"; \
	fi

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

