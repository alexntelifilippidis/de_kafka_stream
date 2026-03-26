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
- **RisingWave** - Streaming SQL database (Kafka → SQL in real-time)
- **Kafka Streams / Flink / Spark Streaming** - Stream processing (planned)
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
- [x] Partition routing (fixed partition, random, or per-message)
- [x] Skewed-key / hot-partition mode for rebalance demos
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
- [x] **Batch consumer mode** (`consumer.poll()` — processes N messages per poll round)
- [x] Write unit tests for consumer
- [x] Add consumer monitoring

**Deliverable:** Working end-to-end producer-consumer flow

---

### Week 4: Stream Processing and Transformations
- [x] RisingWave streaming SQL integration
  - [x] Kafka → RisingWave streaming table
  - [x] Materialized views on top of streaming data
  - [x] Query live data via SQL
- [ ] Choose additional stream processing framework (Kafka Streams/Flink/etc.)
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
- [x] Runtime partition management (alter partitions → force consumer rebalance)
- [ ] Choose additional storage solution (Database, Data Lake, etc.)
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
make add-env PKG=name ENV=risingwave  # Add dependency to specific environment

# Development
make dev           # Start development environment

# ── Producer ────────────────────────────────────────────────────────────────
make produce                              # Send 1 message, random partition
make produce NUM_MESSAGES=10              # Send 10 messages, random partitions
make produce NUM_MESSAGES=10 PARTITION=0  # Send 10 messages, all to partition 0
make produce NUM_MESSAGES=10 PARTITION=1  # Send 10 messages, all to partition 1
make produce NUM_MESSAGES=10 PARTITION=2  # Send 10 messages, all to partition 2
make produce NUM_MESSAGES=10 PARTITION=-1 # Send 10 messages, random (default)

# Skewed-key / hot-partition mode
# SKEW_RATIO=80 means 80% of messages use HOT_KEY → same key → same partition
# → one partition fills up much faster → visible imbalance → triggers rebalance
make produce NUM_MESSAGES=30 SKEW_RATIO=80
make produce NUM_MESSAGES=50 SKEW_RATIO=90 HOT_KEY=EMP-HOT-999

# ── Consumer (single-message mode) ──────────────────────────────────────────
make consume                     # Consume messages indefinitely
make consume MAX_MESSAGES=10     # Stop after 10 messages
make consume GROUP=my-group      # Use a custom consumer group
make consume ENV=risingwave      # Sync RisingWave deps first

# ── Consumer (batch mode) ───────────────────────────────────────────────────
# Uses consumer.poll() — one network round-trip returns up to BATCH_SIZE records.
# Logs partition breakdown per batch so you can see which partition contributed what.
make consume-batch                          # 100 records/poll, unlimited batches
make consume-batch BATCH_SIZE=50            # 50 records per poll
make consume-batch BATCH_TIMEOUT_MS=5000    # Wait 5s per poll before retrying
make consume-batch MAX_BATCHES=3            # Stop after 3 non-empty poll rounds
make consume-batch GROUP=batch-group        # Dedicated consumer group

make test          # Run tests
make format        # Format code

# ── Docker/Podman (auto-detected) ───────────────────────────────────────────
make docker-up     # Start Kafka + RisingWave cluster
make docker-down   # Stop all containers
make docker-logs   # Tail logs

# ── Runtime partition management (forces consumer rebalance) ────────────────
# Kafka only allows INCREASING the partition count, never decreasing.
# After running this, every consumer in the group detects the metadata change
# on the next poll and triggers a group rebalance.
make kafka-alter-partitions TOPIC=codehub NUM_PARTITIONS=6

# ── RisingWave streaming table ──────────────────────────────────────────────
make rw-create-table             # Create employees streaming table (reads from Kafka)
make rw-query-table              # SELECT latest rows
make rw-drop-table               # Drop the table
make rw-delete-data              # DELETE all rows
make rw-delete-data ID=EMP-001   # DELETE a specific employee

# ── Cleanup ─────────────────────────────────────────────────────────────────
make clean         # Clean cache
make clean-all     # Deep clean (cache + venv + docker volumes)
```

---

## ⚡ Advanced Features

### 📦 Batch Consumer

The consumer supports two modes, switched via the `BATCH_MODE` environment variable:

| Mode | How it works |
|---|---|
| **Single** (default) | Iterates `for msg in consumer` — one message at a time |
| **Batch** | Calls `consumer.poll(max_records=N)` — returns up to N messages per round-trip |

Batch mode is significantly more efficient at high throughput: a single poll fetches a full chunk of records from all assigned partitions, and the output shows which partition contributed which records.

```
📦 Batch #1: 47 message(s) across 3 partition(s)
   └─ codehub[0]: 18 msg(s)  offsets 0–17
   └─ codehub[1]: 15 msg(s)  offsets 0–14
   └─ codehub[2]: 14 msg(s)  offsets 0–13
```

**Environment variables:**

| Variable | Default | Description |
|---|---|---|
| `BATCH_MODE` | `false` | Set to `true` / `1` / `yes` to enable |
| `BATCH_SIZE` | `100` | Max records returned per `poll()` call |
| `BATCH_TIMEOUT_MS` | `3000` | ms to wait per poll before retrying |
| `MAX_BATCHES` | _(unlimited)_ | Stop after N non-empty poll rounds |

---

### 🔥 Skewed-Key / Hot-Partition Producer

Used to demonstrate partition imbalance and force a consumer rebalance scenario.

**How it works:**  
Kafka uses Murmur2 hash of the message key to decide which partition to write to. If a large percentage of messages share the same key, they all land on the **same partition** — that partition accumulates lag, its consumer falls behind, and eventually the group coordinator triggers a rebalance.

**Environment variables:**

| Variable | Default | Description |
|---|---|---|
| `SKEW_RATIO` | `0` | % of messages sent with the hot key (0 = disabled) |
| `HOT_KEY` | `EMP-HOT-000` | The key that always routes to the same partition |

```bash
# 80% of 30 messages go to one partition → visible imbalance in Kafka UI
make produce NUM_MESSAGES=30 SKEW_RATIO=80

# 90% skew with a custom hot key
make produce NUM_MESSAGES=50 SKEW_RATIO=90 HOT_KEY=EMP-HOT-999
```

---

### ⚙️ Runtime Partition Alter (Force Rebalance)

Increasing a topic's partition count at runtime is one of the most direct ways to trigger a **consumer group rebalance** in Kafka.

**What happens:**
1. `kafka-topics.sh --alter` updates the broker metadata immediately.
2. On the next `poll()`, every consumer in the group fetches updated metadata, detects the partition count has changed, and the group coordinator initiates a rebalance.
3. Partitions are reassigned across all active consumers.

> ⚠️ **Note:** Kafka only allows *increasing* partition count — you cannot decrease it.

```bash
# Increase codehub from 3 → 6 partitions
make kafka-alter-partitions TOPIC=codehub NUM_PARTITIONS=6

# Output:
# ⚙️  Altering topic 'codehub' → 6 partition(s)...
# ✅ Done! Describe result:
# Topic: codehub  PartitionCount: 6  ReplicationFactor: 1
```

---

### 🗄️ RisingWave Streaming SQL

RisingWave connects directly to Kafka and ingests messages as a **streaming table** — data is available for SQL queries the moment it lands in Kafka.

**Connection details:**

| Field | Value |
|---|---|
| Host | `localhost` |
| Port | `4566` |
| User | `root` |
| Password | _(empty)_ |
| Database | `dev` |

```bash
# Connect via psql
psql -h localhost -p 4566 -U root -d dev

# Or use the RisingWave console at http://localhost:8020
```

**Useful queries:**
```sql
-- See all data in the streaming table
SELECT * FROM dev.public.employees;

-- Count messages per partition
SELECT _rw_kafka_partition, COUNT(*) FROM dev.public.employees GROUP BY 1 ORDER BY 1;

-- Latest arrivals
SELECT * FROM dev.public.employees ORDER BY timestamp DESC LIMIT 10;
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

#### Unrecognized Partition Error
If the producer throws `AssertionError: Unrecognized partition`, the requested partition number does not exist on the topic. Check the current partition count first:
```bash
docker exec kafka kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic codehub
```
Then use a valid partition number (0 to count-1), or increase the partition count:
```bash
make kafka-alter-partitions TOPIC=codehub NUM_PARTITIONS=6
```

---

## 📁 Project Structure
```
de_kafka_stream/
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── Makefile                # Task automation
├── pyproject.toml          # UV configuration
├── uv.lock                 # Dependency lock file
├── docker-compose.yml      # Kafka + RisingWave cluster
├── app/
│   ├── producer.py         # Kafka message producer (partition routing + skewed-key mode)
│   ├── consumer.py         # Kafka message consumer (single + batch mode)
│   ├── rising_wave.py      # RisingWave streaming table management
│   ├── kafka/
│   │   ├── __init__.py
│   │   └── kafka_client.py # Kafka client wrapper (producer, consumer, batch consumer)
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

**Last Updated:** March 26, 2026
