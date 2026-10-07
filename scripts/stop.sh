#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker/local/docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${RED}⛔ Stopping CDC Platform...${NC}\n"

# Check if -v or --remove-volumes flag is passed
if [[ "$1" == "-v" || "$1" == "--remove-volumes" ]]; then
  echo -e "${RED}Removing Docker containers and volumes...${NC}"
  docker compose -f "$DOCKER_COMPOSE_FILE" down -v
  echo -e "${GREEN}✓ All containers and volumes removed${NC}"
else
  echo -e "${RED}Stopping Docker containers...${NC}"
  docker compose -f "$DOCKER_COMPOSE_FILE" down
  echo -e "${GREEN}✓ All containers stopped${NC}"
  echo ""
  echo -e "To also remove volumes, run: $0 -v"
fi

echo ""
echo -e "${GREEN}✅ CDC Platform stopped!${NC}"
