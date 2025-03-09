#!/bin/bash

# Run API script for GullyGuru
# This script runs the API service

# Set up colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting GullyGuru API service...${NC}"

# Function to handle cleanup on exit
cleanup() {
    echo -e "${RED}Stopping API service...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set up trap for cleanup on script termination
trap cleanup SIGINT SIGTERM

# Check if pipenv is installed
if ! command -v pipenv &> /dev/null; then
    echo -e "${RED}Error: pipenv is not installed. Please install it first.${NC}"
    exit 1
fi

# Ensure we're in the project root directory
cd "$(dirname "$0")/.." || exit 1

# Load environment variables
if [ -f .env ]; then
    echo -e "${BLUE}Loading environment variables from .env file...${NC}"
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${RED}Warning: .env file not found. Make sure environment variables are set.${NC}"
fi

# Kill any existing processes using port 8000
echo -e "${BLUE}Checking for processes using port 8000...${NC}"
if command -v lsof &> /dev/null; then
    PORT_PID=$(lsof -ti:8000)
    if [ -n "$PORT_PID" ]; then
        echo -e "${BLUE}Killing process $PORT_PID using port 8000...${NC}"
        kill -9 $PORT_PID 2>/dev/null
        sleep 1
    fi
fi

# Kill any existing API processes
echo -e "${BLUE}Killing any existing API processes...${NC}"
pkill -f "python -m src.main" 2>/dev/null
sleep 1

# Start the API server
echo -e "${BLUE}Starting API server...${NC}"
pipenv run python -m src.main &
API_PID=$!
echo -e "${GREEN}API server started with PID: $API_PID${NC}"

echo -e "${GREEN}API service is running. Press Ctrl+C to stop the service.${NC}"

# Wait for all background processes to finish
wait 