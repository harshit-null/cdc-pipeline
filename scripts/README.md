# CDC Platform Scripts

Quick-start scripts to manage the entire CDC Platform application.

## Scripts

### `./start.sh`
Starts the entire CDC Platform with all services:
- MySQL (database)
- Kafka (message broker)
- Kafka Connect + Debezium (CDC connector)
- Elasticsearch (search engine)
- Kibana (visualization)
- Kafka UI (Kafka management)
- Django API (REST API)
- Kafka Consumer (event processor)

**Usage:**
```bash
./scripts/start.sh
```

**What it does:**
1. Starts all Docker containers
2. Waits for MySQL to be ready
3. Waits for Kafka to be ready
4. Waits for Elasticsearch to be ready
5. Waits for Kafka Connect to be ready
6. Registers the Debezium MySQL connector
7. Displays service status and access URLs

### `./stop.sh`
Stops all running services.

**Usage:**
```bash
# Stop containers (preserves data volumes)
./scripts/stop.sh

# Stop containers and remove all volumes
./scripts/stop.sh -v
```

### `./status.sh`
Shows the status of all services.

**Usage:**
```bash
./scripts/status.sh
```

**Output:**
- Running container list
- Health check status for each service
- Service access URLs

## Service URLs

After starting with `./start.sh`, access services at:

| Service | URL |
|---------|-----|
| Django API | http://localhost:8000 |
| Kafka UI | http://localhost:8080 |
| Kibana | http://localhost:5601 |
| Elasticsearch | http://localhost:9200 |
| Kafka Connect REST API | http://localhost:8083 |
| MySQL | localhost:3307 |

## Workflow

### First Time Setup
```bash
# Start all services
./scripts/start.sh

# Check status
./scripts/status.sh

# View logs
docker compose -f docker/local/docker-compose.yml logs -f
```

### Daily Usage
```bash
# Start services
./scripts/start.sh

# ... work on your project ...

# Stop services
./scripts/stop.sh
```

### Troubleshooting

**View logs for a specific service:**
```bash
docker compose -f docker/local/docker-compose.yml logs -f django
docker compose -f docker/local/docker-compose.yml logs -f kafka-consumer
```

**View Elasticsearch data:**
```bash
# View all products in the index
curl -s http://localhost:9200/products/_search | jq

# View index statistics
curl -s http://localhost:9200/products/_stats | jq

# View index mapping (schema)
curl -s http://localhost:9200/products/_mapping | jq

# Search for specific product
curl -s http://localhost:9200/products/_search?q=name:productname | jq
```

**Stop and remove all data:**
```bash
./scripts/stop.sh -v
```

**Manually restart a specific service:**
```bash
docker compose -f docker/local/docker-compose.yml restart django
```

## Environment

All environment variables are configured in `docker/local/docker-compose.yml`:

- **Django:** DEBUG, SECRET_KEY, ALLOWED_HOSTS, database config
- **Kafka Consumer:** KAFKA_BOOTSTRAP_SERVERS, ELASTICSEARCH_URL, etc.
- **Elasticsearch:** Single-node mode, no security for local dev

To modify settings, edit `docker/local/docker-compose.yml` directly.
