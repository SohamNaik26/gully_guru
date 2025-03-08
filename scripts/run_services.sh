#!/bin/bash

# Run services script for GullyGuru
# This script runs both the API and bot services simultaneously

# Set up colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting GullyGuru services...${NC}"

# Function to handle cleanup on exit
cleanup() {
    echo -e "${RED}Stopping all services...${NC}"
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

# Kill any existing bot or API processes
echo -e "${BLUE}Killing any existing bot or API processes...${NC}"
pkill -f "python -m src.main" 2>/dev/null
pkill -f "python -m src.bot.bot" 2>/dev/null
sleep 1

# Start the API server
echo -e "${BLUE}Starting API server...${NC}"
pipenv run python -m src.main &
API_PID=$!
echo -e "${GREEN}API server started with PID: $API_PID${NC}"

# Wait a moment for the API to start
sleep 2

# Start the Telegram bot
echo -e "${BLUE}Starting Telegram bot...${NC}"
pipenv run python -m src.bot.bot &
BOT_PID=$!
echo -e "${GREEN}Telegram bot started with PID: $BOT_PID${NC}"

# Check if the bot is actually running after a few seconds
sleep 3
if ! ps -p $BOT_PID > /dev/null; then
    echo -e "${RED}Bot process failed to start or exited quickly. Check logs for errors.${NC}"
    # Try to run it directly to see the output
    echo -e "${BLUE}Attempting to start bot directly...${NC}"
    pipenv run python -m src.bot.bot &
    BOT_PID=$!
    echo -e "${GREEN}Telegram bot restarted with PID: $BOT_PID${NC}"
fi

echo -e "${GREEN}All services are running. Press Ctrl+C to stop all services.${NC}"

# Wait for all background processes to finish
wait 