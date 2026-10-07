#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker/local/docker-compose.yml"

# Colors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}📊 CDC Platform Service Status${NC}\n"

# Check if services are running
docker compose -f "$DOCKER_COMPOSE_FILE" ps

echo ""
echo -e "${YELLOW}Service Health Checks:${NC}\n"

# MySQL
if docker exec cdc-mysql mysqladmin ping -h localhost -uroot &>/dev/null; then
  echo -e "${GREEN}✓${NC} MySQL (3307)"
else
  echo -e "${RED}✗${NC} MySQL (3307)"
fi

# Kafka
if docker exec cdc-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list &>/dev/null; then
  echo -e "${GREEN}✓${NC} Kafka (19092)"
else
  echo -e "${RED}✗${NC} Kafka (19092)"
fi

# Elasticsearch
if curl -fs http://localhost:9200 &>/dev/null; then
  echo -e "${GREEN}✓${NC} Elasticsearch (9200)"
else
  echo -e "${RED}✗${NC} Elasticsearch (9200)"
fi

# Kafka Connect
if curl -fs http://localhost:8083/connectors &>/dev/null; then
  echo -e "${GREEN}✓${NC} Kafka Connect (8083)"
else
  echo -e "${RED}✗${NC} Kafka Connect (8083)"
fi

# Kibana
if curl -fs http://localhost:5601/api/status &>/dev/null; then
  echo -e "${GREEN}✓${NC} Kibana (5601)"
else
  echo -e "${RED}✗${NC} Kibana (5601)"
fi

# Kafka UI
if curl -fs http://localhost:8080 &>/dev/null; then
  echo -e "${GREEN}✓${NC} Kafka UI (8080)"
else
  echo -e "${RED}✗${NC} Kafka UI (8080)"
fi

# Django
if curl -fs http://localhost:8000 &>/dev/null; then
  echo -e "${GREEN}✓${NC} Django API (8000)"
else
  echo -e "${RED}✗${NC} Django API (8000)"
fi

echo ""
