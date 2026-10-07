#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker/local/docker-compose.yml"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting CDC Platform...${NC}\n"

# Step 1: Start Docker services
echo -e "${BLUE}[1/7] Starting Docker services...${NC}"
docker compose -f "$DOCKER_COMPOSE_FILE" up -d
echo -e "${GREEN}✓ Docker services started${NC}\n"

# Step 2: Wait for MySQL
echo -e "${BLUE}[2/7] Waiting for MySQL to be ready...${NC}"
for i in {1..30}; do
  if docker exec cdc-mysql mysqladmin ping -h localhost -uroot &>/dev/null; then
    echo -e "${GREEN}✓ MySQL is ready${NC}\n"
    break
  fi
  echo -n "."
  sleep 2
done

# Step 3: Wait for Kafka
echo -e "${BLUE}[3/7] Waiting for Kafka to be ready...${NC}"
for i in {1..30}; do
  if docker exec cdc-kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list &>/dev/null; then
    echo -e "${GREEN}✓ Kafka is ready${NC}\n"
    break
  fi
  echo -n "."
  sleep 2
done

# Step 4: Wait for Elasticsearch
echo -e "${BLUE}[4/7] Waiting for Elasticsearch to be ready...${NC}"
for i in {1..30}; do
  if curl -fs http://localhost:9200 &>/dev/null; then
    echo -e "${GREEN}✓ Elasticsearch is ready${NC}\n"
    break
  fi
  echo -n "."
  sleep 2
done

# Step 5: Wait for Kafka Connect
echo -e "${BLUE}[5/7] Waiting for Kafka Connect to be ready...${NC}"
for i in {1..30}; do
  if curl -fs http://localhost:8083/connectors &>/dev/null; then
    echo -e "${GREEN}✓ Kafka Connect is ready${NC}\n"
    break
  fi
  echo -n "."
  sleep 2
done

# Step 6: Register Debezium connector
echo -e "${BLUE}[6/7] Registering Debezium MySQL connector...${NC}"
if [ -f "$PROJECT_ROOT/debezium/connector.json" ]; then
  curl -X POST -H "Content-Type: application/json" \
    -d @"$PROJECT_ROOT/debezium/connector.json" \
    http://localhost:8083/connectors 2>/dev/null || echo "Connector may already exist"
  echo -e "${GREEN}✓ Debezium connector registration attempt completed${NC}\n"
else
  echo -e "${YELLOW}⚠ Debezium connector.json not found at $PROJECT_ROOT/debezium/connector.json${NC}\n"
fi

# Step 7: Show service status
echo -e "${BLUE}[7/7] Service status:${NC}"
echo ""
docker compose -f "$DOCKER_COMPOSE_FILE" ps
echo ""

echo -e "${GREEN}✅ CDC Platform is ready!${NC}"
echo ""
echo -e "${YELLOW}Service URLs:${NC}"
echo "  • Django API:          http://localhost:8000"
echo "  • Kafka UI:            http://localhost:8080"
echo "  • Kibana:              http://localhost:5601"
echo "  • Elasticsearch:       http://localhost:9200"
echo "  • Kafka Connect:       http://localhost:8083"
echo "  • MySQL:               localhost:3307"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  • View logs:           docker compose -f $DOCKER_COMPOSE_FILE logs -f"
echo "  • View ES products:    curl -s http://localhost:9200/products/_search | jq"
echo "  • View ES index stats: curl -s http://localhost:9200/products/_stats | jq"
echo "  • View ES mapping:     curl -s http://localhost:9200/products/_mapping | jq"
echo "  • Stop services:       docker compose -f $DOCKER_COMPOSE_FILE down"
echo "  • Stop and remove data:docker compose -f $DOCKER_COMPOSE_FILE down -v"
