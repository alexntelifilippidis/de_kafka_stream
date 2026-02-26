# Data Engineering Kafka Stream POC

## 📋 Project Description

This is a Proof of Concept (POC) project focused on building a data engineering pipeline using Apache Kafka for real-time data streaming. The project aims to demonstrate best practices in stream processing, data ingestion, and real-time analytics.

### Goals
- Implement a robust Kafka streaming architecture
- Process real-time data streams efficiently
- Demonstrate data transformation and processing capabilities
- Build a scalable and maintainable data pipeline

### Tech Stack
- **Python** - Core programming language
- **Apache Kafka** - Distributed streaming platform
- **Kafka Streams / Flink / Spark Streaming** - Stream processing
- Additional tools and libraries TBD

---

## 📅 Weekly Tasks and Milestones

### Week 1: Project Setup and Environment Configuration
- [x] Initialize project repository
- [x] Set up development environment
  - [x] Install Python dependencies
- [x] Create project structure
  - [x] Set up app/ directory
  - [ ] Create tests/ directory
  - [x] Add configuration files
- [x] Document requirements and dependencies
- [x] Create docker-compose.yml for Kafka cluster

**Deliverable:** Working local Kafka cluster and project structure

---

### Week 2: Kafka Producer Implementation
- [ ] Design data schema for streaming events
- [x] Implement Kafka producer
  - [x] Configure producer settings (acks, retries, etc.)
  - [ ] Add serialization logic (JSON/Avro)
  - [x] Implement error handling and logging
- [x] Create sample data generator
- [ ] Write unit tests for producer
- [ ] Add monitoring and metrics

**Deliverable:** Functional Kafka producer with test data

---

### Week 3: Kafka Consumer Implementation
- [x] Implement Kafka consumer
  - [x] Configure consumer group and offset management
  - [x] Add deserialization logic
  - [x] Implement message processing logic
- [x] Set up consumer error handling
  - [x] Retry mechanisms
  - [x] Error logging
- [x] Write unit tests for consumer
- [x] Add consumer monitoring

**Deliverable:** Working end-to-end producer-consumer flow

---

### Week 4: Stream Processing and Transformations
- [ ] Choose stream processing framework (Kafka Streams/Flink/etc.)
- [ ] Implement data transformations
  - [ ] Filtering
  - [ ] Mapping
  - [ ] Aggregations
- [ ] Add windowing operations (if applicable)
- [ ] Implement stateful processing
- [ ] Write integration tests

**Deliverable:** Stream processing pipeline with transformations

---

### Week 5: Data Persistence and Storage
- [ ] Choose storage solution (Database, Data Lake, etc.)
- [ ] Implement data sink connectors
- [ ] Set up data partitioning strategy
- [ ] Add data validation and quality checks
- [ ] Implement data retention policies
- [ ] Performance testing and optimization

**Deliverable:** Complete data pipeline with storage

---

### Week 6: Monitoring, Logging, and Documentation
- [ ] Set up comprehensive monitoring
  - [ ] Kafka metrics (lag, throughput, etc.)
  - [ ] Application metrics
  - [ ] Set up dashboards (Grafana/Prometheus)
- [ ] Implement structured logging
- [ ] Add alerting mechanisms
- [ ] Performance benchmarking
- [ ] Complete documentation
  - [ ] Architecture diagrams
  - [ ] API documentation
  - [ ] Deployment guide
  - [ ] Runbook for operations

**Deliverable:** Production-ready POC with monitoring and documentation

---

### Week 7-8: Testing, Optimization, and Demo Preparation
- [ ] End-to-end testing
- [ ] Load testing and performance tuning
- [ ] Security hardening
  - [ ] Add authentication/authorization
  - [ ] Encrypt data in transit
- [ ] Code review and refactoring
- [ ] Prepare demo presentation
- [ ] Create demo scenarios
- [ ] Write final project report

**Deliverable:** Polished POC ready for demonstration

---

## 🚀 Getting Started

### Quick Start
```bash
make init          # First-time setup
make dev           # Start Kafka + run application
make help          # View all commands
```

### Prerequisites
- Python 3.12+
- UV package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Docker or Podman

### Configuration
```bash
# Copy .env.example to .env and configure
cp .env.example .env

# Edit .env with your settings
# LOG_LEVEL: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Common Commands
```bash
# Setup
make init          # Initialize project
make add PKG=name  # Add dependency
make add-env PKG=name ENV=doris  # Add dependency to specific environment

# Development
make dev           # Start development environment
make produce       # Run Kafka producer (default)
make produce ENV=doris      # Run producer with Doris dependencies
make produce ENV=starproject # Run producer with StarProject dependencies
make produce NUM_MESSAGES=10  # Send 10 random employee messages
make consume       # Run Kafka consumer (default)
make consume ENV=doris      # Run consumer with Doris dependencies
make consume ENV=starproject # Run consumer with StarProject dependencies
make consume MAX_MESSAGES=10  # Consume up to 10 messages then stop
make consume GROUP=my-group   # Consume with custom consumer group
make test          # Run tests
make format        # Format code

# Docker/Podman (auto-detected)
make docker-up     # Start Kafka cluster
make docker-down   # Stop Kafka cluster
make docker-logs   # View logs

# Cleanup
make clean         # Clean cache
make clean-all     # Deep clean
```

---

## 🔧 Troubleshooting

### RisingWave Issues

#### Connection Refused / Container Keeps Restarting
If you see errors like "connection refused" or "Streaming vnode mapping not found", RisingWave's internal state may be corrupted:

```bash
# Option 1: Use the make command
make risingwave-reset

# Option 2: Manual cleanup
docker compose down -v
docker volume rm de_kafka_stream_risingwave-data
docker compose up -d
```

#### RisingWave Crashes or OOM (Out of Memory)
If RisingWave keeps crashing, you may need to:
1. Increase Docker's memory limit (Docker Desktop > Settings > Resources)
2. Adjust memory settings in `docker-compose.yml`:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 8G  # Increase if you have more RAM
   ```

#### Checking RisingWave Logs
```bash
# View latest logs
docker logs risingwave --tail 50

# Follow logs in real-time
docker logs -f risingwave

# Check if server is ready
docker logs risingwave 2>&1 | grep "server started"
```

#### Testing Connection
```bash
# Test from inside the container
docker exec risingwave psql -h localhost -p 4566 -U root -d dev -c "SELECT 1;"

# Test from host
psql -h localhost -p 4566 -U root -d dev -c "SELECT 1;"
```

### Kafka Issues

#### Cannot Connect to Kafka
Make sure you're using the correct port:
- Internal (from other containers): `kafka:9092`
- External (from host): `localhost:29092`

---

## 📁 Project Structure
```
de_kafka_stream/
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── Makefile                # Task automation
├── pyproject.toml          # UV configuration
├── uv.lock                 # Dependency lock file
├── app/
│   ├── producer.py         # Kafka message producer
│   ├── consumer.py         # Kafka message consumer
│   ├── rising_wave.py      # RisingWave connection example
│   ├── kafka/
│   │   ├── __init__.py
│   │   └── kafka_client.py # Kafka client wrapper (producer & consumer)
│   └── utils/
│       ├── __init__.py
│       └── logger.py       # Colored logging utility
└── tests/
    ├── __init__.py
    ├── test_producer.py
    └── test_consumer.py    # Consumer unit tests
```

---

## 📝 Notes
- POC project for learning and demonstration
- Weekly tasks are flexible and adjustable
- Use `make help` to see all available commands
- Docker/Podman auto-detected for container operations
- RisingWave requires at least 4GB RAM for stable operation

---

**Last Updated:** February 25, 2026

